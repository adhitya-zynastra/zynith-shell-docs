# Control Center, Lock Screen and Visual Language — Validation Record

**Date:** 2026‑09‑26 (fifth batch). **Implementation:** uncommitted working tree on top of `e521a86`. This batch was
run with no git operations by my instruction, so there is no commit to cite. The changed files are listed in the
[changelog](../../CHANGELOG.md). **Binary tested:** a clean build (`meson compile --clean`, 1003 targets, 0 failures,
6 warnings, all the known libstdc++ `-Wmaybe-uninitialized` ones), then `.cpp`-only incremental rebuilds while fixing
what the visual checks found. `schema_msg.h` changed after that, so a second clean build ran before the final tests
(see the end).

**Conditions.** I was at the desktop for part of the run: focus moved back to my workspace between two checks, and
one Audio-tab open in the log (02:20:22) is mine, not the harness's. All captures were taken on an empty workspace or
cropped to the panel's own rectangle; frames showing private network details were deleted after cropping to the
navigation strip. No real lock was run (standing rule: lockout risk on a daily-driver machine).

## Tests

| Suite | Result |
|---|---|
| Full suite (three runs during the batch) | **124 / 125** — only `upower_charge_limit_integration` (known, third-party) |
| `transient_ui_config_test` | + `[control_center].style` default Zynith, preset selects classic, GUI override wins, reset returns to the preset; + `[shell].display_font_family` default empty, read from the preset |
| `zynith_config_ownership_test` | + lock screen layout: an editor-style save shadows the preset (a widget missing from the saved `widget_order` disappears); clearing `[lockscreen_widgets]` brings the preset back and leaves nothing in `settings.toml`; a second reset reports nothing to clear |
| `config_schema_roundtrip` | passed without a golden change |
| `noctalia config validate` (live configs, new binary) | valid — after one warning was fixed (below) |
| `niri validate` | valid |

## Control Center — what the visual checks found

The first capture of the new Home looked wrong, and three layout bugs sat behind it. All were found by inspecting the
capture, not by any test.

| Seen | Cause | Fix |
|---|---|---|
| Hero clock ≈ 30 px although built at 48, then 60 px | `syncScaledFonts()` re-applied the classic time and date sizes after construction | sizes chosen by style in that one function |
| Avatar ≈ 114 px, overflowing the banner and later the Bluetooth tile | a post-layout pass enforces the classic minimum and grows the avatar to the identity block | the Zynith hero keeps a fixed ≈ 64 px avatar |
| Weather and uptime lines spilling below the banner | the banner's height reserve was a hand estimate that was smaller than the avatar alone | the reserve is now **measured** from the clock column (`Node::measure`) plus headroom |
| Quick-control labels truncated ("Bluetoo…", "Perfor…") after the hero grew | tiles are kept near-square, so less height meant narrower tiles | Zynith tiles are landscape (height = 0.62 × width) |
| Date read `Saturday, 09/26/2026` | the shell-wide default `date_format` (`%A, %x`) | preset `date_format = "%A, %d %B"` in `rice.toml` — also used by the calendar widget; the GUI can override it |

Final state (`07_Assets/screenshots/cc-home-zynith.png`, classic for comparison `cc-home-classic.png`): the time
leads at 60 px Light; date and weather sit under it; identity is small at the lower right; the wallpaper reads as a
stage above; quick controls use the tinted selection material with every label whole. **Classic renders exactly as
before** (large avatar with host and version, separate date/time card, solid primary tiles, bold primary title).

| Check | Result |
|---|---|
| `panel-toggle control-center` over IPC (the `Shift+Super+E` path) | opens attached to the Time bar, centred (panel ≈ x 628–1292 on a 1920 output) |
| Zynith ↔ classic by editing the preset | switches on the next open; restored to `zynith` afterwards |
| Morph, one step (Ctrl+Tab, Home → Media) | one indicator travels between the tabs over ≈ 3 frames at 45 ms and settles; content settles in ≈ 315 ms |
| **Morph, rapid navigation** (three Ctrl+Tab 80 ms apart) | the indicator **continues from wherever it is** — mid-flight between Media and Audio, then on to Display — one continuous glide, no snap-back, no jump (`cc-morph-rapid.png`) |
| Section title during a morph | changes at once rather than crossfading — noted, not changed |
| Left-bar click, then another left-bar click during a capture burst | **not verified** — the second click was not observed in the log or frames; the Ctrl+Tab path above verified the morph instead |

## Performance (Control Center)

Measured with `/proc` sampling (`pstat.sh`) on the installed binary, CC opened over IPC:

| Measurement | Result |
|---|---|
| 10 open/close cycles | threads 34 → 34, fds 101 → 101; RSS 163.3 → 172.5 MB |
| next 10 cycles | RSS 171.4 → 171.0 MB — **plateau**: the first growth is texture caches (banner, album art), not a leak |
| CPU per open/close cycle | ≈ 80–86 ms (8.0–8.6 ticks) |
| CC open and idle, 10 s | Zynith **25 ticks** (≈ 2.5 %); classic **33 ticks** (≈ 3.3 %); CC closed 9 ticks (≈ 0.9 %) |

The open-idle cost exists in both styles, so the hero does not add it. Where it comes from was **not investigated**.

## Lock screen

| Check | Result |
|---|---|
| Editor (`lockscreen-widgets-edit`) on an empty workspace | renders; the clock uses the new Light weight |
| Composition shown | **the old Phase 2 / fourth-batch layout, not the new preset** — see the finding below |
| `settings.toml` around the editor test | **changed** — the editor's exit writes its snapshot (the shell's own write) |
| Power-control arming, failed-password shake, real lock | **not tested** (standing rule) |

**Finding: my lock screen preset has been shadowed since Phase 2.** `settings.toml` has held a full
`[lockscreen_widgets]` table since at least 2026‑09‑20 (it is in the `phase3b` backup), written when the Phase 2
composition was made in the editor. Its `widget_order` wins over the preset's, and a widget missing from the order
is dropped. So neither the fourth batch's power controls nor this batch's composition ever reached the real lock
screen. The editor exit during this test also merged the preset's new `anchor` / `weight` keys into that table. I
had Claude add `noctalia msg lockscreen-widgets-reset`, the way back to the preset. It is **not run**: running it
discards the saved layout, and that is my decision to make.

**Warning fixed.** `config validate` flagged `anchor` on the login box as an unknown setting. Placement already read
it for every widget, but the login box's settings schema lacked it, so the editor could not offer an anchor for the
element that most needs to stay centred. The schema now includes it. This touches placement metadata only, not the
password path.

## Found, not fixed

- **Hangul text renders blank** — the Wi‑Fi tile label and the Network list show nothing for an SSID of five Hangul
  syllables, in both Control Center styles, although Pango is used and Noto Sans CJK KR is installed. Pre-existing;
  cause not investigated.

## Not verified

The new lock composition as a whole, on screen (shadowed — see above). Arming and shake at runtime. The media-bar
click position. The left-bar click-to-retarget morph path in a capture. Other output sizes (no second display). The
display-font path with a real display face (none installed).
