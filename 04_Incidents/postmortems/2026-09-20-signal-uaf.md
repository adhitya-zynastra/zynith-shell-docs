# Postmortem — Use-after-free in `Signal::emit` (shell SIGSEGV on wallpaper apply)

| | |
|---|---|
| **Severity** | Critical — loss of all desktop chrome; the owner hard-powered the machine off |
| **First observed** | 2026‑09‑20 23:45:50 (boot `c357f92e…`) |
| **Recurrences** | 2026‑09‑21 00:46:36, and once more during the owner's manual testing |
| **Fixed in** | `08f5454`, refined in `eaff2b2` |
| **Status** | Resolved, with a regression test that fails against the old code |

## Symptom

The shell vanished — bar, panels **and the wallpaper**, since Noctalia draws all of them. The desktop looked dead
and the machine was powered off with the power button. The owner reported it as a **full system freeze**.

## Evidence

Persistent journald. The boot ends abruptly at 23:45:56 with no shutdown sequence, six seconds after:

```
kernel: noctalia[4575]: segfault at 200000019c ip 00000000016f3144 sp 00007ffca9e9ec00 error 4
systemd-coredump: Process 4575 (noctalia) of user 1000 dumped core.
  #0  Image::applyPalette()
  #1  Signal<>::emit()
  #2  ThemeService::startTransition(Palette const&)::{lambda(float)}
  #3  AnimationManager::tick(float)
```

`200000019c` is a wild pointer, not a null dereference. The same boot contains **no i915/DRM error, no GPU hang or
reset, no GuC/HuC fault, no OOM and no memory-pressure event** — only normal i915 initialisation. niri survived:
it respawned noctalia at 23:45:56.

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
but `disconnect()` implemented *erasure*, and dispatch iterated a snapshot. Each half was reasonable alone; the
combination was not.

## Contributing factors

- Phase 6 made the browser stay open across an apply, which is exactly the window where tiles churn while the
  palette animates.
- Switching to Light mode starts a second palette transition, widening the window. The owner was in Light mode.
- **Neither the wallpaper asset nor Light mode was a cause.** `thumb-1920-1284980.jpg` is 1920×1261 JPEG, sRGB,
  8-bit, no alpha, 447 KB (~9.7 MB decoded) — smaller than many in the same library; and `startTransition` is
  mode-agnostic.

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
  rely on a crash.
- 40 apply/transition cycles with the browser open (dark, light, and light/dark toggling mid-transition while the
  carousel churned tiles): zero crashes, zero new coredumps. The same actions crashed twice in manual use before.

## What remains uncertain

Whether the machine genuinely locked up at kernel level or merely *appeared* dead (no chrome, no wallpaper) and was
powered off. The journal stops too abruptly to distinguish. **UNKNOWN**, and stated as such.

## Prevention

Any shared dispatch primitive must answer three questions in its header: what happens if a callback (a) disconnects
itself, (b) destroys another subscriber, (c) connects a new one. `signal.h` and `animation_manager.h` now do.
