# Phase 1 — The Rice Pass

**Window:** 2026‑09‑19 18:23 → ~19:30 (bounded by the `pre-rice` and `pass3-*` backups).
**Nature:** configuration only. No C++ was compiled in this phase — the patch repository's first Zynith commit
comes later, in Phase 2.

This is the phase I originally thought was the whole project: make the desktop look right. It is also the phase
that established the rule the rest of Zynith follows — configuration first, code only where configuration cannot
reach — because everything here turned out to be achievable without compiling anything.

## Goals

Dark glass desktop with a wallpaper-derived palette; Hyprland keybindings ported to niri; per-application
transparency; a polished bar; a redesigned launcher surface; all applied live with validation and backups.

## What was built

### Configuration restructure

`~/.config/niri/config.kdl` shrank from **635 → 130 lines** by moving concerns into includes
(`rice/rules.kdl`, `rice/binds.kdl`, later `rice/animations.kdl`), with the generated `noctalia.kdl` kept last so
palette nodes win. **VERIFIED** by comparing the pre-rice backup with the live file.

### Glass

`rice/rules.kdl` (144 lines today) establishes:

- a base window rule: `geometry-corner-radius 12`, `clip-to-geometry true`,
  `draw-border-with-background false`, and `background-effect { blur true }` (xray blur of the wallpaper behind
  translucent windows);
- inactive windows at `opacity 0.93`;
- per-application opacity — Zen 0.97/0.94, Spotify 0.92/0.88, VS Code 0.96/0.92 — with **media, images, games and
  screencast targets pinned at 1.0** so content is never degraded;
- floating windows use real (non-xray) blur so they read as glass over other windows;
- privacy: password managers are `block-out-from "screen-capture"`.

### Palette

`rice.toml` `[theme]`: `source = "wallpaper"`, `wallpaper_scheme = "m3-tonal-spot"`, `mode = "dark"`.
The comment block in that file records the schemes that were tried and rejected (m3-content went grey;
vibrant/faithful/soft were too loud or off-language) — a rare case where the decision history survives in the
artifact itself.

### Bar

Flush to the top edge, inset "tab" silhouette with concave corners (`margin_edge = 0`, `margin_ends = 100`,
`concave_edge_corners = true`), `background_opacity = 0.62`.

### Keybindings

`rice/binds.kdl` — 198 lines today, ported from my Hyprland configuration. I did not want to relearn muscle
memory just because the compositor changed.

## Bugs in this phase

See [`bugs.md`](bugs.md).

## Retrospective amendments

| Later phase | What it changed here |
|---|---|
| Phase 6 (`rice.toml`, no commit — config only) | The bar was re-composed from per-widget pills into three glass clusters (`capsule = false` + `capsule_group` for time/status/sys) |
| Phase 6 (`e9e27b0`) | Notification layer rule gained `background-effect { blur true }`; panel radii unified |

## Final state

A coherent dark-glass desktop driven entirely by configuration, with the stock niri config preserved verbatim at
`~/.config/niri/config.kdl.save` and a full backup in `rice-backups/20260919-182322-pre-rice/`.
