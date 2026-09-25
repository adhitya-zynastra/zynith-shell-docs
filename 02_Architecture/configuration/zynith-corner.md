# Zynith Corner

**Added:** 2026‑09‑25, alongside the motion and glass work. **Source:** `src/shell/settings/settings_registry.{h,cpp}`.

## What it is

Zynith Corner is where Zynith's own appearance and behaviour are customised — motion, glass, and, as later work
lands, the bar, launcher, widgets, OSD, Control Center and wallpaper UI. It is **not** the general system settings
application: users, network, devices, applications and system configuration belong somewhere else, eventually.

The distinction I wanted is conceptual rather than a second window. Zynith Corner is a **section of the existing
settings window**, sitting at the top of its sidebar, with one group per Zynith system. `settings-open zynith-corner`
opens it, and `Super+Alt+A` is bound to exactly that.

## Why not a separate panel

Every earlier attempt at "a settings UI for X" in this project produced a second settings universe — the Motion
plugin was the clearest case, with its own panel, its own source of truth and a precedence conflict with the main
UI. Noctalia's settings window already has a registry, a control factory, search, reset, override display and
keyboard navigation. A separate Zynith panel would have to rebuild all of that and would immediately disagree with
the main one about what the current value is.

So the foundation is deliberately thin. **A new Zynith setting is still three edits** — a config field, a schema
line, a registry entry (ADR‑0014) — and the only new thing is where the registry entry points.

## Structure

| Group | Contains | Where the keys live |
|---|---|---|
| **Motion** | animations on/off, speed, preset, four niri trims | `[shell.animation]` |
| **Glass** | transparency mode, opacity (custom only), blur, blur strength, tint, tint colour, tint strength, borders, border colour, border opacity, shadow | `[shell.glass]` + `[shell.panel]` |

Group order follows first declaration in the registry. Motion is declared first, so it is what `Super+Alt+A` lands
on.

**Nothing is duplicated.** The seven motion entries were *moved* from Appearance → Motion, and the transparency,
border and shadow entries were *moved* from Panels → Effects. Each key has exactly one control in the whole window.

Controls appear only when they mean something: opacity only in custom transparency mode, tint colour and strength
only with tint on, border colour and opacity only with borders on, blur strength only with blur on. This uses the
registry's existing `visibleWhen`, not new UI machinery.

## Ownership and reset

Unchanged from [ADR‑0014](../../05_Decisions/ADRs/ADR-0014-extend-noctalia-config.md), and now tested rather
than asserted:

```
defaults (config_types.h)  →  rice.toml (the Zynith preset)  →  settings.toml (the user's changes)
```

Reset calls `clearOverride()`, which **deletes** the key from `settings.toml` so the value falls back to the
preset. `tests/zynith_config_ownership_test.cpp` checks this against a real `ConfigService` in a temporary
directory: an override wins, reset removes the key from the file (it does not write today's value), the preset
shows through again, and a later change to the preset reaches the reset key.

## What it does not do yet

- The later groups — bar, launcher, widgets, OSD, Control Center, wallpaper UI — do not exist. They arrive with
  their systems.
- There is no per-group deep link: `settings-open` selects a section, not a group inside it.
- Out-of-range values in hand-edited TOML are still clamped **silently** by the upstream parser; see the
  correction in [`configurability.md`](configurability.md).
