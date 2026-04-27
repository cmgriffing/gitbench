"""HTML report renderer for GitBench results."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_runs_from_dir(directory: str) -> list[dict]:
    """Load all run envelope JSON files from a directory.

    Args:
        directory: Path to directory containing JSON run files.

    Returns:
        List of run envelope dicts, sorted by timestamp.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    runs = []
    for f in sorted(dir_path.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if "version" in data and "results" in data:
                runs.append(data)
        except (json.JSONDecodeError, KeyError):
            continue

    runs.sort(key=lambda r: r.get("timestamp", ""))
    return runs


def load_runs_from_jsonl(path: str) -> list[dict]:
    """Load run envelopes from a JSONL file.

    Args:
        path: Path to JSONL file.

    Returns:
        List of run envelope dicts, sorted by timestamp.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    runs = []
    for line in file_path.read_text().strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            if "version" in data and "results" in data:
                runs.append(data)
        except (json.JSONDecodeError, KeyError):
            continue

    runs.sort(key=lambda r: r.get("timestamp", ""))
    return runs


def aggregate_runs(runs: list[dict]) -> dict[str, Any]:
    """Aggregate multiple runs into a structured summary for rendering.

    Args:
        runs: List of run envelope dicts.

    Returns:
        Dict with:
        - models: list of model names
        - benchmarks: list of benchmark names
        - model_summaries: {model: {total_runs, total_fixtures, total_passed, pass_at_k}}
        - matrix: {model: {benchmark: {pass_at_k, total, passed, avg_similarity}}}
        - fixtures: {model: {benchmark: [{fixture_id, passed, similarity, error}]}}
        - runs_meta: [{timestamp, model, profile, git_sha}]
    """
    models_set: set[str] = set()
    benchmarks_set: set[str] = set()
    model_data: dict[str, dict] = {}

    for run in runs:
        model = run["model"]
        models_set.add(model)

        if model not in model_data:
            model_data[model] = {
                "total_runs": 0,
                "total_fixtures": 0,
                "total_passed": 0,
                "benchmarks": {},
            }

        model_data[model]["total_runs"] += 1

        for result in run.get("results", []):
            if "error" in result and "benchmark" not in result:
                continue

            bench = result.get("benchmark", "unknown")
            benchmarks_set.add(bench)

            if bench not in model_data[model]["benchmarks"]:
                model_data[model]["benchmarks"][bench] = {
                    "total": 0,
                    "passed": 0,
                    "scores": [],
                    "fixtures": [],
                }

            bd = model_data[model]["benchmarks"][bench]
            bd["total"] += result.get("total", 0)
            bd["passed"] += result.get("passed", 0)

            for score in result.get("scores", []):
                bd["scores"].append(score.get("similarity", 0))
                bd["fixtures"].append({
                    "fixture_id": score.get("fixture_id", "?"),
                    "passed": score.get("passed", False),
                    "similarity": score.get("similarity", 0),
                    "error": score.get("error"),
                    "model_output": score.get("model_output", "")[:200],
                })

    # Build summaries and matrix
    model_summaries = {}
    matrix = {}
    fixtures = {}

    for model, data in model_data.items():
        model_summaries[model] = {
            "total_runs": data["total_runs"],
            "total_fixtures": data["total_fixtures"],
            "total_passed": data["total_passed"],
            "pass_at_k": round(
                data["total_passed"] / data["total_fixtures"], 4
            ) if data["total_fixtures"] > 0 else 0.0,
        }

        matrix[model] = {}
        fixtures[model] = {}

        for bench, bd in data["benchmarks"].items():
            avg_sim = round(sum(bd["scores"]) / len(bd["scores"]), 4) if bd["scores"] else 0.0
            matrix[model][bench] = {
                "pass_at_k": round(bd["passed"] / bd["total"], 4) if bd["total"] > 0 else 0.0,
                "total": bd["total"],
                "passed": bd["passed"],
                "avg_similarity": avg_sim,
            }
            fixtures[model][bench] = bd["fixtures"]

            # Roll up to model summary
            model_summaries[model]["total_fixtures"] += bd["total"]
            model_summaries[model]["total_passed"] += bd["passed"]

        # Recompute pass_at_k after rollup
        sf = model_summaries[model]
        sf["pass_at_k"] = round(
            sf["total_passed"] / sf["total_fixtures"], 4
        ) if sf["total_fixtures"] > 0 else 0.0

    runs_meta = []
    for run in runs:
        runs_meta.append({
            "timestamp": run.get("timestamp", ""),
            "model": run.get("model", ""),
            "profile": run.get("profile", ""),
            "git_sha": run.get("git_sha", ""),
        })

    return {
        "models": sorted(models_set),
        "benchmarks": sorted(benchmarks_set),
        "model_summaries": model_summaries,
        "matrix": matrix,
        "fixtures": fixtures,
        "runs_meta": runs_meta,
    }


def render_html(data: dict[str, Any], title: str = "GitBench Report") -> str:
    """Render aggregated data as a self-contained HTML report.

    Args:
        data: Aggregated data from aggregate_runs().
        title: HTML page title.

    Returns:
        Complete HTML string.
    """
    models = data["models"]
    benchmarks = data["benchmarks"]
    matrix = data["matrix"]
    model_summaries = data["model_summaries"]
    fixtures = data["fixtures"]

    # Prepare chart data
    summary_labels = json.dumps(models)
    summary_values = json.dumps([round(model_summaries[m]["pass_at_k"] * 100, 1) for m in models])

    # Per-benchmark grouped bar data
    bench_datasets = []
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
    for i, model in enumerate(models):
        values = []
        for bench in benchmarks:
            cell = matrix.get(model, {}).get(bench, {})
            values.append(round(cell.get("pass_at_k", 0) * 100, 1))
        bench_datasets.append({
            "label": model,
            "data": values,
            "backgroundColor": colors[i % len(colors)],
        })
    bench_datasets_json = json.dumps(bench_datasets)
    bench_labels_json = json.dumps(benchmarks)

    # Similarity data per model/benchmark
    sim_data = {}
    for model in models:
        sim_data[model] = {}
        for bench in benchmarks:
            fl = fixtures.get(model, {}).get(bench, [])
            sim_data[model][bench] = [
                {"id": f["fixture_id"], "sim": round(f["similarity"] * 100, 1), "passed": f["passed"]}
                for f in fl
            ]
    sim_data_json = json.dumps(sim_data)

    # Runs metadata
    runs_meta_json = json.dumps(data["runs_meta"])

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root {{
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #e2e8f0;
    --text-dim: #94a3b8;
    --accent: #3b82f6;
    --pass: #10b981;
    --fail: #ef4444;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 2rem;
    line-height: 1.6;
  }}
  h1 {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; }}
  h2 {{ font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-dim); }}
  h3 {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 0.75rem; }}
  .meta {{ color: var(--text-dim); font-size: 0.85rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
  }}
  .card .label {{ font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em; }}
  .card .value {{ font-size: 2rem; font-weight: 700; margin-top: 0.25rem; }}
  .card .value.pass {{ color: var(--pass); }}
  .card .value.fail {{ color: var(--fail); }}
  .card .sub {{ font-size: 0.8rem; color: var(--text-dim); margin-top: 0.25rem; }}
  .chart-row {{ display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; margin-bottom: 2rem; }}
  .chart-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
  }}
  canvas {{ max-height: 350px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }}
  th, td {{
    padding: 0.6rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ color: var(--text-dim); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  td.pass {{ color: var(--pass); }}
  td.fail {{ color: var(--fail); }}
  .bar {{
    display: inline-block;
    height: 8px;
    border-radius: 4px;
    background: var(--accent);
    vertical-align: middle;
    margin-left: 0.5rem;
  }}
  .section {{ margin-bottom: 2.5rem; }}
  @media (max-width: 768px) {{
    .chart-row {{ grid-template-columns: 1fr; }}
    body {{ padding: 1rem; }}
  }}
</style>
</head>
<body>

<h1>{title}</h1>
<div class="meta">Generated {generated} &middot; {len(data['runs_meta'])} run(s) &middot; {len(models)} model(s) &middot; {len(benchmarks)} benchmark(s)</div>

<!-- Summary cards -->
<div class="grid" id="summary-cards"></div>

<!-- Charts -->
<div class="chart-row">
  <div class="chart-card">
    <h3>Overall Pass Rate</h3>
    <canvas id="summaryChart"></canvas>
  </div>
  <div class="chart-card">
    <h3>Per-Benchmark Comparison</h3>
    <canvas id="benchChart"></canvas>
  </div>
</div>

<!-- Matrix table -->
<div class="section">
  <div class="chart-card">
    <h3>Results Matrix</h3>
    <table id="matrix-table">
      <thead><tr id="matrix-header"></tr></thead>
      <tbody id="matrix-body"></tbody>
    </table>
  </div>
</div>

<!-- Per-fixture details -->
<div class="section" id="fixture-details"></div>

<!-- Run metadata -->
<div class="section">
  <div class="chart-card">
    <h3>Run History</h3>
    <table>
      <thead><tr><th>Timestamp</th><th>Model</th><th>Profile</th><th>Git SHA</th></tr></thead>
      <tbody id="runs-body"></tbody>
    </table>
  </div>
</div>

<script>
const models = {summary_labels};
const benchmarks = {bench_labels_json};
const summaryValues = {summary_values};
const benchDatasets = {bench_datasets_json};
const simData = {sim_data_json};
const matrix = {json.dumps(matrix)};
const runsMeta = {runs_meta_json};
const modelSummaries = {json.dumps(model_summaries)};

// Summary cards
const cardsEl = document.getElementById('summary-cards');
models.forEach(m => {{
  const s = modelSummaries[m];
  const pct = (s.pass_at_k * 100).toFixed(1);
  const cls = s.pass_at_k >= 0.8 ? 'pass' : s.pass_at_k < 0.5 ? 'fail' : '';
  cardsEl.innerHTML += `
    <div class="card">
      <div class="label">${{m}}</div>
      <div class="value ${{cls}}">${{pct}}%</div>
      <div class="sub">${{s.total_passed}}/${{s.total_fixtures}} fixtures</div>
    </div>`;
}});

// Summary bar chart
new Chart(document.getElementById('summaryChart'), {{
  type: 'bar',
  data: {{
    labels: models,
    datasets: [{{ label: 'Pass %', data: summaryValues, backgroundColor: '#3b82f6' }}]
  }},
  options: {{
    indexAxis: 'y',
    scales: {{ x: {{ max: 100, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}, y: {{ ticks: {{ color: '#e2e8f0' }}, grid: {{ display: false }} }} }},
    plugins: {{ legend: {{ display: false }} }},
    responsive: true,
  }}
}});

// Bench comparison chart
new Chart(document.getElementById('benchChart'), {{
  type: 'bar',
  data: {{ labels: benchmarks, datasets: benchDatasets }},
  options: {{
    scales: {{
      y: {{ max: 100, ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }},
      x: {{ ticks: {{ color: '#e2e8f0', maxRotation: 45 }}, grid: {{ display: false }} }}
    }},
    plugins: {{ legend: {{ labels: {{ color: '#e2e8f0' }} }} }},
    responsive: true,
  }}
}});

// Matrix table
const headerEl = document.getElementById('matrix-header');
headerEl.innerHTML = '<th>Benchmark</th>' + models.map(m => `<th>${{m}}</th>`).join('');

const bodyEl = document.getElementById('matrix-body');
benchmarks.forEach(bench => {{
  let row = `<td>${{bench}}</td>`;
  models.forEach(m => {{
    const cell = matrix[m]?.[bench];
    if (cell) {{
      const pct = (cell.pass_at_k * 100).toFixed(1);
      const cls = cell.pass_at_k >= 0.8 ? 'pass' : cell.pass_at_k < 0.5 ? 'fail' : '';
      const barW = Math.round(cell.pass_at_k * 80);
      row += `<td class="${{cls}}">${{pct}}% <span class="bar" style="width:${{barW}}px"></span> <span style="color:#94a3b8;font-size:0.8rem">${{cell.passed}}/${{cell.total}}</span></td>`;
    }} else {{
      row += '<td style="color:#94a3b8">—</td>';
    }}
  }});
  bodyEl.innerHTML += `<tr>${{row}}</tr>`;
}});

// Fixture details per model
const detailsEl = document.getElementById('fixture-details');
models.forEach(m => {{
  let html = `<div class="chart-card" style="margin-bottom:1rem"><h3>${{m}} — Fixture Details</h3>`;
  benchmarks.forEach(bench => {{
    const fl = simData[m]?.[bench] || [];
    if (fl.length === 0) return;
    html += `<table style="margin-bottom:1rem"><thead><tr><th colspan="3">${{bench}}</th></tr>
      <tr><th>Fixture</th><th>Similarity</th><th>Result</th></tr></thead><tbody>`;
    fl.forEach(f => {{
      const cls = f.passed ? 'pass' : 'fail';
      const label = f.passed ? 'PASS' : 'FAIL';
      html += `<tr><td>${{f.id}}</td><td>${{f.sim}}%</td><td class="${{cls}}">${{label}}</td></tr>`;
    }});
    html += '</tbody></table>';
  }});
  html += '</div>';
  detailsEl.innerHTML += html;
}});

// Run history
const runsBody = document.getElementById('runs-body');
runsMeta.forEach(r => {{
  const ts = r.timestamp ? new Date(r.timestamp).toLocaleString() : '—';
  const sha = r.git_sha ? r.git_sha.slice(0, 8) : '—';
  runsBody.innerHTML += `<tr><td>${{ts}}</td><td>${{r.model}}</td><td>${{r.profile}}</td><td style="font-family:monospace">${{sha}}</td></tr>`;
}});
</script>

</body>
</html>"""
