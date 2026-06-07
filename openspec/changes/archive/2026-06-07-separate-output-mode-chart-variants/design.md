## Context

The shared grouped metric pipeline currently flattens all selected efforts for a provider/base-model group into one `GroupedMetricRow`. In `Both` mode this combines text and JSON-schema values before calculating the deduped median, minimum, maximum, and range whisker. `VerticalGroupedMetricChart` then renders one Recharts `<Bar>` from that combined summary, and each chart renders one flat effort list in its tooltip.

Four affected charts share the same data builder and renderer:

- Pass rate
- Cost per full run
- API time
- Token usage

The Compare page contains two additional, independent Recharts bar charts:

- Overall pass rates
- Pass rates by benchmark

The overall Compare chart currently renders one horizontal category per concrete model variant. The per-benchmark chart renders one series per concrete model variant. In `Both` mode both expose text and `__json_schema` variants as unrelated entries and neither provides the requested pair-level tooltip.

The quadrant chart already expands efforts by output mode, but then selects only one highest-composite point per provider/base-model group. In `Both` mode a strong text or JSON result therefore suppresses its sibling mode entirely.

The output-mode selector, provider/base-model selection, APIs, and stored data already distinguish text from JSON-schema efforts. This change only needs to preserve that distinction through aggregation and presentation.

## Goals / Non-Goals

**Goals:**

- Preserve one X-axis category and navigation target per provider/base-model group.
- Render adjacent text and JSON-schema bars when `Both` is selected.
- Calculate each mode's representative median and effort range independently.
- Make the sibling relationship and output-mode distinction clear without replacing provider color as the primary model identity.
- Trigger one category-level tooltip from either bar and separate its details into `Text` and `JSON` sections.
- Handle groups with only one available output mode without dropping the group.
- Apply consistent mode pairing to every current bar chart, including both Compare page charts.
- Preserve each chart's existing base color meaning while layering a common text/JSON treatment on top.
- Show one independently selected text point and one independently selected JSON point per base model in the quadrant chart when both modes are available.
- Make the distance and direction between paired quadrant points visible without merging their metric values.

**Non-Goals:**

- Change output-mode synchronization or localStorage behavior.
- Change provider/base-model selection semantics.
- Change report APIs, database schemas, routes, or model identities.
- Add paired bars to heatmaps, scatter plots, tables, or time-series charts.
- Compare individual text and JSON efforts one-to-one by reasoning level.
- Redesign the Compare page's non-bar visualizations.
- Change quadrant metric normalization or the composite-score formula.

## Decisions

### Store per-mode summaries inside each grouped metric row

`buildGroupedMetricRows()` will partition extracted efforts by concrete output mode before computing summary statistics. Each visible mode summary will contain its efforts, minimum, maximum, deduped median representative, and whisker offsets. The parent row will retain the provider/base-model category identity and expose the available mode summaries.

This keeps category identity separate from series identity and prevents a median or range from spanning unlike output modes.

Alternative considered: emit two independent rows with mode-suffixed IDs. That would produce separate X-axis categories and labels, weakening the visual grouping and making a shared category tooltip harder.

### Render output modes as sibling Recharts series

The shared vertical renderer will receive the selected output mode and render one `<Bar>` for a single-mode selection or two `<Bar>` series for `Both`. Both series use the same category key, compact `barGap`, and a per-series width that scales with the number of model categories.

Each series owns its corresponding range whisker. Null mode values remain absent, so a group with only one mode keeps its category and displays an empty sibling slot.

Alternative considered: stack the bars. Stacking implies addition and makes direct comparison of absolute values harder.

### Preserve each chart's base color and encode mode through treatment

Text bars will use the chart's existing solid base color. JSON bars will use that same base color with reduced fill opacity and a visible matching outline. The overview grouped metric charts continue using provider colors, Compare overall continues using pass-rate status colors, and Compare by benchmark continues assigning a stable color per canonical model effort. A mode legend shown in `Both` mode will label the solid and translucent outlined treatments.

Using a second global color for JSON would compete with provider, performance, or model-series colors. Opacity alone was rejected because it is less distinct on varied backgrounds; the outline supplies a second visual cue.

### Use one shared category tooltip

Recharts `BarChart` uses axis/category tooltips by default. The custom tooltip will continue resolving the row by X-axis label, so hovering or keyboard-focusing either sibling bar opens the same tooltip.

In `Both` mode the tooltip will render ordered `Text` and `JSON` sections. Each section will show its own representative median and its reasoning-effort list using the chart-specific value formatting. If a mode has no data for the group, its section will state `No data`. Single-mode selections will show only the selected section.

The representative median will be displayed at the section level rather than relying only on equality with an individual effort, because an even-sized set can produce a median between two effort values.

### Pair concrete model variants on the Compare page

Compare data shaping will canonicalize each concrete selected model name into a model-effort identity plus output mode. The `__json_schema` suffix remains an internal lookup key and will not create a separate visible model label or legend identity in `Both` mode.

The overall chart will render one horizontal category per canonical model effort with adjacent text and JSON bars. Its axis/category tooltip can therefore resolve either sibling to one pair and show separate mode sections.

The per-benchmark chart must retain benchmarks as categories and canonical model efforts as series groups. It will render each model effort's text and JSON bars consecutively, then use item-level tooltip activation to resolve the hovered data key to the canonical model effort. Hovering either sibling will show that model effort's text and JSON values for the active benchmark instead of all selected models.

Alternative considered: use the default category tooltip for the per-benchmark chart. That would include every selected model and mode for one benchmark, producing an oversized tooltip and failing the pair-level interaction.

### Select the best quadrant effort independently per output mode

Quadrant candidate points will be partitioned by provider/base-model group and output mode. Normalized X/Y scores will still be calculated over all visible candidates so text and JSON points share one comparable coordinate system. The highest-composite candidate will then be selected independently for `text` and `json_schema`.

In a single-mode view this produces the same one-point-per-base-model behavior as today. In `Both`, it produces up to two points per base model, and the two selected points may represent different reasoning levels.

Alternative considered: plot every reasoning effort in both modes. That would preserve all data but substantially increase clutter and change the chart from base-model comparison to effort-level exploration.

### Connect and style paired quadrant points

Each available text/JSON point pair will be rendered as one logical scatter pair. A subtle neutral connector will run between their coordinates, making mode direction and magnitude visible without implying an ordered path.

Text points will use a solid provider-colored circle. JSON points will use a lightly filled provider-colored circle with a stronger provider-colored outline. When both coordinates are identical, the JSON point will render as a larger ring around the solid text point so neither mode disappears.

The provider legend remains responsible for color. A mode legend shown in `Both` mode will explain solid `Text`, outlined `JSON`, and the connector.

Alternative considered: offset overlapping points by a few pixels. That improves visibility but falsifies the plotted metric coordinates.

### Use one paired quadrant tooltip

Hovering or keyboard-focusing either point will resolve the provider/base-model pair and show one tooltip with ordered `Text` and `JSON` sections. Each available section will identify its selected reasoning effort and show both raw metric values. An unavailable sibling mode will show `No data`.

The tooltip remains free of an explanatory footnote, preserving the existing quadrant tooltip requirement.

### Rank quadrant points by visible mode variant

The ranked list and "Best blend" label will treat each selected output-mode point as an independent ranked result. Labels will include the mode so text and JSON results from the same base model are distinguishable. A base model may therefore occupy two ranked positions in `Both` mode.

Alternative considered: rank each base model by the mean of its two mode scores. That would retain one row per model but conceal meaningful mode divergence and would not identify the actual best plotted point.

### Sort categories using the visible mode summaries

Each grouped row will expose a sort value derived from the arithmetic mean of its available visible mode representative values. In `Both` mode this gives equal weight to text and JSON while retaining one category order. If only one mode is available, its representative value is used directly.

Pass rate remains descending. Cost, API time, and token usage remain ascending. Single-mode ordering therefore remains behaviorally unchanged.

Compare overall pass rate also sorts descending by the selected representative or the mean of available text and JSON values. Compare by benchmark preserves benchmark order and canonical model-effort series order; it does not sort benchmarks by mode values.

Alternative considered: sort by text only. That gives stable ordering when toggling from `Text` to `Both`, but systematically subordinates JSON results and produces surprising order for JSON-only groups.

### Keep mode-specific formatting in chart components

The shared renderer will own bar geometry, styling, legends, event behavior, and tooltip activation. Individual chart components will continue owning semantic formatting and footnotes, and will render their mode sections from the shared row structure.

Compare page charts will reuse shared mode-style helpers and model-variant pairing helpers, but will retain their own geometry because one is horizontal and the other is a benchmark-by-model grouped chart. This avoids forcing unlike chart shapes through the overview renderer while keeping every current bar-chart implementation consistent, including the pass-rate component reused on benchmark pages.

## Risks / Trade-offs

- [Two bars reduce available width for large selections] -> Scale bar width by category and visible series count, keep compact intra-pair spacing, and preserve the fixed chart height.
- [Reduced opacity can make JSON bars appear disabled] -> Add a clear outline and mode legend, and retain pointer/click behavior.
- [Missing-mode empty slots may look like rendering defects] -> Preserve the paired category spacing and explicitly show `No data` in the shared tooltip.
- [Two whiskers can overlap visually] -> Attach each whisker to its own bar series and keep sibling bars separated by a small gap.
- [Mean-based sorting can place a category differently from either single-mode view] -> Document the rule in specs and use it consistently in every chart that sorts model categories.
- [Compare by-benchmark can show many model pairs] -> Keep model pairs consecutive, use compact pair spacing, consolidate the legend by canonical model effort, and show only the hovered pair in the tooltip.
- [Compare tooltips currently do not exist] -> Add focused tooltip payload helpers so pair resolution is testable without relying only on browser interaction.
- [Quadrant pairs can overlap or cross other pairs] -> Keep connectors thin and neutral, draw them behind points, and use a larger JSON ring only for coincident coordinates.
- [Twice as many quadrant points can crowd labels and ranking] -> Keep points unlabeled in the plot, retain the top-six ranked list, and include mode in ranking labels.
- [Independent per-mode selection can choose different reasoning levels] -> Show each selected effort explicitly in the paired tooltip and ranking metadata.
- [Current tests focus mainly on report APIs] -> Extract or add focused tests for pure grouping and sorting helpers, then verify the production build.

## Migration Plan

1. Extend the grouped metric row types and builder with independent mode summaries and a visible-mode sort value.
2. Update the shared vertical grouped chart to render one or two mode series, mode-specific whiskers, and the mode legend.
3. Update each affected chart's sorting and tooltip section rendering.
4. Add Compare-specific model-variant pairing, paired bar rendering, consolidated legends, and pair-level tooltips.
5. Update quadrant point selection to retain the best candidate per group and output mode, then add pair connectors, mode styling, overlap handling, paired tooltips, and mode-specific ranking.
6. Add focused tests for aggregation, model-variant pairing, quadrant selection, missing modes, shared tooltip data, and sorting.
7. Run web tests and the Astro production build.

Rollback is limited to the web presentation layer: restore the prior flattened grouped row and single-series renderer. No persisted data migration is required.

## Open Questions

None.
