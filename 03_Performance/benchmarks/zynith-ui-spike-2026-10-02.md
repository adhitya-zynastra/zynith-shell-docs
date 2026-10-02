# Zynith UI (Quickshell) — Stage 1 spike (2026‑10‑02)

Subject: the Quickshell prototype on branch `feature/zynith-ui` of the implementation repository, running
**beside** the native shell (which kept every surface and every exclusive role). Gates from the
[Quickshell study §7](../../02_Architecture/Zynith-Quickshell-Architecture-Study.md). All numbers were taken by
Claude with `~/.config/zynith/scripts/benchmarks/spike.sh`; I was using the desktop during the runs.

**Conditions.** Yoga Slim 7i, Core Ultra 5 125H, 15 GB, Intel Arc iGPU, eDP-1 1920×1200 @ 60 Hz; niri 26.04;
Quickshell 0.3.1 (Fedora COPR) on Qt 6.11; profile **Balanced** (automatic); load average 1.3–2.2 (a native build
had just finished). Three audio streams uncorked but silent, so the spectrum stream ran without producing bars.
The prototype: one bar (workspaces, clock, media, visualizer, audio, network, battery, profile), the Home panel,
four focused panels, the OSD (disabled), the Zynith.Native module (niri model, spectrum).

| Gate | Result | Reference | Verdict |
|---|---|---|---|
| Startup: spawn → config loaded | 425–491 ms (10 runs) | — | — |
| Startup: spawn → bar visible | **562–640 ms** (hashed crop of the bar) | native: wallpaper visible 430–506 ms | pass (≤ 1 s) |
| Memory | **PSS 62–63 MB idle**, 79–80 MB after panel cycles; anonymous 32 MB | native shell RSS 128–206 MB | pass (≤ 250 MB) |
| Idle CPU, 60 s, bar visible | **0.52–0.57 %** of one core | native shell, same windows: 2.08–2.17 % | borderline vs my 0.5 % target; ≈ ¼ of the native shell |
| Threads | 15 | native 34 | — |
| Panel frame pacing (open, 300 ms) | mean 16.0–17.0 ms; first frames 20–38 ms (≈ 8 % of frames > 20 ms, ≤ 3 per 10 opens > 33 ms) | — | pass, first-frame hitch noted |
| Panel frame pacing (close, 200 ms) | mean 16.0 ms, worst 17.3 ms | — | pass |
| CPU per panel open + close | **≈ 160 ms** (Home), 108 ms (System), 66 ms (empty panel) | native Control Center 84–90 ms per cycle (Batch 7) | **regression ≈ 1.5–1.8×** |
| Live reload of QML | 186 ms | native: rebuild + restart | — |

**Verdict: Stage 1 passes** on memory, startup, idle and pacing. The one regression is the CPU cost of opening a
panel, documented here rather than hidden.

> **Amended the same afternoon — read [Re-measurement](#re-measurement-single-instance-same-conditions) first.**
> Two things were wrong with the table above:
>
> 1. **Crash-relaunched copies were running.** While these runs were taken, the prototype had been crashing on
>    live reload ([postmortem](../../04_Incidents/postmortems/2026-10-02-zynith-ui-reload-crash.md)), and
>    Quickshell's crash handler had left relaunched copies running. Each copy shared Qt's pages, so the measured
>    process's PSS (62–63 MB) was understated.
> 2. **The native reference was taken under a different power profile.**
>    - The native figure (84–90 ms per cycle) comes from Batch 7 on 2026‑09‑26, under TuneD `balanced`.
>    - These runs were under `powersave` (platform profile `low-power`). TuneD's log shows it continuously since
>      2026‑09‑30, apart from 54 s at 12:54.
>
>    Measured side by side under the same profile, the gap is smaller and depends on the UI profile.
>
> The original rows stay as they were measured.

## What the panel cost is made of (attribution runs)

| Variation (Balanced, 10 cycles each) | ms per cycle |
|---|---|
| as shipped | 162–166 |
| no stagger | 159 |
| no shadows | 151 |
| no blur region | 158 |
| no keep-warm (windows recreated) | 185 |
| no click-catcher window | 146 |
| Performance profile | 119 |
| empty panel (floor: show/hide, catcher, animation, routing) | 66 |

Per thread, the main (QML + basic render loop) thread takes ~138 of ~150 ms. Scene-graph timing shows steady
animation frames at 0–1 ms; the cost sits in first frames after a window maps (21 ms, of which 12 ms swap) and in
first renders of new text (glyph preparation). Remapping a hidden layer surface costs about as much as creating it.

## Changes made because of these measurements

- Closed panels stay **warm** for a profile-defined time (Performance 0, Balanced 30 s, Enhanced 2 min, Max 10 min)
  and do no work while hidden: the sampler, Wi‑Fi scanning and timers follow visibility (−20 ms per cycle).
- A bug where a warm surface unloaded its content on close was fixed; the entrance now plays once per showing.
- The launcher no longer runs `cmake` on every start when the native module is current.
- Earlier, during development: the palette service had been shadowed by QtQuick's own `Palette` type and silently
  showed fallback colours; renamed `Scheme`.

## Re-measurement: single instance, same conditions

Taken 13:53–14:01 after the reload-crash fix (`e381281`). Conditions:

- one prototype instance;
- the native shell freshly restarted on the clean `67f09d4` build;
- TuneD `powersave` throughout;
- load 1.5–2.0;
- two audio streams uncorked.

Raw output: [`zynith-ui-spike-2026-10-02-rerun.txt`](zynith-ui-spike-2026-10-02-rerun.txt). Claude ran the scripts. The
A/B alternates the native Control Center and the prototype's Home panel in the same minute, with the same
open 0.7 s → close 0.5 s pattern and ten cycles per round.

| | UI profile Performance | UI profile Balanced |
|---|---|---|
| Startup → bar visible | 575–648 ms (5 runs) | 584–612 ms (3 runs) |
| Idle CPU, 60 s | **0.10 %** (no visualizer in this profile, so no spectrum stream) | **0.65 %** (the spectrum stream is held) |
| Native shell idle, same 60 s | 2.65 % | 2.82 % |
| PSS idle → after 10 panel cycles | **77 → 90 MB** | **79 → 96 MB** |
| Panel open + close, prototype Home | **126–131 ms** | **181–187 ms** |
| Panel open + close, native Control Center, same minute | **112–127 ms** | **110–117 ms** |
| Frames per open / close | 7.7 / 6.0 | 14.5 / 11.0 |
| Open frame pacing | mean 16.1 ms, worst 23 ms | mean 16.4 ms, worst 43.5 ms (2 of 10 opens had a frame > 33 ms) |
| 20 live reloads | survived (new gate) | — |

What changes:

- **Memory:** the real figure is **77–79 MB** PSS idle, not 62–63 MB. It is still well inside the 250 MB gate and
  below the native shell.
- **Panel cost under Performance:** roughly at parity with the native Control Center (+3–14 ms).
- **Panel cost under Balanced:** **≈ 1.6×** the native Control Center (+65–75 ms per cycle).
  - The Balanced animations are longer (scale 1.0 against 0.6), so each open and close draws about twice as many
    frames.
  - Per frame, the prototype spends more CPU than the native shell. Its QML bindings and the basic render loop
    run on the main thread.
  - The regression is real, but it is a per-frame cost in the richer profiles, not a fixed tax on every panel.
- **Idle:** 0.65 % in Balanced, which is still below the native shell under the same conditions. In Performance
  the visualizer is off and the prototype idles at 0.10 %.

Since this re-run, the *automatic* profile follows power (`127f3b8`): it is at most Balanced on battery, and
Performance while power saving is on or the battery is low. On this machine today that means Performance.

## After the second batch (14:44)

The prototype now also has the launcher, clipboard, notifications (off), Quick Settings, Wallpaper panel, window
behaviour generator and the native `NetworkState`. Same conditions: TuneD `powersave`, UI profile Performance by
the adaptive rule. Raw output is at the end of the re-run file.

| | Result |
|---|---|
| Startup → bar visible | 562–649 ms (5 runs) |
| Idle CPU, first minute after a start | 0.20 % (still settling) |
| Idle CPU, settled | **0.05 %** (3 ticks / 60 s; 2.2 + 1.6 wakeups/s on the two busiest threads) |
| Native shell, same minute | 2.60 % |
| PSS idle → after 10 panel cycles | 75 → 89 MB |
| Panel open + close (Home) | 122 ms, against 112–127 ms for the native Control Center measured at 13:5x under the same profile |
| 20 live reloads | survived |

## Open

- Idle 0.5 % is mostly the spectrum's PipeWire thread processing silent buffers (~0.7 % of its own over 12 s of
  cycles) while a sink runs: the visualizer holds the stream so it can wake on sound. Same design as the native
  shell; a sound-onset trigger without a running stream is not available from PipeWire.
- Panel first-frame hitch and per-frame cost in Balanced and above. Candidates:
  - a content layer cache during the entrance, for profiles without stagger;
  - pre-warming the first panel;
  - merging the click-catcher into the panel surface, which saves one surface map per open (≈ 16 ms in the
    attribution runs);
  - fewer per-frame bindings on the card.
- Not measured: multi-monitor, long sessions (leaks), Enhanced/Max on the Legion.
