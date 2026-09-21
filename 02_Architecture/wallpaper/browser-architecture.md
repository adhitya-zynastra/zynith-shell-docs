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
        ├─ promotion window: focus−1 … focus+3, leaning in the direction of travel
        │                    prefetched at 768 px (display tier)
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

## Focus ≠ apply

A standing, tested invariant:

| Action | Result |
|---|---|
| Scrolling, arrow keys, clicking a **neighbour** | focus only |
| `Enter`, or clicking the **already-focused** card | apply, via the unchanged `applyWallpaperFromEntry()` |

Re-activating the same wallpaper within 600 ms is treated as one gesture, so a double-click does not run palette
extraction and a wallpaper transition twice.

## Live backdrop

The browser uses `Panel::ModalBackdropMode::Live` → `ScreenVeil::showTint()`: a tint-only veil with **no image
node**. The previous `Snapshot` mode blurred one screencopy, which froze the desktop — applying a wallpaper changed
nothing on screen until the browser closed. Measured cost of the two modes was 210 vs 202 ms CPU per open+close, so
this is a correctness fix, not a performance one.
