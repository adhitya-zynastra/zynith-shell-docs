# Zynith Shell — Engineering Documentation

**Documentation version 1.0** · source commit `57debbc` · last audited phase **6** · machine-readable metadata in
[`VERSION.json`](VERSION.json)

Zynith Shell is a desktop environment built on **Fedora 44 + niri 26.04 + a locally patched Noctalia 5.1.0**.
It is not a fork and not a theme: it is a small, reviewed patch series over the packaged Noctalia shell, plus a
configuration layer that owns the design language, plus two Luau plugins. The Fedora package stays installed and
untouched; the patched build lives in `~/.local/opt/noctalia` and niri launches it with a fallback to `/usr/bin/noctalia`.

> **Engineering motto, as stated by the project owner:** *FAST. OPTIMIZED ASF. PERFORMANCE GODLY. STABLE ASH.*
> The priority order that actually governs decisions is: correctness → stability → security → responsiveness →
> resource efficiency → maintainability → configurability → aesthetics.

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
