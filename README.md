# Zynith Shell — My Engineering Record

**Documentation version 1.1** · source commit `57debbc` · last audited phase **6** · machine-readable metadata in
[`VERSION.json`](VERSION.json)

Zynith Shell is my attempt to build a Fedora Wayland desktop that is cinematic and configurable without giving up
the stability of the distribution underneath it, or spending CPU I would rather give to my actual work.

This repository is the engineering record of that project: what I built, why I chose each approach, what broke,
and what I could not establish. I did the design and the decisions; **Claude Code acted as my engineering
assistant** — it inspected the system, wrote the patches I specified, ran the benchmarks, chased the backtraces,
and drafted these documents from the evidence. Where a measurement or an investigation is attributed in these
pages, it is attributed to whoever actually performed it.

## What it is, concretely

A desktop built on **Fedora 44 + niri 26.04 + a locally patched Noctalia 5.1.0**. It is not a fork and not a
theme: it is a small, reviewed patch series over the packaged Noctalia shell, plus a configuration layer that
owns the design language, plus two Luau plugins. The Fedora package stays installed and untouched; my patched
build lives in `~/.local/opt/noctalia` and niri launches it with a fallback to `/usr/bin/noctalia`.

**Why niri and Noctalia.** Both were already on the machine and already my session before the project started
(**VERIFIED** — see [Phase −1](01_Phases/Phase_-1/README.md)); the decision I actually made was to build *on*
them rather than replace them. My reasons for originally adopting niri are not recorded anywhere I can cite, so
I am not going to reconstruct them here. What I can say is what made the stack worth keeping: Noctalia 5.1 is a
native C++ shell rather than a scripted one, so the whole desktop chrome — bar, panels, notifications, OSD, lock
screen and wallpaper — is one process with one animation clock, instead of a pile of widgets each running its own
timer. That single property is what made the resource targets in this project reachable at all.

**Why Hyprland is still installed.** This is my daily-driver laptop. I was never willing to be one bad build away
from having no desktop, so Hyprland 0.56.2 and its configuration stay untouched as a working fallback session.
That decision cost me something later — it is the direct cause of the notification outage in Phase 6 — and I would
still make it again.

## How I decide things

> *FAST. OPTIMIZED ASF. PERFORMANCE GODLY. STABLE ASH.*

That is the motto, and it is not a joke about benchmarks — it is a statement that optimization is only worth
having if the machine still boots into a working desktop afterwards. When the two collided, stability won; the
[Signal use-after-free postmortem](04_Incidents/postmortems/2026-09-20-signal-uaf.md) is what that looks like in
practice. The priority order I actually apply is: correctness → stability → security → responsiveness → resource
efficiency → maintainability → configurability → aesthetics. Aesthetics is last on that list and is still the
reason the project exists; the ordering is about what gives way when two of them conflict, not about what I care
about. The longer form is in [`00_Project/philosophy.md`](00_Project/philosophy.md).

Two rules follow from it and appear everywhere in this repository. **Anything expressible as configuration is
configuration** — the Phase 6 bar redesign contains zero lines of C++. And **no optimization is claimed without a
before and after**, including the ones that turned out to be worthless: removing the bar's 1 Hz update measured no
improvement and was reverted rather than written up as a win.

## Start here

| If you want to… | Read |
|---|---|
| Understand what this project is | [`00_Project/overview.md`](00_Project/overview.md) |
| See the whole system from hardware upward | [`02_Architecture/system/layers.md`](02_Architecture/system/layers.md) |
| Find a file | [`00_Project/repository-map.md`](00_Project/repository-map.md) |
| Understand configuration precedence (**read before editing anything**) | [`02_Architecture/configuration/precedence.md`](02_Architecture/configuration/precedence.md) |
| Build, test, validate, recover | [`06_Reference/maintenance.md`](06_Reference/maintenance.md) |
| Diagnose a symptom | [`06_Reference/troubleshooting/index.md`](06_Reference/troubleshooting/index.md) |
| Know why something is the way it is | [`05_Decisions/ADRs/`](05_Decisions/ADRs/) |
| See what broke and why | [`04_Incidents/`](04_Incidents/) |
| Check performance claims | [`03_Performance/README.md`](03_Performance/README.md) |
| Continue development | [`06_Reference/future-work.md`](06_Reference/future-work.md) |

## Project history at a glance

Timeline is **RECOVERED** from git author dates and the timestamped backups in `~/.config/rice-backups/`.

| Phase | Window (local time) | Theme | Key commits |
|---|---|---|---|
| −1 | before 2026‑09‑19 18:23 | Stock Fedora/niri/Noctalia desktop | — (pre-project) |
| 0 | 2026‑09‑19 ~18:00–18:23 | Inspection and baseline, no changes | — |
| 1 | 2026‑09‑19 18:23–19:30 | Rice pass: glass, palette, binds, bar | config-only + `a176ada` base |
| 2 | 2026‑09‑19 19:38–21:49 | Lock/unlock transitions, modal power menu | `bf0a376`…`4289b62` |
| 3 | 2026‑09‑20 02:06–02:43 | Motion plugin panel (animation settings) | plugin + `rice-backups/…-phase3b` |
| 4 | 2026‑09‑20 02:43–03:02 | OSD system | `40c1936` |
| 5 | 2026‑09‑20 03:02–14:09 | Notifications + sound | `803664d` |
| 6 | 2026‑09‑20 16:03 → 2026‑09‑21 05:20 | Persistent shell UX: bar, control center, wallpaper browser, stability | `82fb4b0`, `99ac272`, `46296d0`, `e9e27b0`, `08f5454`, `eaff2b2`, `57debbc` |

Full detail per phase in [`01_Phases/`](01_Phases/). Cross-phase amendments in
[`01_Phases/cross-phase-matrix.md`](01_Phases/cross-phase-matrix.md).

## Current verified state

- **Commit:** `57debbc` · **working tree:** clean · **build:** clean (`meson compile --clean` then full build)
- **Tests:** 118 / 119 — the single failure (`upower_charge_limit_integration`) is pre-existing and unrelated;
  see [`04_Incidents/known-failures.md`](04_Incidents/known-failures.md)
- **Config validation:** `niri validate` ✓, `noctalia config validate` ✓
- **Crashes:** no new coredumps since the lifetime fixes of `08f5454`

## Documentation conventions

Evidence tags **VERIFIED / RECOVERED / INFERRED / UNKNOWN** are defined in
[`DOCUMENTATION_POLICY.md`](DOCUMENTATION_POLICY.md). Anything not establishable from surviving evidence is marked
UNKNOWN rather than guessed.

## Rebuilding this documentation

```sh
~/Documents/Dev/ZynithShell/scripts/build-docs.sh      # charts, diagrams, DOCX, PDF
```
