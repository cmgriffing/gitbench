const allowedModelResultFilters = new Set(["benchmark", "difficulty", "tag"]);

export function json(res: any, status: number, body: unknown): void {
  res.status(status).setHeader("content-type", "application/json");
  res.end(JSON.stringify(body));
}

export function rejectUnsupportedQuery(
  query: Record<string, unknown>,
  allowed: Set<string> = allowedModelResultFilters,
): string | null {
  for (const key of Object.keys(query)) {
    if (!allowed.has(key)) return key;
  }
  return null;
}

export function queryString(value: unknown): string | undefined {
  if (Array.isArray(value)) return value[0] ? String(value[0]) : undefined;
  return value === undefined ? undefined : String(value);
}
