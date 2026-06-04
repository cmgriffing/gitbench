import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { DatabaseSync } from "node:sqlite";

test("build-db creates a queryable SQLite database from results JSON", () => {
  const dir = mkdtempSync(path.join(tmpdir(), "gitbench-build-db-"));
  const inputPath = path.join(dir, "results.json");
  const outputPath = path.join(dir, "gitbench.db");

  try {
    writeFileSync(inputPath, JSON.stringify(makeResults()));

    const result = spawnSync(
      process.execPath,
      [
        "scripts/build-db.mjs",
        "--input",
        inputPath,
        "--output",
        outputPath,
        "--schema",
        path.resolve("data/schema.sql"),
      ],
      {
        cwd: process.cwd(),
        encoding: "utf8",
      },
    );

    assert.equal(result.status, 0, result.stderr);

    const db = new DatabaseSync(outputPath, { readOnly: true });
    try {
      assert.equal(
        db.prepare("SELECT COUNT(*) AS count FROM models").get().count,
        1,
      );
      assert.equal(
        db.prepare("SELECT COUNT(*) AS count FROM fixture_results").get().count,
        2,
      );
      assert.equal(db.prepare("PRAGMA integrity_check").get().integrity_check, "ok");
      assert.deepEqual(db.prepare("PRAGMA foreign_key_check").all(), []);
      assert.deepEqual(
        db
          .prepare(
            `SELECT fixture_id, duration_ms, api_duration_ms
             FROM fixture_results
             ORDER BY fixture_id`,
          )
          .all()
          .map((row) => ({ ...row })),
        [
          { fixture_id: "f001", duration_ms: 25, api_duration_ms: 12.5 },
          { fixture_id: "f002", duration_ms: 40, api_duration_ms: null },
        ],
      );

      const schema = readFileSync(path.resolve("data/schema.sql"), "utf8");
      assert.match(schema, /idx_benchmark_summaries_leaderboard/);
    } finally {
      db.close();
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

function makeResults() {
  return {
    models: [
      {
        name: "openai/gpt-test:high",
        provider: "openai",
        baseModel: "gpt-test",
        reasoningLevel: "high",
      },
    ],
    benchmarks: ["commit_messages"],
    model_summaries: {
      "openai/gpt-test:high": {
        total_runs: 1,
        total_fixtures: 2,
        total_passed: 2,
        pass_at_k: 1,
        total_cost_usd: 0.01,
        avg_cost_usd: 0.01,
      },
    },
    model_runtimes: {
      "openai/gpt-test:high": {
        total_ms: 12.5,
        avg_ms: 12.5,
        min_ms: 12.5,
        max_ms: 12.5,
        fixture_count: 1,
      },
    },
    matrix: {
      "openai/gpt-test:high": {
        commit_messages: {
          pass_at_k: 1,
          total: 2,
          passed: 2,
          avg_similarity: 0.95,
        },
      },
    },
    fixtures: {
      "openai/gpt-test:high": {
        commit_messages: [
          {
            fixture_id: "f001",
            passed: true,
            similarity: 0.95,
            error: null,
            model_output: "full output",
            reasoning_level: "high",
            input_tokens: 10,
            output_tokens: 5,
            total_tokens: 15,
            cost_usd: 0.01,
            duration_ms: 25,
            api_duration_ms: 12.5,
            purpose: "purpose",
            difficulty: "easy",
            tags: ["basic"],
          },
          {
            fixture_id: "f002",
            passed: true,
            similarity: 0.95,
            error: null,
            model_output: "full output",
            reasoning_level: "high",
            input_tokens: 10,
            output_tokens: 5,
            total_tokens: 15,
            cost_usd: 0.01,
            duration_ms: 40,
            purpose: "purpose",
            difficulty: "easy",
            tags: ["basic"],
          },
        ],
      },
    },
    fixture_index: {
      "commit_messages/f001": {
        id: "f001",
        benchmark: "commit_messages",
        prompt: "prompt",
        expected: "expected",
        description: "description",
        setup: ["git init"],
        purpose: "purpose",
        difficulty: "easy",
        tags: ["basic"],
      },
      "commit_messages/f002": {
        id: "f002",
        benchmark: "commit_messages",
        prompt: "prompt",
        expected: "expected",
        description: "description",
        setup: ["git init"],
        purpose: "purpose",
        difficulty: "easy",
        tags: ["basic"],
      },
    },
    runs_meta: [
      {
        timestamp: "2026-01-01T00:00:00Z",
        model: "openai/gpt-test:high",
        profile: "default",
        git_sha: "abc123",
        benchmark_suite_version: "0.1.0",
        reasoning_level: "high",
      },
    ],
    base_model_groups: [
      {
        provider: "openai",
        baseModel: "gpt-test",
        levels: [
          {
            level: "high",
            modelName: "openai/gpt-test:high",
            pass_at_k: 1,
            total_cost_usd: 0.01,
          },
        ],
      },
    ],
  };
}
