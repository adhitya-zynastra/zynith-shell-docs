# Control Center

## Shape

A floating panel with **12 tabs**. Zynith changed the navigation from a left rail to a **horizontal icon row above
the content** (`[control_center] top_nav = true`), using the existing `RovingListNavHost` switched to its
horizontal axis; the scroll rail is dropped because the row fits.

Two Zynith-added entry points:

- `hover_open` — resting on the bar's time cluster for `hover_open_delay_ms` (350 ms) opens the panel at Home. A
  one-shot `Timer`, armed on hover and cancelled the moment the pointer leaves. It arms for **any widget in the
  capsule group containing the clock**, because the cluster reads as one control.
- Bar widgets (network, bluetooth, …) open the panel at their own tab.

## Section transitions

The transition is content-only: the shell, backdrop and navigation stay stationary while the outgoing container
fades out and the incoming one fades in over a **~34 px** travel (it used to be a full body height, which read as
the panel re-opening). An interrupted switch continues from the outgoing content's real offset rather than
snapping back.

## Retargeting instead of rebuilding

`PanelManager::openPanel()` used to destroy and rebuild any panel that was already open, so clicking a second bar
widget replayed the entire opening animation and re-initialised every tab. `Panel::retargetOpen(context)` now
offers the live panel the new context first; the Control Center implements it by switching tabs.
**Measured: 96.7 → 58.3 ms CPU and 643 → 398 context switches per navigation.**

## Cost

Open and idle costs the same as the bar alone (1.00 % of one core). A page transition costs 2.28 %, rapid
switching 4.00 %.

## Planned

True **morphing** between sections — the content region transforming rather than cross-fading — is designed but
not implemented (`06_Reference/future-work.md`).

## Section transitions — what already exists (Phase 6 audit)

Phase 6's remaining scope listed "Control Center uses appropriate internal morph transitions" as outstanding, so
I had Claude audit what `57debbc` actually does before building anything. The behavioural requirement turns out to
be **already met**, by the Phase 6e panel-retarget work rather than by anything named "morph".

Switching Wi-Fi → Bluetooth → Audio today (`control_center_panel.cpp`, `layoutTabContainers`):

| Requirement | Status at `57debbc` |
|---|---|
| Outer surface stays stable | **Met** — `Panel::retargetOpen()` takes a new context in place; the panel is not destroyed and rebuilt |
| Entrance animation not replayed | **Met** — this is precisely what `retargetOpen()` fixed (`e9e27b0`) |
| Only the content region transitions | **Met** — `layoutTabContainers` offsets and fades the tab containers; the shell, backdrop and navigation do not move |
| Travel is short enough to read as navigation, not re-opening | **Met** — `min(bodyHeight × 0.10, kTabTransitionTravel × contentScale)`, with the code commenting that a full-height slide "reads as the panel re-opening, which is exactly what section navigation must not look like" |
| Direction-aware | **Met** — direction comes from the visible-tab ordinal delta |
| Interruption continues from the real position | **Met** — the outgoing container animates from `m_tabTransitionOutgoingStart`, its actual current offset, rather than snapping back |

Measured when that work landed: **96.7 → 58.3 ms CPU and 643 → 398 context switches per navigation**.

### What is therefore still missing

Not the Control Center's behaviour — the **reusable primitive**. The logic above is bespoke: hand-rolled offset,
opacity and z-index interpolation inside one panel's layout method. Nothing else in the shell can use it, so the
launcher, the settings sheet and any future surface would each grow their own copy.

The genuine remaining work is to **extract this into a shared, interruptible, retargetable morph primitive on the
existing `AnimationManager`** — with the Control Center becoming its first consumer rather than its
implementation. That is a refactor with a behaviour-preservation obligation (the six properties in the table are
the acceptance criteria), not a new feature.

Stated this way because the distinction matters for anyone reading the Phase 6 scope later: building a morph
primitive and then claiming it fixed Control Center entrance replay would be taking credit for `e9e27b0`.

> **Phase 6A amendment.** The extraction described above has been done. The six transition members are replaced
> by a `MorphTransition` (`src/render/animation/morph_transition.{h,cpp}`), which the Control Center now consumes.
> `layoutTabContainers` is unchanged apart from reading `progress()`, `direction()` and `carry()` off the
> primitive. The six behavioural properties in the table above are the acceptance criteria for the refactor;
> how each was checked, and which could only be checked indirectly, is recorded in
> [`morph-primitive.md`](../animation/morph-primitive.md).
