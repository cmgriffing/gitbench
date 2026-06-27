## Context

The Overview page currently renders `EmailCta` between the About card and the chart sections. The CTA is functionally correct, but its outer container uses the same generic `.card` visual style as surrounding dashboard content, so it does not read as a distinct offer.

The component already imports `Mail` and `ArrowRight` from `lucide-react`, uses a shadcn `Button`, and opens a dialog for email capture. The implementation should build on those existing primitives and design tokens instead of adding a new visual system.

## Goals / Non-Goals

**Goals:**

- Make the CTA visually distinct from ordinary report cards while staying within the GitBench dark UI aesthetic.
- Use existing brand colors, especially purple and teal, for the background, border, icon, and focus treatment.
- Add a large clipped mail icon as a decorative background element that makes the email action recognizable.
- Keep foreground text, button, and dialog behavior accessible and readable on all supported viewports.
- Align the card copy and dialog copy around one offer: the GitBench analysis PDF delivered by email.

**Non-Goals:**

- Do not change the email signup endpoint, HubSpot payload, privacy link behavior, or submission state machine.
- Do not add a new dependency or asset pipeline.
- Do not redesign the full Overview page or other chart sections.
- Do not introduce marketing-page layout patterns that make the dashboard feel less like a report interface.

## Decisions

### Use a dedicated CTA shell instead of `.card`

The CTA should use its own container classes so it can have a stronger background, border, and clipped decorative layer without changing all cards globally.

Alternative considered: modify `.card` or add a `.card--prominent` style. This is broader than needed and risks changing ordinary dashboard cards that should remain quiet.

### Use the existing teal highlight for the oversized mail icon

The large background mail icon should use the existing bright teal brand highlight, such as `#01fee0` or the corresponding token, at low opacity. This gives the CTA a different visual note than the default purple button while still matching the token set.

Alternative considered: use the purple accent for every layer. That would stay on brand, but it would reduce contrast because the site already uses purple heavily for buttons, borders, and glows.

### Keep the oversized icon decorative and non-interactive

The clipped mail icon should be absolutely positioned behind the CTA content, hidden from assistive technology, and prevented from intercepting pointer events. It should sit mostly toward the right or lower edge so it reinforces the offer without sitting under dense paragraph text.

Alternative considered: use the large icon as a visible foreground illustration. That would compete with the copy and primary button in a compact dashboard layout.

### Pair the background mail icon with a smaller foreground cue

The component should keep or restore a small foreground icon tile. If the large background icon remains `Mail`, the foreground icon can be `FileText`, `Download`, or a compact `Mail` tile depending on which reads better in the final composition.

Alternative considered: only use the background icon. That makes the card more atmospheric, but the first-glance affordance is weaker.

### Align card and dialog messaging

The card headline, button, dialog title, and dialog description should consistently describe requesting the GitBench analysis PDF. The dialog should not switch to a broader "updates" framing unless the product intent changes.

Alternative considered: keep "Get GitBench updates" in the dialog. That is less specific than the card CTA and can make the email request feel like a newsletter signup instead of a PDF delivery.

## Risks / Trade-offs

- Large decorative icon reduces readability -> Keep it low opacity, place it away from dense text, and verify desktop plus mobile screenshots.
- Stronger CTA visual treatment feels too promotional -> Keep the layout compact, dashboard-native, and focused on the report PDF rather than a landing-page hero treatment.
- Gradient and clipped layers cause layout issues on narrow screens -> Use stable positioning, `overflow-hidden`, responsive icon sizing, and ensure the button/text stack remains above the decorative layer.
- Copy changes imply a PDF delivery promise the backend does not fulfill -> Keep copy aligned with the actual intended follow-up. If the current flow only captures interest, use "Get the analysis" rather than promising automatic attachment delivery.

## Migration Plan

Implement this as a UI-only change to `EmailCta`. The existing API, tests, and backend behavior remain unchanged. If the visual direction is rejected, the component can be reverted to the current generic card treatment without data migration.

## Open Questions

- Should the button say "Get the PDF" or "Get the Analysis PDF"?
- Should the foreground icon remain `Mail`, or should it switch to a PDF-oriented icon so the large background mail icon is not duplicated?
