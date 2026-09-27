# Known Failures (accepted, unresolved)

## `upower_charge_limit_integration` — 1 of 125 tests

**Status:** pre-existing, unrelated, deliberately not fixed.

- **Symptom:** `SIGSEGV`, consistently, on every run.
- **Backtrace:** the crash is inside `sdbus::Message::operator=(Message&&)` called from the test's own
  `FakeBattery::completeSuccess` — the frames are the test binary and `libsdbus-c++.so.2`. **No Zynith or shell
  code appears on the stack.**
- **Evidence it predates this work:** a coredump for the same binary exists from **2026‑09‑19 19:37**, before any
  Phase 2+ change to the areas under suspicion, and it fails identically with and without every Phase 6 change.
- **Why it is not fixed:** project policy forbids modifying unrelated infrastructure to improve a test count. It is
  a D-Bus harness interaction with sdbus-c++ 2.2.1, not a defect in the shell.
- **What would settle it:** running the test against a different sdbus-c++ version, or auditing the fake object's
  message lifetime. Neither has been done.

## Shell crash in `Select::~Select` on a Control Center teardown — cause inferred, not proven

Two crashes on 2026‑09‑26 (02:18 at exit, 12:16 when the panel closed). The most likely cause, a dangling
`ScrollView` pointer in top-navigation mode, was fixed in Batch 7. The release cores cannot confirm it. Closed only
if no recurrence is seen. Details:
[`2026-09-26-lock-reload-crash.md`](postmortems/2026-09-26-lock-reload-crash.md).

## Deliberately untested

| Area | Why |
|---|---|
| Lock / unlock under automation | Risk of locking me out of my daily-driver machine. Validated visually and by timing arithmetic instead. Batch 7 consequence: the fix for the reload-while-locked crash is verified by reasoning and the full suite only |
| Per-process GPU memory | `intel_gpu_top` requires privileges not available in this environment; only `gt_act_freq_mhz` was readable |
| Frame timing / jank | No instrumentation exists |
