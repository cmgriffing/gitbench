## MODIFIED Requirements

### Requirement: ProviderIcon maps provider slugs to Simple Icons
A `ProviderIcon` React component SHALL render the appropriate brand icon from `@icons-pack/react-simple-icons` for a given provider slug. The component SHALL accept a `provider` prop (lowercase string, e.g. `"anthropic"`, `"openai"`) and a `size` prop (number, default 16). It SHALL use `color="default"` on the icon component to render the brand's canonical color.

For icons rendered at sizes ≤14 pixels, the component SHALL apply a subtle background circle (`rgba(255,255,255,0.08)`) behind the icon to ensure visibility of dark brand colors against dark backgrounds.

For the Anthropic provider specifically, the component SHALL override the simple-icons default color (`#191919`) with the Anthropic palette color (`#D97757`) to ensure visibility on dark backgrounds.

#### Scenario: Anthropic icon renders
- **WHEN** `<ProviderIcon provider="anthropic" size={16} />` renders
- **THEN** the Anthropic brand icon is displayed at 16×16 pixels in the Anthropic palette color (#D97757), not the simple-icons default (#191919)

#### Scenario: Anthropic icon at small size with color override
- **WHEN** `<ProviderIcon provider="anthropic" size={12} />` renders
- **THEN** the Anthropic brand icon is displayed at 12×12 pixels in the Anthropic palette color (#D97757) with a subtle white background circle

#### Scenario: OpenAI icon renders
- **WHEN** `<ProviderIcon provider="openai" size={20} />` renders
- **THEN** the OpenAI brand icon is displayed at 20×20 pixels in the OpenAI brand color

#### Scenario: Small icon receives background circle
- **WHEN** `<ProviderIcon provider="google" size={12} />` renders
- **THEN** a subtle `rgba(255,255,255,0.08)` background circle appears behind the icon

#### Scenario: Large icon does not receive background circle
- **WHEN** `<ProviderIcon provider="meta" size={20} />` renders
- **THEN** no background circle is rendered behind the icon

#### Scenario: Unknown provider falls back to initial circle
- **WHEN** `<ProviderIcon provider="unknown-provider" size={16} />` renders
- **THEN** a colored circle with the first letter "U" is displayed at 16×16 pixels
