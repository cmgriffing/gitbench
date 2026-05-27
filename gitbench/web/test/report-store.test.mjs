import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { DatabaseSync } from "node:sqlite";

import { NodeSqliteReportStore } from "../src/lib/node-sqlite-report-store.ts";

function withStore(fn) {
  const dir = mkdtempSync(path.join(tmpdir(), "gitbench-store-"));
  const dbPath = path.join(dir, "gitbench.db");
  const db = new DatabaseSync(dbPath);
  try {
    db.exec(readFileSync(path.resolve("data/schema.sql"), "utf8"));
    seed(db);
    fn(new NodeSqliteReportStore(db));
  } finally {
    db.close();
    rmSync(dir, { recursive: true, force: true });
  }
}

function seed(db) {
  db.exec(`
    INSERT INTO models (name, provider, base_model, reasoning_level)
    VALUES ('openai/gpt-test:high', 'openai', 'gpt-test', 'high');
    INSERT INTO benchmarks (name) VALUES ('commit_messages');
    INSERT INTO runs (
      timestamp, model_name, profile, git_sha, benchmark_suite_version,
      reasoning_level
    )
    VALUES (
      '2026-01-01T00:00:00Z', 'openai/gpt-test:high', 'default', 'abc123',
      '0.1.0', 'high'
    );
    INSERT INTO model_summaries (
      model_name, total_runs, total_fixtures, total_passed, pass_at_k,
      total_cost_usd, avg_cost_usd
    )
    VALUES ('openai/gpt-test:high', 1, 1, 1, 1.0, 0.01, 0.01);
    INSERT INTO model_runtimes (
      model_name, total_ms, avg_ms, min_ms, max_ms, fixture_count
    )
    VALUES ('openai/gpt-test:high', 25, 25, 25, 25, 1);
    INSERT INTO benchmark_summaries (
      model_name, benchmark_name, pass_at_k, total, passed, avg_similarity
    )
    VALUES ('openai/gpt-test:high', 'commit_messages', 1.0, 1, 1, 0.95);
    INSERT INTO fixtures (
      benchmark_name, fixture_id, prompt, expected, description, setup_json,
      purpose, difficulty
    )
    VALUES (
      'commit_messages', 'f001', 'prompt', 'expected', 'description',
      '["git init"]', 'purpose', 'easy'
    );
    INSERT INTO fixture_tags (benchmark_name, fixture_id, tag)
    VALUES ('commit_messages', 'f001', 'basic');
    INSERT INTO fixture_results (
      model_name, benchmark_name, fixture_id, passed, similarity, error,
      model_output, reasoning_level, input_tokens, output_tokens, total_tokens,
      cost_usd, duration_ms, purpose, difficulty, tags_json
    )
    VALUES (
      'openai/gpt-test:high', 'commit_messages', 'f001', 1, 0.95, NULL,
      'full output', 'high', 10, 5, 15, 0.01, 25, 'purpose', 'easy',
      '["basic"]'
    );
    INSERT INTO base_model_groups (id, provider, base_model)
    VALUES (1, 'openai', 'gpt-test');
    INSERT INTO base_model_group_levels (
      group_id, level, model_name, pass_at_k, total_cost_usd
    )
    VALUES (1, 'high', 'openai/gpt-test:high', 1.0, 0.01);
  `);
}

test("summary returns compact report data without full model output", () => {
  withStore((store) => {
    const summary = store.getSummary();
    assert.equal(summary.models.length, 1);
    assert.equal(summary.benchmarks[0], "commit_messages");
    assert.deepEqual(summary.fixtures, {});
    assert.deepEqual(summary.fixture_index, {});
    assert.equal(
      summary.model_token_summaries["openai/gpt-test:high"].total_tokens,
      15,
    );
  });
});

test("benchmark and model result queries return scoped rows", () => {
  withStore((store) => {
    const benchmark = store.getBenchmark("commit_messages");
    assert.equal(benchmark.benchmark, "commit_messages");
    assert.equal(benchmark.tag_counts.basic, 1);

    const model = store.getModelResults("openai/gpt-test:high", {
      benchmark: "commit_messages",
      difficulty: "easy",
      tag: "basic",
    });
    assert.equal(model.results.commit_messages[0].model_output, "");
  });
});

test("fixture detail returns full outputs and missing resources return null", () => {
  withStore((store) => {
    const fixture = store.getFixture("commit_messages", "f001");
    assert.equal(fixture.outputs[0].model_output, "full output");

    assert.equal(store.getBenchmark("missing"), null);
    assert.equal(store.getModelResults("missing"), null);
    assert.equal(store.getFixture("commit_messages", "missing"), null);
  });
});
