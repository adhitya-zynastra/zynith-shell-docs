# Launcher, OSD, Notifications and Audio — Validation Record

**Date:** 2026‑09‑25. **Implementation:** `b106c38`. **Binary tested:** a clean build (`meson compile --clean`, 1002
targets, zero failures, the same 6 libstdc++ warnings as earlier clean builds; `config_types.h` changed, so ADR‑0013
applied), then one incremental rebuild of `.cpp` files only (launcher query timing, sound debug log). The installed
binary is the committed tree. Claude drove every check on the live desktop while I was using it.

Resource figures are the shell process's `VmRSS` (MiB), threads and file descriptors from `/proc`; CPU is
`utime+stime` (100 ticks/s). Layer counts are `niri msg layers`.

## Tests

| Suite | Result |
|---|---|
| Full suite | **124 / 125** — only `upower_charge_limit_integration`, unrelated and pre-existing |
| `transient_ui_config_test` (new) | pass — defaults, preset `style = "classic"`, range clamping of width/icon size/duration, override then reset |

## Launcher

| Check | Result |
|---|---|
| Open / close over IPC | panel layer 1 → **0** after close |
| Query cost (debug log) | **0.23–0.28 ms** per query, 3 and 80 results |
| Query `alacritty` via IPC context | filtered to 3 results, first selected with the `↵` hint (`launcher-zynith.png` shows the unfiltered view) |
| Down ×3 after a click in the search bar | selection on the 4th result |
| Esc | closes; panel layer 0 |
| Enter on `alacritty` | Alacritty window 0 → 1, launcher closed; test window closed afterwards |
| 20 open/close cycles | RSS 163.4 → 163.5 MiB, threads 33 → 33, fds 82 → 82, **1.33 CPU‑s total** (~66 ms per open+close), no layer left |
| `style = "classic"` via `rice.toml` | renders exactly as before (`launcher-classic.png`); `rice.toml` restored byte-identical |

No letters were typed: queries went in through the launcher's IPC context argument.

## OSD

| Check | Result |
|---|---|
| One `volume-up` | OSD shown; **1** OSD layer |
| 10 more at 60 ms | still **1** layer — content retargeted, hold restarted |
| After the hold | **0** layers — surface destroyed |
| Cues for those 11 events | 7 `volume-change` plays (existing cooldown) |
| Sink mute + unmute, mic mute + unmute | **3** `mute` cues: sink unmute, mic mute, mic unmute — sink mute is silent by design |
| Brightness down, up | OSD shown; brightness back to 100 %; 0 layers after |
| `duration_ms = 3000` | present at 2.5 s, gone at 4.7 s |
| Animations off | present at 0.3 s, gone at 4.3 s; niri's generated animations back to normal after restore |
| Glass | tinted fill, glass border colour (`osd-glass.png`) |

**My mistake during the check:** the volume run pushed the sink to 105 % (overdrive enabled) while I had media
playing; it was restored to its prior value within about a second.

## Notifications and audio

| Check | Result |
|---|---|
| Single, burst of 6, critical | rendered on glass with the accent disc; critical keeps its Error border; **1** layer surface for all cards |
| Cues for those 8 notifications | **3 plays, 5 "still playing, not restarted"** — never more than one stream |
| `max_visible = 4` preset, burst of 6 | settles at 4 cards; the rest queue (`notification-stack.png`) |
| DND on, notify | no toast, **0** cues; DND off again afterwards |
| `-t 1500` | layer present at 0.6 s, **0** at 3.2 s |
| Action button | `notify-send -A` printed `ok`, exit 0 |
| Expiry | D‑Bus `NotificationClosed` reason 1 emitted |
| × | dismissed the card under the pointer |
| Hover | pauses expiry (observed: a card under the resting pointer outlived its 1.2 s timeout) |
| History | listed in the Control Center's Notifications tab |
| `notification-clear-active` | **0** layers |

## Whole session

RSS 175.0 MiB after the restart, 177.1 MiB after every check above; threads 33–34; no crashes (the only coredump is
the known test binary). Warnings: Bluetooth reconnect timeouts, the documented GTK template outputs, the `emacsclient`
hook — and one `rice.toml` parse error of my own making: a test appended a second `[shell.launcher]` table for a few
seconds before it was replaced with an in-table edit.

## Not verified

- Caps Lock / Num Lock (would toggle my own lock state), media (my own playback), keyboard layout (one layout).
- Lock/unlock cues (no lock testing, by rule) and a held shortcut.
- GPU memory.
