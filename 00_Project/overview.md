# Project Overview

**Evidence basis:** live inspection of the machine on 2026‑09‑21, git history of
`~/.local/src/noctalia-lockfade/source`, and the timestamped backups in `~/.config/rice-backups/`.

## What Zynith is

Zynith Shell is a desktop environment assembled from three layers I control to different degrees:

1. **Upstream, untouched** — Fedora 44, the kernel, Wayland, niri 26.04, PipeWire, the Noctalia RPM.
2. **A reviewed patch series** over Noctalia 5.1.0's source, built locally to `~/.local/opt/noctalia`
   (15 Zynith commits at the time of writing over the pristine base; 16 in total. Base commit `a176ada` = "noctalia 5.1.0 pristine (Fedora SRPM
   noctalia-5.1.0-1.fc44)"). **VERIFIED** by `git log`.
3. **A configuration layer** that owns the design language: `~/.config/noctalia/rice.toml`,
   `~/.config/niri/rice/*.kdl`, plus two Luau plugins under `~/.local/share/noctalia/plugins/`.

The split matters: anything that can be expressed as configuration is configuration, and the C++ patch is reserved
for behaviour the shell cannot otherwise express. That is why the bar redesign is zero lines of C++ while the
wallpaper carousel is ~900.

## What Zynith is not

- **Not a fork.** The Fedora `noctalia-5.1.0-1.fc44` package stays installed. `~/.config/niri/config.kdl`
  spawns `~/.local/opt/noctalia/bin/noctalia` with a fallback to `/usr/bin/noctalia`, so a broken local build
  degrades to the packaged shell rather than to no shell. **VERIFIED** — see `06_Reference/configuration/niri.md`.
- **Not a Hyprland replacement.** Hyprland 0.56.2 remains installed and its configuration under `~/.config/hypr`
  is deliberately untouched, as a fallback session. **VERIFIED** (`rpm -q hyprland`).
- **Not a Caelestia clone.** Caelestia and ZynAku were read as *reference archaeology* for interaction and motion
  ideas; no code or architecture was imported. See `05_Decisions/ADRs/ADR-0009-reference-archaeology.md`.

## Design language

Dark, cinematic, glassy, wallpaper-derived, restrained. Concretely:

- Colours come from the wallpaper through Noctalia's Material‑3 generator (`m3-tonal-spot`, dark mode), so the whole
  shell re-tints when the wallpaper changes.
- Surfaces are translucent with compositor blur (`ext-background-effect` via niri layer rules), one shared corner
  radius, one shadow direction.
- Motion is a small hierarchy of durations and long-tail easings rather than per-component timings.

## Operating constraints the project has always honoured

I set these at the outset and they are reflected throughout the implementation:

| Constraint | Where enforced |
|---|---|
| Never act as a second owner of `~/.local/state/noctalia/settings.toml` (the GUI owns it) | `02_Architecture/configuration/precedence.md` |
| Do not modify Hyprland's configuration | nothing in the repo touches `~/.config/hypr` |
| Do not break the packaged Noctalia | local prefix + spawn fallback |
| No polling, no daemons, no per-frame subprocesses | `02_Architecture/shell/event-model.md` |
| Validate before applying generated config | the shell's niri fragment writer: `niri validate` on a temp copy, atomic replace, full-config rollback |
| Stability outranks aesthetics | `04_Incidents/` — the UAF fix reverted a perf-motivated design |
