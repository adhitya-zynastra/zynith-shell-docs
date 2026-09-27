# Zynith Control Center and lock screen (Batch 7) — Validation Record

**Date:** 2026‑09‑26. **Implementation:** uncommitted working tree on top of `e521a86` (Batches 5–7, no-git).
The batch brief named `e521a86` with 124/125 tests as the baseline. That was outdated: the tree already carried
the uncommitted fifth and sixth batches (127/128). Everything below is measured against that real state.

**Conditions.**
- I was at the machine for part of the run.
- The run was interrupted by the lock-screen crash in the
  [postmortem](../../04_Incidents/postmortems/2026-09-26-lock-reload-crash.md) and a hard power-off. The build tree
  lost freshly generated files (0-byte protocol headers) and was rebuilt clean.
- Captures were taken only on a workspace verified empty in the same script, cropped to the shell surface, with
  the Wi‑Fi network name pixelated. My workspace was restored after each capture.
- Section switches were driven by IPC (`panel-open control-center <section>`), not synthetic keys.
- The only pointer clicks landed on the always-visible left bar. Hover-open used pointer movement only.
- No real lock was run.

## Build and tests

| Check | Result |
|---|---|
| Clean build (`meson compile --clean`, 1017 targets) | **1017 / 1017, 0 failures** (final build, after every code change of the batch). The binary measured below is that build, installed and confirmed byte-identical to the build output |
| Warnings | 6 — the known libstdc++ inlining diagnostics in `config_service.cpp` / `fixed_palette.cpp`; none from Batch 7 code |
| Full suite | **127 / 128** — the known `upower_charge_limit_integration` |
| `zynith_config_ownership` (extended) | stash → reset → preset back → restore → saved layout back, equal to the one reset; restore without a stash fails with a reason |
| `noctalia config validate` (new binary, new preset) | valid; the new clock keys are known, with no "unknown setting" |
| `niri validate` | valid |

The first clean build failed on a real error: my new clock member was named `m_face`, which already exists (the
analog face). It was renamed to `m_typeface` and the build continued from the clean state.

## Control Center — the morph, measured

Command-bar strip captures (490 × 56 px, ≈ 13 ms apart; the panel presents at 60 Hz, so consecutive captures
sometimes repeat a frame). The capsule's edges were read on a pixel row inside the capsule above the glyphs (row 15:
capsule fill ≈ +19 luminance over the bar). Cinematic tempo, effective speed 0.64.

| Run | Travel | Settled (≤ 1 px) | Overshoot | Largest frame-to-frame velocity change |
|---|---|---|---|---|
| One switch, Home → Media | centre 54 → 92 px (38 px) | **258 ms** (274 ms on the development build) | 0 | 0.36 px/ms |
| Four switches 80 ms apart, Home → Media → Audio → Display → System | centre 54 → 210 px, width 74 → 82 px | **569 ms** after first motion (604 / 582 ms on development builds) | 0 | 1.92 px/ms — a single repeated frame (145 → 145 → 168 px): one missed presentation on the first visit to a section, then the capsule is where the spring puts it. The development-build run showed the same pattern (1.31 px/ms after a ≈ 40 ms stall) |

For comparison, the Batch 6 nav indicator (same `ElementMove` spring, 36 px) settled at 277 ms.

**What the filmstrips caught, and what changed because of them.** Each item was seen in a contact sheet
([one switch](../../07_Assets/screenshots/cc-zynith-command-bar-switch.png),
[burst](../../07_Assets/screenshots/cc-zynith-command-bar-morph.png)):

1. **The whole strip jumped** at the moment of a switch: the items were sized against the *active* section's
   actions (Home has three, Media one). Now sized against the widest section's actions. Re-captured: no jump.
2. **The incoming label showed beside the capsule** for ≈ 3 frames ("Med…"). The label's ink now waits for the
   capsule to arrive (within 12 px of rest). Re-captured: clean.
3. **In the burst, every item passed through flashed its half-unfolded label.** Now an item the capsule has left
   may only lose ink. Re-captured: clean.
4. **The very first capture had no labels at all.** At my default width (0.85 × 780) the strip went icon-only.
   Because an item's unfold does not depend on its height, the sizing now shrinks items (38 → 34 px here) to keep
   the labels.
5. **Header actions were filled squares** that did not belong to the capsule language. Now every action is a
   capsule, and the stateless ones are clear.
6. **Section headings were inconsistent.** Helper-built headings became muted labels, while most sections'
   hand-built titles stayed bold. Withdrawn: helper headings are now the `Subtitle` role
   ([plates capture](../../07_Assets/screenshots/cc-zynith-section-plates.png)).

## Control Center — attachment and entry points

| Check | Evidence | Result |
|---|---|---|
| IPC open attaches to the anchor bar and centres over it | log `origin command`; capture: panel frame x 620–1301 (centre 960.5), Time bar centre 959.5 | ✅ centred within 1 px |
| A click on another bar's widget moves the attachment | IPC open (Time bar), then a click on the left bar's brightness widget → log `origin bar-widget default/brightness @ 12,1064 16x16 edge=left reveal=right`; capture shows the panel attached to the left bar on Display ([capture](../../07_Assets/screenshots/cc-zynith-attached-left-bar.png)) | ✅ |
| Hover-open (pointer rests on the Time bar clock) | log `origin bar-widget Time/clock @ 933,1170 55x25 edge=bottom reveal=up` | ✅ — the first attempt did nothing because the auto-hidden bar had not been revealed; the retry approached from the edge. Same behaviour as Batch 6 |
| `Shift+Super+E` | bound to `noctalia msg panel-toggle control-center` (`niri/rice/binds.kdl`), the IPC path verified above | not pressed: synthetic letter keys are excluded by my testing rules |
| Direct section open (`sidebar_section = "none"`) | Audio and System captures | ✅ Zynith header without navigation (title + clear capsule close) |

## Lock screen (editor only)

| Check | Result |
|---|---|
| Reset made the preset live | `lockscreen-widgets-reset` → `ok: previous layout kept for lockscreen-widgets-restore`; stash 6.4 KB, 24 widget entries; `settings.toml` without `[lockscreen_widgets]` |
| Composition in the editor | time, eyebrow date, identity group, glass capsule field, corner periphery, power capsule and the visualiser horizon, as designed ([capture](../../07_Assets/screenshots/lock-aperture-editor.png)) |
| Eyebrow date legibility | **failed** on the first capture (`on_surface_variant` on a light wallpaper region); fixed to `on_surface` + shadow; re-captured legible ([focal](../../07_Assets/screenshots/lock-aperture-focal.png)) |
| Editor exit without an edit | `settings.toml` byte-identical (hash before/after) in both runs — dirty-only save confirmed |
| Power capsule | one concentric glass capsule with four clear items ([capture](../../07_Assets/screenshots/lock-power-capsule.png)); arm/confirm logic unchanged and not pressed |

## Resources (final clean build)

| Measurement | Result |
|---|---|
| 20 cycles of open Home → switch to Audio → close (IPC), round 1 | threads 33 → 33, fds 83 → 83, RSS 161.2 → 166.2 MB; **90 ms CPU per cycle** |
| the same, round 2 | threads 33 → 33, fds 83 → 83, RSS 165.1 → 166.1 MB (the plateau: round 1's rise is warm-up, not growth); **84 ms CPU per cycle** |
| Idle, nothing open, **no audio stream playing** (checked with `pactl` before and after) | **3 ticks / 10 s**, twice (≈ 0.3 % of one core). Batch 6's pre-change baseline was 10 ticks / 10 s. Batch 6 could not measure after its change, because audio never stopped for 25 minutes. This closes that open item |

A cycle here includes a section switch, so it is not directly comparable to Batch 6's open/close-only figure
(80–86 ms). The command bar's per-frame work is a position/frame-size update per item plus a redraw. It requests no
layout pass (`setFrameSize`).

**Classic regression check:** after restoring my setting to `classic`, the panel renders exactly as the `e521a86`
classic ([capture](../../07_Assets/screenshots/cc-classic-batch7.png), network name pixelated).

## Not verified

- **The real lock screen:** blur, tint, password states, entrance and exit choreography, the unlock bridge — and the
  reload-while-locked crash fix. No automated lock, by rule.
- **Other output sizes** (no second display) and fractional scales. The 1 px margin in the label-fit rule was
  reasoned, not tested.
- **Fonts:** Inter, Space Grotesk and Sora are not installed. Every "display face" in these captures is the
  Montserrat fallback.
- **The `Select::~Select` crash cause:** inferred, not proven (release cores).
