## Why

The existing email/PDF CTA on the Overview page reads like a standard dashboard card, so it blends into the surrounding report content instead of acting like a clear offer. The page already has a valuable analysis handoff; the UI should make that next action easier to notice and understand.

## What Changes

- Introduce a dedicated visual treatment for the email/PDF CTA instead of relying on the generic `.card` appearance.
- Use a more distinctive background and border treatment built from the existing GitBench purple and teal brand colors.
- Add a large, clipped background mail icon as a bright decorative watermark that reinforces the email interaction without reducing text readability.
- Add or restore a smaller foreground icon treatment so the CTA has an immediate visual anchor.
- Tighten CTA copy so the card and modal consistently describe the same offer: getting the GitBench analysis PDF by email.
- Preserve the existing dialog-based email capture flow, HubSpot-backed submission behavior, privacy link, validation, and success/error states.
- Preserve responsive behavior so the CTA remains legible and uncluttered on desktop, tablet, and mobile widths.

## Capabilities

### New Capabilities

- `email-analysis-cta`: Defines the Overview page CTA for requesting the GitBench analysis PDF by email, including its visual prominence, messaging alignment, and responsive behavior.

### Modified Capabilities

None.

## Impact

- Affected web UI code:
  - `gitbench/web/src/components/EmailCta.tsx`
  - Potentially `gitbench/web/src/styles/global.css` if a shared CTA class or tokenized styling is preferred over inline utility classes.
- Existing email signup API behavior in `gitbench/web/api/email-signups.ts` is not expected to change.
- No data model, report API, CLI, or dependency changes are expected.
