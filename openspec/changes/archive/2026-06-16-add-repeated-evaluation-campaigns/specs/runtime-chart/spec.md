## ADDED Requirements

### Requirement: RuntimeBarChart ranks models by mean per-trial API time

`RuntimeBarChart` SHALL rank comparable model configurations by mean API time per complete trial for the selected campaign and SHALL expose total campaign API time and trial variability as secondary detail.

#### Scenario: Render campaigns with different trial counts

- **WHEN** model summaries contain different planned trial counts
- **THEN** bar magnitude SHALL use mean API time per complete trial
- **AND** the tooltip SHALL show completed trials, total API time, and campaign completeness

#### Scenario: Preserve reasoning-effort range meaning

- **WHEN** a bar aggregates multiple reasoning efforts
- **THEN** its existing range-whisker encoding SHALL continue to represent reasoning-effort range
- **AND** repeated-trial variability SHALL use separately labeled detail

