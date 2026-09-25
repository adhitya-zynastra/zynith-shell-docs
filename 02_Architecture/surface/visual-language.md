# Zynith Visual Language

**Written:** 2026‑09‑26 (fifth batch). This page records the shared decisions the Control Center, lock screen,
launcher, OSD and notifications are built on, so each surface consumes a token instead of inventing a value.
Validation: [`tracks-cc-lock-visual.md`](../../03_Performance/benchmarks/tracks-cc-lock-visual.md).

## Material

| Role | Token | Used by |
|---|---|---|
| Surface fill | palette `surface` at the surface's own opacity key, tinted by `[shell.glass]` (`shell::glass`) | bars, attached and floating panels, OSD, notifications, lock screen tiles |
| Card inside a surface | `surface_variant` at the card opacity step (`glass::cardOpacity`) | Control Center cards, launcher search bar |
| **Selection / active** | `primary` at 0.16–0.18 fill + `primary` hairline at 0.5–0.55 + `primary` foreground | launcher selected row, Control Center navigation indicator, Control Center active quick controls |
| Idle control | card fill + `on_surface` hairline at 0.07, `on_surface_variant` foreground | Control Center quick controls |
| Error / destructive | `error` fill + `on_error` foreground, only in an armed or failed state | lock screen power controls when armed, critical notifications, failed password |
| Ambient accent | `primary` → `tertiary` | lock screen horizon visualiser |

Solid `primary` fills are no longer used for "on" or "selected" in the Zynith styles. A tinted fill with an edge
reads as a state of the surface; solid primary blocks read as a row of buttons, and on a light wallpaper-derived
primary the text on them loses contrast.

## Geometry

| Token | Value on this desktop | Rule |
|---|---|---|
| Outer surface radius | 16 px (`max(radiusXl × corner scale, 16)`) | panels, notification cards, lock screen tiles |
| Inner card radius | ≈ 7 px (`radiusXl × corner_radius_scale 0.6`) | cards inside a panel — outer radius minus the padding |
| Pill | height / 2 | password field, search bar, tags |
| Hairline | 1 px (`Style::borderWidth`) | every edge above |
| Quick-control tile | landscape, height = 0.62 × width (Zynith); near-square 0.82 (classic) | Control Center Home |
| Spacing | 4 / 8 / 12 / 16 (`spaceXs…spaceLg`) × density | all surfaces; Control Center and launcher scale it by `density` |

## Typography

| Role | Face | Where |
|---|---|---|
| Interface | `[shell].font_family` (Montserrat here) | all shell text |
| **Display** | `[shell].display_font_family` *(new)*, empty = the interface face; set **Light** at display sizes | Control Center hero clock (60 px) and section titles, lock screen clock (`weight = "light"`) |
| Technical | JetBrains Mono Nerd Font | bar clock variants, terminal contexts |

Dates are written one way: `"%A, %d %B"` ("Saturday, 26 September") — the preset's `[shell].date_format`, used by
the Control Center hero and the calendar widget, and the lock screen's date line.

The brief named Inter (interface) and Space Grotesk (display). **Neither is installed on this machine**, and this work
does not install packages or download fonts. The display role therefore falls back to Montserrat Light. Once Space
Grotesk is installed, `display_font_family = "Space Grotesk"` in `rice.toml` changes every display moment at once.

## Motion

Unchanged from [`motion-language.md`](../animation/motion-language.md): entrances decelerate on `animNormal`, exits
accelerate on the shorter `animExit`, and state changes within a surface are morphs around a shared element
(`MorphTransition`) — the Control Center's navigation indicator. The lock screen keeps its approved Phase 2
choreography, plus the failed-password shake.

## Placement

Surfaces name their coordinate space ([`coordinate-model.md`](../layout/coordinate-model.md)); widgets name their
anchor ([`responsive-layout.md`](../layout/responsive-layout.md)). No surface carries a resolution-specific offset.
