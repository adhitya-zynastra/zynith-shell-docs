# ADR-0010 — Session-scoped wallpaper resources with two quality tiers

**Status:** Accepted · **Date:** 2026‑09‑21 (Phase 6, `eaff2b2` + `57debbc`)

## Context
The browser must let a user sweep a large collection at 20+ items/second *and* judge a wallpaper's real quality,
without a permanent cache or unbounded memory growth. Three designs were tried in sequence.

## Decision
1. **Session scope.** A `ThumbnailService` session opens with the browser and closes with it. Entries acquired
   during a session are tagged; `endSession()` evicts only that session's idle entries.
2. **Two tiers.** Every entry is prefetched at **384 px** (preview) when the browser opens; a **768 px** display
   tier is held for a window around the focus (`focus−1 … focus+3`) that leans in the direction of travel.
3. **Both tiers held simultaneously** per tile — the preview draws until the promoted texture exists.
4. **Decode gate** during motion, opened when the settle *begins*.

## Alternatives
- *Lazy per-viewport loading* (the first design) — rejected: visible loading gaps during fast scrolling.
- *One tier at display resolution for everything* — rejected: ~1.5 MB × collection is unaffordable.
- *Decode every source at native resolution* — rejected outright; catastrophic for large repositories.
- *Permanent global cache* — rejected: violates the bounded-resource rule and leaks across sessions.

## Consequences
- Rapid traversal costs a constant ~18 decodes regardless of distance travelled.
- 132 previews cost ≈3 MB RSS (textures live on the GPU; 53 MB of texture bytes at peak).
- Re-opening the browser re-decodes its landing set, by design, because close releases everything.
- Ownership must stay explicit: the desktop wallpaper lives in `SharedTextureCache` and is never touched.
