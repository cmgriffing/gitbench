## ADDED Requirements

### Requirement: Info tip uses CSS tooltip on desktop, inline text on mobile
Section blurbs that are helpful but not critical SHALL use the `info-tip` CSS class pattern. On viewports wider than 768px, the blurb SHALL render as a positioned tooltip that appears on hover over the section label. On viewports 768px or narrower, the blurb SHALL render as a static paragraph below the section label. No JavaScript SHALL be required.

#### Scenario: Tooltip appears on desktop hover
- **WHEN** a desktop user hovers over a section label with `class="info-tip"`
- **THEN** the blurb text appears as a positioned tooltip below the label

#### Scenario: Blurb is always visible on mobile
- **WHEN** a page is rendered on a 375px viewport
- **THEN** all `info-tip` blurbs are visible as static paragraphs below their section labels

#### Scenario: No JavaScript dependency
- **WHEN** JavaScript is disabled in the browser
- **THEN** info tips still work correctly via CSS `:hover` on desktop and `position: static` override on mobile

### Requirement: Info tip shows ⓘ icon on desktop only
On viewports wider than 768px, the section label inside an `info-tip` SHALL display a ⓘ character as a `::after` pseudo-element on the label `<span>`. On viewports 768px or narrower, the icon SHALL be hidden.

#### Scenario: ⓘ icon visible on desktop
- **WHEN** a page is rendered on a 1024px viewport
- **THEN** each `info-tip` section label span is followed by a low-opacity ⓘ character

#### Scenario: ⓘ icon hidden on mobile
- **WHEN** a page is rendered on a 375px viewport
- **THEN** no ⓘ icon appears after info tip section labels

### Requirement: Info tip styling uses existing design tokens
The info tip SHALL use the site's existing CSS custom properties for colors and typography. The tooltip SHALL have `position: absolute`, dark card background, subtle border, and box shadow matching the app aesthetic. The inline mobile variant SHALL have `position: static` with transparent background, no border, and no shadow.

#### Scenario: Tooltip matches app aesthetic
- **WHEN** an info tip tooltip is visible on desktop
- **THEN** it uses `var(--card)` background, `var(--border)` border, and `0 4px 12px rgba(0,0,0,0.35)` box shadow

#### Scenario: Mobile blurb inherits text styling
- **WHEN** an info tip blurb is visible on mobile
- **THEN** it uses the same `text-sm`, `var(--text-mid)`, and `leading-relaxed` styling as other page prose

### Requirement: Info tip markup is a simple div wrapper
The info tip markup SHALL consist of a `<div class="info-tip">` wrapping a `<div class="section-label">` and a `<p class="info-blurb">`. No `<details>`, `<summary>`, or other interactive elements SHALL be used.

#### Scenario: Clean markup structure
- **WHEN** inspecting an info tip section in the DOM
- **THEN** the structure is `<div class="info-tip">` > `<div class="section-label">` + `<p class="info-blurb">`
