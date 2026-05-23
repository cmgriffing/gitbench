## ADDED Requirements

### Requirement: Info toggle uses native `<details>` element
Section blurbs that are helpful but not critical SHALL use the HTML `<details>` element as a collapsible info toggle. The `<details>` element SHALL contain a `<summary>` with the section label and an optional `<p>` with the blurb text. The toggle SHALL render `open` by default in the HTML so mobile users see text inline without interaction.

#### Scenario: Toggle renders closed on desktop
- **WHEN** a page is loaded on a viewport wider than 768px
- **THEN** all `details.info-toggle` elements are closed (content hidden) after a small inline script runs

#### Scenario: Toggle renders open on mobile
- **WHEN** a page is loaded on a viewport 768px or narrower
- **THEN** all `details.info-toggle` elements remain open, with blurb text visible inline

#### Scenario: Desktop toggle reveals blurb on click
- **WHEN** a desktop user clicks the `<summary>` of a closed `details.info-toggle`
- **THEN** the blurb text expands below the section label

#### Scenario: Toggle is keyboard accessible
- **WHEN** a user tabs to a `<summary>` element and presses Enter or Space
- **THEN** the `<details>` element opens or closes

### Requirement: Info toggle shows ⓘ icon on desktop only
On viewports wider than 768px, the `<summary>` element of an info toggle SHALL display a ⓘ character as a `::after` pseudo-element. On viewports 768px or narrower, the icon SHALL be hidden.

#### Scenario: ⓘ icon visible on desktop
- **WHEN** a page is rendered on a 1024px viewport
- **THEN** each `details.info-toggle > summary` is followed by a low-opacity ⓘ character

#### Scenario: ⓘ icon hidden on mobile
- **WHEN** a page is rendered on a 375px viewport
- **THEN** no ⓘ icon appears after info toggle summaries

### Requirement: Info toggle styling uses existing design tokens
The info toggle SHALL use the site's existing CSS custom properties for colors and typography. The `<summary>` SHALL hide the default disclosure triangle via `list-style: none`. The blurb text SHALL use `text-sm` sizing and `--color-text-mid` color consistent with existing page prose. The ⓘ pseudo-element SHALL use `font-size: 0.7rem` and `opacity: 0.4`.

#### Scenario: Toggle summary has no default triangle
- **WHEN** an info toggle is rendered
- **THEN** no disclosure triangle icon appears next to the summary text

#### Scenario: Blurb inherits existing text styling
- **WHEN** an info toggle blurb is visible
- **THEN** it uses the same `text-sm`, `--color-text-mid`, and `leading-relaxed` classes as the existing About section prose

### Requirement: Info toggle script runs before paint
The inline script that closes info toggles on desktop SHALL be placed in the document `<head>` or immediately after the first toggle element to close toggles before the user sees them open. The script SHALL be fewer than 10 lines. No external library or framework SHALL be required.

#### Scenario: No flash of open toggles on desktop
- **WHEN** a page with info toggles loads on a 1024px viewport
- **THEN** toggles appear closed to the user (no visible flash of open content)

#### Scenario: Script degrades gracefully
- **WHEN** JavaScript is disabled in the browser
- **THEN** info toggles remain open on all viewports (same behavior as mobile)
