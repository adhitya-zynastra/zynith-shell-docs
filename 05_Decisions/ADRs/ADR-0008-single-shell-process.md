# ADR-0008 — One shell process, many layer-shell surfaces

**Status:** Accepted (inherited from Noctalia, deliberately preserved) · **Date:** 2026‑09‑19

## Context
Bar, panels, notifications, OSD, lock screen and wallpaper could each be a separate process, as in many modular
desktop setups. Noctalia does not work that way, and I had to decide whether to keep that or work around it.

## Decision
I kept the single-process model deliberately rather than by default: every surface is a layer-shell surface created by one process sharing one
GPU context, one `AnimationManager`, one `ThumbnailService`, one texture manager and one Wayland connection.

## Consequences
- **Efficiency:** ~1.4 % of one core at idle for the entire chrome, and caches are genuinely shared — the wallpaper
  browser and the control center use the same thumbnail service.
- **Blast radius:** a fault in a shared primitive takes down all chrome at once, as the `Signal` UAF did. This is
  the direct justification for ADR‑0011's strictness and for the regression tests.
- Resource ownership must be explicit *within* the process (session tagging in `ThumbnailService`), because
  process boundaries are not doing that job.
