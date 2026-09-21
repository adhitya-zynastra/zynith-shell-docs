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
