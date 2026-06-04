import { useMemo, type ReactNode } from "react";
import ProviderIcon from "@/components/ProviderIcon";
import { getProviderColor } from "@/lib/provider-colors";
import type { GroupedMetricRow } from "@/components/charts/model-groups";
import { modelGroupPath } from "@/lib/routes";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ErrorBar,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const HORIZONTAL_CHART_INNER_HEIGHT = 340;
const HORIZONTAL_CHART_ROW_GAP = 3;
const VERTICAL_CHART_HEIGHT = 350;

export function truncateName(name: string, maxLen = 16): string {
  if (!name || name.length <= maxLen) return name || "";
  return `${name.slice(0, maxLen - 1)}…`;
}

export function horizontalChartBarSize(rowCount: number): number {
  const rows = Math.max(1, rowCount);
  const rowHeight = HORIZONTAL_CHART_INNER_HEIGHT / rows;
  return Math.max(
    3,
    Math.min(28, Math.floor(rowHeight - HORIZONTAL_CHART_ROW_GAP)),
  );
}

export function verticalChartBarSize(rowCount: number): number {
  return Math.max(12, Math.min(28, 400 / Math.max(1, rowCount)));
}

export function providerLegend(rows: GroupedMetricRow[]) {
  const seen = new Set<string>();
  const providers: { slug: string; color: string }[] = [];
  for (const row of rows) {
    const key = row.provider.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    providers.push({
      slug: row.provider,
      color: getProviderColor(row.provider),
    });
  }
  return providers;
}

export function ProviderLegend({ rows }: { rows: GroupedMetricRow[] }) {
  const providers = providerLegend(rows);
  if (providers.length === 0) return null;
  return (
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
      {providers.map((provider) => (
        <span
          key={provider.slug}
          style={{ display: "inline-flex", alignItems: "center", gap: 5 }}
        >
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: provider.color,
              flexShrink: 0,
            }}
          />
          {provider.slug}
        </span>
      ))}
    </div>
  );
}

interface TickProps {
  x: number;
  y: number;
  payload: { value: string };
  rowMap?: Record<string, GroupedMetricRow>;
}

export function VerticalGroupTick({ x, y, payload, rowMap }: TickProps) {
  const row = rowMap?.[payload.value];
  return (
    <g transform={`translate(${x},${y})`}>
      <g transform="rotate(-40)">
        <foreignObject
          x={-138}
          y={-6}
          width={138}
          height={32}
          style={{ overflow: "visible" }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 3,
              fontSize: 9,
              fontFamily: "var(--font-mono)",
              color: "var(--text-mid)",
              justifyContent: "flex-end",
              width: 138,
            }}
          >
            <ProviderIcon provider={row?.provider ?? ""} size={12} />
            <span
              style={{
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
                maxWidth: 118,
              }}
            >
              {truncateName(row?.baseModel ?? payload.value, 10)}
            </span>
          </div>
        </foreignObject>
      </g>
    </g>
  );
}

export function HorizontalGroupTick({ x, y, payload, rowMap }: TickProps) {
  const row = rowMap?.[payload.value];
  return (
    <g transform={`translate(${x},${y})`}>
      <foreignObject
        x={-112}
        y={-10}
        width={106}
        height={22}
        style={{ overflow: "visible" }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            gap: 4,
            fontSize: 10,
            fontFamily: "var(--font-mono)",
            color: "var(--text-mid)",
            whiteSpace: "nowrap",
          }}
        >
          <ProviderIcon provider={row?.provider ?? ""} size={12} />
          <span>{truncateName(row?.baseModel ?? payload.value, 14)}</span>
        </div>
      </foreignObject>
    </g>
  );
}

export function rowMap(rows: GroupedMetricRow[]) {
  return rows.reduce(
    (acc, row) => {
      acc[row.id] = row;
      return acc;
    },
    {} as Record<string, GroupedMetricRow>,
  );
}

interface VerticalGroupedMetricChartProps {
  rows: GroupedMetricRow[];
  yDomain: [number, number];
  yTickFormatter: (value: number) => string;
  renderTooltip: (entry: GroupedMetricRow) => ReactNode;
}

export function VerticalGroupedMetricChart({
  rows,
  yDomain,
  yTickFormatter,
  renderTooltip,
}: VerticalGroupedMetricChartProps) {
  const rowsById = useMemo(() => rowMap(rows), [rows]);

  return (
    <>
      <div className="card">
        <ResponsiveContainer width="100%" height={VERTICAL_CHART_HEIGHT}>
          <BarChart
            data={rows}
            layout="horizontal"
            margin={{ top: 12, right: 20, left: 0, bottom: 58 }}
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
              tickFormatter={yTickFormatter}
              axisLine={false}
              tickLine={false}
            />
            <Bar
              dataKey="representativeValue"
              radius={[4, 4, 0, 0]}
              barSize={verticalChartBarSize(rows.length)}
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
              {rows.map((entry) => (
                <Cell key={entry.id} fill={getProviderColor(entry.provider)} />
              ))}
              <ErrorBar
                dataKey="rangeWhisker"
                width={9}
                stroke="rgba(229,232,238,0.76)"
                strokeWidth={1.7}
                isAnimationActive={false}
              />
            </Bar>
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              content={({ active, label }: any) => {
                if (!active || !label) return null;
                const entry = rowsById[String(label)];
                if (!entry) return null;
                return renderTooltip(entry);
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <ProviderLegend rows={rows} />
    </>
  );
}

export function paddedDomain(
  rows: GroupedMetricRow[],
  fallback: [number, number],
  options: { floor?: number; ceiling?: number; paddingRatio?: number } = {},
): [number, number] {
  if (rows.length === 0) return fallback;
  const min = Math.min(...rows.map((row) => row.minValue));
  const max = Math.max(...rows.map((row) => row.maxValue));
  const span = Math.max(max - min, Math.abs(max) * 0.08, 1);
  const padding = span * (options.paddingRatio ?? 0.12);
  const lower = Math.max(options.floor ?? -Infinity, min - padding);
  const upper = Math.min(options.ceiling ?? Infinity, max + padding);
  if (lower === upper) {
    return [Math.max(options.floor ?? -Infinity, lower - 1), upper + 1];
  }
  return [lower, upper];
}

export function zeroAnchoredDomain(
  rows: GroupedMetricRow[],
  fallback: [number, number],
  options: { ceiling?: number; paddingRatio?: number } = {},
): [number, number] {
  if (rows.length === 0) return fallback;
  if (options.ceiling != null) return [0, options.ceiling];

  const max = Math.max(0, ...rows.map((row) => row.maxValue));
  if (max === 0) return [0, fallback[1]];

  const padding = max * (options.paddingRatio ?? 0.12);
  return [0, max + padding];
}

export function formatCompactDecimal(
  value: number,
  maxFractionDigits = 2,
): string {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: maxFractionDigits,
  }).format(value);
}

export const tooltipStyle = {
  background: "var(--card)",
  border: "2px solid var(--border)",
  borderRadius: 10,
  padding: "8px 12px",
  fontSize: 12,
  fontFamily: "var(--font-mono)",
  color: "var(--text-dim)",
};
