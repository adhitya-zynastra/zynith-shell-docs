# Phase 4 — OSD System

**Window:** 2026‑09‑20 02:40 (`phase4-osd` backup) · **Commit:** `40c1936`
("osd: zynith layout, value glide, event-loop hold"), refined by `803664d`.

## Goal

Volume and brightness OSDs that match the Zynith language: compact glass card, wallpaper-derived colour, smooth
entrance, value transition and disappearance — without adding a second animation engine or any resident timer.

## Implementation

| Change | Detail |
|---|---|
| Layout | Accent-tinted icon disc + title line over the bar + value; taller card. Text-only OSDs (media, layout) and the vertical layout keep the original look |
| Value glide | The progress bar animates to new values on the shell `AnimationManager` and **retargets mid-glide** instead of stacking animations |
| Card silhouette | `osdCardRadius()` scales radius with card height (×0.36), floored by the themed radius; the compositor blur region uses the same value so glass and fill share one outline |
| Placement | `[osd]` in `rice.toml`: `bottom_center`, `offset_y = 56`, `scale 1.0`, `background_opacity 0.72` |

## The performance finding that justified the phase

The on-screen hold (1.4 s) was implemented as an `animateTimer` — an animation whose only job was to wait. That
keeps the frame clock running for the entire hold. Replacing it with a `TimerManager` one-shot removed
**~50–80 wakeups per second** while a static OSD was visible. **RECOVERED** from the session record and the patch
README; the current code uses `Timer`.

## Retrospective amendments

| Later phase | Change |
|---|---|
| Phase 5 (`803664d`) | Mute cue behaviour moved into `AudioOsd::showOutput/showInput`; volume cue cooldown 70 → 110 ms |
| Phase 6 (`e9e27b0`) | Easings switched to `EaseOutQuint`; **`kHideDelayMs` pinned at 1400 ms** because it had been derived from the motion tiers and would otherwise have drifted to 1.82 s |
