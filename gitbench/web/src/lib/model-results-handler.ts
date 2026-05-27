import { getReportStore } from "./node-sqlite-report-store.ts";
import { json, queryString, rejectUnsupportedQuery } from "./report-api.ts";

export function handleModelResults(req: any, res: any, model: string) {
  const unsupported = rejectUnsupportedQuery(req.query, new Set([
    "provider",
    "model",
    "benchmark",
    "difficulty",
    "tag",
  ]));
  if (unsupported) {
    json(res, 400, { error: `Unsupported query parameter: ${unsupported}` });
    return;
  }

  const result = getReportStore().getModelResults(model, {
    benchmark: queryString(req.query.benchmark),
    difficulty: queryString(req.query.difficulty),
    tag: queryString(req.query.tag),
  });
  if (!result) {
    json(res, 404, { error: `Model not found: ${model}` });
    return;
  }
  json(res, 200, result);
}
