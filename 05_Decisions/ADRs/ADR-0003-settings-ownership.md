# ADR-0003 — Zynith never writes `settings.toml`

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 0/1) · **Evidence:** VERIFIED — the file is only ever read by
Zynith tooling; `rice.toml` carries the design layer.

## Context
Noctalia's settings GUI owns `~/.local/state/noctalia/settings.toml` and rewrites it wholesale. It also *overrides*
everything in `~/.config/noctalia/*.toml`.

## Decision
I made this a hard rule rather than a guideline: Zynith's design lives in `rice.toml` (and `lockscreen.toml`,
`motion.toml`), and Zynith **never** becomes a second writer of `settings.toml`. Where the GUI has written a
conflicting key, that is reported to me to change in the GUI rather than silently overwritten.

## Why
Two writers and one file is a corruption bug waiting for a race, and the one that loses is always the one the
user can see. I would rather be told to go and change something in the GUI myself than have my desktop quietly
fight a settings panel.

## Alternatives
- *Write settings.toml directly* — rejected: two writers, last-writer-wins, and the user's GUI changes would be
  silently destroyed.

## Consequences
- Some settings genuinely cannot be controlled from `rice.toml` once the GUI has touched them — this is the
  documented cause of "my rice.toml edit did nothing" (bar widget list, bar thickness, bar font).
- Troubleshooting must always check precedence first.

> **Later note (2026‑09‑25).** The decision text above names `motion.toml` as part of the design layer. The
> Motion plugin and `motion.toml` have since been retired; `[shell.animation]` now lives in `rice.toml`
> (ADR‑0015). The rule itself — Zynith never writes `settings.toml` — is unchanged.
