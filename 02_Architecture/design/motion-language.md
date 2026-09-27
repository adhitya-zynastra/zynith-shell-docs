# Motion Language — Roles, Physics, Interruption

**Implemented 2026‑09‑26 (sixth batch).** Code: `src/render/animation/motion_role.*`, `motion_physics.*`,
`motion_value.*`, `animation_manager.*`, `morph_transition.*`. Tests: `motion_language_test`. Earlier record:
[`animation/motion-language.md`](../animation/motion-language.md) (batch 4: exit tokens and the first morph).

## Why roles

Before this batch every call site chose a duration and a curve: 72 sites, 10 easings, `EaseOutCubic` 44 times.
A role names *why* something moves; the role table decides *how*. I had Claude derive the role set from those 72
call sites, grouped by what they animate, and then add roles only where the research evidence required them:
- staged content, which Zynith has never done;
- springs for elements that get retargeted.

## The roles

| Role | Model | Parameters (tempo 1) | Reduced motion | Used by now |
|---|---|---|---|---|
| `focus` | tween | 130 ms `EaseOutCubic` | 90 ms fade | every `Button` state crossfade |
| `surface-reveal` | tween | 300 ms `EaseOutQuint` | snap | every panel reveal (attached and detached) |
| `surface-dismiss` | tween | 200 ms `EaseInQuad` | snap | every panel dismissal |
| `content-reveal` | tween | 150 ms `EaseOutCubic`, **delay 50 ms** | 90 ms fade | — (Batch 7) |
| `content-dismiss` | tween | 100 ms `EaseInQuad` | 90 ms fade | — |
| `element-move` | **spring** | ω 30/s, ζ 1.0 → 99 % in ≈ 221 ms | snap | the Control Center nav indicator |
| `element-resize` | **spring** | ω 26/s, ζ 1.0 → 99 % in ≈ 255 ms | snap | — |
| `morph` | tween | 300 ms `EaseOutQuint` | snap | Control Center section content |
| `scene-change` | tween | 520 ms `EaseOutCubic` | 150 ms fade | — |

Durations are the existing `Style` motion tokens, so they keep one owner. `[shell.animation].speed` divides tween
durations and delays, and multiplies spring frequencies.

## Physics — which model, and why

Each choice is labelled by where it comes from:
- **Measured:** frame-level evidence from the research record.
- **Inferred:** a design conclusion drawn from that evidence.
- **Chosen:** an implementation choice.

| Role family | Model | Reasoning |
|---|---|---|
| surface reveal / dismiss | tween | **Measured:** the reference drawer arrives in ≈ 230 ms, fits ease-out, and has at most ≈ 1 % overshoot (M1). **Inferred:** a reveal is a clip progress, and nobody retargets it mid-flight in a way that needs velocity. **Chosen:** keep the existing curve; only the dismissal changed (see below) |
| element move / resize | critically damped spring | **Measured:** selections and indicators get retargeted mid-flight (M2, M5, M10). **Inferred:** only a spring keeps velocity through a retarget. **Chosen:** ζ = 1, so there is no overshoot; ω set so the settle time matches the tween it replaces (EaseOutCubic over 300 ms reaches 99 % at ≈ 235 ms) |
| content staging | delayed tween | **Measured:** surface first, content ≈ 50–250 ms later (M10, M1). **Chosen:** a 50 ms delay, on the short end of that range |
| focus | short tween | the existing 130 ms state crossfade, unchanged |
| morph | tween progress (`MorphTransition`) | choreography of one frame changing content; its continuity is the carried state |

Not built, deliberately:
- underdamped springs for layout (reference overshoot is ≤ 1.3 %, and my proposal capped it at 1.5 %; ζ = 1
  simply removes it);
- velocity-driven deformation (Ryoku's `BlobRect`), which has no consumer yet;
- parallax.

**Spring maths.** `motion::step` is the closed-form damped-oscillator solution for a constant target, exact for any
time step. A sparse compositor frame lands where wall time says the motion should be, the same way tweens already
advance. A spring rests within 0.4 % of its travel (never more than half a pixel), then lands exactly on the target
and leaves the manager.

## Interruption and retargeting

- `AnimationManager::retarget(id, to)`:
  - a spring keeps its **position and velocity** and bends toward the new target;
  - a tween restarts its curve from its current value (position only).
- `MotionValue::setTarget` retargets when live and starts otherwise. Repeating the same target is a no-op, so layout
  passes may call it every frame.
- A generation token makes a superseded entry inert. A completion that runs in the same tick as a newer start
  cannot clear the newer entry.
- **Test with teeth:** the retarget check compares the observed position with the physics prediction for the
  *kept* velocity and for a *reset* velocity, 20 ms after the retarget. A mutation that zeroes velocity on retarget
  fails four checks.

## Reduced motion

`[shell.animation].enabled = false` is Zynith's reduced-motion setting:
- spatial roles **snap** (their end state is applied at once);
- state-change roles (`focus`, `content-*`, `scene-change`) keep a **short fixed fade** (90–150 ms, independent of
  tempo), so a state change is still visible without movement;
- running springs land on their target on the next tick.

Previously everything snapped. The fades apply only when animations are off, which is not my configuration.

## One behaviour changed on purpose

Attached panels (the Control Center at its bar) used to close on upstream Noctalia's 300 ms `EaseInOutQuad`. Its
slow tail left a sliver at the bar for about 350 ms at my Cinematic tempo (measured before the change). They now
close on `surface-dismiss`, like detached panels already did since batch 4. The before/after figures are in the
validation record.

## Migration state

Remaining raw `animate()` sites are listed by the inventory in the validation record. They migrate with their
surfaces in Batch 7. I would rather each surface choose its roles when it is redesigned than bulk-convert timings
nobody is looking at.
