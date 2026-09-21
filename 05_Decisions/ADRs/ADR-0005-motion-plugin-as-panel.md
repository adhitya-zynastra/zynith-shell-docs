# ADR-0005 — Animation settings as a plugin *panel*, not a service

**Status:** Accepted (but superseded in intent — see Consequences) · **Date:** 2026‑09‑20 (Phase 3)

## Context
Zynith needed a UI for motion presets, global speed and advanced controls, with one source of truth that also
generates niri's `animations.kdl`.

## Decision
Implement it as a Luau plugin **panel** (`Super+Alt+A`). `motion.json` is the source of truth; committing writes
`motion.toml` and `animations.kdl` (the latter validated with `niri validate` and replaced atomically).

## Rationale
Noctalia plugin **services** arm an unconditional 1 s repeating timer even when idle. A panel exists only while
open, so the "no resident polling" rule is preserved by construction.

## Consequences
- No background cost; all work happens on open or commit.
- **It created a second settings surface.** The owner has since stated that customization should live in one
  primary surface, so this decision is scheduled to be revisited — tracked in `06_Reference/future-work.md`.
  The *functionality* (presets, speed, validation, atomic write) is to be preserved when it moves.

## Revisit when
Folding animation settings into the main settings surface begins.
