## 1. CTA Visual Shell

- [x] 1.1 Replace the outer generic `.card` treatment in `EmailCta` with a dedicated CTA container that uses a stronger branded background, border, and shadow.
- [x] 1.2 Add stable responsive layout classes so the CTA content and trigger button stay aligned on desktop and stack cleanly on mobile.
- [x] 1.3 Keep decorative layers behind foreground content with explicit positioning, stacking, and `overflow-hidden`.

## 2. Icon Treatment

- [x] 2.1 Add a large clipped decorative mail icon in the CTA background using a bright teal or teal-purple brand accent at low opacity.
- [x] 2.2 Mark the large background icon as decorative and non-interactive with `aria-hidden` and pointer-event-safe styling.
- [x] 2.3 Restore or add a smaller foreground icon or icon tile that communicates the email/PDF action without duplicating the background treatment too heavily.

## 3. Copy And Dialog Alignment

- [x] 3.1 Update the CTA headline, body copy, and trigger label to describe the GitBench analysis PDF clearly and concisely.
- [x] 3.2 Update the dialog title and description so they match the card offer instead of generic updates language.
- [x] 3.3 Preserve the privacy link, validation messaging, success confirmation, error handling, submitting state, and close/reset behavior.

## 4. Verification

- [x] 4.1 Run the web build from `gitbench/web` with `pnpm build`.
- [x] 4.2 Verify the CTA visually on desktop and mobile viewports, checking that text, button, foreground icon, and background mail icon do not overlap incoherently.
- [x] 4.3 Verify the dialog still opens, validates email input, displays loading/error/success states, and resets on close.
