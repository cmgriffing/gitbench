## ADDED Requirements

### Requirement: Pricing pipeline aggregates campaign costs at explicit scopes

The pricing pipeline SHALL calculate attempt cost, mean cost per complete trial, total campaign cost, and cost consumed by operational failures as separate values.

#### Scenario: Price a complete campaign

- **WHEN** all attempts have token usage and applicable model pricing
- **THEN** the campaign SHALL expose mean complete-trial cost and total cost
- **AND** the total SHALL reconcile with priced target, judge, retry, and configured safety calls

#### Scenario: Pricing is unavailable

- **WHEN** any call lacks applicable pricing data
- **THEN** affected aggregates SHALL be marked partial
- **AND** the pipeline SHALL not present the known subtotal as a complete campaign total

