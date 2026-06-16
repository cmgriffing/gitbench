## ADDED Requirements

### Requirement: TokenUsageChart ranks models by mean per-trial token usage

`TokenUsageChart` SHALL rank comparable model configurations by mean token usage per complete trial and SHALL expose total campaign tokens, trial counts, and reasoning-token detail separately.

#### Scenario: Compare campaigns with different trial counts

- **WHEN** two model summaries use different trial counts
- **THEN** bar magnitude SHALL use mean tokens per complete trial
- **AND** the tooltip SHALL show total tokens and completed trials

#### Scenario: Preserve reasoning-effort range meaning

- **WHEN** a bar aggregates multiple reasoning efforts
- **THEN** the range-whisker encoding SHALL continue to represent reasoning-effort range
- **AND** trial variability SHALL be separately labeled

