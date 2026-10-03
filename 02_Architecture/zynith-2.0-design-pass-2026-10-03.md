# Zynith 2.0 — the reference-driven design pass (2026‑10‑03)

I asked for the design phase proper: Zynith had to stop looking like a generic QML desktop and read as one
environment. Claude re-read Zynith's own written language, **Optics** ([design-language.md](design/design-language.md)),
re-extracted frames from the reference videos in `~/Videos/Downloaded/` (Caelestia, Ryoku, Imperative, End4) and
implemented the language in the Quickshell UI, then applied it surface by surface. No reference code was copied;
the principles came from the earlier source study ([design-research-2026-09.md](design/design-research-2026-09.md)).

## What was taken from where

| Reference | Principle | Zynith's form of it |
|---|---|---|
| Ryoku | paper-and-ink restraint; tracked caps section names; one composed clock | indexed **section heads** in the data voice with a hairline rule ("02  LEVELS ───"); the Control Panel's time as the one big readout |
| Imperative | small grouped pills; mono data; seconds in small type | **readouts**: values in JetBrains Mono, uppercase, tracked, tabular; mono values under bar icons |
| Caelestia | one container, dense but calm; drawer-like origins | the lens material on every panel; groups in a bar set apart by **rules**, not nested capsules |
| Optics (own) | accent is light, not paint; one signal per surface | an **exposure mark** (a 2 px accent tick at the leading edge) for "on" and "current"; ink for levels; the accent only for the one live thing |

## The foundation (in `ui/`)

- Type: a `data` role (mono, caps, tracked, tabular) and `displayXL`; Inter for language, Space Grotesk for numerals.
- Components: `SectionHead`, `Readout`, `Plate` (a tone step), `Signal` (edge light), `FocusBrackets` (the
  autofocus corners, glide between targets).
- Tokens: `radiusSurface / radiusPlate / radiusControl`; `plate`, `signalFill`, `signalEdge`, `signalGlow`, `rule`.

## Surfaces

| Surface | Before | After | Capture |
|---|---|---|---|
| Control Panel | boxed modules, accent-filled tiles, three gold sliders | indexed section heads; composed time readout; tiles neutral with an exposure mark; ink levels with mono readouts | `07_Assets/screenshots/optics-control-panel.png` |
| Bars | filled capsule groups, pill in pill | groups set apart by hairline ticks (`group_style`: rule · plate · capsule); mono readouts under volume, brightness, battery (`readouts`) | `optics-rail-rules.png` |
| Launcher | icon chips, accent-tinted selection | tracked category tabs with a gliding mark; tone-step selection with an exposure mark; mono key legend | `optics-launcher.png` |
| Notifications | caps captions, accent progress | app and time in the data voice; ink progress; the critical edge as an error-coloured exposure mark | `optics-notification.png` |
| OSD | tinted disc, accent bar | plain glyph; "VOLUME … 065" in the data voice; an ink line with a mark of light at its head | — |
| Settings | a grid of 23 equal cards | the wallpaper as a hero band, the machine as readouts, categories as typeset rows under indexed heads, each with a phrase saying where it stands | `optics-settings-home.png` |

The accent budget was the main correction while doing it: the first Control Panel pass lit four tiles and three
sliders in the accent at once; on review, "on" became a mark at the edge and levels became ink.

## Desktop widgets — visually verified

The brief noted they had never been seen uncovered. Claude rendered the desktop layer's own pixels
(`zynith-ui ipc captureBar desktop@eDP-1 <png>`), so windows did not matter. All twelve render from their saved
geometry; the overlapping hour/minute clocks and the weather under them are my own composition.

## Not done yet

Wallpaper browser, overview and lock screen in the new language; widget framework consistency pass; toggles and
segmented controls still use the accent fill. **UNKNOWN** how the hover states read by pointer — no input
injection here.
