# Postmortem — Use-after-free in `Signal::emit` (shell SIGSEGV on wallpaper apply)

| | |
|---|---|
| **Severity** | Critical — loss of all desktop chrome; I hard-powered the machine off |
| **First observed** | 2026‑09‑20 23:45:50 (boot `c357f92e…`) |
| **Recurrences** | 2026‑09‑21 00:46:36, and once more during my manual testing |
| **Fixed in** | `08f5454`, refined in `eaff2b2` |
| **Status** | Resolved, with a regression test that fails against the old code |

This is the most serious thing that went wrong in Zynith, and the one I most want a future maintainer to
understand, because the defect was structural rather than accidental.

## What I observed

I was browsing wallpapers with the browser open and applied one. The shell vanished — bar, panels **and the
wallpaper**, because Noctalia draws all of them. What was left looked like a dead machine: no chrome, no
wallpaper, nothing responding the way I expected. I held the power button down.

I reported it to Claude as a **full system freeze**, and I want that wording preserved here rather than quietly
corrected, because it shaped the first hour of the investigation. I also said explicitly that I did not want it
dismissed as a random crash, and that I did not want anyone deliberately reproducing a hard freeze to prove a
point.

## What I initially suspected

A GPU or driver fault. The failure was total and visual, it happened while images were being decoded and
uploaded, and this is an Intel Arc / i915 laptop. My second suspicion was the wallpaper itself — the file I had
just applied — on the theory that something about that specific image had killed the decoder.

Both turned out to be wrong, and the evidence that ruled them out is more useful than the guesses.

## What Claude investigated

I asked Claude to work from logs rather than from reproduction. It pulled the persistent journal for the
previous boot, located the coredumps, extracted backtraces, and separately audited the same boot for GPU, memory
and thermal events. It also characterised the specific wallpaper file I had applied, to test my second theory.

## What the evidence showed

The boot ends abruptly at 23:45:56 with no shutdown sequence, six seconds after:

```
kernel: noctalia[4575]: segfault at 200000019c ip 00000000016f3144 sp 00007ffca9e9ec00 error 4
systemd-coredump: Process 4575 (noctalia) of user 1000 dumped core.
  #0  Image::applyPalette()
  #1  Signal<>::emit()
  #2  ThemeService::startTransition(Palette const&)::{lambda(float)}
  #3  AnimationManager::tick(float)
```

Three facts settled it:

- `200000019c` is a **wild pointer**, not a null dereference — the signature of a freed object, not of an
  uninitialised one.
- The same boot contains **no i915/DRM error, no GPU hang or reset, no GuC/HuC fault, no OOM and no
  memory-pressure event** — only normal i915 initialisation. My driver theory had no supporting evidence at all.
- niri **survived** and respawned noctalia at 23:45:56. The compositor was alive the whole time.

The wallpaper theory died too: `thumb-1920-1284980.jpg` is 1920×1261 JPEG, sRGB, 8-bit, no alpha, 447 KB
(~9.7 MB decoded) — smaller than many others in the same library.

## Root cause

`Signal::emit()` dispatched from a **copy** of the slot vector while `ScopedConnection::disconnect()` **erased**
from the canonical vector. A subscriber destroyed part-way through a dispatch was therefore still invoked through
the copied `std::function`, with its captured `this` already freed.

```cpp
// before
void emit(Args... args) {
  auto snapshot = m_state->slots;             // copies the std::functions
  for (auto& slot : snapshot)
    if (slot.callback) slot.callback(args...); // owner may already be destroyed
  …
}
```

`Image` subscribes to `paletteChanged()`. A palette transition emits **every animation frame**, and its handlers
rebuild UI nodes — so with the wallpaper browser open, where carousel tiles bind and unbind continuously,
destruction-during-dispatch was routine rather than exotic.

### Why the architecture allowed it

The primitive was half-way between two designs: the reaping code at the end of `emit()` expected *tombstoning*,
but `disconnect()` implemented *erasure*, and dispatch iterated a snapshot. Each half was reasonable on its own;
the combination was not. Nothing in the header said which design it was supposed to be, so both halves could look
correct to whoever was reading one of them.

## Contributing factors

- Phase 6 made the browser stay open across an apply, which is exactly the window where tiles churn while the
  palette animates. My own Phase 6 design decision widened the hazard window.
- Switching to Light mode starts a second palette transition, widening it further. I was in Light mode.
- **Neither the wallpaper asset nor Light mode was a cause**; `startTransition` is mode-agnostic.

## Fix

Dispatch now walks the canonical list by index and re-reads each slot immediately before calling it; disconnecting
during a dispatch marks the slot dead instead of erasing it; reaping happens when the outermost dispatch unwinds;
slots connected during a dispatch wait for the next emit. `eaff2b2` then removed the per-invocation
`std::function` copy by moving slots into a `std::deque` (stable addresses) — same guarantees, no allocation.

`AnimationManager::tick` had the same *family* of defect on the same stack (range-iterating a vector while calling
setters that can start animations or destroy nodes) and was given the equivalent contract: additions parked,
cancels marked dead, index-based walk. **Honest caveat:** the animation test passes against the old code too, so
that part is hardening, not a demonstrated field cause.

## Verification

- `tests/signal_dispatch_test.cpp` detects a stale invocation via a liveness registry — it **fails against the
  pre-fix dispatch and passes with the fix**. Freed memory often reads back fine, so the test deliberately does not
  rely on a crash. The first version of this test did not reproduce the bug at all, because the destroying slot
  was registered last; registering it first was what made the defect visible.
- 40 apply/transition cycles with the browser open (dark, light, and light/dark toggling mid-transition while the
  carousel churned tiles): zero crashes, zero new coredumps. The same actions crashed twice in manual use before.

## What remains uncertain

Whether the machine genuinely locked up at kernel level or merely *appeared* dead — no chrome, no wallpaper — and
was powered off by me on that basis. The journal stops too abruptly to distinguish, and I am not willing to
reproduce a hard freeze to find out. **UNKNOWN**, and it stays UNKNOWN.

## Engineering lesson

This changed two things for the rest of the project.

**Any shared dispatch primitive must answer three questions in its own header**: what happens if a callback
(a) disconnects itself, (b) destroys another subscriber, (c) connects a new one. `signal.h` and
`animation_manager.h` now do, and that requirement is recorded in
[ADR‑0011](../../05_Decisions/ADRs/ADR-0011-signal-lifetime.md).

**A regression test that does not fail against the old code is not a regression test.** I now treat "the test
passes before and after" as a reason to distrust the test, not to celebrate the fix — which is exactly why the
`AnimationManager` half is labelled hardening above instead of being presented as a proven repair.
