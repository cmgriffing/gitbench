## MODIFIED Requirements

### Requirement: Overview page includes introductory content
The root page (`/`) SHALL be titled "Overview" and SHALL include an About section with multi-paragraph introductory text written in the conversational prose voice. The About text SHALL explain what GitBench is, what it tests (204 fixtures across 17 Git skill categories), and that results are transparent and reproducible. It SHALL NOT include a "Learn more →" link to methodology. Chart sections on the Overview page SHALL use the info-toggle pattern for blurb text that provides non-obvious context. Chart sections where the title and axes are self-explanatory SHALL have no blurb text at all.

#### Scenario: About section is always visible
- **WHEN** navigating to `/`
- **THEN** the About card contains multiple paragraphs of conversational prose visible without interaction on all viewports

#### Scenario: Runtime chart has info tip
- **WHEN** navigating to `/` on desktop
- **THEN** the Runtime chart section label has a ⓘ icon, and hovering reveals the blurb as a positioned tooltip

#### Scenario: Runtime blurb is inline on mobile
- **WHEN** navigating to `/` on a mobile viewport
- **THEN** the Runtime blurb appears as a static paragraph below the section label without the ⓘ icon

#### Scenario: Pass Rate chart has no blurb
- **WHEN** navigating to `/`
- **THEN** the Pass Rate chart section has no prose paragraph between the section label and the chart

#### Scenario: No "Learn more" link to methodology
- **WHEN** navigating to `/`
- **THEN** no link labeled "Learn more" appears in any section blurb or the About text

## ADDED Requirements

### Requirement: Section blurbs follow voice guidelines
All section blurbs across Astro pages SHALL use the conversational prose voice: short sentences, fragments permitted, no emdashes, contractions preferred, hedging removed. Blurbs SHALL NOT describe what is already visually apparent from chart titles, axis labels, or badge text.

#### Scenario: No emdashes in section blurbs
- **WHEN** searching all `.astro` files for the emdash character (—) outside the Methodology page
- **THEN** no instance is found

#### Scenario: Fragments appear naturally
- **WHEN** reading section blurbs across the site
- **THEN** multiple sentence fragments or very short sentences (under 6 words) appear

### Requirement: Info tips replace always-visible blurbs on specific sections
The following sections on Astro pages SHALL use the `<div class="info-tip">` pattern for their blurb text (CSS tooltip on desktop, inline text on mobile):
- `index.astro`: Quadrant Comparison, Runtime, Benchmark Matrix
- `explore.astro`: top page blurb
- `compare.astro`: top page blurb
- `benchmarks/[name].astro`: Model Leaderboard
- `history.astro`: Run Log

#### Scenario: Info tips render on specified sections
- **WHEN** navigating to the Overview page
- **THEN** the Quadrant Comparison, Runtime, and Benchmark Matrix sections each have a `<div class="info-tip">` element wrapping their section label and blurb

#### Scenario: Info tips absent from deleted sections
- **WHEN** navigating to the Overview page
- **THEN** the Pass Rate, Cost, and Token Usage sections have no `<div class="info-tip">` element and no blurb paragraph

### Requirement: Always-visible blurbs on critical sections
The following sections SHALL retain always-visible blurb text (not inside a toggle):
- `index.astro`: About section (multi-paragraph, conversational voice)
- `models/index.astro`: top page blurb (explains provider → model → level hierarchy)
- `fixtures/[benchmark]/[fixture].astro`: Baseline Repository section (explains setup commands)

#### Scenario: About section is always visible
- **WHEN** navigating to `/`
- **THEN** the About card text is rendered directly (not inside a `<details>` element)

#### Scenario: Models hierarchy blurb is always visible
- **WHEN** navigating to `/models`
- **THEN** the hierarchy explanation paragraph is rendered directly above the provider cards

### Requirement: Deleted section blurbs
The following sections SHALL have no blurb text at all (neither always-visible nor in a toggle):
- `index.astro`: Pass Rate (Model Summary), Cost per Full Run, Token Usage
- `benchmarks/[name].astro`: Per-Fixture Comparison
- `models/[provider]/[model]/index.astro`: top page blurb
- `models/[provider]/[model]/[level].astro`: Fixture Gallery blurb
- `history.astro`: Pass Rate Over Time
- `fixtures/[benchmark]/[fixture].astro`: Model Outputs blurb
- `benchmarks/index.astro`: top page blurb

#### Scenario: No blurb on deleted sections
- **WHEN** navigating to any of the listed page sections
- **THEN** no prose paragraph appears between the section label and the chart/table/content
