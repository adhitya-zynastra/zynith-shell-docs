# ADR-0001 — niri as the compositor, Hyprland kept as a fallback

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 0) · **Evidence:** VERIFIED — both packages installed, niri is
the active session, `~/.config/hypr` untouched.

## Context
The machine already ran a Hyprland + JaKooLit configuration. The owner wanted a new desktop built on niri, but
could not afford to lose a working session on a daily-driver machine.

## Decision
Build on niri 26.04. Leave Hyprland 0.56.2 installed and its configuration byte-for-byte untouched as a fallback
session.

## Alternatives
- *Replace Hyprland entirely* — rejected: no recovery path if niri or the shell broke.
- *Develop in a VM* — rejected: the project is explicitly about the owner's real hardware, display scaling and GPU.

## Consequences
- Two notification daemons exist on the machine, which later caused a real outage (see ADR‑0012 and the postmortem).
- Every session-scoped change must be written so it does not leak into the Hyprland session.
