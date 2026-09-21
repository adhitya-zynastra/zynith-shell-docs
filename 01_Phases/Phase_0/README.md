# Phase 0 — Inspection and Baseline

**Window:** 2026‑09‑19, roughly 18:00 → 18:23 (ends at the `pre-rice` backup). **Deliverable:** an architecture
plan and a set of backups — deliberately **zero** functional change.

## Purpose

The owner's instruction was explicit: *"First DO NOT change anything. Inspect … Then report a short architecture
plan. After that, begin implementing it LIVE."* Phase 0 exists because the target was a working daily-driver
machine, not a scratch VM.

## What was established

| Finding | Consequence for later phases |
|---|---|
| Noctalia 5.1 is the **native C++ rewrite**, not the older QML shell | All shell work is C++ + TOML, not QML |
| niri config uses **positional includes**; the generated `noctalia.kdl` must stay last | `config.kdl` was restructured into `rice/*.kdl` includes |
| Noctalia merges `~/.config/noctalia/*.toml` **alphabetically**, and `settings.toml` overrides all | Birth of the precedence rule that governs every later change |
| Only core Material‑3 colour roles are valid (`primary`, `surface_variant`, `on_surface`, …) | Later attempts to use `surface_container_high` / `outline_variant` were rejected by the validator |
| Hyprland config exists and must remain a working fallback | Nothing in the project touches `~/.config/hypr` |

## Baseline against the engineering motto

The motto (*FAST · OPTIMIZED · PERFORMANT · STABLE · MAINTAINABLE*) was **not** scored at this point, because no
measurements were taken. Scoring it retrospectively would be invention. The first measured baseline in this
documentation set is Phase 6 (`03_Performance/baselines/`).

## Artifacts

`~/.config/rice-backups/20260919-182322-pre-rice/` — the canonical "before" snapshot, and the only surviving
evidence of the pre-project configuration.
