# ADR-0011 — Dispatch safety over dispatch speed in shared primitives

**Status:** Accepted · **Date:** 2026‑09‑21 (Phase 6, `08f5454` → `eaff2b2`)

## Context
A use-after-free in `Signal::emit` took down the entire shell (see the postmortem). The first fix copied each
`std::function` before invoking it, which is safe but allocates per callback per dispatch.

## Decision
Keep the strong guarantee, remove the cost: slots live in a `std::deque` (stable addresses), disconnection during
a dispatch marks a slot **dead** rather than erasing it or clearing its callable, dispatch re-reads each slot
immediately before calling, and reaping happens when the outermost dispatch unwinds. `AnimationManager::tick`
follows the same contract with a pending-additions list.

## Rationale
The hazard is structural, not statistical: a palette transition emits every frame while UI nodes are being
destroyed. A guarantee that depends on "subscribers usually outlive a dispatch" is not a guarantee.

## Consequences
- Every shared dispatch primitive must document what happens if a callback disconnects itself, destroys another
  subscriber, or connects a new one.
- Changing these files requires a **clean rebuild** before any measurement (ADR‑0013).
- Regression tests must fail against the old implementation to be worth keeping.
