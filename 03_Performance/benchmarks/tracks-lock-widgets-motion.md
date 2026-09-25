# Lock Screen, Widgets, Motion and Corrections — Validation Record

**Date:** 2026‑09‑25/26. **Implementation:** `e521a86`. **Binary tested:** a clean build (`meson compile --clean`,
1003 targets, zero failures). It showed 8 warnings: the known 6 libstdc++ ones plus 2 new `-Wshadow` warnings of my
own, fixed before commit. Then `.cpp`-only incremental rebuilds. The installed binary is the committed tree.

**Conditions I should state.** I was using the desktop during part of this run and, for a few minutes, testing the
same Control Center myself. Two panel opens in the log are mine, not the harness's; they are excluded below. One
synthetic click meant for the auto-hidden top bar landed in my browser. A lock screen editor capture showed a private
chat window instead of the editor; it was deleted unviewed beyond identifying what it was.

## Tests

| Suite | Result |
|---|---|
| Full suite | **124 / 125** — only `upower_charge_limit_integration` |
| `config_schema_roundtrip` | failed after `[bar].reference` was added (golden serialization drifted); golden updated — a new key, not a regression |
| `responsive_layout_test` | + anchored widget placement: free scales; right keeps 60 px from the right edge on 3440; top-left keeps its offset; bottom keeps 60 px from the bottom |
| `transient_ui_config_test` | + `[osd].reference`, `[control_center].anchor_bar`, bar/OSD default `workspace`; `key_hints` removed |

## Coordinate model and Control Center position

| Check | Result |
|---|---|
| Time bar, `reference = "output"` | spans x 880–1039, **centre 959.5** (was 980 on `workspace`) |
| Media and Time bars against a line at x = 960 | line passes through the middle of both |
| `panel-toggle control-center` over IPC (what `Shift+Super+E` runs), `anchor_bar = "Time"` | opens bottom-centre on the Time bar |
| CC open at the Time bar, then click Network on the left bar | the panel **moves to the left bar** on the Network section (log: opened, opened — rebuilt at the new bar, no close) |
| Hover-open from the Time bar's clock | centred on the bar (≈ x 630–1290) — after the fix below |
| Click on the Media bar | **not verified** — the bar was auto-hidden behind windows |

**Bug found from my report ("clicking the bottom or top bar doesn't open it centred").** With open-near-click on, an
attached panel is placed at the click, clamped to `[barLeft + inset, barRight − panelWidth − inset]`. A 780 px panel
on a 160 px bar makes that range empty, so the clamp pinned it to the bar's left edge. A panel that does not fit along
its bar is now centred on it.

**Bug found by the harness.** With the CC open at one bar, a click on another bar's widget retargeted the section in
place, leaving the panel on the first bar. Retarget-in-place now requires the same source bar.

## Audio

| Check | Result |
|---|---|
| `volume-mute` | 80 ms later: **not yet muted** (cue playing); 580 ms later: muted |
| Unmute | cue plays (existing `AudioOsd` path) |
| Mute then unmute 30 ms apart | ends **unmuted**; the pending mute was cancelled; one cue |
| 10 notifications, 60 ms apart, retrigger floor 110 ms | 1 stream start, 4 retriggers, 5 coalesced |
| Same, floor 150 ms (committed) | 1 start, 3 retriggers, 6 coalesced — one stream throughout |
| Stream start latency (debug log) | **first buffer 20 ms after `play()`** in all three samples |

The 20 ms says the "delayed" sounds were not stream start-up: they were plays dropped while an earlier chime was still
sounding (315 ms), so the chime a user heard often belonged to an older notification.

## Launcher, lock screen, widgets, motion

| Check | Result |
|---|---|
| Launcher (Zynith) | no footer strip, no scrollbar beside the results (`launcher-no-footer.png`) |
| Lock screen editor (`lockscreen-widgets-edit`) | its layer surface is created; the composition was **not** visually verified (the capture showed an application window) |
| Power-control arming | **not runtime-tested** — the editor disables widget input, and no real lock was run (standing rule) |
| Failed-auth shake | **not runtime-tested** — would need a real lock and a wrong password |
| CC morph | the indicator is drawn on the selected tab in every capture; mid-transition frames were **not** captured |
| `settings.toml` | unchanged by the checks (hash compared around the editor test) |

## Not verified

Media-bar click position; lock screen composition, arming and shake at runtime; CC morph frames; Glass tint on bars
and attached panels at runtime (code path only); wallpaper carousel toggle applying on next open (code path only).
