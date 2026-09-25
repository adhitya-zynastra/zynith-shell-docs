# Zynith Motion Language

**Written:** 2026‑09‑25 (fourth batch). **Engine:** `AnimationManager` (unchanged). **Shared leg:** `MorphTransition`.

## What "morph" means in Zynith

A **morph** is a continuous transformation of shared visual state between two states of one surface. Something that
exists in both states keeps its identity and moves, resizes or restyles from where it is to where it will be.

A morph is **not** "A fades or slides out, B fades or slides in". That is a transition, and Zynith calls it one.

Practically: before building a morph, name the shared element. If there is none, it is a transition.

## Tokens

All durations are *base* values that `AnimationManager` divides by the effective shell speed (0.8 × preset × speed;
at the Cinematic preset, ×1.56 on screen).

| Motion | Duration | Curve | Used by |
|---|---|---|---|
| Enter / reveal | `animNormal` 300 | `EaseOutQuint` — decisive arrival | panels, OSD, notifications, bar reveal |
| **Exit / dismiss** | **`animExit` 200** *(new)* | `EaseInQuad` — accelerating away | panels, OSD, bar hide |
| Morph between states | `animNormal` 300 | `EaseOutQuint`, retargetable | Control Center sections |
| Feedback | `animFast` 130 | `EaseOutCubic` | hover, press, state chips |

The one change to *timing*: exits used to take as long as entrances (≈470 ms on screen at Cinematic), which is what
made dismissals feel like they lingered. They now take ≈312 ms. Entrances were left as they were. The bar's reveal
moved from `EaseOutCubic` to `EaseOutQuint` so it arrives like everything else.

Not changed, deliberately: the lock screen's Phase 2 choreography (approved timings), the wallpaper carousel's
own physics, and niri's springs (generated from the same speed setting).

## Control Center: a true morph

Before this batch, switching sections moved the outgoing page ~34 px and faded it while the incoming page travelled
in — a transition. Now (`control_center_panel.cpp`):

- **The shared element is the selection indicator.** One pill, behind the navigation, moves and resizes from the old
  tab's button rect to the new one. The buttons no longer draw their own selected fill, so there is only ever one
  selection on screen, in motion between the two states.
- **The frame and header do not move.** The panel surface, its glass, the title line and the header actions are the
  same nodes before and after.
- **Content reshapes rather than travels.** The leaving section settles 3 % inward about its top centre as it
  dissolves; the arriving one resolves from 3 % overscale onto the same frame. Nothing slides.
- **Retargeting carries the drawn state.** `MorphTransition::carry` now holds the leaving section's current reveal
  (it held a Y offset), and the indicator starts each leg from where it is drawn — mid-flight after an interruption —
  so a burst of switches is one continuous motion, never a queue.

This is one `MorphTransition` leg on the panel's `AnimationManager`, as before; no new engine or primitive.

**What this is not.** Section *content* is different per section, so there is no content-level shared geometry to
morph. The morph is the indicator plus the stable frame; the content is honestly a dissolve.

## Also in this batch

- Lock screen: a rejected password gets a ~360 ms damped horizontal shake of the password pill — the only lock
  screen motion that answers the user directly. One animation on the surface's manager, restored exactly on completion.
