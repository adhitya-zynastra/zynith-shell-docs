# Responsive Layout

**Written:** 2026‑09‑25. **Code:** `src/ui/responsive.h`, `src/ui/controls/carousel_geometry.h`.
**Test:** `tests/responsive_layout_test.cpp`.

Until this batch every Zynith surface was tuned on one display — this laptop's 1920×1200 panel at scale 1 — and
most sizes were either fixed or a fixed fraction of the output. That works on the display it was tuned on. On a
wider display a fraction-of-width card simply gets bigger rather than the layout showing more; on a small one a
fixed size spills off the edge.

This page describes the smallest set of rules I had Claude add so that components size themselves from the space
they actually get.

## Units

- **Logical pixels.** Wayland hands the shell logical sizes, so the output's **scale factor is already applied**:
  a 2560×1600 panel at scale 1.25 is a 2048×1280 logical output, and is laid out exactly as a 2048×1280 one.
- **UI scale** (`contentScale()`) is the shell's own accessibility scale. It multiplies a component's
  *preferences*, never the space available.

## The primitive (`ui::responsive`)

Three functions, all `constexpr`, no configuration dependency, no state:

| Function | Meaning |
|---|---|
| `resolve(Extent{min, preferred, max}, available, uiScale, maxFraction)` | The preference × UI scale, clamped to [min, max] × UI scale, then capped at `maxFraction` of the available space and at the available space itself. Never below 1. |
| `fitCount(available, item, gap, minCount, maxCount)` | How many items of a width, with gaps, fit; bounded. A negative gap counts as zero, so it cannot divide by zero. |
| `space(base, densityFactor, uiScale)` | A spacing token at a density and UI scale. |

The minimum **yields** to the available space: a display too small for the minimum gets a smaller component, not
one that overflows. That was a deliberate choice over the alternative (honour the minimum and clip).

**Density** is a shared enum, `LayoutDensity { Compact, Comfortable, Spacious }` → factor 0.75 / 1.0 / 1.35
(`layoutDensityFactor`). Comfortable is 1.0, so the default reproduces the previous spacing exactly. It is used by
the Control Center today; any surface can adopt it by adding its own `density` key.

### What it is not

No layout engine, no constraint solver, no breakpoints, and nothing per frame. Callers resolve these values when
their available size or configuration changes — `doLayout` — and use the result like any other layout value.
Output geometry (width, height, scale) is not a separate primitive: the shell already receives it as the surface's
logical size.

## First consumer: the wallpaper carousel

Before this batch the focused card was **a fixed fraction (40 %) of the band width**, and the number of visible
neighbours was derived from the geometry — but because the card grew with the band, the geometry always resolved
the same way. Every display showed **five cards**, just larger.

Now:

1. The focused card width is `resolve({320, carousel_card_width, 1400}, band, uiScale, 0.40)`, with
   `[wallpaper].carousel_card_width` defaulting to 760. The 0.40 cap is the old fraction, so on any band up to the
   laptop's the card is exactly what it used to be; at 1920 the 760 default sits just under the 761.6 px cap. The
   focused image frame is 752 px, still under the 768 px display tier (no upscaling).
2. The arc (`ui::carousel::fitArc`) keeps a fixed total angle of 63° per side, spread over N + 1 steps, with the
   orbit radius chosen so travel at the focus is one stride. It picks the **largest N** (≤ 6) for which every card
   on a side is legible (drawn scale ≥ 0.42) **and shows at least 20 % of its drawn width past the card in front
   of it**, inside the viewport. Nearer cards paint over farther ones, so a card that merely touches the screen
   edge is not a visible card.
3. Depth, scale, opacity and sink are normalised over the arc angle, not over a card count, so the far-edge card
   looks the same whether there are two or six per side.

At N = 2 the step is 63°/3 = **21°**, exactly the old constant — the laptop's composition is unchanged. Its outer
pair shows about 25 % past the inner cards, which is what the 20 % threshold is calibrated against.

**How it got here.** The first version counted a card as soon as any of it was on screen and capped the card at
46 % of the band. The unit test passed; the screen did not. At logical 2560 it counted 7 cards, but the third pair
showed only ~22 px past their neighbours, and at logical 1536 the outer pair disappeared entirely, leaving 3. The
occlusion criterion and the 40 % cap replaced both before commit. Runtime evidence is in the
[validation record](../../03_Performance/benchmarks/tracks-wallpaper-layout-cc.md).

### Resolved geometry

Computed by compiling the shipped headers against each output (band = logical width − the panel's 2 × 8 px side
margins). Rows marked *seen* were also observed on this laptop's panel by changing niri's output scale; the rest
are **computed, not observed**.

| Output | Logical width | Card | Per side | Visible | Step | |
|---|---|---|---|---|---|---|
| 1366×768 @1 | 1366 | 540 px | 2 | 5 | 21.0° | |
| 1920×1200 @1.25 | 1536 | 608 px | 2 | 5 | 21.0° | seen |
| **1920×1200 @1 (this laptop)** | **1920** | **760 px** | **2** | **5** | **21.0°** | seen |
| 2560×1600 @1.25 | 2048 | 760 px | 2 | 5 | 21.0° | |
| 2560×1440 @1, 3840×2160 @1.5 | 2560 | 760 px | 2 | 5 | 21.0° | seen (as the laptop at scale 0.75) |
| (laptop at scale 0.6) | 3200 | 760 px | 3 | 7 | 15.75° | seen |
| 3440×1440 @1 | 3440 | 760 px | 3 | 7 | 15.75° | |
| 3840×2160 @1 | 3840 | 760 px | 4 | 9 | 12.6° | |
| 5120×1440 @1 | 5120 | 760 px | 5 | 11 | 10.5° | |
| 1920×1200 @1, UI scale 1.25 | 1920 | 762 px | 2 | 5 | 21.0° | |

The count steps up at logical **2720** (3 per side), **3560** (4), **4392** (5) and **5224** (6) — roughly every
two strides of width, because each new pair has to clear the pair in front of it. Between steps, extra width shows
more of the existing outer pair (at 2560 it is about 69 % exposed instead of 25 %). A narrower display shrinks the
card and keeps the composition. A larger `carousel_card_width` means fewer neighbours on the same display. The view
additionally shrinks the card to fit its own body height on a short display.

### Cost

`fitArc` runs at most 21 iterations of a few trigonometric calls (each candidate N re-checks its whole side),
once per layout (open, resize, configuration change). Nothing about it runs per frame. The pool of card nodes is sized for the ceiling
(`kMaxPoolSize = 2 × (kMaxPerSide + 4) + 1`).

The ceiling of six per side also bounds the resource side: the promotion window (focus − 1 … focus + 3) and the
preview tier are unchanged, so a wider display draws more cards from textures the session already holds rather
than decoding more.

## Second consumer: Control Center density

`[control_center].density` scales the Control Center's **frame rhythm** — the gap between navigation and
content, the navigation's padding and the gap inside the content column — through `space()`. Each tab's internal
spacing is its own and is not touched. The panel's width was already clamped to the output by `PanelManager`.

## Window move and resize

Not part of the primitive, but part of the same track: niri's native pointer gestures are used as-is.

| Gesture | Action |
|---|---|
| `Mod` + left-drag | interactive move (right-click while moving toggles floating/tiling) |
| `Mod` + right-drag | interactive resize |
| `Mod` + middle-drag | view movement / workspace switch |

`Mod` is `Super`, now stated explicitly in `config.kdl` as `input { mod-key "Super" }`. Binding
`Mod+MouseLeft` or `Mod+MouseRight` would override the gestures; none exist in any included file. Nothing in the
shell emulates or intercepts these — niri handles them before a client sees the pointer. See
[`niri.md`](../../06_Reference/configuration/niri.md).

## Known limitations

- Only two consumers so far. The launcher, OSD and notifications still use their own fixed sizes; they are due to
  be redesigned and should adopt `resolve()` then rather than be retrofitted now.
- Seen on hardware: logical 1536, 1920, 2560 and 3200, all on this laptop's panel via niri's output scale.
  Everything else in the table is computed.
- The 0.40 band cap, the 20 % exposure threshold and the legibility threshold are tuned by eye on this display.
- The display-tier set grows with the arc: since `679c0c1` every visible card is promoted (plus one lead), so a
  9-card arc holds 10 display-tier textures instead of the laptop's 6. Before that change, cards behind the
  direction of travel drew from the 384 px preview — up to ~1.6× upscaled on a 9-card arc.
