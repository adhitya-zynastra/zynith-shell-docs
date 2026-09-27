# Design Foundation — What Batch 6 Implemented

**Written:** 2026‑09‑26 (sixth batch). **Implementation:** uncommitted working tree on top of `e521a86` (this batch,
like the fifth, ran with no git operations by my instruction). **Validation:**
[`foundation-batch6.md`](../../03_Performance/benchmarks/foundation-batch6.md).

The design research ([`design-research-2026-09.md`](design-research-2026-09.md)) concluded that Zynith's visual
problem is structural: no spatial origin, one surface treatment, and typography and motion without semantics. This
batch builds the foundation future surfaces inherit. **It redesigns no screen.** I had Claude inspect the existing
systems first and extend them; nothing that worked was replaced.

| Part | Page | Built on (unchanged owner) |
|---|---|---|
| Design tokens: geometry, typography, semantic colour, contrast | [`design-tokens.md`](design-tokens.md) | `Style` constants, the palette/theme engine, the text renderer |
| Surface and depth hierarchy | [`surface-hierarchy.md`](surface-hierarchy.md) | Glass (ADR‑0016), the shared shadow helper, layer-shell layers |
| Spatial model ("Optics") | [`spatial-model.md`](spatial-model.md) | the position-reference model (ADR‑0018), `PanelManager` placement, attached-panel reveal |
| Motion language | [`motion-language.md`](motion-language.md) | `AnimationManager`, `MorphTransition`, `MotionService` |

## Status — implemented, consumed, or only defined

The brief asked me not to call a primitive complete if it is only conceptual. This table is the honest state.

| Primitive | Implemented + tested | Consumed at runtime by | Not yet consumed |
|---|---|---|---|
| Motion roles | yes | buttons (Focus), every panel's reveal/dismiss, Control Center section morph, Control Center nav indicator | ContentReveal, ContentDismiss, ElementResize, SceneChange |
| Spring channel in `AnimationManager` | yes | the nav indicator (ElementMove); **Batch 7:** the command bar's item expansions | — |
| `MotionValue` / `MotionRect` | yes | the nav indicator; **Batch 7:** one `MotionValue` per command-bar item | — |
| Geometry tokens | yes | Surface radius: panels, toasts, wallpaper browser (it replaced three private copies); **Batch 7:** spacing, plate/control radius, pill, control and icon sizes in the Zynith Control Center (command bar, Home, section plates) and the lock `session_actions` capsule | the other surfaces' private spacing |
| Typography roles | yes (incl. tabular figures, measured) | the face list is fed from config at runtime; **Batch 7:** Zynith Home (Display time, Data media readout, Label/Micro/Subtitle), section headings (Subtitle), command-bar labels, chips; the lock clock's `face`/`tabular` | launcher, OSD, notifications |
| Semantic colour | yes | the nav indicator's selection fill and edge; **Batch 7:** Hairline (command-bar rule, plates), Muted (captions, readouts), SelectionFill/Edge (chips), Accent (avatar focus), Error/OnError (armed power action) | launcher, OSD, notifications |
| Contrast (`legibleOn`) | yes | — | all (lock screen and desktop widgets, Batch 7) |
| Surface roles | yes | layer choice of the OSD, desktop widgets, wallpaper, panel default | `material()` (tested equal to Glass; no surface switched to it) |
| Spatial origin | yes | carried by bar-widget, bar-area and command opens; recorded and logged by `PanelManager` | no surface derives its entrance geometry from it yet |

## Configuration ownership

**No configuration key was added, removed or changed in this batch.** Tokens, roles and the hierarchy are design
system constants in code. The existing user preferences they honour keep their single owners:
- `[shell].corner_radius_scale` — radii;
- `[shell].font_family` and `display_font_family` — faces;
- `[shell.animation].enabled` and `speed` — reduced motion and tempo;
- `[shell.glass]`, `[shell.panel]` and each bar's and the dock's own opacity and `shadow` — materials;
- `[bar].layer` and `[notification].layer` — the layers of those surfaces, which stay config-owned; the role supplies
  only the default.

## Performance constraints kept

- One animation engine: the spring is a second kind of entry in `AnimationManager`'s list, ticked by the same loop.
- No polling, helpers or per-frame work outside active animations. A settled spring leaves the manager empty, which
  is what lets a surface stop requesting frames. This is tested, and measured at runtime (validation record).
- Contrast and type resolution are evaluated when something changes, never per frame.
- The spatial origin is a small value copied once per open request.

## Relationship to the existing systems

- **`AnimationManager`** stays the only clock. It gained `animate(role, …)`, `animateSpring`, `retarget` and
  `sample`. Raw `animate(from, to, ms, easing)` still works for the 60-odd call sites not yet migrated.
- **`MorphTransition`** stays the choreography primitive for a surface changing state around a shared frame, and
  gained a role-timed `start`. Shared-element *geometry* now uses `MotionRect`: a progress leg carries position,
  but a spring per edge also carries velocity.
- **Glass** remains the single owner of fill, tint, blur and border. The surface hierarchy calls it and adds depth,
  lifetime, layer and the shadow-key choice.
- **The coordinate model** is unchanged. An origin is recorded in the same output-local space as the existing
  anchor, and placement is still `PanelManager`'s.
