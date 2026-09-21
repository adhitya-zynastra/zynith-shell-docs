# Postmortem — Incremental build produced a mixed `Signal::State` layout

| | |
|---|---|
| **Severity** | High — startup crash plus **hours of invalid performance data** |
| **Date** | 2026‑09‑21, during the `eaff2b2` work |
| **Status** | Resolved by a clean rebuild; prevention documented |

This one produced no user-visible failure on my desktop at all. It cost time instead: it sent the investigation
after a performance regression that never existed.

## What I observed

Two distinct failures from one cause:

1. The shell **crashed at startup** inside `Button::Button()` → `ui::button()` → `DesktopMediaPlayerWidget::create()`
   — a constructor with no obvious relationship to the change being made.
2. Idle CPU measurements were **wildly inflated**: noctalia read 6.9 % and niri 6.2 % of a core, versus a true
   baseline near 1.3 % / 0.4 %.

## What I initially suspected

That the lifetime fix had a real cost. The numbers were internally consistent and pointed at the commit that had
just changed dispatch, so the obvious reading was that the safety work had made the shell measurably more
expensive — which would have been a genuine, and unwelcome, engineering trade-off to write up.

## What Claude investigated, and what the evidence showed

I had Claude bisect by rebuilding the neighbouring commits and re-measuring each one.
Bisecting by rebuilding the two neighbouring commits *also* produced suspect numbers (`08f5454` 6.92 %,
`e9e27b0` 3.67 %), because those builds were incremental too — the bisection was measuring its own contamination
at every point. The tell was that a **fresh clean build** of the same tree behaved completely differently. Only
after `meson compile --clean` did the picture become consistent, and the supposed regression evaporated: 1.3 %
idle and **38 ms per apply**, against the 192 ms the skewed binary had reported.

## Root cause

`src/ui/signal.h` had its `State` struct changed (`std::vector<Slot>` → `std::deque<Slot>`, plus a new field).
`signal.h` is included by a large fraction of the shell. A `meson setup --reconfigure` was issued mid-session and
the subsequent incremental compile left some translation units built against the **old** layout and others against
the **new** one. Every object that stored or crossed a `Signal` then disagreed about its size and field offsets —
classic ODR/ABI skew. `Button`'s constructor connects to `paletteChanged()`, which is why it faulted first.

## Why the measurements were wrong

The skewed binary did *extra* and *incorrect* work every frame. Every CPU figure taken from it — including an
apparent "regression" attributed to the lifetime fix, and an apparent 192 ms cost per wallpaper apply — was an
artifact. After a clean rebuild the same measurements read 1.3 % idle and **38 ms per apply**.

## Fix

```sh
cd ~/.local/src/noctalia-lockfade/build
meson compile --clean && meson compile -j 12
meson install --quiet
```

## Engineering lesson, now project policy

1. **Any change to the layout of a widely-included header requires a clean rebuild** before the binary is run or
   measured. Adding or reordering members, or changing a container type, all qualify.
2. Never run `meson setup --reconfigure` in the middle of a measurement session.
3. A crash in an unrelated constructor immediately after a header change is a build-integrity symptom until proven
   otherwise — check the build before debugging the code.
4. Performance figures carry a **build type** field; anything not from a clean build is marked
   `INVALID / CONTAMINATED` and never enters an authoritative table
   (`03_Performance/benchmarks/contaminated-measurements.md`).

The wider lesson I took from this is that measurement has a prerequisite, and the prerequisite is a build you can
vouch for. Every performance table in this documentation therefore carries a build-state column, and the numbers
this incident produced are preserved — clearly labelled as invalid — rather than deleted, because the record of
*why* several hours of figures were discarded is itself worth keeping.
