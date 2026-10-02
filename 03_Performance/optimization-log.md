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

## O‑10 · The Zynith UI stops following every access point (`feature/zynith-ui` `b136894`)
The prototype's Wi‑Fi icon read Quickshell's `Networking` module, which follows every access point
NetworkManager knows. On this campus that is 40 of them (4 distinct names, 30 hidden), each updating its strength
on every background scan. Claude found it by bisecting the idle prototype service by service, each one alone in
its own instance for 15 s: `Network` alone cost **68 wakeups/s and ≈ 0.4 % of a core**, and every other service
cost 0–1 wakeups/s.
The fix is a native `NetworkState` that follows NetworkManager's own object and the access point in use. The
list of nearby networks, and the signals behind it, exists only while the Wi‑Fi panel holds it.
- **`Network` alone: 68 → 0 wakeups/s.**
- **Whole prototype idle (Performance profile, 60 s): 0.23 % → 0.03 % of a core, 7–9 → 2 wakeups/s.**

Decision record: [ADR‑0020](../05_Decisions/ADRs/ADR-0020-measure-builtins-before-adopting.md).
*Conditions: TuneD `powersave`; three audio streams uncorked; the native shell running beside it.*

## O‑11 · The Zynith UI calls the shell's socket instead of `noctalia msg` (`feature/zynith-ui` `7061d00`)
Clipboard, Quick Settings and the Wallpaper panel asked the native shell for data by running `noctalia msg …`.
Each such process starts the whole 34 MB shell binary only to forward one line to the shell's socket. Claude timed
20 calls of `status` each way:

- through the CLI: **1.22 s wall, 1.19 s CPU (≈ 60 ms per call)**;
- straight to the socket: **0.009 s wall, 0.003 s CPU (≈ 0.15 ms per call)**.

Opening the Wallpaper panel made three such calls, so it had cost ≈ 180 ms of CPU before drawing anything. Zynith.Native's
`CoreClient` now speaks the socket's one-shot protocol: connect, write, half-close, read to EOF. Without the
half-close, the shell would wait out its 100 ms receive timeout on its own main loop. This stands in for the helper
protocol (Architecture 2.0 §4.2) until that exists.
*Conditions: TuneD `powersave`; shell `4f68939`-based build.*

## O‑12 · Nine-patch shadow instead of a blurred `MultiEffect`: no effect, reverted
The Stage 1 attribution runs had put the panel shadow at ≈ 14 ms per open + close. Claude replaced the
`MultiEffect` drop shadow with a pre-blurred nine-patch image, with no offscreen pass and no blur, and alternated the
two in place, three rounds each, under the same conditions (Balanced, TuneD `powersave`, music playing):

- effect: **328–332 ms** per cycle;
- image: **321–335 ms** per cycle.

That is no measurable difference, so the change was reverted rather than kept for its theory. The earlier 14 ms
had come from removing shadows altogether, which also removes their window padding, so it never showed that the
blur itself was the cost.

## O‑13 · Visualizer: per-frame work limited to each bar's level (`feature/zynith-ui` `dfdfb1d`)
Every bar's count, and with it its colour (a JS mix per bar), was bound to the spectrum's value list, so it was
recomputed on every frame. Counts and colours now follow the band count, which changes only with the profile.
**Main thread 194 → 185 ticks per 20 s** with music playing (Balanced). The remaining cost is the frame itself:
Qt's render-loop timing gives ≈ 2 ms per bar frame, most of it the buffer swap.

What music costs, measured in the same 20 s (Balanced, nothing open):

| | CPU |
|---|---|
| Zynith UI, whole process | **11.2 %** of a core (main thread ≈ 9 %, spectrum thread ≈ 0.7 %) |
| native shell, same music | **15.4 %** |

At 30 visualizer frames a second, ≈ 2 ms each is ≈ 6 % before any widget work. Performance turns the visualizer
off; the Balanced rate (30 fps) is unchanged and is a UX choice for me to make.
