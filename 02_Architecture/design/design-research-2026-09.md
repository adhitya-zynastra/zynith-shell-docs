# Design Research — References, Measurements, Audit

**Date:** 2026‑09‑26. **Status:** research record. Nothing in the shell was changed by this work.
**Proposal built on it:** [`design-language.md`](design-language.md). **Architecture and roadmap:**
[`design-roadmap.md`](design-roadmap.md).

I stopped feature work because the shell had become technically mature but visually simple. I had Claude study
the reference material I collected, measure what it could rather than describe it, read the reference source trees,
and then audit Zynith against what it found. This page is the evidence. The proposal pages argue from it.

**Evidence tags** follow the documentation policy: **VERIFIED** (measured from frames or read in source),
**INFERRED** (a conclusion the evidence supports but does not prove), **UNKNOWN**.

**Provenance.** The videos are third-party showcase recordings I downloaded. Frames and contact sheets taken from
them stay local, in `~/.cache/zynith/design-research-2026-09-26/`, and are not added to this repository. The three
source trees are GPL‑3.0 projects. They were read for architecture and design ideas only, and no code was copied.

## 1. What was inspected

The brief named `~/videos/downloads/`. The material is actually in `~/Videos/Downloaded/`.

| ID | Video | Length, fps | What it shows |
|---|---|---|---|
| v1 | *Caelestia Shell V2* | 59 s, 50 fps | Caelestia's own showcase: dashboard with tabs, sidebar, settings, bar moved top → left, wallpaper picker with palette change, lock screen |
| v2 | *arch linux hyprland caelestia shell rice setup showcase* | 127 s, 30 fps | a user's Caelestia rice (warm mountain wallpaper): frame border, dashboard Media ↔ Performance, sidebar, session rail, lock, scheme changes |
| v3 | *Ryoku Arch* | 30 s, 30 fps (1728 × 1080) | NieR-style login, monochrome desktop, settings "Hub", accordion wallpaper carousel, top-edge visualiser |
| v4 | *CachyOS Hyprland End4-dots* | 133 s, 60 fps | illogical-impulse: "cookie" clock, lock screen, sidebar, Material settings, wallpaper-aware clock placement |
| v5 | *CachyOS Hyprland Imperative-dots Showcase* | 65 s, 60 fps | Imperative shell: two-state lock, bar popovers, skewed wallpaper carousel |
| v6 | *Arch Hyprland Setup. My Daily Driver* | 103 s, 60 fps | the same Imperative shell: lock, calendar/network/Bluetooth/audio popovers, drawer, circular wallpaper reveal |

| Tree | Project | Seen in | Licence |
|---|---|---|---|
| `caelestia/` | caelestia-dots/shell (Quickshell/QML) | v1, v2 | GPL‑3.0 |
| `quickshell/` | **Clavis Shell** (StatIndet) — a **niri** shell, Quickshell/QML + C++ | no video | GPL‑3.0 |
| `ryoku-arch/` | Ryoku-dev/ryoku-arch — a full Arch distribution with a Hyprland desktop | v3 | GPL‑3.0 |

There is no local source for End4 or Imperative; they are video-only evidence.

**Method.** I had Claude decode every video in full with ffmpeg:
- **Survey:** a per-frame change signal (to find cuts and transitions) and 2 s contact sheets over the whole
  length — all 60 sheets were inspected.
- **Frame level:** for the signature transitions, dense frame extraction and a per-frame bounding box of what
  changed against a reference frame (or a chord along one row, for a circular reveal).
- **Curve fit:** normalised progress fitted against easing curves and against damped springs.

Recording frame pacing is irregular by about ±1 frame, so curve fits closer than ≈ 0.03 RMS are
indistinguishable. The tools were temporary and live with the evidence, not in the shell.

## 2. Motion — measured

| # | Transition | Duration | Best fit | Observed | Tag |
|---|---|---|---|---|---|
| M1 | Caelestia dashboard opening from the top bar (v1 2.19 s) | 230 ms to within 1 %; settles by ≈ 400 ms | ease-out quad (RMS .031); critically damped spring ω 24/s (.047) | the panel is *pulled out* of the edge: its height grows while content stays anchored to its bottom; ≈ 1.1 % overshoot then back (561 → 555 px) | VERIFIED |
| — | the same, from source | 500 ms, `expressiveDefaultSpatial` (0.38, 1.21, 0.22, 1) | — | that curve reaches ≈ 100 % at 45–50 %, overshoots ≈ 1.3 %, settles by the end — **matches M1** | VERIFIED |
| M2 | Caelestia tab Dashboard → Media (v1 6.22 s) | ≈ 220 ms visual (400 ms standard curve in source) | — | horizontal pager: both pages visible mid-way; the panel's height changes to the new page at the same time; underline indicator slides | VERIFIED |
| M3 | Ryoku settings window leaving fullscreen (v3 15.40 s) | ≈ 350 ms | — | compositor window animation with a visible under/overshoot (width 410 → 390 → 380 → 392 at tile scale) | VERIFIED (compositor, not shell) |
| M4 | Ryoku ghost display word POWER → BEAUTY (v3 15.13 s) | ≈ 250 ms | — | halftone/dither dissolve between two words | VERIFIED |
| M5 | Ryoku accordion carousel, one step (v3 17.05 s) | ≈ 200 ms | — | the focused card collapses to a sliver while its neighbour expands; filename label only on the focused card | VERIFIED |
| M6 | Imperative lock, idle → authenticate (v6 1.50 s) | ≈ 300 ms | — | clock rises ≈ 15–20 px and fades; identity group rises ≈ 35 px and fades in; overlapping, same direction | VERIFIED |
| M7 | Imperative wallpaper change (v6 86.70 s) | ≈ 550 ms (start and end partly extrapolated) | ease-out quad (RMS .032); overdamped spring | circular reveal centred on the chosen card (≈ 961, 525); the bar recolours on the same frame the reveal begins | VERIFIED; duration INFERRED |
| M8 | Imperative skewed carousel, focus step (v6 85.2 s) | ≈ 400 ms | — | ≈ 20° sheared cards; the focused one widens; floating filter bar of colour dots | VERIFIED |
| M9 | End4 right sidebar (v4 77.13 s) | ≈ 70–100 ms | — | rigid slide, content painted from the first frame | VERIFIED |
| M10 | Imperative media popover (v5 10.40 s) | container 180 ms; content +100–250 ms | ease-out quad (RMS .048); spring ω 27.5/s, ζ .85 (≈ .6 % overshoot) | grows from a ≈ 110 px seed near the bar to 695 × 647; **surface first, content second**; surface opacity also ramps | VERIFIED |

**What the numbers say.**
- **Spatial arrival clusters at 180–240 ms** (M1, M2, M5, M10), with deceleration dominant and either no overshoot
  or ≈ 1 %. That overshoot is below what reads as "bounce"; it reads as mass.
- **Scene-scale changes are slower**, 300–550 ms (M6, M7), and move in one direction.
- **Closing is faster** where source is available: 200–360 ms against 350–500 ms opening (Caelestia, Clavis, Ryoku).
- **Nothing measured is a plain fade or a plain slide.** Each has a shape, size or origin change.

## 3. Source study — architecture

| Idea | Caelestia | Clavis | Ryoku |
|---|---|---|---|
| **Token system** | one `Appearance` singleton: rounding 12/17/25/full, spacing 7–20, padding 5–15, type 11–28, M3 expressive curves and durations; transparency *off* by default | static logical-px `Metrics` (spacing 2–24, corners 4–28, control heights, lock tokens with breakpoints); M3 type scale; semantic motion roles | one shared module (`Ryoku.Ui` `Tokens.qml`) for shell, settings and apps; a history lesson: eleven drifting theme copies collapsed into one; local adapters may *name* roles, never *define* values |
| **Surfaces** | **one fullscreen layer per monitor**: frame, bar and every panel; input `Region` mask; one shared shadow | layer surfaces per module; Keystone island attached to an edge | **one frame scene per monitor** + one menu manager (replacement at a shared anchor, stale-close protection, one close path) |
| **Panel shape** | `ShapePath` with reversed arcs = concave fillets into the frame; radius flattens to h/2 while small | bezier "ears" (`AttachedEdgeCurve`) | SDF: rounded boxes unioned by a **circular smooth-min**, so any surfaces fuse with true fillets, animated for free |
| **Motion** | M3 expressive; popout wrapper with `Behavior` on x/y/w/h (one container glides between popouts); content scale .8 → 1 + fade | **semantic roles** (`elementResize`, `elementMoveFast`, `desktopCardReflow`, `scroll`, `clickBounce`); Keystone chooses the curve **per change**: grow 500 ms overshoot ≈ 3.5 %, shrink 360 ms none, hover deltas 360 ms, radius its own track | app set 90/110/170/210 ms ("a settings sheet that animates for half a second feels like it is thinking"); shell set 100–500 ms; one tempo multiplier, zero under reduce-motion; **`BlobRect`**: deformation driven by its own velocity through an underdamped spring (k 200, c 16) |
| **Colour** | Material roles from the wallpaper | Material; blur via niri `ext-background-effect` from a generated fragment | resolution chain scheme → wallpaper → signature default; **`Ink.legible`** corrects text floating on the wallpaper in CIE L* (40 → 3:1, 50 → 4.5:1); accent clamped L* 30–88 |
| **Rules worth keeping** | edges are gesture zones (hover top → dashboard; 50 px drags) | no supporting text unless needed; never restate a switch's state; busy states never shift layout | emphasis by inversion not colour; accent only on the frame; depth is a hairline; control chosen by value kind and option count |

## 4. Reference comparison

| | Strongest visual idea | Strongest interaction | Strongest motion | Strongest architecture | Weakest | Could inform Zynith | Must not be copied |
|---|---|---|---|---|---|---|---|
| **Caelestia** | panels as extrusions of one screen frame, one shadow | edges as gesture zones | drawer pull with ≈ 1 % overshoot; one popout container gliding | one scene per monitor; `Behavior`-based retargeting | Material defaults everywhere; polls every 0.5–1 s; opaque black loses the wallpaper | surfaces that grow *from* something; one container that retargets | the frame-and-drawer silhouette itself |
| **Ryoku** | paper-and-ink restraint; typography as composition; the clock composed against the wallpaper | accordion: focus = expansion | the POWER → BEAUTY dissolve; velocity-driven give | single token module; SDF union frame; per-monitor surface manager | monochrome is a brand, not a system others can wear | contrast-solved ink tiers; accent budget; `Ink.legible` | bone-on-black palette, kanji glosses, dither and poster ornaments, the seal |
| **Clavis** | expressive shapes, disciplined density | Keystone: one object that becomes every notification/OSD/media view | direction-aware curves (grow ≠ shrink); hover as physical growth | semantic motion roles; niri blur fragment; written UI rules | the island is Apple's pattern | motion roles; asymmetric grow/shrink; the UI copy rules | the island itself |
| **End4** | Material 3 expressive shapes; manga wallpaper integration | clock placement that avoids the wallpaper's subject | fast, rigid sidebars (≈ 80 ms) | — (no source) | translucent grey windows flatten everything | scene-aware placement | cookie shapes, illogical-impulse layouts |
| **Imperative** | bar pills that grow into popovers; two-state lock | idle ↔ authenticate lock | circular wallpaper reveal from the chosen card; surface-first/content-second | — (no source) | busy popovers (orbit diagrams) that decorate rather than inform | seed-grown surfaces; staged content | the skewed carousel, the lens-circle lock |

## 5. Zynith audit

Inspected read-only:
- **Tokens and primitives:** `src/ui/style.h`, `render/animation/`, `shell/surface/glass.*`, the rect SDF shader,
  `PanelManager`'s attached geometry and the backdrop.
- **Captures:** this session's Control Center (both styles), the lock screen editor and the documented launcher.

| Area | Finding | Tag |
|---|---|---|
| Type | ramp 11 / 13 / 14 / 16 / 20 px — the largest step is 1.8× the smallest; no display role. Every large size (hero clock, lock clock) is an ad-hoc multiplier. One face (Montserrat) for language, numerals and data; no tabular figures anywhere | VERIFIED |
| Space | 4 / 8 / 12 / 16 only — no 24, 32 or 48, so nothing can be generous on purpose | VERIFIED |
| Radius | 3 / 6 / 9 / 12 × corner scale 0.6 (1.8–7.2 px) plus a 16 px panel floor; no concentric rule for nested shapes | VERIFIED |
| Surfaces | one archetype: a rounded rectangle with fill and an optional hairline. The Control Center tabs apply the same card style 35 times | VERIFIED |
| Material | one level: fill opacity + one card step + tint + compositor blur. No material hierarchy, no edge highlight, shadows only on bars | VERIFIED |
| Motion | a fixed-curve tween (10 easings, 44 × `EaseOutCubic`); four duration tokens chosen per call site; no bezier curves, no springs, **no velocity continuity** on retarget (`MorphTransition` keeps position, not velocity); one shared-element transition (the CC indicator) | VERIFIED |
| Placement | island bars (a left rail, an auto-hidden top media pill, a 160 px bottom time pill). A 664 px Control Center attaches to the 160 px Time bar, so its concave bar-side corners flare into empty space: the attachment metaphor does not read | VERIFIED |
| Colour | wallpaper-derived palette (good). Classic Control Center: solid primary on 3 of 6 tiles + primary title + primary clock, so the accent is everywhere and marks nothing. Text on the wallpaper (desktop clock, lock) uses panel roles with no contrast correction | VERIFIED |
| Renderer | already has what most of the proposal needs: an SDF rect with per-corner concave shapes, insets and shadows; a shell-rendered blurred wallpaper (backdrop, lock veil). Shell surfaces submit full-buffer damage every frame | VERIFIED |
| Owner signal | the Zynith Control Center style from the fifth batch was overridden back to `classic` in `settings.toml` at 03:30, within an hour of shipping | VERIFIED |

## 6. Why Zynith reads as simple

The problem is not polish. It is that Zynith has **no structural idea**:
1. **No origin.** In every reference, UI comes *from* somewhere — the frame (Caelestia, Ryoku), the island
   (Clavis), the bar pill (Imperative). In Zynith panels appear beside whichever island was clicked, often wider
   than it, so nothing grows out of anything.
2. **One surface archetype.** Card inside panel, everywhere. The references have strips, plates, slivers, islands,
   readouts and full-bleed stages. They choose one per job.
3. **Flat type.** A 1.8× ramp cannot make a focal point; the references span 2.5–5× and give display, language and
   data their own faces.
4. **Motion without physics.** Tweens restart at zero velocity, curves are chosen per call site, and growth and
   shrink behave the same. The references measure as fast arrival with a sub-perceptual settle, asymmetric
   grow/shrink, and one object carried through a change.
5. **Accent without a budget.** When the accent fills tiles, titles and clocks at once, nothing is emphasised.
6. **Blind to the wallpaper's content.** The palette follows the wallpaper; the composition does not.
7. **No signature.** Nothing in a two-second clip says "Zynith".

The fifth-batch Control Center proved the point: it changed sizes, weights and tints inside the same structure, and
I switched it back.
