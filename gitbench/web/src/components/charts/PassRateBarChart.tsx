import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { GitBenchData } from "@/lib/types";
import { loadPassRateChart } from "@/lib/report-client";
import { modelGroupPath } from "@/lib/routes";
import { getProviderColor } from "@/lib/provider-colors";
import ProviderIcon from "@/components/ProviderIcon";
import ModelSelector from "@/components/charts/ModelSelector";
import { useSyncedModelSelection } from "@/components/charts/useSyncedModelSelection";
import {
  buildGroupedMetricRows,
  passRateMetric,
  benchPassRateMetric,
} from "@/components/charts/model-groups";
import {
  ProviderLegend,
  VerticalGroupTick,
  formatCompactDecimal,
  paddedDomain,
  rowMap,
  tooltipStyle,
} from "@/components/charts/grouped-chart-ui";

interface PassRateBarChartProps {
  benchmarkName?: string;
}

export default function PassRateBarChart({ benchmarkName }: PassRateBarChartProps = {}) {
  const [data, setData] = useState<GitBenchData | null>(null);
  const { selectedGroups, setSelectedGroups } = useSyncedModelSelection(data);

  useEffect(() => {
    loadPassRateChart(benchmarkName).then(setData);
  }, [benchmarkName]);

  const chartData = useMemo(() => {
    if (!data) return [];
    const extractor = benchmarkName
      ? benchPassRateMetric(benchmarkName)
      : passRateMetric;
    return buildGroupedMetricRows(
      data,
      selectedGroups,
      extractor,
      "max",
    ).sort((a, b) => b.representativeValue - a.representativeValue);
  }, [data, selectedGroups, benchmarkName]);

  const rowsById = useMemo(() => rowMap(chartData), [chartData]);
  const yDomain = useMemo(
    () => paddedDomain(chartData, [0, 100], { floor: 0, ceiling: 100 }),
    [chartData],
  );

  const fixtureCount = useMemo(() => {
    if (!data || !benchmarkName) return 204;
    return Math.max(
      0,
      ...Object.values(data.matrix).map(
        (byBenchmark) => byBenchmark[benchmarkName]?.total ?? 0,
      ),
    );
  }, [data, benchmarkName]);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <div className="max-w-xs ml-auto w-full mb-3">
        <ModelSelector
          data={data}
          value={selectedGroups}
          onChange={setSelectedGroups}
        />
      </div>
      <div
        className="card"
      >
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={chartData}
            layout="horizontal"
            margin={{ top: 5, right: 20, left: 0, bottom: 58 }}
          >
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.04)" />
            <XAxis
              type="category"
              dataKey="id"
              tick={(props: any) => (
                <VerticalGroupTick {...props} rowMap={rowsById} />
              )}
              axisLine={false}
              tickLine={false}
              interval={0}
              height={62}
            />
            <YAxis
              type="number"
              domain={yDomain}
              tick={{
                fill: "var(--text-dim)",
                fontSize: 11,
                fontFamily: "var(--font-mono)",
              }}
              tickFormatter={(value: number) =>
                `${formatCompactDecimal(value, 2)}%`
              }
              axisLine={false}
              tickLine={false}
            />
            <Bar
              dataKey="range"
              radius={[4, 4, 4, 4]}
              barSize={Math.max(
                12,
                Math.min(28, 400 / Math.max(1, chartData.length)),
              )}
              cursor="pointer"
              onClick={(entry: any) => {
                if (entry?.provider && entry?.baseModel) {
                  window.location.href = modelGroupPath(
                    entry.provider,
                    entry.baseModel,
                  );
                }
              }}
            >
              {chartData.map((entry) => (
                <Cell key={entry.id} fill={getProviderColor(entry.provider)} />
              ))}
            </Bar>
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              content={({ active, label }) => {
                if (!active || !label) return null;
                const entry = rowsById[String(label)];
                if (!entry) return null;
                return (
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
                    {entry.efforts.map((effort) => (
                      <div
                        key={effort.modelName}
                        style={{ color: "var(--text-dim)" }}
                      >
                        {effort.reasoningLevel ?? "default"}:{" "}
                        {effort.value.toFixed(1)}%
                        {effort.modelName ===
                        entry.representativeEffort.modelName
                          ? " (best)"
                          : ""}
                      </div>
                    ))}
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
                      % of {fixtureCount} fixture{fixtureCount !== 1 ? "s" : ""} passed
                    </div>
                  </div>
                );
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ProviderLegend rows={chartData} />
    </div>
  );
}
