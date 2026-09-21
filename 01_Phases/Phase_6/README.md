# Phase 6 — Persistent Shell UX, Wallpaper Browser, and Stability

**Window:** 2026‑09‑20 16:03 → 2026‑09‑21 05:20. **The largest phase**, spanning seven commits and two
significant incidents.

| Sub-phase | Commit | Date | Theme |
|---|---|---|---|
| 6a | `82fb4b0` | 09‑20 16:23 | Clock hover→Control Center, CC top navigation, panel silhouette |
| 6b | — (config) | 09‑20 ~20:00 | Bar recomposed into glass clusters (zero C++) |
| 6c | `99ac272` | 09‑20 21:02 | Cinematic carousel + shared ScrollView knobs |
| 6d | `46296d0` | 09‑20 22:23 | Compact menu + full-width orbit carousel (spatial correction) |
| 6e | `e9e27b0` | 09‑20 23:24 | Carousel input fix, live backdrop, panel retarget, motion retune |
| 6f | `08f5454` | 09‑21 02:23 | **Use-after-free fix** (Signal / AnimationManager) |
| 6g | `eaff2b2` | 09‑21 03:47 | Session-scoped thumbnails; allocation-free dispatch |
| 6h | `57debbc` | 09‑21 05:20 | Eager previews + promoted, predictive display tier |

## 6a — Bar interaction and Control Center navigation

Widgets record their config type (`Widget::widgetType()`); resting on the clock arms a one-shot `Timer` that opens
the Control Center at Home (`control_center.hover_open`, `hover_open_delay_ms = 350`). Cancelled the instant the
pointer leaves — no polling, no new gesture type. `control_center.top_nav` turns the section rail into a horizontal
icon row. `zynithPanelRadius()` gives panel background, shadow, attached corners and the blur region one radius.

## 6b — Bar composition (configuration only)

`capsule = false` removes per-widget pills; three deliberate clusters replace them: **time** (clock + CAVA
visualiser in one surface), **status** (network/bluetooth/volume/brightness/battery), **sys** (CPU/RAM/temp
accordion). Clock `font_scale = 1.12` leads the hierarchy; `[widget.network] show_label = false` removed the
`enp0s20f0u2u4u1` string. A/B over three interleaved 60 s samples showed **no CPU regression** (1.07–1.12 % either
way).

## 6c–6d — The carousel, and a spatial correction

`99ac272` introduced `CarouselView` over the existing `VirtualGridAdapter`. `46296d0` then **corrected the
composition** after the owner rejected it: the control menu had grown to contain the cards. The fix separates a
compact 1000 px control card from a full-width, undecorated carousel band on one surface.
Architecture: `02_Architecture/wallpaper/browser-architecture.md`.

## 6e — Three bugs and a motion retune

| Bug | Root cause | Fix |
|---|---|---|
| Clicking a card did nothing | Cards carry a depth-derived z-index (≤1000) and `WallpaperTile` **is** an `InputArea`, so each card sat above the hit-test overlay (z 50) and swallowed presses | Overlay raised to z 5000; hit-testing maps through the card's **drawn** rect |
| Applying a wallpaper changed nothing on screen until the browser closed | The modal backdrop was a **frozen screencopy** over the live desktop | `ScreenVeil::showTint()` (no image node) + `Panel::ModalBackdropMode::Live` |
| Control Center replayed its whole opening animation when navigating from a bar widget | `openPanel()` **destroyed and rebuilt** an already-open panel | `Panel::retargetOpen()`; CC switches tabs with the shell stationary — 96.7 → 58.3 ms CPU and 643 → 398 context switches per navigation |

Motion: tiers raised to 130/300/520, long-tail easings added, CC content travel cut from a full body height to
~34 px, interrupted tab switches continue from the outgoing content's real offset.

## 6f — The use-after-free

Three field `SIGSEGV`s with an identical backtrace. Full postmortem:
[`04_Incidents/postmortems/2026-09-20-signal-uaf.md`](../../04_Incidents/postmortems/2026-09-20-signal-uaf.md).

## 6g — Resource model and dispatch cost

Session-scoped thumbnails with ownership tagging, a decode gate, and the removal of the per-invocation
`std::function` copies that `08f5454` had introduced. Also: `applyPluginSourcesToRegistry()` ended in an
unconditional `registry.scan()` that ran on **every config apply**, so one wallpaper apply re-walked the plugin
directories three times — **6 manifest loads per apply → 0**.

## 6h — Wallpaper quality

Eager preview loading for the whole collection plus a promoted, direction-aware display tier.
See `04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md`.

## Also fixed in this phase (environment, not code)

- **Notifications were dead** — SwayNotificationCenter owned the D-Bus name in the niri session.
- **btop showed no CPU box** — its own config listed `shown_boxes = "proc mem net"`.

## Verified final state (`57debbc`)

- Working tree clean; **clean** build (`meson compile --clean` + full build)
- Tests **118 / 119**; the failure is pre-existing and unrelated (`04_Incidents/known-failures.md`)
- `niri validate` ✓, `noctalia config validate` ✓, no new coredumps
- Focus ≠ apply re-verified; wallpaper visibly updates behind the open browser; hover→CC works across the whole
  time cluster

## Not done in Phase 6

Morph primitive, Control Center morphing, launcher redesign and style variants, lock-screen recomposition and power
controls, the configurability architecture, folding settings into one surface, and the GTK template optimization.
All tracked in `06_Reference/future-work.md` as **planned**, not completed.
