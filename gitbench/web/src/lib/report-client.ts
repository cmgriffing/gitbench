import type {
  BenchmarkDetail,
  FixtureDetail,
  ModelResultsFilters,
} from "@/lib/report-store";
import type { GitBenchData } from "@/lib/types";

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export interface HeatmapChartData {
  models: GitBenchData["models"];
  benchmarks: GitBenchData["benchmarks"];
  base_model_groups: GitBenchData["base_model_groups"];
  matrix: Record<string, ([number, number, number] | null)[]>;
}

export function loadSummary(): Promise<GitBenchData> {
  return getJson<GitBenchData>("/api/summary");
}

function loadChartData(
  chart: "pass-rate" | "cost" | "runtime" | "tokens" | "quadrant" | "heatmap",
  params: Record<string, string | undefined> = {},
): Promise<GitBenchData> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) query.set(key, value);
  }
  const suffix = query.size ? `?${query}` : "";
  return getJson<GitBenchData>(`/api/charts/${chart}${suffix}`);
}

export function loadPassRateChart(benchmark?: string): Promise<GitBenchData> {
  return loadChartData("pass-rate", { benchmark });
}

export function loadCostChart(): Promise<GitBenchData> {
  return loadChartData("cost");
}

export function loadRuntimeChart(): Promise<GitBenchData> {
  return loadChartData("runtime");
}

export function loadTokenChart(): Promise<GitBenchData> {
  return loadChartData("tokens");
}

export function loadQuadrantChart(): Promise<GitBenchData> {
  return loadChartData("quadrant");
}

export function loadHeatmapChart(): Promise<HeatmapChartData> {
  return getJson<HeatmapChartData>("/api/charts/heatmap");
}

export function loadBenchmark(benchmark: string): Promise<BenchmarkDetail> {
  return getJson<BenchmarkDetail>(
    `/api/benchmarks/${encodeURIComponent(benchmark)}`,
  );
}

export function loadModelResults(
  model: string,
  filters: ModelResultsFilters = {},
) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value);
  }
  const suffix = params.size ? `?${params}` : "";
  const path = model.split("/").map(encodeURIComponent).join("/");
  return getJson(`/api/models/${path}/results${suffix}`);
}

export function loadFixture(
  benchmark: string,
  fixture: string,
): Promise<FixtureDetail> {
  return getJson<FixtureDetail>(
    `/api/fixtures/${encodeURIComponent(benchmark)}/${encodeURIComponent(fixture)}`,
  );
}

export function loadHistory(): Promise<Pick<GitBenchData, "runs_meta">> {
  return getJson<Pick<GitBenchData, "runs_meta">>("/api/history");
}
