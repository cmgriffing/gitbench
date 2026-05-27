import type { GitBenchData } from "@/lib/types";
import { loadSummary } from "@/lib/report-client";

let cachedData: GitBenchData | null = null;
let pendingData: Promise<GitBenchData> | null = null;

export async function loadData(): Promise<GitBenchData> {
  if (cachedData) {
    return cachedData;
  }

  if (!pendingData) {
    pendingData = loadSummary()
      .then((data) => {
        cachedData = data;
        return data;
      })
      .catch((error) => {
        pendingData = null;
        throw error;
      });
  }

  return pendingData;
}

export function getCachedData(): GitBenchData | null {
  return cachedData;
}
