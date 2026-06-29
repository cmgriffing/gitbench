import assert from "node:assert/strict";
import test from "node:test";
import { glob } from "node:fs/promises";

/**
 * Consolidated report API should expose no more than 11 Vercel serverless function
 * route files under `web/api`. This test guards the function budget
 * so future additions are explicit.
 */
test("API route file count stays within the 11-function budget", async () => {
  const apiDir = new URL("../api/", import.meta.url);
  const files = [];
  for await (const entry of glob("**/*.ts", { cwd: apiDir.pathname })) {
    files.push(entry);
  }
  files.sort();
  assert.ok(
    files.length <= 11,
    `Expected at most 11 API route files but found ${files.length}:\n${files.join("\n")}`
  );
});
