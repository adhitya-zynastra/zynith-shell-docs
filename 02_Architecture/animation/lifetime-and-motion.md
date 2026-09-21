# Animation, Signals and Lifetime Safety

This is the most safety-critical document in the set. Two shared primitives — `Signal` and `AnimationManager` —
are touched by every component, and a lifetime bug in either takes down the whole shell. One already did; see
`04_Incidents/postmortems/2026-09-20-signal-uaf.md`.

## The motion stack

```
   input event ──► component decides a target
                        │
                        ▼
              AnimationManager::animate(from, to, durationMs, easing, setter, onComplete, owner)
                        │   duration ÷ MotionService::speed()      (global speed, 0.05–4.0)
                        │   MotionService::enabled() == false  →   setter(to) immediately
                        ▼
              TimerManager::tick ──► AnimationManager::tick ──► setter(value) each frame
                        │
                        ▼
              Node property (position / size / opacity / scale / z) ──► render
```

There is exactly **one** animation engine. Components never run their own frame clock; a component that needs a
dwell (the OSD's 1.4 s hold) uses a one-shot `TimerManager::Timer`, not an animation, because an animation would
keep the frame clock alive. **VERIFIED** — `osd_overlay.cpp` `kHideDelayMs` is a pinned constant with a comment
saying exactly this.

## Duration tiers (`src/ui/style.h`)

| Tier | Base | Used for |
|---|---|---|
| `animFast` | 130 ms | Micro-interactions: hover, toggles, focus rings — must feel instant |
| `animNormal` | 300 ms | Surfaces: panel reveal, content transitions, OSD, toasts |
| `animSlow` | 520 ms | Large/cinematic motion |

All three are *base* values divided by `[shell.animation].speed`. At the machine's configured speed of 0.8 the
effective values are 162 / 375 / 650 ms. Raised from 100/200/400 in `e9e27b0` and paired with long-tail easings
(`EaseOutQuint`, `EaseInOutQuint`, `EaseOutExpo`, added in the same commit) so motion departs immediately and
settles slowly — "lower perceived velocity with unchanged input latency".

> **Trap:** anything that derives a *timeout* from these tiers drifts when they change. `kHideDelayMs` was
> `animSlow*3 + animFast*2` and would silently have become 1.82 s; it is now pinned at 1400 ms.

## Signal — dispatch contract

`src/ui/signal.h`. The contract, in the order it must be reasoned about:

1. **Slots live in a `std::deque`.** Addresses stay valid when a callback connects new slots during a dispatch, so
   `emit()` invokes the stored callable in place without copying it.
2. **`emit()` walks the canonical list by index and re-reads each slot immediately before calling it.** It never
   dispatches from a snapshot copy — that was the use-after-free.
3. **Disconnecting during a dispatch marks the slot `dead`; it does not erase it and does not clear the callable.**
   A slot can be disconnected by the callback that is currently running, and destroying its `std::function`
   mid-call would pull the closure out from under it.
4. **Reaping happens when the outermost dispatch unwinds** (`dispatchDepth` counts nested emits).
5. **Slots connected during a dispatch are not called until the next emit** (`count` is captured up front).
6. `emit()` holds a `shared_ptr` to the state, so a callback may destroy the object that owns the Signal.

```cpp
void emit(Args... args) {
  auto state = m_state;                 // callback may destroy the Signal's owner
  ++state->dispatchDepth;
  const std::size_t count = state->slots.size();
  for (std::size_t i = 0; i < count && i < state->slots.size(); ++i) {
    Slot& slot = state->slots[i];       // re-read: an earlier callback may have killed it
    if (slot.dead || !slot.callback) continue;
    slot.callback(args...);             // in place: deque addresses are stable
  }
  if (--state->dispatchDepth == 0)
    std::erase_if(state->slots, [](const Slot& s){ return s.dead || !s.callback; });
}
```

## AnimationManager — tick contract

`src/render/animation/animation_manager.{h,cpp}`. A setter runs arbitrary shell code and may start animations,
cancel others, or destroy nodes (whose destructors call `cancelForOwner`). None of that may move the storage the
tick is walking:

1. **Additions during a tick go to `m_pending`** and are merged when the tick finishes. A new animation therefore
   starts on the *next* tick — imperceptible, and it means the vector cannot reallocate mid-walk.
2. **Cancellation during a tick marks the entry `dead`** (and finished) instead of erasing it. Callables are kept
   until reaping, for the same reason as Signal.
3. **The walk is index-based**, never an iterator or a reference held across a setter call.
4. `reduceMotion()` follows the identical contract.

## Retargeting and interruption

Continuity comes from callers passing the *current* value as `from`, not from the engine:

| Site | Behaviour on interruption |
|---|---|
| Panel reveal / close | `animate(m_detachedRevealProgress → target)` — continuous |
| `ScrollView::animateScrollTo` | starts from the live offset; a wheel step retargets `m_targetScrollOffset` |
| Carousel settle | goes through `ScrollView::scrollBy`, so it inherits the above |
| Control Center tab switch | interrupted switches continue from the outgoing content's real offset (`m_tabTransitionOutgoingStart`) rather than snapping back |
| OSD value bar | retargets mid-glide instead of stacking |

## Regression protection

`tests/signal_dispatch_test.cpp` and `tests/animation_reentrancy_test.cpp`. The Signal test **fails against the
pre-fix dispatch and passes with the fix** — it detects a stale invocation with a liveness registry rather than
relying on a crash, because freed memory often reads back fine. The animation test documents the tick contract but
passes against the old code too, so it is hardening rather than proof; this is stated in the test's own header
comment and in the postmortem.
