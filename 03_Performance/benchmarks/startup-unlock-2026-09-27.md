# Startup grey interval and unlock reveal (2026‑09‑27)

Branch `feature/live-wallpaper`: `4f4169c` (startup), `651d7b1` (unlock). All measurements taken by Claude; the
lock/unlock samples needed my password, so I entered it at each prompt. Machine: Fedora 44, niri 26.04, Intel Arc
iGPU, eDP-1 1920×1200 @ 60 Hz. Screen-side values come from a 48×48 crop sampled with `grim` every ~17 ms (hashed
and averaged in memory, never stored); niri refuses screencopy while the session is locked (0 samples while
locked — VERIFIED), so the lock screen itself is never captured.

## Where the login grey came from (real login, 2026-09-27 00:44, VERIFIED from journal + shell log)

| t (s) | event |
|---|---|
| 10.022 | PAM authentication success (gdm-password) |
| 10.458 | session opened; user manager up |
| 11.082 | niri.service starting |
| 11.35 → 11.94 | niri GPU/modeset init; greeter still on screen |
| 11.975 | niri output eDP-1 up — **niri's default grey background from here** |
| 12.056 | niri ready, spawns the shell |
| 12.424 | shell `run()` (≈370 ms exec + constructor) |
| 12.424 → 13.003 | `initServices` 579 ms — blocking D-Bus round-trips (NetworkManager secret agent ≈280 ms, BlueZ, UPower…) |
| 13.003 → 13.327 | `initUi` 324 ms; wallpaper surface created at 13.325, then `transition_on_startup` (900 ms) |

So ~1.4 s of grey came from the wallpaper waiting behind ~900 ms of service setup it does not need. niri has no
`layout { background-color }` set, hence grey.

## Fix and measurement

`Application::paintEarlyBackground()` creates backdrop + wallpaper right after GL init and presents the first frame
with a bounded local event pump, before the services; niri's `DoScreenTransition` crossfades to it (the shell's own
startup transition would stall behind the blocked main loop and then jump).

Shell restart benchmark (`startbench.py`, 5 rounds each, quiet CPU, load1 ≈ 1–1.9; the grey between two shells is
the same compositor state the login shows):

| | grey interval ms | wallpaper visible after spawn ms | run() reached ms |
|---|---|---|---|
| before (1ba8cec build) | 1045 / 1055 / 1086 mean / 1192 (min/med/mean/max) | 1033 / 1040 / 1068 / 1171 | 142–243 (first log) |
| after (4f4169c) | **463 / 506 / 495 mean / 527** | **430 / 489 / 473 / 506** | 126–205 |

Early background presented 218 ms after it started (backdrop blur + 4K texture). What remains is process
start → `run()` (126–205 ms: dynamic loading of 124 libraries is 40–50 ms warm; the rest is the `Application`
constructor — not profiled further, **UNKNOWN** breakdown) plus Wayland/GL setup (~120 ms).

**Not measured:** the real login after the change. That needs a logout/login, which I did not do during this
session; the next login's journal + shell log (`startup: run() reached …`, `startup: early background presented …`)
will give it. The greeter → niri hand-off (10.0 → 11.97 s) is outside the shell and unchanged.

## Unlock reveal

Root cause found by measurement, not by reading: the unlock veil is a `WallpaperNode` (blurred wallpaper) under a
tint, and `RenderContext` never passed node opacity to wallpaper draws. Fading the veil faded only its tint; the
image stayed opaque until the veil was destroyed, then the desktop appeared in one step. The old 210 ms ease-out
fade, clocked from `unlock()` before niri presented anything, hid part of this.

| sample | reveal curve (after `session unlock requested`) | largest single-sample jump |
|---|---|---|
| before (old binary) | 18 % at +60 ms, 45 % at +81, 73 % at +120, 100 % ≈ +270 | front-loaded (crop partly over a desktop widget) |
| intermediate 1 (curve + present-sync only) | fade never started — `requestRedraw()` skips `prepareFrame()`; veil held 2 s then removed | — (discarded, fixed) |
| intermediate 2 (+ `requestUpdate`) | smooth to 50 % at +596 ms, then **+50 % jump** at veil destruction | 49.8 % |
| intermediate 3 (+ zero-frame confirm) | same plateau — veil rendered 34 frames to opacity 0, screen still at 50 % → image ignores opacity | 49.8 % |
| **final** (`651d7b1`, wallpaper opacity honoured) | 2 % +164, 12 % +258, 51 % +387, 84 % +487, 97 % +621, 100 % +664 | **10.9 %** |

Final timeline: authenticated → `session unlock requested` 475 ms (lock UI exit animation, unchanged); veil fade
starts 21 ms later on its first presented frame; 30 frames over 669 ms; removed after a presented zero-opacity
frame. Windows and the workspace are never recreated: the session lock is an overlay; niri keeps the workspace;
only the veil changes.

Other observation: the audio visualizer desktop widget reappears ~1.6 s after unlock (`spectrum active` → `ring
buffer primed` 1.4 s). It is live content, not part of the reveal; left as a known late element.

## Tests performed

Wrong password then correct password (twice, VERIFIED: failure path unchanged, unlock proceeds); four
lock → unlock cycles with a live wallpaper running (exactly one renderer throughout, none restarted); shell restarts
only while unlocked. **Not tested:** suspend/resume and lid close with the new build; rapid lock/unlock cycling
(deliberately not automated — lockout policy).
