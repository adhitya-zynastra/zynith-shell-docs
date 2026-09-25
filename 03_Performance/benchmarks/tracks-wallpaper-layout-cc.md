# Wallpaper, Responsive Layout and Control Center — Validation Record

**Date:** 2026‑09‑25. **Implementation:** `b49ec4e` (responsive layout + carousel) → `09990f8` (Control Center) →
`c5dd72d` (Personalization). **Binary tested:** a clean build (`meson compile --clean`, 1000 targets, zero
failures, the same 6 libstdc++ `-Wmaybe-uninitialized`/`-Wrestrict`/`-Wstringop-overflow` warnings as the previous
two clean builds), then incremental rebuilds for the changes described below. The installed binary is byte-identical
to the final build of the committed tree. The two intermediate commits were **not** built on their own.

This was an implementation-first batch. Validation aimed at the behaviours the batch promised, not at a campaign.
Claude drove every check on the live desktop while I was using it; where that interfered, it is recorded below.

## About the incremental rebuilds

After the clean build, three changes were made and built incrementally:

1. `bar_instance.h` gained a `bool` member (the hover-open confirm fix). ADR‑0013 requires a clean build after a
   layout change to a *widely-included* header; this one is included only through `bar.h`, which reaches four
   translation units, all of which ninja rebuilt from its dependency files. I judged that outside ADR‑0013's scope.
2. `carousel_geometry.h` changed inline functions and constants only — no struct layout.
3. Include order and line wrapping in three `.cpp` files.

No CPU figure below is compared against a figure from a different build, so no A/B conclusion rests on these builds.

## Tests

| Suite | Result |
|---|---|
| Full suite | **123 / 124** — only `upower_charge_limit_integration`, unrelated and pre-existing |
| `responsive_layout_test` (new) | pass — extent/fit/density, carousel counts at 1366 → 20000 px, count non-decreasing in width, degenerate input |
| `zynith_config_ownership_test` | pass — one control per key after the Control Center options moved to Personalization |
| `morph_transition_test`, `signal_dispatch_test`, `animation_reentrancy_test` | pass |

## Runtime checks

### Control Center

| Check | Result |
|---|---|
| Clock route after config reload | `widget.clock: left=panel-toggle control-center home` in the resolved-bindings log |
| Network, Bluetooth, volume, brightness, battery clicks, panel closed → open → switching | each lands on its section (Network, Bluetooth, Audio, Monitor, Power); **one** `opened` log line for five clicks — no close, no reopen |
| Rapid retarget: 9 clicks at 60 ms gaps, starting on the active section | first click toggled closed (correct: it was the active section), second reopened 143 ms later, the remaining 7 retargeted in place; final section = last click; **0.44 CPU‑s** for the whole script |
| Ctrl+Tab ×1, ×2, Ctrl+Shift+Tab, Ctrl+PgUp | Network → Bluetooth → Weather → Calendar → Weather → Bluetooth |
| 12 × Ctrl+Tab at 30 ms | stopped at the last section (no wrap, same as the wheel), no backlog; **0.25 CPU‑s** for the script |
| Escape | closes |
| Density compact / comfortable / spacious (set through `rice.toml`, then reverted byte-for-byte) | with the navigation row in the same place, the section title's top edge sits at y = 665 / 670 / 678 px — see `cc-density.png`. Deliberately subtle: frame rhythm only |
| Panel keyboard interactivity while open | `exclusive` (`niri msg layers`) |

**A regression found and fixed during this check.** Routing the clock to Home collided with hover-open, which
also opens Home. Resting on the clock for 350 ms opened the panel, and the click that followed toggled it shut
(log: opened 15:37:10.242, closing 15:37:13.172). Before this batch that click retargeted to Calendar, so the
problem did not show. Fix in `09990f8`: a click that lands while the hover-opened panel is still up, before the
pointer leaves the time cluster, confirms the open. Re-test after the fix:

| Sequence | Result |
|---|---|
| hover 1 s, then click | stays open on Home (no `closing` line) |
| click again | closes |
| approach and click | opens |
| click | closes |

### Wallpaper browser (1920×1200, scale 1)

Session: 168 wallpapers. Resource figures are `VmRSS` (MiB), thread count and open file descriptors of the shell
process from `/proc`; CPU is `utime+stime` (100 ticks/s).

| Check | Result |
|---|---|
| Visible cards | **5** (focus + 2 per side), the same composition as before the batch — `carousel-1920.png` |
| Right arrow | focus moves one card; `settings.toml` hash unchanged (no apply) |
| Wheel 30 forward + 30 back at 25 detents/s | **0.42 CPU‑s** over the ~5.4 s script; RSS 177.3 → 177.5 MiB; threads 34 → 34; fds 101 → 101 |
| Right ×30 + Left ×30 at ~28/s | **0.47 CPU‑s** over the ~6 s script; RSS 177.5 → 180.1 MiB; threads and fds unchanged |
| Click on a neighbour | focus only — `settings.toml` and the niri palette export unchanged |
| Double-click on the focused card (clicks 120 ms apart) | **one** apply (`applied wallpaper …`), second rejected: `ignoring repeat apply … within the double-click guard` |
| Palette | `noctalia.kdl` regenerated after the apply |
| Session statistics at close | **181 decodes** (168 previews + 13 display-tier), 336 cache hits, **0 evictions**, peak idle 64.7 MB |
| RSS before open / 2.5 s after open / 3 s and 8 s after close | 175.7 / 194.7 / 177.8 / 177.8 MiB; threads 34 throughout |
| Restore | original wallpaper set back through `noctalia msg wallpaper-set`; `settings.toml` then **byte-identical** to its pre-test copy |

The session was about 120 traversal steps at 25–28 per second. 181 decodes for 168 entries and zero evictions is
the evidence that traversal does not cause load/unload churn: the decode gate lets only landing positions promote.

### Responsive geometry at other logical widths

niri's `output … scale` was changed temporarily (not written to config) and set back to 1 afterwards.

| Logical width | Code | Visible cards |
|---|---|---|
| 1920 (scale 1) | final | **5** |
| 3200 (scale 0.6) | final | **7** — focus + 3 per side, card still 760 logical px (`carousel-3200.png`) |
| 2560 (scale 0.75) | first version | 7 *counted*, **5 perceptible** — the third card showed ~22 px past its neighbour |
| 1536 (scale 1.25) | first version | **3** — the outer pair was entirely covered |

**The first version was wrong, and the runtime check is what showed it.** `fitArc` counted a card as visible if
any of it was on screen, ignoring that the nearer card paints over it; and the 46 % band cap left no room for the
outer pair on narrow outputs. Fixed before commit: a neighbour counts only when ≥ 20 % of its drawn width shows
past the card in front (the laptop's outer pair shows ~25 %), and the band cap is the pre-responsive 40 %. The
2560 and 1536 rows were not re-run on the final code; the final code's values for them (5 and 5) are computed, and
the unit test asserts them.

**A misreading, corrected.** The first multi-scale run captured no browser at all, and I briefly took that for a
~3 s IPC open latency after a scale change. The log says otherwise: the key-repeat storm described under *Input*
had left the browser open, so each iteration's first toggle **closed** it before the screenshot and the second
reopened it just after (closing 15:51:40.998, screenshot 15:51:44.85, opened 15:51:44.967). With the state known,
the repeat run opened the panel **48 ms** after `noctalia msg panel-toggle wallpaper` at both scale 1 and 0.6.
Separately, one `IpcPollSource dispatch took 1667.2ms` warning was logged at the `wallpaper-set` restore of a
13 MB JPEG — the IPC handler decodes synchronously. Pre-existing behaviour, not investigated here.

### Input

| Check | Result |
|---|---|
| `Mod`+left-drag, floating throwaway window | moved by exactly the drag: x 995 → 695 (−300) |
| `Mod`+right-drag from the lower-right | resized by exactly the drag: 921×1176 → 721×876 (−200, −300) |
| `Mod+MouseLeft` / `Mod+MouseRight` binds | none in any included file |
| `Super+Alt+A` | opens Personalization with Motion, Glass, Control Center, Wallpaper Browser (`personalization-groups.png`) |

**Key-repeat storm, found in the log.** Between 15:51:24 and 15:51:29 the wallpaper panel opened and closed 13
times at ~150 ms intervals. None of it came from the test scripts. `Mod+W` spawns `noctalia msg panel-toggle
wallpaper` without `repeat=false`, so a held key re-spawns the command on every repeat. I was using the desktop
at the time; that I held the key is inferred from the pattern, not confirmed. Seventeen `noctalia msg` binds now
carry `repeat=false`. The fix is `niri validate`-clean but was **not** runtime-tested — that would mean sending a
held letter key, which the testing rules forbid while I have an editor open.

### Ownership and safety

| Check | Result |
|---|---|
| `settings.toml` | written only by the shell's own apply path during the apply test; after the IPC restore it was **byte-identical** to the pre-test copy (15:47). It changed again at 15:53:18 while I had the Settings window open; nothing the scripts ran at that moment writes it, so that change is presumably mine — which key is **UNKNOWN**. The Glass overrides in the screenshots (blur strength 20, tint) predate the session |
| Generated fragments | rewritten once at the first start: header comment only (“Settings -> Personalization”), bodies identical |
| `noctalia.kdl` last include; one `blur` node | yes / yes |
| Errors in the shell log since the first restart | 0 `[ERR]`. Warnings: Bluetooth reconnect timeouts, the documented GTK template outputs, the `emacsclient` template hook (exit 127) |
| Crashes | none; the shell was restarted deliberately four times for installs |
| Synthetic input | pointer, arrows, Escape, Ctrl+Tab/PgUp only after a click inside a shell panel. **One exception:** `Super+Alt+A` was sent once as a chord; niri consumes the bind before any client sees the key |

## Observed, not investigated

- The Control Center's Audio tab read "No output device selected, 0 %" once, shortly after a shell restart, while
  the bar's volume widget read 100. Out of scope for this batch (audio redesign); recorded in future work.

## Not verified

- Media → Media routing: no media was playing, so the widget had nothing to click.
- 2560 and 1536 logical on the final code (computed only).
- Held-key behaviour after `repeat=false`.
- GPU memory — not observable from `/proc`.
