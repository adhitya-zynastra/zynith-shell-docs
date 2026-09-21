# ADR-0003 — Zynith never writes `settings.toml`

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 0/1) · **Evidence:** VERIFIED — the file is only ever read by
Zynith tooling; `rice.toml` carries the design layer.

## Context
Noctalia's settings GUI owns `~/.local/state/noctalia/settings.toml` and rewrites it wholesale. It also *overrides*
everything in `~/.config/noctalia/*.toml`.

## Decision
Zynith's design lives in `rice.toml` (and `lockscreen.toml`, `motion.toml`). Zynith never becomes a second writer
of `settings.toml`; where the GUI has written a conflicting key, that is reported to the user to change in the GUI
rather than silently overwritten.

## Alternatives
- *Write settings.toml directly* — rejected: two writers, last-writer-wins, and the user's GUI changes would be
  silently destroyed.

## Consequences
- Some settings genuinely cannot be controlled from `rice.toml` once the GUI has touched them — this is the
  documented cause of "my rice.toml edit did nothing" (bar widget list, bar thickness, bar font).
- Troubleshooting must always check precedence first.
