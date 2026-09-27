# Design Foundation (Batch 6) — Validation Record

**Date:** 2026‑09‑26. **Implementation:** uncommitted working tree on top of `e521a86` (no-git batch).
**Binary tested:** a clean build (`meson compile --clean`, required by ADR‑0013 because `animation_manager.h` and
`panel_manager.h` changed layout): **1017 targets, 0 failures, 6 warnings — all the known libstdc++
`-Wmaybe-uninitialized` ones, none from project sources.** One `.cpp`-only edit (`bar.cpp`, the hover-open origin)
landed while it ran and was picked up incrementally afterwards; that is safe under ADR‑0013, which is about headers.

**Conditions.** I was using the desktop throughout. At 09:31 a browser tab began playing audio, which drives the
bar's spectrum visualiser; this confounded one measurement (idle CPU, below). Captures were limited to the Control
Center's nav strip (icons only) and 12 px-wide strips, deleted after the numbers were extracted. No real lock was
run. Pointer clicks landed only on the always-visible left bar; hover-open used pointer movement only.

## Tests

| Suite | Result |
|---|---|
| Full suite | **127 / 128** — the single failure is `upower_charge_limit_integration` (known, third-party) |
| `motion_language` (new) | spring physics exactness, the role table's invariants, retargeting, reduced motion, tempo, `MotionValue`/`MotionRect` lifetime, `MorphTransition` roles — passed 3 × in a row |
| `design_tokens` (new) | tokens reproduce the values they replaced, type-ramp order, face fallback lists, semantic colours, WCAG maths, surface hierarchy agreeing with Glass and the existing layers |
| `spatial_model` (new) | edge mapping, **reveal direction equals the attached-panel rule for every bar position**, origin formatting, requests carrying origins, lifetime policy |
| `cairo_text_renderer` (extended) | tabular figures end to end |
| `animation_manager`, `animation_reentrancy`, `morph_transition` | unchanged and passing after the engine change |
| `noctalia config validate`, `niri validate` | valid (no configuration changed in this batch) |

**Two tests were made to fail on purpose (mutation testing),** to prove they can catch the fault they exist for:

| Mutation | What the test reported |
|---|---|
| `retarget()` zeroes a spring's velocity | 4 checks failed, including the one comparing the observed position with the kept-velocity and reset-velocity predictions |
| the renderer ignores font features | "tnum digits not tabular (1111 **28 px** vs 0000 **52 px**)" |

A first version of the retarget check used a loose bound on frame-to-frame velocity change and **could not have
caught** a velocity reset: a reset (≈ 770 px/s) is smaller than the spring's legitimate pull. It was replaced before
the mutation test.

## Runtime — spatial origins (debug log, installed binary)

| Opened by | Logged origin |
|---|---|
| IPC `panel-toggle control-center` | `origin command` |
| Left-bar network widget click | `origin bar-widget default/network @ 12,904 16x16 edge=left reveal=right` |
| Resting the pointer on the Time bar's clock (hover-open, no click) | `origin bar-widget Time/clock @ 933,1170 55x25 edge=bottom reveal=up` |

The rectangles are the widgets' own nodes in output-local pixels; the clock's centre is x ≈ 960, where the Time bar
sits. One click (at y 912, without a preceding pointer move) registered nothing and changed nothing — Wi-Fi
state was checked. It is a harness artefact; the retry with a move first opened as expected.

## Runtime — motion (nav-strip captures, ≈ 15 ms apart; Cinematic tempo, effective speed 0.64)

| | Baseline (batch-5 binary, EaseOutQuint legs) | After (`element-move` spring via `MotionRect`) |
|---|---|---|
| One switch, 36 px | settled within 1 px at **234 ms**; overshoot 0; largest frame-to-frame velocity change 0.46 px/ms | settled at **277 ms**; overshoot 0; **0.27 px/ms** — the spring starts from rest instead of at full speed |
| Three switches 80 ms apart, 108 px | settled at 492 ms; overshoot 0; 1.28 px/ms, with a **54 ms frame stall** at the first retarget | run 1 (first after restart): 504 ms, a **~100 ms stall**, 1.88 px/ms; runs 2–3: 495 / 506 ms, stalls ≤ 2 frames, **0.49 / 1.00 px/ms** |
| Settled indicator, pixels | — | **identical to the baseline** (mean absolute difference 0.0; the selection colours now come from semantic tokens) |

**What this does and does not show.**
- The spring is a little slower to settle than EaseOutQuint (277 vs 234 ms for one step): EaseOutQuint front-loads
  its motion, while the spring accelerates from rest. Both are well inside the measured reference range.
- **Frame stalls dominate the frame-to-frame metric.** The panel stops presenting frames for 50–100 ms when it
  enters a section for the first time; the spring keeps integrating against wall time, so it is in the right
  place when frames resume. The stall is pre-existing (54 ms in the baseline) and is a section-build cost, not a
  motion-model property. Velocity continuity is therefore established by the discriminating unit test, not by this
  capture.

## Runtime — attached close (`surface-dismiss` replaced upstream's 300 ms `EaseInOutQuad`)

The close is a rigid translation, so the nav pill moves exactly with the curve. Tracked in a 12 px strip through it:
the first ≈ 25 % of the travel linearises as `√(Δy/520) ∝ t` — the `EaseInQuad` shape — with a fitted duration of
**≈ 287 ms**, against **312 ms** predicted for the new role at speed 0.64.

**This is consistent with the change, but it does not prove it.** In its first half, the old `EaseInOutQuad`
(469 ms here) has the same squared shape, equivalent to `EaseInQuad` over 332 ms. The content fades before the
second half, where the two curves differ. The change is therefore established by code and the role tests. An
earlier strip method used for the baseline could not see the panel's upper part against a dark background, and a
"sliver lingering 350 ms" I first noted from it was **the Time bar staying visible until it auto-hides**, not the
panel. That observation was wrong and is withdrawn.

## Runtime — resources and idle

| Measurement | Result |
|---|---|
| Threads / fds / RSS across ≈ 12 Control Center open/close cycles on the new binary | 33 / 83 / 167.9 MB at install → 33 / 83 / 169.7 MB after (stable) |
| Idle CPU, nothing open — baseline (09:25, no audio playing) | 10 ticks / 10 s |
| Idle CPU, nothing open — after (09:48, **a browser tab playing audio**, spectrum active) | 57–70 ticks / 10 s, all on the render thread — **confounded, not a result** |
| Idle CPU, nothing open, after, with no stream playing | **not obtained** — a watcher waited 25 minutes (09:52–10:16) for every audio stream to be paused; audio never stopped |

Why the new code cannot hold the frame loop open while idle is argued and tested, not assumed:
- a settled spring leaves the manager (the `hasActive() == false` checks);
- the only spring owner, the nav indicator, is destroyed with its panel;
- button crossfades are the same finite tween as before.

> **Amendment (Batch 7, 2026‑09‑26).** Measured at last, with no stream playing: **3 ticks / 10 s**, twice, on the
> Batch 7 clean build ([`control-center-lock-batch7.md`](control-center-lock-batch7.md)). That is below this page's
> 10-tick baseline.

A runtime confirmation needs a quiet moment. I had Claude arm a watcher that samples only when every audio stream
is paused. It waited 25 minutes and audio never stopped, so **idle CPU after this batch remains unmeasured under
clean conditions.** It is the first thing to re-measure before Batch 7.

## Migration inventory

72 raw `animate()` / `fadeTo()` call sites existed before this batch; **67 remain**. Migrated to roles: the button
state crossfade (every button) and the four panel reveal/dismiss calls. The Control Center section morph
(`MorphTransition` role start) and nav indicator (`MotionRect`) were moved to roles as well. The rest migrate with
their surfaces in Batch 7.

## Not verified

- **Reduced motion at runtime:** unit-tested only. Turning animations off would have changed my live desktop.
- **Typography roles and contrast on screen:** no surface consumes them yet.
- **Other output sizes:** no second display.
- **The old attached-close curve's second half:** the content fades before it can be tracked.
