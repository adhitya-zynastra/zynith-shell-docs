# Postmortem — Focused wallpaper rendered below source quality

| | |
|---|---|
| **Severity** | Medium — functional correctness of the browser (users judge wallpapers by what it shows) |
| **Reported** | 2026‑09‑21, by me, while browsing wallpapers |
| **Fixed in** | `57debbc` |

## What I observed

Some wallpapers looked visibly soft **while focused** — which is precisely the state in which I decide whether I
want one. My framing when I reported it matters more than the symptom: a browser that shows a degraded
representation will make me reject a good wallpaper for the browser's fault. A blurry browser is *functionally
incorrect* even when its memory usage is excellent, and I did not want it treated as a cosmetic complaint.

## What I initially suspected

Nothing specific, and I said so — but I did say what I did not want: I did not want the thumbnail size increased
until someone understood the pipeline. The resource model had been carefully bounded two commits earlier, and
raising a constant to make the symptom go away would have quietly undone that work without anyone knowing which
part of it was actually wrong.

## What Claude investigated

Arithmetic first, then instrumentation: what size the focused card actually draws at, what size texture it was
actually holding, and where in the promotion path the two diverged.

## What the evidence showed

The focused card's image frame is **753.6 px** wide (`cellW 761.6` minus padding). The eager-loading work had made
every card use a **384 px** preview, with only the *selected* card promoting to 768 px — and only after motion had
settled, because the decode gate defers decodes while the carousel moves.

Objective anchors for a 753 px render of a known 1800×1261 source, measured with a Laplacian standard-deviation
focus metric on identical crops:

| representation | Laplacian SD |
|---|---|
| from the 384 px tier (what was shown) | 1 681 |
| from the 768 px tier | 5 939 |
| direct from source | 6 360 |

So the preview tier carried ~3.5× less detail than the display tier — a 1.96× upscale. Neighbour cards were also
affected: they draw at ~640 px (u=1) and ~480 px (u=2), both above 384.

Temporary instrumentation confirmed the pipeline end-to-end before it was removed:

```
zdbg tile focused promoted=true heldPx=768 browsePx=384 usedPromoted=true frameW=753.6 texW=768
```

## Root cause and contributing design flaw

Promotion *replaced* the texture: the tile released the 384 px entry and acquired 768 px. During a flick each newly
focused card therefore had **no** texture and fell back to a loading placeholder — a wall of hourglasses at 66
items/second.

## Fix

1. A tile **holds both tiers** and draws the promoted one only once it is genuinely decoded, so a card never blanks.
2. Promotion follows a **window** around the focus (`focus−1 … focus+3`) that **leans in the direction of travel**
   and reverses when the user reverses; its members are prefetched predictively.
3. The decode gate now opens when the **settle begins** rather than when it ends — the landing item is already
   known then, so the display-quality decode overlaps the settle animation.
4. A window change forces the bound tiles to re-evaluate (they cache their promotion state).

## Verification

- `frameW = 753.6` against `texW = 768` — no perceptible upscaling
- warm cache: the sharp frame appears **in the same frame the settle completes** (1 ms); cold first fling ~300 ms
- mid-flick at 66 items/s: every card populated, no placeholders
- session counters: 146 decodes, 96 cache hits, 0 evictions, peak idle 53 MB
- memory: 159.8 MB before → 163.2 MB after preparing 132 previews → 165.7 MB after close

## Engineering lesson

Two things came out of this that outlived the bug itself.

**"Bounded resources" is a means, not an end.** The eager-loading design was measured, disciplined and
memory-efficient, and it was still wrong, because it optimised the number I was tracking instead of the thing the
browser is for. The fix kept the resource discipline — the session still releases everything on close, and peak
idle stayed at 53 MB — while moving the quality decision to where the user actually looks.

**A metric you have not validated can be more damaging than no metric.** The invalid comparison below briefly
convinced us the fix had failed, and had it been trusted it would have sent the work off to change things that
were already correct.

## Note on an invalid metric

An early comparison put the rendered card at 3 242 against 6 398 for the reference and suggested the fix had not
worked. That comparison was **invalid**: the reference chain used ImageMagick's Lanczos resampling while the shell
uses GPU bilinear filtering, and the crops were not aligned. The instrumented `texW` value is the authoritative
evidence. Recorded here because the wrong number was briefly believed.
