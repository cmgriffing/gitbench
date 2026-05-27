import { getReportStore } from "../../src/lib/node-sqlite-report-store.ts";
import { json, rejectUnsupportedQuery } from "../../src/lib/report-api.ts";

export default function handler(req: any, res: any) {
  const unsupported = rejectUnsupportedQuery(req.query, new Set(["benchmark"]));
  if (unsupported) {
    json(res, 400, { error: `Unsupported query parameter: ${unsupported}` });
    return;
  }

  const benchmark = String(req.query.benchmark ?? "");
  const result = getReportStore().getBenchmark(benchmark);
  if (!result) {
    json(res, 404, { error: `Benchmark not found: ${benchmark}` });
    return;
  }
  json(res, 200, result);
}
