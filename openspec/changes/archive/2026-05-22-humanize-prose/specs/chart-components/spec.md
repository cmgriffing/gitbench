## ADDED Requirements

### Requirement: Chart tooltip footnotes use conversational fragments
React chart components that display a separator + explanatory footnote in their Recharts `<Tooltip>` content SHALL use short conversational fragments. Each footnote SHALL be a single line (or fragment), not a multi-sentence explanation. Footnotes SHALL follow the conversational prose voice: no emdashes, contractions preferred, no hedging.

#### Scenario: PassRateBarChart footnote is a fragment
- **WHEN** hovering a bar in PassRateBarChart
- **THEN** the tooltip footnote below the separator reads "% of 204 fixtures passed"

#### Scenario: CostValueChart footnote is a fragment
- **WHEN** hovering a bar in CostValueChart
- **THEN** the tooltip footnote below the separator reads "API cost for 204-fixture run. — = local/Ollama"

#### Scenario: RuntimeBarChart footnote includes latency caveat
- **WHEN** hovering a bar in RuntimeBarChart
- **THEN** the tooltip footnote below the separator reads "Wall-clock time. Includes API latency."

#### Scenario: TokenUsageChart footnote is a fragment
- **WHEN** hovering a bar in TokenUsageChart
- **THEN** the tooltip footnote below the separator reads "Tokens in + out. Fewer is more efficient."

#### Scenario: TimeSeriesChart footnote is minimal
- **WHEN** hovering a point in TimeSeriesChart
- **THEN** the tooltip footnote below the separator reads "Pass rate on this date."

### Requirement: ScatterPlot and QuadrantComparisonChart drop tooltip footnotes
The ScatterPlot and QuadrantComparisonChart React components SHALL NOT display a separator + footnote in their Recharts `<Tooltip>` content. The axes and labels on these charts are sufficient to understand the data.

#### Scenario: ScatterPlot has no footnote
- **WHEN** hovering a dot in ScatterPlot
- **THEN** no separator line or explanatory footnote appears in the tooltip

#### Scenario: QuadrantComparisonChart has no footnote
- **WHEN** hovering a point in QuadrantComparisonChart
- **THEN** no separator line or explanatory footnote appears in the tooltip
