import { handleModelResults } from "../../../../src/lib/model-results-handler.ts";

export default function handler(req: any, res: any) {
  const provider = String(req.query.provider ?? "");
  const model = String(req.query.model ?? "");
  handleModelResults(req, res, `${provider}/${model}`);
}
