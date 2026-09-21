# Event Model — how the shell decides to do work

The rule is stated as a motto ("no polling") but it is enforced by structure.

## Sources of work

| Source | Mechanism | Examples |
|---|---|---|
| Wayland events | `wl_display` fd in the main loop | pointer, keyboard, frame callbacks, configure |
| Timers | `TimerManager` (one-shot and repeating) | hover intent (350 ms), carousel settle (90 ms), OSD dwell (1400 ms) |
| Animation frames | `AnimationManager::tick`, driven only while animations exist | every animated property |
| inotify | config directory watch | `rice.toml` edits apply live |
| D-Bus | sdbus-c++ | notifications, logind, UPower, network, bluetooth |
| PipeWire | its own loop | volume changes, spectrum data for the visualiser |
| Poll sources | `PollSource` fds | `ThumbnailService` and `WallpaperScanner` signal completion with eventfd |

## The one periodic tick

A single 1 Hz `TimeService` tick drives the clock-dependent surfaces (bar, desktop widgets, lockscreen widgets,
settings window, idle manager). **Measured:** disabling the bar's part of it changed idle CPU not at all
(1.10 % vs 1.00 %, within noise), so it was left alone rather than counted as an optimization.

## Background threads

| Thread pool | Purpose | Notes |
|---|---|---|
| `ThumbnailService` workers | image decode + downsample | results land via eventfd; the main thread uploads textures |
| `WallpaperScanner` worker | directory walk + `stat` | was synchronous upstream and froze the shell on large folders |
| Mesa / PipeWire internal | driver and audio | not ours |

Thread count is **33–34** and did not move across any stress run.

## What the shell deliberately does *not* do

- No per-frame subprocess, no shell script on a timer, no resident helper process.
- No plugin **services** (they arm an unconditional 1 s timer) — the Motion settings are a *panel*.
- No animation used as a timer. A dwell is a `Timer`; using an animation would keep the frame clock alive, which
  is exactly the defect Phase 4 removed from the OSD.
- No work for surfaces that are merely visible: an open Control Center costs the same as the bar alone.

## Consequence for reviewers

If a change adds a repeating timer, a thread, or a subprocess, it needs a justification in the commit message and
a measurement. The three optimizations that mattered most in this project all came from *removing* work that ran
when nothing had changed.
