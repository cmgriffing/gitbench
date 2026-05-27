import { getReportStore } from "../src/lib/node-sqlite-report-store.ts";
import { json, rejectUnsupportedQuery } from "../src/lib/report-api.ts";

export default function handler(req: any, res: any) {
  const unsupported = rejectUnsupportedQuery(req.query, new Set());
  if (unsupported) {
    json(res, 400, { error: `Unsupported query parameter: ${unsupported}` });
    return;
  }
  json(res, 200, { runs_meta: getReportStore().getHistory() });
}
