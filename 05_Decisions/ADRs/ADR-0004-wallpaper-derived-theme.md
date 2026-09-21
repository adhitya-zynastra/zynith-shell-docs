# ADR-0004 — Wallpaper-derived palette as the colour source of truth

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 1) · **Evidence:** VERIFIED — `rice.toml [theme] source = "wallpaper"`, `wallpaper_scheme = "m3-tonal-spot"`, `mode = "dark"`.

## Context
I wanted one colour identity across the bar, panels, OSD, notifications, lock screen **and** niri's own window
decorations — and I did not want to hand-maintain a palette every time I changed wallpaper, because I knew I
would stop doing it within a week.

## Decision
Generate the palette from the current wallpaper using Noctalia's Material‑3 generator, scheme `m3-tonal-spot`,
dark mode. Noctalia exports it to `~/.config/niri/noctalia.kdl`, which `config.kdl` includes **last** so its nodes
win.

## Alternatives
`m3-content` (went grey on the reference wallpaper), vibrant/faithful/soft (too loud or off-language), and a
hand-written static palette (rejected: would not follow the wallpaper). The rejected schemes are recorded in a
comment in `rice.toml` — the artifact carries its own decision history.

## Consequences
- Changing the wallpaper re-tints the entire shell, which is a feature — and is also why a palette transition
  animates every frame, which is the code path that later exposed the `Signal` use-after-free.
- Only the core Material‑3 roles exist; `surface_container_high` and friends are rejected by the validator.
