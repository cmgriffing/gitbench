import { useState, useEffect, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
  Tooltip,
} from "recharts";
import type { GitBenchData } from "@/lib/types";
import { loadData } from "@/lib/load-data";
import ModelSelector from "./ModelSelector";
import ProviderIcon from "@/components/ProviderIcon";
import { modelLevelPath } from "@/lib/routes";
import { getProviderColor } from "@/lib/provider-colors";

/** Truncate a model name for display, preserving end characters. */
function truncateName(name: string, maxLen = 10): string {
  if (!name || name.length <= maxLen) return name || "";
  return name.slice(0, maxLen - 1) + "…";
}

interface CustomTickProps {
  x: number;
  y: number;
  payload: {
    value: string;
    index: number;
    coordinate: number;
  };
  modelMap?: Record<
    string,
    {
      provider: string;
      baseModel: string;
      reasoningLevel: string | null;
      name: string;
    }
  >;
}

function CustomXAxisTick(props: CustomTickProps) {
  const { x, y, payload, modelMap } = props;
  const modelName = payload.value;
  const info = modelMap?.[modelName];
  const baseName = truncateName(info?.baseModel || modelName);

  return (
    <g transform={`translate(${x},${y})`}>
      <g transform="rotate(-40)">
        {/* Provider icon + model name + level */}
        <foreignObject
          x={-100}
          y={-4}
          width={120}
          height={32}
          style={{ overflow: "visible" }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              gap: 3,
              fontSize: 9,
              fontFamily: "var(--font-mono)",
              color: "var(--text-mid)",
              whiteSpace: "nowrap",
              justifyContent: "center",
            }}
          >
            <ProviderIcon provider={info?.provider || ""} size={12} />
            <span>{baseName}</span>
            {info?.reasoningLevel && (
              <span style={{ color: "var(--text-dim)", fontSize: 8 }}>
                {info.reasoningLevel}
              </span>
            )}
          </div>
        </foreignObject>
      </g>
    </g>
  );
}

export default function PassRateBarChart() {
  const [data, setData] = useState<GitBenchData | null>(null);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);

  useEffect(() => {
    loadData().then((d) => {
      setData(d);
      setSelectedModels(d.models.map((m) => m.name));
    });
  }, []);

  // Compute unique providers for legend (must be before any early return — Rules of Hooks)
  const uniqueProviders = useMemo(() => {
    if (!data) return [];
    const seen = new Set<string>();
    const result: { slug: string; color: string }[] = [];
    for (const name of selectedModels) {
      const info = data.models.find((m) => m.name === name);
      if (!info) continue;
      const slug = info.provider.toLowerCase();
      if (seen.has(slug)) continue;
      seen.add(slug);
      result.push({
        slug: info.provider,
        color: getProviderColor(info.provider),
      });
    }
    return result;
  }, [data, selectedModels]);

  if (!data) return <div>Loading...</div>;

  const chartData = selectedModels
    .map((name) => {
      const summary = data.model_summaries[name];
      const info = data.models.find((m) => m.name === name);
      if (!summary) return null;
      return {
        name,
        provider: info?.provider || "",
        baseModel: info?.baseModel || name,
        reasoningLevel: info?.reasoningLevel,
        passRate: Math.round(summary.pass_at_k * 1000) / 10,
        raw: summary.pass_at_k,
      };
    })
    .filter((d): d is NonNullable<typeof d> => d !== null)
    .sort((a, b) => b.passRate - a.passRate);

  const modelMap = chartData.reduce(
    (acc, d) => {
      acc[d.name] = d;
      return acc;
    },
    {} as Record<string, (typeof chartData)[number]>,
  );

  const chartHeight = 350;
  const bottomMargin = 60; // room for -40° rotated labels below axis

  return (
    <div>
      <div className="max-w-xs ml-auto w-full mb-3">
        <ModelSelector
          initialSelected={selectedModels}
          onChange={setSelectedModels}
        />
      </div>
      <div className="card">
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart
            data={chartData}
            layout="horizontal"
            margin={{ top: 5, right: 20, left: 0, bottom: bottomMargin }}
          >
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.04)" />
            <XAxis
              type="category"
              dataKey="name"
              tick={(props: any) => (
                <CustomXAxisTick {...props} modelMap={modelMap} />
              )}
              axisLine={false}
              tickLine={false}
              interval={0}
              height={bottomMargin}
            />
            <YAxis
              type="number"
              domain={[0, 100]}
              tick={{
                fill: "var(--text-dim)",
                fontSize: 11,
                fontFamily: "var(--font-mono)",
              }}
              tickFormatter={(v: number) => `${v}%`}
              axisLine={false}
              tickLine={false}
            />
            <Bar
              dataKey="passRate"
              radius={[4, 4, 0, 0]}
              barSize={Math.max(
                12,
                Math.min(28, 400 / Math.max(1, chartData.length)),
              )}
              cursor="pointer"
              onClick={(data: any) => {
                const entry = data && chartData[data.tooltipPayload?.[0]?.payload?.index ?? data.activeTooltipIndex];
                if (entry?.provider && entry?.baseModel && entry?.reasoningLevel) {
                  window.location.href = modelLevelPath(entry.provider, entry.baseModel, entry.reasoningLevel);
                }
              }}
            >
              {chartData.map((entry, index) => (
                <Cell key={index} fill={getProviderColor(entry.provider)} />
              ))}
            </Bar>
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                const entry = modelMap[label];
                const displayLabel = entry
                  ? `${entry.provider}/${entry.baseModel}:${entry.reasoningLevel}`
                  : label;
                return (
                  <div
                    style={{
                      background: "var(--card)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 8,
                      padding: "8px 12px",
                      fontSize: 12,
                      fontFamily: "var(--font-mono)",
                      color: "var(--text-dim)",
                    }}
                  >
                    <div style={{ color: "var(--text)", marginBottom: 2 }}>
                      {displayLabel}
                    </div>
                    <div style={{ color: "var(--text-bright)" }}>
                      Pass Rate: {payload[0].value}%
                    </div>
                  </div>
                );
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {/* Provider legend */}
      {uniqueProviders.length > 0 && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 14,
            justifyContent: "center",
            marginTop: 10,
            fontSize: 10,
            fontFamily: "var(--font-mono)",
            color: "var(--text-dim)",
          }}
        >
          {uniqueProviders.map((p) => (
            <span
              key={p.slug}
              style={{ display: "inline-flex", alignItems: "center", gap: 5 }}
            >
              <span
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  backgroundColor: p.color,
                  flexShrink: 0,
                }}
              />
              {p.slug}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
