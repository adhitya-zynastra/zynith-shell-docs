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

## Contextual routing and in-place retargeting (three-track batch 2, 2026‑09‑25)

I asked for each bar widget to open the Control Center on its own section, and for a click on a second widget
while the panel is open to switch the content in place. I had Claude audit what already existed before writing
anything, and nearly all of it did.

### Routing

Each route is a default left-click action, `panel-toggle control-center <section>`, declared upstream in
`src/shell/bar/widget_gesture_defaults.cpp`:

| Bar widget | Section | Source |
|---|---|---|
| clock | **home** | **Zynith preset** — `[widget.clock.actions] left = "panel-toggle control-center home"` in `rice.toml`; upstream opens `calendar` |
| network | network | upstream default |
| bluetooth | bluetooth | upstream default |
| media | media | upstream default |
| volume | audio | upstream default (output and microphone variants) |
| brightness | monitor (Display) | upstream default |
| battery | power | upstream default |

The clock change is a preset, not a code change: the action table is per-widget configuration
(`[widget.<name>.actions]`), so the upstream default stays intact and the route can be changed back without a
build.

### Clock click after hover-open

Hover-open on the time cluster already opened Home, and that collided with the new route. Resting on the clock for
350 ms opened the panel, and the click that followed — the click I had moved there to make — toggled it shut. With
the old Calendar route the same click retargeted, so the conflict only appeared once both opened Home. Claude found
it in the first runtime check (opened 15:37:10.242, closing 15:37:13.172).

The fix (`09990f8`) is in `Bar`: when the hover timer opens the Control Center it sets
`BarInstance::hoverOpenedControlCenter`, which is cleared the moment the pointer leaves the time cluster. A
`panel-toggle control-center …` click that arrives while the flag is set goes through `openPanel` instead of
`togglePanel` — it confirms the open, or retargets it if the clock is routed elsewhere — and clears the flag, so the
next click toggles normally. Re-tested: hover then click stays open; the next click closes; approach-and-click opens;
click closes.

### What a click does

`PanelManager::togglePanel` (unchanged apart from a corrected comment):

| Panel state | Click on | Result |
|---|---|---|
| closed | any routed widget | opens directly on that section; no intermediate section is shown |
| open on section A | the widget for A | closes (the toggle) |
| open on section A | the widget for B | `openPanel` → `Panel::retargetOpen("B")` → the tab switches in place through `MorphTransition` |

The retarget path never destroys the panel, so the outer entrance animation is not replayed, and the morph
carries the outgoing content's current offset and opacity. A burst of clicks therefore retargets one transition
from wherever it is instead of queueing a backlog (the same property `morph-primitive.md` verified for wheel
navigation).

### Keyboard

Added in this batch: **Ctrl+Tab / Ctrl+Shift+Tab** and **Ctrl+PageDown / Ctrl+PageUp** cycle sections,
browser-tab style. They go through `selectAdjacentVisibleTab`, the same path as the wheel over the navigation, so a
held chord retargets the morph rather than stacking transitions. Unlike browser tabs they **stop at the ends** rather
than wrap, because the wheel path does. Plain Tab stays with focus traversal.

### Verified

On the final build (details in the
[validation record](../../03_Performance/benchmarks/tracks-wallpaper-layout-cc.md)):

- Network, Bluetooth, volume, brightness and battery each opened their section; five clicks produced **one**
  `opened` log line — every switch after the first was a retarget. See `cc-routing.png`.
- Nine clicks at 60 ms gaps ended on the last-clicked section with no backlog, 0.44 CPU‑s for the whole script.
- Ctrl+Tab ×12 at 30 ms stopped at the last section, 0.25 CPU‑s.
- Density: the frame rhythm changes by a few pixels per step (`cc-density.png`). Intentionally subtle.
- Not verified: media → Media (nothing was playing, so the widget had nothing to show).

### Morph and anchoring (2026‑09‑26)

Section switching is now a morph around one shared selection indicator — see
[`motion-language.md`](../animation/motion-language.md). Where the panel opens is defined by the bar's position
reference and `[control_center].anchor_bar` — see [`coordinate-model.md`](../layout/coordinate-model.md).

### Density and placement of options

`[control_center].density` (`compact` / `comfortable` / `spacious`, factor 0.75 / 1.0 / 1.35) scales the frame
rhythm through `ui::responsive::space` — see [`responsive-layout.md`](../layout/responsive-layout.md). It takes effect
the next time the panel opens. The Control Center's appearance options (density, top navigation, hover-open, hover
delay, width) moved to **Personalization → Control Center**; its functional options (tabs, shortcuts, sidebar
modes, placement) stay in its own section (ADR‑0017).
