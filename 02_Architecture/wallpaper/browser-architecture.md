# Wallpaper Browser Architecture

Current as of `57debbc`. The browser is the most heavily engineered subsystem in Zynith because it is the one that
combines a large on-disk collection, GPU textures, rapid input, and a palette transition that re-tints the shell.

## How the resource model got here

The current design is the third one, and the two I discarded explain it better than the final version does on its
own.

I started from a **bounded viewport working set**, because the rule I had set for the whole project was that
nothing holds resources it is not using. That model is correct on paper and it measured well. It was also wrong:
once I started sweeping the collection at the speed I actually wanted to browse at, previews could not be prepared
fast enough, and the browser showed me loading placeholders instead of wallpapers. The memory number was
excellent and the feature did not work.

So I changed the policy: the browser now **eagerly prepares the whole collection at the 384 px preview tier for
the lifetime of the browsing session**, and releases all of it on close. That fixed the traversal gaps and
introduced the next problem — every card, including the one I was looking at, was now being drawn from a preview
that is smaller than the frame it fills. That is the
[quality regression](../../04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md), and the fix for
it is the promoted display tier described below.

What survived all three designs is the boundary, not the policy: resources are scoped to the browsing session and
nothing leaks past close. What changed is that I stopped treating peak memory as the thing being optimised and
started treating it as a budget the feature has to fit inside.

## Surfaces

Carousel mode (`[wallpaper] carousel = true` in `rice.toml`) splits the browser into two regions on **one**
layer-shell surface:

```
 ┌─ output (1920×1200) ───────────────────────────────────────────────────────┐
 │  ┌──────────── compact control card (1000 px wide, centred) ───────────┐   │
 │  │ title · filter · Built-In/Wallpaper/Community · palette · ★ · flatten│   │
 │  └──────────────────────────────────────────────────────────────────────┘   │
 │                              (deliberate gap)                               │
 │        ◀─────────────── full-width carousel band ───────────────▶           │
 │            card      card        FOCUSED CARD        card      card         │
 │              ╲         ╲             ▲                ╱         ╱           │
 │               ╲─────────╲────────────┴───────────────╱─────────╱            │
 └─────────────────────────────────────────────────────────────────────────────┘
```

The surface is floating, `fillsWidth`/`fillsHeight`, and **undecorated** (`hasDecoration() == false`), so only the
control card reads as a panel. The desktop behind is dimmed by a **live** tint veil, never a screencopy — see
"Live backdrop" below.

## Geometry: one orbit, not per-card placement

`src/ui/controls/carousel_view.cpp`. A single logical coordinate drives everything:

```
 u = index − focusPosition            (signed distance from the focus, in items)
 θ = u · kAngleStepRad                (21° per item)
 x = cx + Rx·sin θ                    Rx = stride / kAngleStepRad  → spacing at the focus
 depth = (1 − cos θ) / (1 − cos θmax) equals the scroll axis exactly
 y = apex + sink · depth^0.55
 scale   = 1 − (1 − 0.52)·depth^0.6
 opacity = 1 − (1 − 0.26)·depth
 z       = (1 − depth) · 1000
```

Consequences worth knowing:

- **The scroll axis stays linear** (`offset = index × stride`); the curve is applied only when drawing. That is why
  one wheel detent is exactly one item.
- **Visible card count is derived, not fixed**: the layout walks outward until a card would be illegible
  (< 0.42 drawn scale) or fully outside the viewport, capped at 3 per side. On this display that resolves to
  **5 cards**.

> **Amendment, 2026‑09‑25 (three-track batch 2).** The count was derived, but because the card was 40 % of the
> band and the stride a fixed ratio of the card, the geometry was scale-invariant: every display resolved to the
> same 5 cards, only larger. The card is now sized from a preference (`[wallpaper].carousel_card_width`, 760) and
> only *bounded* by the band (at the old 40 %), and the 21° step is replaced by a fixed 63° arc spread over as many
> cards as the band carries (at most 6 per side). A card now counts as visible only if a fifth of it shows past the
> card in front — the old "partly on screen" test ignored occlusion. The laptop still resolves to 5 cards at exactly
> 21°; logical 3200 was seen to resolve to 7; 3440 computes to 7 and 3840 to 9. Details and the full table:
> [`responsive-layout.md`](../layout/responsive-layout.md). The `θ = u · kAngleStepRad` line above now reads
> `θ = u · angleStep`, with `angleStep` resolved per layout, and the card pool grew from 16 to 21 slots.
- **Hit-testing walks the drawn rects front-to-back** (`m_slotGeometry`, nearest depth wins), so overlapping cards
  resolve exactly as painted.
- **The hit-test overlay sits above the cards** (`kOverlayZIndex = 5000` vs card z ≤ 1000). It has to:
  `WallpaperTile` is itself an `InputArea`, so a card above the overlay silently swallows presses — that was a real
  bug (`04_Incidents/`).

## Resource pipeline

```
 collection (WallpaperScanner, background thread, dir-mtime cache)
        │
        ├─ on open: beginSession() ─ prefetch EVERY entry at 384 px (preview tier)
        │                            ordered outward from the focused item
        │
        ├─ promotion window: every visible card + 1 lead in the direction of travel
        │                    (focus−1 … focus+3 until 679c0c1), prefetched at 768 px (display tier)
        │
        ├─ tile holds BOTH tiers; draws the promoted texture if decoded, else the preview
        │                    → a card never blanks, and never shows a spinner mid-flick
        │
        └─ on close: endSession() ─ drops only the entries THIS session parked
                                    (other surfaces' idle entries keep their own tag)
```

### Why two tiers

The focused card's image frame is **753.6 px** wide. A 384 px preview stretched to that is a 1.96× upscale — about
3.5× less detail by Laplacian standard deviation (1681 vs 5939 on an identical crop). A single tier cannot serve
both "hold the whole collection" and "the focused wallpaper must be trustworthy to evaluate".
Measured at `57debbc`: `frameW = 753.6, texW = 768` — no perceptible upscaling.

### The decode gate

`ThumbnailService::pauseDecodes()/resumeDecodes()`. While the carousel is moving, a cache *miss* records intent
instead of queueing work; reopening the gate queues only what is **still held**. A fling therefore decodes what it
lands on rather than everything it flew past — measured 54.4 % → 3.96 % CPU during movement.

The gate opens when the **settle begins**, not when it ends: the landing item is already known then, so the
display-quality decode overlaps the settle animation instead of starting after it.

### Session ownership

`beginSession()` raises the idle budget (128 MB / 512 entries) and tags every entry acquired during the session.
`endSession()` evicts only entries carrying that tag. Entries another surface parked (control center, file dialogs)
keep their own tag and survive; referenced entries are not idle at all. **The desktop wallpaper is never at risk —
it lives in `SharedTextureCache`, a different cache entirely.**

### Lifecycle, re-verified 2026‑09‑25

The responsive change added cards on wide outputs but no new resource path, so I had Claude re-run the lifecycle on
the final build rather than redesign anything. One browsing session over 168 wallpapers, about 120 traversal steps
at 25–28 per second by wheel and keyboard, one neighbour click and one apply: **181 decodes** (168 previews + 13
display-tier), 336 cache hits, **0 evictions**, peak idle 64.7 MB; RSS 175.7 MiB before open, 194.7 MiB just after
open, 177.8 MiB 3 s and 8 s after close; threads constant at 34. Full conditions in the
[validation record](../../03_Performance/benchmarks/tracks-wallpaper-layout-cc.md).

> **Amendment (`679c0c1`).** The decode counter over-counted in-flight duplicates, so "181" above is an upper
> bound. Two changes followed. The promotion window is now derived from the arc — every visible card plus one lead
> card in the direction of travel — rather than fixed at −1 … +3, so no visible card is drawn from the 384 px
> preview. And promotion waits for the real initial focus; a provisional focus on entry 0 used to decode entries 0–3
> at 768 px on every open. **Trade-off:** the display-tier set now grows with the output — 6 textures on this
> laptop, at most 14 on the widest arc (~1.4 MiB each at 768 × 480), inside the session's 128 MB idle budget, and
> still decoded only when motion settles. A plain open/close is now exactly 174 decodes: 168 previews + 6.

## Focus ≠ apply

A standing, tested invariant:

| Action | Result |
|---|---|
| Scrolling, arrow keys, clicking a **neighbour** | focus only |
| `Enter`, or clicking the **already-focused** card | apply, via the unchanged `applyWallpaperFromEntry()` |

Re-activating the same wallpaper within 600 ms is treated as one gesture, so a double-click does not run palette
extraction and a wallpaper transition twice. Re-verified on the final build: a double-click 120 ms apart logged one
`applied wallpaper` and one `ignoring repeat apply … within the double-click guard`.

## Live backdrop

The browser uses `Panel::ModalBackdropMode::Live` → `ScreenVeil::showTint()`: a tint-only veil with **no image
node**. The previous `Snapshot` mode blurred one screencopy, which froze the desktop — applying a wallpaper changed
nothing on screen until the browser closed. Measured cost of the two modes was 210 vs 202 ms CPU per open+close, so
this is a correctness fix, not a performance one.
