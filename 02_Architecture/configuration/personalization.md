# Personalization

**Added:** 2026‑09‑25 as "Zynith Corner" (`8c2b4eb`); **renamed Personalization** the same day in the second batch
(ADR‑0017). **Source:** `src/shell/settings/settings_registry.{h,cpp}`.

## What it is

Personalization is where the desktop shell's appearance and behaviour are customised — motion, glass, the Control
Center's frame and the wallpaper browser today; the bar, launcher, widgets and OSD as those systems land. It is
**not** the general system settings application, and it is **not** "Zynith Settings": that is a future system-wide
hub, described in [`settings-information-architecture.md`](settings-information-architecture.md), which is expected
to contain Personalization as one of its categories.

The distinction is conceptual rather than a second window. Personalization is a **section of the existing settings
window**, sitting at the top of its sidebar, with one group per system. `settings-open personalization` opens it,
and `Super+Alt+A` is bound to exactly that.

### Why the name changed

"Zynith Corner" named a brand, not what the section holds, and a branded area would have had nowhere sensible to go
once a real Zynith settings hub exists. "Appearance" is already an existing Noctalia section. "Personalization" is
the conventional settings-hub name for appearance *and* behaviour customization, which is what the groups are.

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
| **Control Center** | style *(new, fifth batch: `zynith` / `classic`)*, density, top navigation, hover-open, hover delay, width | `[control_center]` |
| **Wallpaper Browser** | cinematic carousel on/off, card size *(new)* | `[wallpaper]` |
| **Launcher** | style *(new)*, width, height, icon size, density, key hints *(new)*; show icons, app grid, compact *(moved)* | `[shell.launcher]` |
| **OSD** | orientation, scale, opacity, border *(moved)*; display duration *(new)* | `[osd]` |
| **Sounds** | shell sounds, sound volume, volume/mute/notification cue files *(moved from Services → Audio)* | `[audio]` |
| **Notifications** | scale, opacity, border *(moved)* | `[notification]` |

Group order follows first declaration in the registry. Motion is declared first, so it is what `Super+Alt+A` lands
on.

**Nothing is duplicated.** The seven motion entries were *moved* from Appearance → Motion, the transparency, border
and shadow entries from Panels → Effects, and the Control Center's top navigation, hover-open, hover delay and width
from Control Center → Layout. Each key has exactly one control in the whole window. The Control Center section keeps
its functional options — placement, sidebar modes, tabs, shortcuts, calendar.

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

## Audit — does every visible setting do something? (2026‑09‑26)

I reported options that changed nothing. Claude traced every Personalization key to its runtime consumer:

| Group | Finding | Change |
|---|---|---|
| Glass — tint, tint colour, tint strength | reached floating panels, OSD and notifications, **not bars or bar-attached panels** — which is where my Control Center lives | tint now applies to bars and attached panels too (`shell::glass::tinted`), alpha still owned by `[bar].background_opacity` |
| Glass — transparency, opacity, borders | floating panels only, by design (an attached panel must match its bar) | descriptions now say so |
| Wallpaper Browser — carousel | said "applies after the shell restarts"; the panel is rebuilt on every open | description corrected: next open |
| Launcher — key hints | removed with the footer | — |
| Launcher, Control Center, OSD, notifications | apply on the next open / next appearance (their surfaces are temporary) — stated where it was not | — |
| Motion, Sounds, wallpaper card size, CC hover | live | — |

Runtime confirmation of the Glass-on-bars change is still outstanding (see the validation record).

## Fifth batch additions (2026‑09‑26)

| Key | Where it is set | Control |
|---|---|---|
| `[control_center].style` — `zynith` (default) / `classic` | Personalization → Control Center | segmented; lands on the next open (the panel is built on open) |
| `[shell].display_font_family` — empty = the interface font | Appearance → Interface, beside the interface font | text or font picker, placeholder "Interface font" |
| clock widget `weight` — `light` / `regular` / `bold` (default `bold`) | desktop and lock screen widget editors, digital clocks only | segmented |

The display font is an appearance-wide typography role, not a Control Center option, so it sits beside `font_family`
rather than in a Personalization group — one owner per property (ADR‑0016). The lock screen composition itself is not
a setting: it is the preset in `lockscreen.toml`, and the editor's changes are overrides in `settings.toml`.
