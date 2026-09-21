# Optimization Log

Chronological. Each entry states what was changed, why, what it cost, and — where the answer was "nothing" —
says so. I have kept the failures in the same list as the successes deliberately: O‑05 measured within noise and
is recorded as a correctness fix rather than a performance one, and the bar's 1 Hz update was reverted after
measurement rather than written up as a win. A log that only contains wins is a marketing document.
Source data: `benchmarks/optimizations.csv`.

## O‑01 · OSD hold moved off the frame clock (Phase 4, `40c1936`)
The 1.4 s on-screen hold was an `animateTimer` — an animation whose only purpose was to wait, which keeps the frame
clock alive. Replaced with a one-shot `TimerManager::Timer`. **~50–80 wakeups/s removed** while a static OSD was
visible. *Provenance: RECOVERED from the session record and the patch README; not re-measured on a clean build.*

## O‑02 · Thumbnail idle set (Phase 6, `46296d0`)
`ThumbnailService::release()` destroyed a texture the moment its last owner let go, so scrolling back over content
just visited re-decoded it. Added a bounded LRU of zero-owner entries.
**20 forward + 20 back: 36 → 23 decodes** (the return sweep fell from 20 to 3). Counts are build-independent.

## O‑03 · Decode gate during motion (Phase 6, `46296d0`)
Full-size previews made a fling a decode storm. While the carousel moves, a cache *miss* records intent instead of
queueing; reopening the gate queues only what is still held.
**Movement CPU 54.4 % → 3.96 % of a core**, and a ~248 MB transient disappeared.

## O‑04 · Panel retarget instead of rebuild (Phase 6, `e9e27b0`)
`openPanel()` destroyed and rebuilt an already-open panel, so navigating the Control Center from a bar widget
replayed the whole opening animation and re-initialised every tab.
**96.7 → 58.3 ms CPU and 643 → 398 context switches per navigation**, plus the visual fix.

## O‑05 · Live backdrop instead of a screencopy (Phase 6, `e9e27b0`)
Measured **210 vs 202 ms** CPU per browser open+close — *within noise*. Recorded as a **correctness** fix, not a
performance one. Kept here because the temptation to claim a win was real.

## O‑06 · Allocation-free dispatch (Phase 6, `eaff2b2`)
The first lifetime fix copied a `std::function` per callback per dispatch. Stable storage (`std::deque`) plus dead
flags gave the same guarantees with no allocation. *No isolated before/after CPU figure exists: the attempted
measurement was contaminated by an incremental build (see `benchmarks/contaminated-measurements.md`). The
justification is structural — an allocation per callback in a signal that fires every animation frame.*

## O‑07 · Plugin registry rescans (Phase 6, `eaff2b2`)
`applyPluginSourcesToRegistry()` ended in an unconditional `registry.scan()` and runs on **every** config apply, so
one wallpaper apply re-walked the plugin directories and re-parsed every manifest three times.
**6 manifest loads per apply → 0.** Direct cost was only ~5 ms; the win is allocations, I/O and log noise.

## O‑08 · Eager previews with a promoted tier (Phase 6, `57debbc`)
Lazy loading caused visible gaps at speed; a single high tier was unaffordable. Two tiers plus prediction:
**traversing 20, 50 or 100 wallpapers each costs 18 decodes**, 132 previews cost ~3 MB RSS, and the focused card
renders at 768 px into a 753.6 px frame.

## O‑09 · Identical post-hooks run once per apply (Phase 6, `3f355c5`)
The builtin `gtk3` and `gtk4` templates carry the *same* `post_hook` — both invoke
`assets/templates/gtk/apply.sh`, which rewrites both `gtk.css` files in one run (which is also why they are
pinned `hook_async = false`). Running it per template meant executing the identical script twice per palette
change, each run spawning a subprocess tree. `processConfigTemplates` now keeps a per-pass set of *rendered* hook
commands and skips a repeat.
**Process forks per palette change 2695 → ~2180 (−19%)**, three runs at 2226 / 2119 / 2199. Counts are
build-independent, so the comparison holds.
**Re-measured on a clean build (`ccfe125`, 986 targets): 2200 / 2170 / 2217 forks per apply — the −18 % holds.**
*CPU is still not quoted. The before (165 ms) and after (240–320 ms) were taken under different desktop
conditions — audio was playing during the second set, so the bar's CAVA visualiser was animating — and I did not
control for it. Recorded as UNCONTROLLED; see `baselines/idle-conditions.md`.*
This is the redundant half only; the dominant cost is the 11-of-21 enabled templates targeting absent software,
which is user configuration. See `04_Incidents/postmortems/2026-09-21-template-fork-storm.md`.

## Rejected after measurement

| Idea | Measurement | Verdict |
|---|---|---|
| Remove the bar's once-per-second update | Idle CPU unchanged (1.10 % vs 1.00 %, within noise) | Reverted — it was not the cost |
| Dirty-gate the shared layout pass | Layout of a small tree twice a second is microseconds | Not attempted; risk outweighed benefit |
| Lower the session idle budget to shrink RSS | Peak idle never reached the ceiling anyway | Ceiling kept as headroom; documented as unexercised |
