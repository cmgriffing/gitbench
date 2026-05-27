import { chartData, type ChartKey } from "./chart-data.ts";
import { getReportStore } from "./node-sqlite-report-store.ts";
import { json, queryString, rejectUnsupportedQuery } from "./report-api.ts";

export function chartHandler(req: any, res: any, chart: ChartKey): void {
  const unsupported = rejectUnsupportedQuery(req.query, new Set(["benchmark"]));
  if (unsupported) {
    json(res, 400, { error: `Unsupported query parameter: ${unsupported}` });
    return;
  }

  const benchmark = queryString(req.query.benchmark);
  json(res, 200, chartData(chart, getReportStore().getSummary(), benchmark));
}
