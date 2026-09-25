# ADR-0016 — Glass is a shared model of decisions, not a renderer

**Status:** Accepted, implemented · **Date:** 2026‑09‑25

## Context
Every translucent shell surface decided its own fill, border and blur, with a separate opacity key per surface
type. The launcher, Control Center, OSD, notifications, widgets and lock screen are all due to be reworked, and I
wanted them to share one surface language instead of each growing its own glass code.

Three facts shaped it. Surface colours are already palette roles resolved live (`ColorSpec`), which is what keeps
the desktop wallpaper-derived. Existing keys already covered part of the ground — transparency mode, borders,
shadow. And niri controls blur strength globally, not per surface.

## Decision
1. `shell::glass` returns a `SurfaceStyle` of palette roles and a blur flag. It draws nothing, owns no nodes, and
   allocates nothing per frame.
2. **Reuse keys that already mean the right thing** (`transparency_mode`, `borders`, `shadow`,
   `corner_radius_scale`); add `[shell.glass]` only for what they could not express.
3. **Custom opacity is a fourth transparency mode**, not an optional float beside the mode. The three named modes
   stay the coarse presets; `custom` unlocks the slider.
4. **Tint is a role inside `ColorSpec`**, mixed in `resolveColorSpec()`, so it follows palette changes.
5. **Blur strength is intent-level (0–100) and compositor-global**, generated into niri's `blur {}` node through
   the ADR‑0015 fragment writer. 50 reproduces the existing tuning exactly.
6. No blur request behind an opaque fill.

## Why
Point 2 is the one I would defend hardest. A second border toggle or a second opacity control beside the existing
ones gives a property two owners — the exact problem ADR‑0014 exists to prevent. Point 4 because the alternative, a
pre-mixed fixed colour, silently stops following the wallpaper. Point 5 because niri gives no choice: a second
`blur` node is a config error.

## Alternatives
- *A rendering layer that draws glass for each surface* — rejected: a new abstraction over a scene graph that
  already draws these surfaces, with no benefit over returning the style.
- *An optional `glass.opacity` overriding the mode* — rejected: the schema has no optional-float binding, and a
  value that silently replaces an enum is harder to reason about than a mode that says `custom`.
- *Exposing niri `passes`/`offset` directly* — rejected: implementation internals a user cannot reason about.
- *All sixteen palette roles for tint* — rejected: text roles are meaningless as a tint.

## Consequences
- Only floating panels consume glass fully today; attached panels follow the bar's opacity and only the blur gate.
- Blur strength affects windows as well as shell surfaces. Stated in the UI.
- `ColorSpec` grew two fields. It is in a widely-included header, so the change required a clean rebuild
  (ADR‑0013).
