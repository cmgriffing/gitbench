import { chartHandler } from "../../src/lib/chart-api.ts";

export default function handler(req: any, res: any) {
  chartHandler(req, res, "tokens");
}
