# ADR-0001 — niri as the compositor, Hyprland kept as a fallback

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 0) · **Evidence:** VERIFIED — both packages installed, niri is
the active session, `~/.config/hypr` untouched.

## Context
My machine already ran a Hyprland + JaKooLit configuration that worked. I wanted to build the new desktop on
niri, but this is the laptop I work on every day, so I could not afford a window in which I had no usable
session at all.

## Decision
Build on niri 26.04. Leave Hyprland 0.56.2 installed and its configuration byte-for-byte untouched as a fallback
session.

## Alternatives
- *Replace Hyprland entirely* — rejected: no recovery path if niri or the shell broke.
- *Develop in a VM* — rejected: the whole point is how this behaves on my real hardware, display scaling and GPU.

## Consequences
- Two notification daemons exist on the machine, which later caused a real outage (see ADR‑0012 and the postmortem).
- Every session-scoped change must be written so it does not leak into the Hyprland session.
