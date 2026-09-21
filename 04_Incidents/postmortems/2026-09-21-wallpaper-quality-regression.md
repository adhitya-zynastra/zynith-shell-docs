# Postmortem — Focused wallpaper rendered below source quality

| | |
|---|---|
| **Severity** | Medium — functional correctness of the browser (users judge wallpapers by what it shows) |
| **Reported** | 2026‑09‑21 by the project owner |
| **Fixed in** | `57debbc` |

## Symptom

Some wallpapers appeared visibly soft **while focused** — the state in which the user evaluates them. The owner's
framing was the important part: a browser that shows a degraded representation can cause a good wallpaper to be
rejected for the browser's fault.

## Diagnosis (arithmetic first, then instrumentation)

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

## Contributing design flaw

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

## Note on an invalid metric

An early comparison put the rendered card at 3 242 against 6 398 for the reference and suggested the fix had not
worked. That comparison was **invalid**: the reference chain used ImageMagick's Lanczos resampling while the shell
uses GPU bilinear filtering, and the crops were not aligned. The instrumented `texW` value is the authoritative
evidence. Recorded here because the wrong number was briefly believed.
