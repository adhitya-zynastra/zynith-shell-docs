# Surface Hierarchy — Depth, Lifetime, Material

**Implemented 2026‑09‑26 (sixth batch).** Code: `src/shell/surface/surface_role.*`. Tests: `design_tokens_test`
(hierarchy section), `spatial_model_test` (lifetimes).

The research found one surface treatment everywhere. The hierarchy gives each surface a role that decides its depth,
whether it is persistent or transient, its layer-shell layer and its material. **Not everything is glass.**

| Depth | Role | Lifetime | Layer | Material | Examples |
|---|---|---|---|---|---|
| 0 | Scene | persistent | Background | the wallpaper | wallpaper |
| 1 | Atmosphere | persistent | Bottom | **no chrome**: no fill, blur or shadow | desktop widgets, the visualiser |
| 2 | Frame | persistent | Top | glass at the frame's own opacity (a bar's `background_opacity`), blur only when translucent, the frame's own `shadow` | bars, dock |
| 3 | Surface | transient | Top | Glass panel surface (`[shell.glass]` + `[shell.panel]`), `[shell.panel].shadow` | Control Center, launcher, wallpaper browser |
| 3 | Embedded | inherits | inherits | a **tone step** (surface-variant at the card opacity): no blur, no shadow, hairline if card borders are on | cards inside a surface |
| 4 | Overlay | transient | Top | panel glass over a scrim | the power menu |
| 5 | Floating | transient | Overlay | panel glass, `[shell].popup_shadows` | OSD, toasts |

**Why Floating is above Overlay.** Brief feedback (a volume change, a notification) must stay visible while a modal
is open. That is already how the shell behaves: the OSD is on the Overlay layer and modal panels are on Top. The
hierarchy records it instead of contradicting it.

## Where it is real, not only documented

- **Layers come from the role** for surfaces with a fixed layer: the OSD (Floating), desktop widgets (Atmosphere),
  the wallpaper (Scene) and the panel default (Surface). The values are identical to before.
- Bars and notifications keep **config-owned** layers (`[bar].layer`, `[notification].layer`); the role gives only
  the default.
- **Materials call Glass.** `material(Surface)` is tested to equal `glass::panelSurface` for the same config, so the
  hierarchy cannot drift from the owner of fill, tint, blur and border (ADR‑0016). No surface has been switched to
  `material()` yet; that happens as each is redesigned.
- **Shadows reuse their owners:** `[shell.panel].shadow`, `[shell].popup_shadows`, and a bar's or the dock's own
  flag. No shadow setting was added. Shadow blur stays the shared 12 px helper, because surface sizes depend on its
  bleed.

## Persistent vs transient

- **Persistent** (scene, atmosphere, frame): always mapped. It has no origin; it *is* the origin transient UI grows
  from. Its changes are element motion; bars returning from auto-hide use the surface roles.
- **Transient** (surface, overlay, floating): created on demand and destroyed after dismissal. It has an origin
  ([`spatial-model.md`](spatial-model.md)). It enters with `surface-reveal` and leaves with the shorter
  `surface-dismiss`.

This is `shell::spatial::policy(Lifetime)`, and a test checks every role against it.
