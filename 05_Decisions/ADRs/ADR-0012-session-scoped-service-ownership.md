# ADR-0012 — Session-conditional systemd units, not enable/disable

**Status:** Accepted · **Date:** 2026‑09‑21 (Phase 6)

## Context
SwayNotificationCenter's user unit starts in any graphical session and claims
`org.freedesktop.Notifications`, which silently disabled all Zynith notifications in the niri session. I still
need swaync in the Hyprland fallback, so I could not simply remove it.

## Decision
Use a systemd drop-in with `ConditionEnvironment=!XDG_CURRENT_DESKTOP=niri` rather than disabling the unit.

## Alternatives
- *`systemctl --user disable swaync`* — rejected: breaks the Hyprland session.
- *Mask the unit* — same objection, more forceful.
- *Change Noctalia to take the name forcibly* — rejected: D-Bus name stealing is hostile and racy.

## Consequences
- The pattern generalises: on a multi-session machine, any singleton service must be session-conditional.
- Documented in troubleshooting, because the failure mode is completely silent.
