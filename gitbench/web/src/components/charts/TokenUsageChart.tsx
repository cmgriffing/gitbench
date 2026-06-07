import { useEffect, useMemo, useState } from "react";
import type { GitBenchData } from "@/lib/types";
import { loadTokenChart } from "@/lib/report-client";
import ProviderIcon from "@/components/ProviderIcon";
import ModelOutputControls from "@/components/charts/ModelOutputControls";
import { useSyncedModelSelection } from "@/components/charts/useSyncedModelSelection";
import {
  buildGroupedMetricRows,
  tokenMetric,
  writeStoredOutputMode,
} from "@/components/charts/model-groups";
import {
  GroupedMetricTooltipSections,
  VerticalGroupedMetricChart,
  formatCompactDecimal,
  tooltipStyle,
  zeroAnchoredDomain,
} from "@/components/charts/grouped-chart-ui";

function formatTokens(value: number): string {
  if (value >= 1_000_000)
    return `${formatCompactDecimal(value / 1_000_000, 2)}M`;
  if (value >= 1_000) return `${formatCompactDecimal(value / 1_000, 2)}K`;
  return formatCompactDecimal(value, 2);
}

export default function TokenUsageChart() {
  const [data, setData] = useState<GitBenchData | null>(null);
  const {
    selectedGroups,
    setSelectedGroups,
    outputMode,
    setOutputMode,
    availableOutputModes,
  } = useSyncedModelSelection(data);

  useEffect(() => {
    loadTokenChart().then(setData);
  }, []);

  const chartData = useMemo(() => {
    if (!data) return [];
    const rows = buildGroupedMetricRows(
      data,
      selectedGroups,
      tokenMetric,
      "median",
      outputMode
    ).sort((a, b) => a.sortValue - b.sortValue);

    // Compute stacked segment totals for each row
    for (const row of rows) {
      const textMode = row.modes.text;
      if (textMode) {
        let textIn = 0, textOut = 0, textReason = 0;
        for (const effort of textMode.efforts) {
          textIn += effort.inputTokens ?? 0;
          textOut += effort.outputTokens ?? 0;
          textReason += effort.reasoningTokens ?? 0;
        }
        row.textInputTokens = textIn;
        row.textOutputTokens = textOut;
        row.textReasoningTokens = textReason;
        row.hasReasoningData = textMode.efforts.some(
          (e) => e.reasoningLevel && (e.reasoningTokens ?? 0) > 0
        );
      }
      const jsonMode = row.modes.json_schema;
      if (jsonMode) {
        let jsonIn = 0, jsonOut = 0, jsonReason = 0;
        for (const effort of jsonMode.efforts) {
          jsonIn += effort.inputTokens ?? 0;
          jsonOut += effort.outputTokens ?? 0;
          jsonReason += effort.reasoningTokens ?? 0;
        }
        row.jsonInputTokens = jsonIn;
        row.jsonOutputTokens = jsonOut;
        row.jsonReasoningTokens = jsonReason;
        row.hasReasoningData = row.hasReasoningData || jsonMode.efforts.some(
          (e) => e.reasoningLevel && (e.reasoningTokens ?? 0) > 0
        );
      }
    }
    return rows;
  }, [data, selectedGroups, outputMode]);

  const yDomain = useMemo(
    () => zeroAnchoredDomain(chartData, [0, 1]),
    [chartData]
  );
  const allZero =
    chartData.length === 0 || chartData.every((row) => row.maxValue === 0);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <ModelOutputControls
        data={data}
        selectedGroups={selectedGroups}
        onSelectedGroupsChange={setSelectedGroups}
        outputMode={outputMode}
        onOutputModeChange={(mode) => {
          setOutputMode(mode);
          writeStoredOutputMode(mode);
        }}
        availableOutputModes={availableOutputModes}
      />
      {allZero ? (
        <div className="card p-8 text-center">
          <div className="font-display text-base text-(--text-dim) mb-1">
            No token data available
          </div>
          <div className="font-mono text-xs text-(--text-dim) opacity-60">
            Token usage data was not collected for these benchmark runs.
          </div>
        </div>
      ) : (
        <VerticalGroupedMetricChart
          rows={chartData}
          outputMode={outputMode}
          yDomain={yDomain}
          yTickFormatter={formatTokens}
          renderTooltip={(entry) => (
            <div style={tooltipStyle}>
              <div
                style={{
                  color: "var(--text)",
                  marginBottom: 4,
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                <ProviderIcon provider={entry.provider} size={14} />
                {entry.provider}/{entry.baseModel}
              </div>
              <GroupedMetricTooltipSections
                entry={entry}
                outputMode={outputMode}
                formatRepresentative={formatTokens}
                renderEffort={(effort) => (
                  <span style={{ color: "var(--text-dim)" }}>
                    {effort.reasoningLevel ?? "default"}:{" "}
                    {formatTokens(effort.value)}
                    {effort.inputTokens || effort.outputTokens
                      ? ` (in ${formatTokens(
                          effort.inputTokens ?? 0
                        )} / out ${formatTokens(effort.outputTokens ?? 0)}${effort.reasoningLevel && effort.reasoningTokens !== undefined ? ` / r ${formatTokens(effort.reasoningTokens ?? 0)}` : ""})`
                      : ""}
                  </span>
                )}
              />
              <div
                style={{
                  borderTop: "1px solid rgba(255,255,255,0.06)",
                  margin: "6px 0",
                }}
              />
              <div
                style={{
                  color: "var(--text-dim)",
                  fontSize: 10,
                  lineHeight: 1.4,
                }}
              >
                Tokens in + out. Fewer is more efficient.
              </div>
            </div>
          )}
        />
      )}
    </div>
  );
}
