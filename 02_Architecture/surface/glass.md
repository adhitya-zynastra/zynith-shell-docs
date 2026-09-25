# Glass — The Shared Surface Model

**Added:** 2026‑09‑25. **Source:** `src/shell/surface/glass.{h,cpp}`, `src/ui/palette.{h,cpp}` (tint),
`src/compositors/niri/niri_config_fragments.cpp` (blur strength). **Decision:** [ADR‑0016](../../05_Decisions/ADRs/ADR-0016-glass-surface-model.md).

## What I wanted

Glass is most of what makes Zynith look like Zynith, and it was scattered: every surface type carried its own
opacity knob and made its own decisions about fill, border and blur. The Control Center, launcher, OSD,
notifications, settings, widgets and lock screen are all going to be reworked, and I did not want each of them to
grow its own glass code. So before touching any of them, the surface decisions move into one place they can all
consume.

## What it is — and deliberately is not

`shell::glass` is a set of **decisions**, not a renderer. Given the configuration it returns a `SurfaceStyle`:
a fill, a border colour, whether to draw a border, and whether to ask the compositor for blur. It draws nothing,
owns no scene nodes, allocates nothing per frame and creates no surfaces. Blur remains the compositor's job.

Everything it returns is a **palette role** (`ColorSpec`), never a resolved colour. That is the property that
keeps glass wallpaper-derived: a surface's colours re-resolve against whatever palette is live, so a wallpaper
change re-tints every glass surface without anything needing to re-apply its style.

## Properties

| Property | Key | Notes |
|---|---|---|
| Transparency | `shell.panel.transparency_mode` | solid / soft / glass (1.0 / 0.80 / 0.55) — unchanged — plus new **custom** |
| Opacity | `shell.glass.opacity` | used only in custom mode |
| Blur on/off | `shell.glass.blur` | also off automatically behind an opaque fill |
| Blur strength | `shell.glass.blur_strength` 0–100 | **compositor-global**, see below |
| Tint on/off | `shell.glass.tint` | |
| Tint colour | `shell.glass.tint_role` | primary / secondary / tertiary / surface_variant |
| Tint strength | `shell.glass.tint_strength` 0–1 | RGB mix; never changes opacity |
| Border on/off | `shell.panel.borders` | unchanged key, moved into Zynith Corner |
| Border colour | `shell.glass.border_role` | outline / primary / secondary / tertiary / surface_variant |
| Border opacity | `shell.glass.border_opacity` 0–1 | scales the fill's alpha, as the border always has |
| Shadow | `shell.panel.shadow` | unchanged key, moved into Zynith Corner |
| Radius | `shell.corner_radius_scale` | unchanged, global; not duplicated here |

The existing keys were kept where they already meant the right thing. Adding a second border toggle or a second
opacity control beside the old ones would have given each property two owners.

Tint and border colours are a **curated subset** of the sixteen palette roles. The `On*` roles are text colours
and make no sense as a tint, so they are not offered.

### Why blur strength is global

I expected per-surface blur strength. niri does not support it. A shell surface can only *request* blur for a
region (`ext-background-effect`); how strong that blur is comes from niri's single top-level `blur {}` node, and a
second `blur` node is a hard config error. So `blur_strength` generates `~/.config/niri/rice/glass.kdl`, through
the same validated writer as motion, and it affects every blurred surface — windows included. The Zynith Corner
description says so.

The 0–100 scale is intent-level rather than exposing niri's `passes` and `offset`, which a user cannot reason
about: `passes = 1 + round(4·s)`, `offset = 1 + 6·s`. **50 lands exactly on passes 3 / offset 4.0**, the tuning
this desktop has used since Phase 1. `noise 0.025` and `saturation 1.25` stay fixed.

### The tint lives in ColorSpec

A tint is a blend of two roles, and `ColorSpec` could only express one. Baking the blend into a fixed colour would
freeze it at the palette of the moment. So `ColorSpec` gained an optional `tint` role and `tintStrength`, mixed in
`resolveColorSpec()` — the single function every role already goes through. Untinted specs are unaffected, and
equality includes the tint, so a changed tint re-applies.

## Consumers

**Today: floating (detached) panel surfaces**, through both panel hosts (`PanelManager`, `PersistentPanelHost`).
`panel_surface_style.h` delegates to `shell::glass`, so the hosts did not each have to be rewritten. On this
desktop's configuration that is the **launcher, clipboard and session menu**.

**Partly:** panels *attached* to the bar — here the **Control Center and wallpaper panel** — take the bar's opacity
for their fill so they read as part of it. They do go through the glass blur gate, so `glass.blur = false` affects
them, but fill, tint and border colour do not.

**Not yet:** the bar, OSD, notifications, dock and desktop widgets still use their own opacity keys. They move onto
glass with their own redesigns — and when the bar does, attached panels follow automatically.

## Behaviour preserved

With default settings the model reproduces the previous panel exactly — `Surface` at the mode's opacity,
`Outline` at the same alpha — and `tests/glass_surface_test.cpp` checks that equality directly.

## One behaviour change

Previously **every** decorated panel requested compositor blur, including in Solid mode, where the fill is opaque
and the blur is invisible work. The glass gate stops requesting it behind an opaque fill or when glass blur is
off. That is the only visible-to-the-compositor change at default settings, and it is a reduction.
