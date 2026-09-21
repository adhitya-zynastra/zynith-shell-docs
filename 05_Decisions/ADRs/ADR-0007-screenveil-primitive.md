# ADR-0007 — One veil primitive for every full-screen transition

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 2), extended 2026‑09‑20 (Phase 6)

## Context
niri refuses compositor actions while the session is locked, so the unlock could not be bridged with
`DoScreenTransition`. Separately, the modal power menu and later the wallpaper browser both needed a dimmed
full-screen backdrop.

## Decision
Add one primitive — `ScreenVeil` (`src/shell/veil/screen_veil.{h,cpp}`): a short-lived, full-screen,
click-through layer surface that draws an optional blurred texture under a palette tint and fades on the shell's
own `AnimationManager`. No timers, no polling; the owner destroys it when the fade completes.

Three modes now exist: **wallpaper** (lock/unlock bridge), **image** (screencopy snapshot, power menu), and
**tint-only** (Phase 6, for surfaces that must not freeze what is behind them).

## Consequences
- Three unrelated features share one ~200-line primitive instead of three ad-hoc implementations.
- The *snapshot* mode is a correctness hazard wherever live content matters — that is exactly how the wallpaper
  browser's "applying changes nothing on screen" bug happened, and why `showTint()` exists.
