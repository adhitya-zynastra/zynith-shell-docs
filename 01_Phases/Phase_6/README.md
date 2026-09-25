# Phase 6 — Persistent Shell UX, Wallpaper Browser, and Stability

**Window:** 2026‑09‑20 16:03 → 2026‑09‑21 05:20. **The largest phase**, spanning seven commits and two
significant incidents.

Phase 6 was supposed to be polish. It is the phase where I found out what I had actually built.

The plan was a bar redesign and a nicer wallpaper picker. What it turned into was a resource-lifecycle problem
(how do you hold a whole wallpaper collection without holding a whole wallpaper collection), a lifetime-safety
problem in a primitive the entire shell depends on, a D-Bus ownership conflict inherited from an environment that
predates the project, and a measurement-integrity problem that invalidated hours of numbers. The browser is
comfortably the largest thing here by line count — 1 560 insertions across `99ac272`, `46296d0` and `57debbc`,
against 613 for the lifetime work — and the lifetime work is what the phase was actually about, which is roughly
the opposite of what I expected going in.

The through-line is that every one of those problems was reached by pushing on something cosmetic until it
stopped being cosmetic. Keeping the wallpaper browser open across an apply is a UX nicety; it is also what made a
latent use-after-free reproducible.

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
composition** after I rejected the first result: the compact control menu had grown wide to contain the cards,
which is not what I asked for. The fix separates a
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

## Later amendment — Phase 6A (2026‑09‑25, `a147fc1`)

The "Not done in Phase 6" list above is the state at `57debbc` and is left as it was. Two of its items have since
moved:

- **Morph primitive — done.** `MorphTransition` extracted from the Control Center's bespoke transition state;
  the Control Center now consumes it. A refactor with preserved behaviour, verified at runtime with a zero-jump
  retarget trace, ~420 stress cycles, and an interleaved A/B showing no regression.
  → [`morph-primitive.md`](../../02_Architecture/animation/morph-primitive.md),
  [`phase6a-motion.md`](../../03_Performance/benchmarks/phase6a-motion.md)
- **Control Center morphing — done, and was already behaviourally correct** from `e9e27b0`.
- **Motion settings in the main surface — model and UI done** (`ccfe125`); **niri generator decided but not
  migrated** ([ADR‑0015](../../05_Decisions/ADRs/ADR-0015-niri-animation-ownership.md)), so `Super+Alt+A` still
  opens the plugin deliberately.

Tests moved from 118 / 119 to **119 / 120** because the suite gained `morph_transition_test`.

## Later amendment — motion, configuration and glass system tracks (2026‑09‑25)

Three foundation systems, built as system tracks inside Phase 6 rather than as a new phase:
`aaa69b0` (glass), `f5cad71` (motion), `8c2b4eb` (Zynith Corner).

- **Motion ownership finished.** The shell now generates `animations.kdl`; the Motion plugin and `motion.toml` are
  retired; `Super+Alt+A` opens Zynith Corner. The migrated desktop reproduces the plugin's last output byte for
  byte. → [`motion-settings.md`](../../02_Architecture/animation/motion-settings.md), ADR‑0015 amendment
- **Zynith Corner** — a section in the existing settings window, not a new panel.
  → [`zynith-corner.md`](../../02_Architecture/configuration/zynith-corner.md)
- **Glass** — a shared surface model over the semantic palette, consumed by floating panels first.
  → [`glass.md`](../../02_Architecture/surface/glass.md), ADR‑0016
- Validation: [`tracks-motion-glass.md`](../../03_Performance/benchmarks/tracks-motion-glass.md). Tests 122 / 123.
