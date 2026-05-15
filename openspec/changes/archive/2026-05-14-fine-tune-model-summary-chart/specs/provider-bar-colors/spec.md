## ADDED Requirements

### Requirement: Provider color palette maps provider slugs to distinct colors
A provider color palette SHALL map known provider slugs to hand-picked, high-contrast colors suitable for dark backgrounds. Unknown providers SHALL receive a deterministic hue via a golden-angle hash function, rendered as `hsl(hue, 55%, 48%)`.

The known provider colors SHALL be:

| Provider   | Color     |
|------------|-----------|
| anthropic  | `#D97757` |
| google     | `#4285F4` |
| meta       | `#0668E1` |
| mistral    | `#F59E0B` |
| openai     | `#10A37F` |
| deepseek   | `#4F46E5` |
| xai        | `#E5E7EB` |

#### Scenario: Known provider returns hand-picked color
- **WHEN** `getProviderColor("anthropic")` is called
- **THEN** it returns `#D97757`

#### Scenario: Unknown provider returns deterministic hue
- **WHEN** `getProviderColor("some-new-provider")` is called
- **THEN** it returns a color in `hsl(hue, 55%, 48%)` format where hue is deterministic for that string

#### Scenario: Case-insensitive lookup
- **WHEN** `getProviderColor("AnThRoPiC")` is called
- **THEN** it returns `#D97757`

### Requirement: Provider legend renders colored dots below the chart
The PassRateBarChart SHALL render a provider legend below the chart card. The legend SHALL display one entry per unique provider present in the currently displayed model set. Each entry SHALL consist of a small colored dot (using the provider's palette color) followed by the provider name in mono font. Providers SHALL be displayed in a horizontal flex row.

#### Scenario: Legend shows only displayed providers
- **WHEN** the chart shows models from Anthropic, Google, and Mistral
- **THEN** three legend entries appear: Anthropic, Google, Mistral

#### Scenario: Legend uses provider palette colors
- **WHEN** the legend renders an Anthropic entry
- **THEN** its dot is rendered in the Anthropic palette color (#D97757)

#### Scenario: Single-provider charts show one entry
- **WHEN** all displayed models are from OpenAI
- **THEN** only one legend entry (OpenAI) appears
