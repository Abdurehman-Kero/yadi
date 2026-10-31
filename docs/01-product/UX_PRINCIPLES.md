# UX Principles

Visual: white/neutral background, ≤3 brand colours, clear type hierarchy, consistent spacing, minimal shadows, no gradients by default, no decorative animation.

Screens (MVP): Today dashboard · Tasks · Schedule · Assistant · Settings.

Rules
1. One obvious primary action per screen.
2. Every screen designs loading, empty, error and success states.
3. Show what Yadi understood and what it did; never show fake success.
4. AI mistakes are easy to correct; uncertainty is stated honestly.
5. Preserve user input on recoverable errors.
6. Confirm only high-impact or hard-to-reverse actions; offer undo for routine ones.
7. Don't encode priority/status/errors by colour alone (icon + text).
8. Keyboard operable, visible focus, WCAG 2.2 AA contrast, labelled controls, responsive from phone to desktop.
9. Plain, short language.

## Patterns in use (2026-10-31)
- **Today:** Tell Yadi at the top, then next up and the rest of today, with what needs attention at the side.
- **Schedule:** a day strip above a day drawn to scale; details and moving live in a modal, so the timeline stays calm.
- **Tasks:** one-click completion, grouped by when; secondary actions in a menu.
- **Forms:** essentials first, the rest under "More options"; primary action bottom right.
- **Confirmations** are brief toasts that do not move the layout; errors stay until dealt with.
- **Words:** statuses say what they mean to the person ("Needs details", "Ready to plan"), not system terms.
