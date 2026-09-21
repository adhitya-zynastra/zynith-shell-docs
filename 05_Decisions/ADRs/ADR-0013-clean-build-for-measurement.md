# ADR-0013 — Clean builds are mandatory for measurement after header layout changes

**Status:** Accepted · **Date:** 2026‑09‑21 (Phase 6)

## Context
An incremental build after a layout change to `src/ui/signal.h` produced mixed struct layouts across translation
units: a startup crash in an unrelated constructor, and hours of inflated CPU numbers that were briefly believed
to be a real regression.

## Decision
Any change to the layout of a widely-included header (adding/reordering members, changing a container type)
requires `meson compile --clean` before the binary is run or measured. Every recorded measurement carries a
`build` field; only `clean` may be quoted in authoritative tables.

## Consequences
- Slower iteration on such changes; accepted.
- A crash in an unrelated constructor right after a header change is treated as a build-integrity symptom first.
- `03_Performance/benchmarks/contaminated-measurements.md` exists so the discarded numbers are never resurrected.
