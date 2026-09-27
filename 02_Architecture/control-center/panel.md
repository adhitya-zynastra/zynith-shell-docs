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

## Zynith style (fifth batch, 2026‑09‑26)

`[control_center].style = "zynith" | "classic"` (Personalization → Control Center). **Zynith is the default; Classic
is the previous panel**, and every Zynith path sits behind the flag, as with the launcher.

**What changed, and why.** The Home section was a column of equal cards: a user card, a separate date/time card,
then shortcut buttons as solid primary blocks. Each element carried the same visual weight, so nothing led. The Zynith
style keeps every function but changes the hierarchy:

| Element | Classic | Zynith |
|---|---|---|
| Home — time and date | its own card beside the user card | the **hero**: 60 px Light time over date and weather, in the lower left of the wallpaper banner — the banner becomes the stage instead of a card background |
| Home — identity | name, host, version, uptime beside a ≈ 114 px avatar | name and uptime only, lower right of the same banner, beside a ≈ 64 px avatar |
| Quick controls | near-square tiles; solid `primary` when on, solid surface when off | landscape tiles (height 0.62 × width); the shared selection material: `primary` 0.18 tint + 0.55 primary hairline when on, card fill + 0.07 hairline when off |
| Section title | Title size, bold, primary | header size, medium weight, on-surface, display face — the title names the section, the indicator carries the colour |
| Navigation | the batch‑4 morph indicator | unchanged — the one moving shared object |

The banner's height is **measured** from the clock column (`Node::measure`) plus headroom, rather than estimated,
so a different display face or font size cannot overflow it. The date is `[shell].date_format`, which the preset now
sets to `"%A, %d %B"`.

The hero keeps both existing interactions: the wallpaper overlay (click/keyboard → wallpaper) and a new invisible
overlay on the clock that opens Weather, as the classic date/time card did. The hero does not use the hover-card
treatment — the banner stays a picture, not a button.

**Not done**, deliberately: no new sections, no rearrangement of Audio/Network/Bluetooth/Media/Calendar/System
contents, and no second animation engine. The other sections change only through the shared title, control material
and radius.

Evidence: `07_Assets/screenshots/cc-home-zynith.png`, `cc-home-classic.png`, `cc-morph-rapid.png`; validation in
[`tracks-cc-lock-visual.md`](../../03_Performance/benchmarks/tracks-cc-lock-visual.md). The first build of this
design had three layout bugs, which only the capture showed; they are recorded there.

> **Amendment (Batch 7, 2026‑09‑26).** The fifth-batch Zynith style above was a restyle inside the classic
> structure, and I switched back to Classic within the hour. Batch 7 replaced it — the Home code of the fifth batch
> was discarded (the Classic Home is back to its `e521a86` form) and the section below describes what `zynith` means
> now.

## Zynith Control Center (Batch 7, 2026‑09‑26)

`[control_center].style = "zynith"` now changes the panel's **structure**, not only its colours. `classic` is the
previous panel and stays selectable (Personalization → Control Center, or
`noctalia msg control-center-style-set classic`). Every Zynith path is behind the flag.

### Composition

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ( ⌂ Home )  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌  ◌                    ⚙  ⏻  ✕   │ ← command bar
│──────────────────────────────────────────────────────────────────────────────│ ← one hairline
│ ┌ stage ──────────────────────────────────────────────────────────────────┐  │
│ │ (the wallpaper, clear above, settling into the surface below)           │  │
│ │ 22:27                                               Name        (◉)    │  │ ← the focal readout
│ │ Saturday, 26 September · ☁ 24° Cloudy               user@host          │  │
│ └─────────────────────────────────────────────────────────────────────────┘  │
│ ┌ band ───────────────────────────────────────────────────────────────────┐  │
│ │ [art] Track · Artist                                   Playing · 1:23    │  │ ← now playing
│ └─────────────────────────────────────────────────────────────────────────┘  │
│ ( chip )  ( chip )  ( chip )                                                 │ ← controls
│ ( chip )  ( chip )  ( chip )                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Element | Classic | Zynith |
|---|---|---|
| Navigation | a tray of icon buttons (or a left rail) plus a separate title row | **one command bar**: the sections on the left, the section's own actions and close on the right, no title row — the unfolded item names the section |
| Selection | an indicator behind the active icon | a **capsule** that travels between items while the old item folds its label away and the new one unfolds its label (below) |
| Divider | the tray's own fill | one hairline between navigation and content |
| Home | four equal cards (user, media, date/time, shortcut grid) | a **stage** (the wallpaper with the time as the focal readout and identity opposite), a now-playing **band**, and **chips** |
| Sections' containers | bordered cards (`setCardStyle`) | embedded **plates**: a lighter tone step, a hairline only when `[shell].card_borders` asks for one, the plate radius token |
| Section headings | Title size, bold | the `Subtitle` role (16 px, medium, on-surface) for headings built by the shared helpers — one weight lighter than the Title-size bold titles most sections build themselves, so the two read as one family |
| Header actions | filled square icon buttons | clear capsules: every action gets the capsule radius; close and Home's settings/session become the Ghost variant. Sections' own action buttons keep their variants and selected states (a DND toggle, a destructive clear) |

### The command bar

The bar is the old `m_sidebar` row. With the command bar it has no fill, and the per-section header actions move
into it (`justify = SpaceBetween`: navigation left, actions right).

Its items are **placed by hand**, not by the flex pass:

- Each item is a `Button` that does not participate in layout. `doLayout` arranges it once at its **unfolded** size,
  measured from the label text: `height + gap + text`, with the glyph centred in the collapsed square.
- Each item then shows a visible width of `collapsed + e × (unfolded − collapsed)`, where `e` is its **expansion**, a
  `MotionValue` (0 = icon, 1 = icon + label).
- The item clips its children, so the label is revealed by the width. The label's ink fades in over the second half
  of the unfold, so a half-open item never shows a squeezed word.
- Positions are cumulative, so when the old label folds and the new one unfolds, every item between them slides.
- The geometry changes through `setFrameSize` / `setPosition`, which repaint **without asking for a layout pass**, so
  the whole reconfiguration costs one redraw per frame.
- The strip's width is pinned to the widest unfolded state, so nothing else in the bar moves.

The **selection capsule** is the batch-6 `MotionRect` on the `ElementMove` spring. Its destination is where the new
item **will be** once every expansion has settled (`commandBarNavRest`), not where it is mid-motion, so it makes one
journey there and the items converge on it. Expansions use the same role, so both start from rest together and
arrive together. A burst of switches retargets both from their current position and velocity. The section content
still switches through the existing `MorphTransition` (`Morph` role): **one** section morph, **one** travelling
capsule, **N** expansion values — no new animation engine, and all of them are entries in the panel's
`AnimationManager`.

**Responsive, labels first.**
- An item's unfold (gap + label) does not depend on its height, so the items shrink, from the medium control
  height (38 px) down to 30 px, to make room for the widest label beside the actions. At my default width
  (0.85 × 780) that gives 34 px items with labels.
- Only if even 30 px leaves no room does the strip go icon-only (tooltips name the items). It may then shrink to
  28 px before anything overlaps.
- The room is measured against the **widest section's actions** plus close, not the active section's. The first
  capture measured the active one, and the whole strip jumped at the moment of a switch: Home has three actions,
  most sections one.
- Keyboard handling is unchanged: the roving navigation, Ctrl+Tab and the wheel over the bar all go through
  `selectTab`.

**Label ink follows the capsule.** Items and capsule converge on the same end state, but by different paths. The
first filmstrip showed the incoming word ("Med…") beside the capsule for about three frames. The fix:
- the active item's label ink is capped by how close the capsule is to its rest (it appears within the last 12 px);
- an item the capsule has left may only lose ink. Otherwise, in a burst of switches, every item passed through on
  the way flashed its half-unfolded word.

**When a section is opened directly** (`sidebar_section = "none"`, as in my settings), the panel has no navigation.
It shows the classic title row with the Zynith header treatment (title, clear capsule actions).

### Home

Built by `HomeTab::createZynith()` / `layoutZynith()`. The classic view is untouched, and both share the data paths:
`sync()`, the clock timer, the wallpaper layers, the avatar picker and the shortcut instances.

- **Stage.**
  - The user card becomes the stage: the wallpaper layers with a vertical scrim (clear down to 34 % of the height,
    then settling to 82 % of the surface colour at the bottom).
  - The **time** is set in the `Display` type role (64 px, light, tabular figures, the display face).
  - Beneath the time: one readout line with the date (`[shell].date_format`), a separator and the weather.
  - Identity sits opposite: name (`Subtitle`), `user@host` and uptime (`Micro`), and a 48 px avatar with a hairline
    ring that becomes the accent focus ring on hover or focus.
  - Interactions are kept: the stage opens the wallpaper browser (its pointer target ends before the identity, so
    the avatar keeps its picker), and the time and date open Weather (the clock column sits above the stage's target).
- **Band.** Now playing as one plate: 40 px art, track, artist, and the status as a `Data` readout (monospaced,
  tabular), so the position ticks without jitter. The accent is used only while playing. Click → Media.
- **Chips.** The shortcuts as 38 px capsules, three across. An active toggle uses the selection material
  (`SelectionFill` / `SelectionEdge`, accent label). Everything else is a quiet tone step. Right-click and the scroll
  wheel still reach the shortcut. The Noctalia version line is not shown on the Zynith Home; it is in Settings → About.

### Where things live

| Concern | Code |
|---|---|
| Style switch and command bar | `ControlCenterPanel::create`, `layoutCommandBarNav`, `applyCommandBarNavGeometry`, `commandBarNavRest`, `syncCommandBarNavTargets` |
| Plates and headings for every section | `control_center::setZynithSurfaces`, `applySectionCardStyle`, `addTitle`, `makeCardHeaderRow` (`tab.cpp`) |
| Home | the "zynith Home" section of `home_tab.cpp` |
| Style from a script | `noctalia msg control-center-style-set zynith|classic` — the same `settings.toml` override the Settings window writes |

### Evidence (Batch 7)

Captures were taken on a verified-empty workspace, cropped to the panel. The Wi‑Fi chip's network name is
pixelated in the Home capture.
- **Home:** [`cc-zynith-home.png`](../../07_Assets/screenshots/cc-zynith-home.png).
- **Section plates** (System, opened directly): [`cc-zynith-section-plates.png`](../../07_Assets/screenshots/cc-zynith-section-plates.png).
- **One switch, Home → Media**, every second frame ≈ 26 ms apart:
  [`cc-zynith-command-bar-switch.png`](../../07_Assets/screenshots/cc-zynith-command-bar-switch.png).
- **Four switches 80 ms apart, Home → System:**
  [`cc-zynith-command-bar-morph.png`](../../07_Assets/screenshots/cc-zynith-command-bar-morph.png).
- **Attachment moved to the left bar** by a click on its brightness widget:
  [`cc-zynith-attached-left-bar.png`](../../07_Assets/screenshots/cc-zynith-attached-left-bar.png).

Numbers are in [`control-center-lock-batch7.md`](../../03_Performance/benchmarks/control-center-lock-batch7.md).

The attachment model is untouched. Which bar the panel attaches to, centring when the panel is wider than its
bar, and a click on another bar's widget moving the attachment all live in `PanelManager` and the bar's position
reference ([`coordinate-model.md`](../layout/coordinate-model.md)); the Zynith style only changes what is inside the
panel.
