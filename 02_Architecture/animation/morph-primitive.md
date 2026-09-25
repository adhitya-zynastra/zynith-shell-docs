# MorphTransition — The Shared Transition Primitive

**Added:** Phase 6A, `a147fc1`. **Source:** `src/render/animation/morph_transition.{h,cpp}`.
**Test:** `tests/morph_transition_test.cpp`.

## What this is, and what it is not

This is a **refactor**, not a new capability. The behaviour it provides already existed — the Control Center has
had continuous, interruptible section transitions since `e9e27b0`. What did not exist was a way for anything
*else* to have them: the logic lived as six member variables and a hand-rolled interpolation inside one panel's
layout method. The launcher and the lock screen would each have grown their own copy.

`MorphTransition` is that logic lifted out, with explicit lifetime rules. The Control Center now consumes it
rather than implementing it.

**It is not a second animation engine.** It owns no timer, no scheduler, and no per-frame loop. It is bookkeeping
around a single `AnimationManager::animate()` call, and the manager remains the only thing that advances time.

## The property that matters

A transition that restarts on retarget reads as a glitch. The one that matters is:

```
  A ────────●──────> B          the user reverses at ●
            │
            └────────> A        the reversal starts from ●, not from B
```

The caller reads the live visual state immediately before retargeting and hands it in as `carry`.
`MorphTransition` stores and returns it; it never inspects the scene graph itself. That is deliberate — it has no
opinion about *what* is being morphed, which is why the Control Center, and later the launcher and lock screen,
can share it without sharing a layout model.

## API

```cpp
void  bind(AnimationManager* animations, const void* owner);
void  start(int direction, float carry, float durationMs, Easing easing,
            std::function<void(float)> onFrame, std::function<void()> onSettle);
void  cancel();                       // idempotent; does not settle
bool  active()    const;
float progress()  const;              // 0..1 of the current leg
int   direction() const;              // carried for the caller; never interpreted
float carry()     const;              // the state handed in at retarget
```

`direction` and `carry` are carried, not applied. The primitive does not know what a direction means.

## Lifetime contract

This is the part worth reading before changing it, because the project has already lost a desktop to this family
of bug ([the `Signal` use-after-free](../../04_Incidents/postmortems/2026-09-20-signal-uaf.md)).

1. `start()` tags the animation with `owner`, so a `Node` destructor's `cancelForOwner()` reaches it when the
   scene node being morphed goes away.
2. The destructor cancels, so a running leg cannot call back into a destroyed `MorphTransition`.
3. **The frame and settle callables are owned by `AnimationManager`, not by this object.** This is the one
   non-obvious decision. The first draft held them as members and released them on retarget — which would destroy
   the callable whose `operator()` is on the stack when `start()` is re-entered from inside `onFrame`, which is
   exactly what a rapid retarget does. The manager already solves this: a cancel during a tick only *tombstones*
   the entry, keeping its callables alive until the tick unwinds
   (`animation_manager.cpp`), and a tombstoned entry is never stepped again and never fires its completion.
4. **A retargeted leg does not settle.** Only the leg that reaches progress 1.0 runs `onSettle`. This falls out of
   (3) — `tick()` checks `!dead` before queuing a completion — and it is the semantics the Control Center needs:
   an interrupted switch must not run the finishing logic for a tab it is no longer going to.

## Control Center integration

| Concern | Before (`e9e27b0`) | After (Phase 6A) |
|---|---|---|
| Transition state | 6 members: anim id, progress, direction, outgoing-start, active, outgoing tab | `MorphTransition m_tabMorph` + the outgoing tab id |
| Interruption carry | `m_tabTransitionOutgoingStart`, set in `selectTab` | `carry` parameter → `m_tabMorph.carry()` |
| Cancel on close | manual id check + `m_animations->cancel()` | `m_tabMorph.cancel()` (idempotent) |
| Visual behaviour | travel capped at `min(bodyHeight × 0.10, kTabTransitionTravel × contentScale)`, direction-aware, opacity cross-fade, z-order during transition | **unchanged** — still in `layoutTabContainers` |

The interpolation maths did not move. `layoutTabContainers` now reads `progress()`, `direction()` and `carry()`
off the primitive instead of off its own members. The outgoing tab id stayed a panel member deliberately: it is
about *what* is being morphed, not about the morph.

One ordering change: `start()` is now called *before* the first layout pass, because `layoutTabContainers` reads
the leg's state and the pre-animation frame has to see it. Previously the members were assigned first and
`animate()` called last; the net effect is identical.

## Tests

`tests/morph_transition_test.cpp`, registered in `meson.build`. Covers: basic progression and settle; retarget
(previous leg must **not** settle, carry and direction update, new leg restarts at 0); a 60-step rapid reversal
chain where exactly one leg settles; **retarget from inside `onFrame`** — the hazard that drove the lifetime
design; cancellation, including idempotence and no frames after cancel; destruction during an active leg;
`cancelForOwner` (the `Node` destructor path); motion disabled, which must land on the end state rather than a
half-applied one; an unbound morph; and several independent morphs on one manager.

One thing the test had to learn the hard way: **`AnimationManager::tick()` ignores its `deltaMs` argument** and
derives progress from `steady_clock`, so a fixed duration stays correct when the compositor delivers sparse frame
callbacks. A test that ticks a synthetic clock never completes anything. The test sleeps real time instead, and
says so in a comment so the next person does not rediscover it.

## Verification

**Unit test** — `morph_transition_test` passes; suite **119 / 120** (the suite gained this test; the one failure
is still the unrelated `upower_charge_limit_integration`).

**Runtime, in the real shell.** The unit test proves the primitive; it does not prove the Control Center actually
takes the retarget path when sections are switched quickly. So I had Claude add temporary logging, build it
incrementally (a `.cpp`-only change, no ABI risk), drive three scenarios through `noctalia msg`, then revert —
and prove the revert by rebuilding and getting a binary **byte-identical** to the clean one (`b12c8ff8…`).

| Scenario | Carry logged | First drawn frame | Jump |
|---|---|---|---|
| Home → Network, complete | 0.00 | 0.00 | 0 px |
| Network → Bluetooth, complete | 0.00 | 0.00 | 0 px |
| **→ Network 80 ms later (reversal, dir −1)** | **7.18** | **7.18** | **0 px** |
| Bluetooth → Audio → System → Bluetooth, 60 ms apart | 9.29 · −8.95 · 8.94 | 9.29 · −8.95 · 8.94 | 0 px each |

Carry is non-zero exactly when a leg was interrupted and zero when it was not, and the first frame of every leg
sits exactly on it. That last property also validates the one ordering change (`start()` before the first layout
pass). Trace: `03_Performance/benchmarks/phase6a-retarget-trace.txt`.

**Stress and performance** — ~420 navigation cycles and 200 reopen-during-teardown cycles with no crash, no new
coredump and no leak; interleaved A/B against `ccfe125` shows no regression. Details, including two measurement
mistakes made on the way, in [`phase6a-motion.md`](../../03_Performance/benchmarks/phase6a-motion.md).

**How each preserved Control Center property was checked**

| Property | Evidence |
|---|---|
| Outer surface stable / no entrance replay | `retargetOpen()` path untouched by the refactor; overlay layer holds one surface throughout stress |
| Only content transitions | interpolation code unchanged (diff confined to where state is read from) |
| Travel cap ~34 px | same expression; carries observed at ≤ 9.3 px, inside the cap |
| Direction-aware | logged `dir` flips on reversal |
| Retarget from real offset | zero-jump trace above |
| Close mid-transition is safe | 420 closes issued with no dwell after the last switch |

Visual smoothness itself was not measured — there is no frame-timing instrumentation in the shell.

## What this does not do

No springs, no multi-property interpolation, no declarative state description, no morph graph. The prompt for
this phase asked for the smallest robust foundation, and the Control Center's actual need is one scalar progress
leg with carry-over. Adding a property system before a second consumer exists would be speculative.
