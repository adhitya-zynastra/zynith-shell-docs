# Phase 6A — Motion Refactor Measurements

**Change measured:** `a147fc1` — the Control Center's section transition moved onto the shared `MorphTransition`
primitive. **Comparator:** `ccfe125`. Both clean builds (`b12c8ff8…` for 6A; the comparator an incremental
rebuild of `ccfe125` verified to have recompiled all seven translation units that include the changed header).

**Machine state:** fresh boot 2026‑09‑25, the desktop in normal use (Zen, VSCodium, several kitty windows open).
**Conditions for every quoted number:** no panel open, no media playing (checked per sample by the script), same
launch method for both binaries.

Raw data: `phase6a-*.csv` in this directory. Scripts: `scripts/measure-idle.sh`, `measure-cc.sh`,
`measure-cc-openclose.sh`, `ab-round.sh`.

## Result: no regression

Interleaved A/B, alternating A → B → A → B, each round restarting the shell identically, warming 60 s, and
verifying the running binary by content before measuring:

| | A — `ccfe125` | B — Phase 6A |
|---|---|---|
| Open/close cycle, shell CPU | 111.5 · 108.5 · 105.0 · 103.5 → **107.1 ms** | 110.0 · 106.0 · 104.5 · 104.0 → **106.1 ms** |
| Complete section switch, shell CPU | 71.3 · 66.7 · 67.0 · 60.3 → **66.3 ms** | 64.7 · 63.3 · 69.0 · 60.3 → **64.3 ms** |
| niri per switch | 62.3–64.0 ms | 61.0–64.7 ms |
| Context switches per switch | 180–205 | 177–185 |

Idle floor, sequential but same boot and conditions: **1.98–2.09 %** (A) vs **1.83–2.12 %** (B) of one core.
Retargeting switches (80 ms dwell, every switch interrupts the previous): 19.3–21.5 ms (A) vs 20.5–21.2 ms (B).

Code-level expectation agrees: the refactor adds one `std::function` wrap per *leg* and one indirect call per
*frame* — microseconds and nanoseconds against a ~65 ms switch.

## What went wrong on the way — and why it is recorded

### 1. A sequential comparison produced a phantom ~5 % regression

The first comparison measured the baseline, then installed 6A and measured again. Complete switches read
61–65 ms before and 66–71 ms after; open/close 108–110 ms before and 113–118 ms after. It looked like a small,
consistent regression, and it survived a second round taken after further warm-up.

It was **system drift over time**, not the code. The A/B shows it directly: the *same* `ccfe125` binary measured
111.5 ms in round A1 and 105.0 ms in round A2. A before/after taken in sequence folds that drift into the
difference; interleaving cancels it. The sequential "after" rows are kept in `phase6a-cc-*.csv`, labelled.

**Lesson:** for any difference smaller than about 10 %, a sequential before/after on a live desktop is not
evidence. Interleave, or do not claim a delta.

### 2. The first A/B was not an A/B

The swap step used `cp` onto the installed executable. A running binary cannot be overwritten in place
(`Text file busy`), the script did not check the exit status, and **all four "alternating" rounds ran the same
binary.** The version line printed each round would have shown it — I did not read it until afterwards.

Kept as `phase6a-aa-accidental.csv`, because by accident it is an **A/A test**: one binary, four restarts,
open/close spanning **103.0–113.5 ms**. Restart-to-restart noise alone is wider than the phantom regression in
(1). The corrected script writes alongside and renames (the running process keeps its inode), then refuses to
measure unless the running executable's content matches the intended binary.

### 3. The media check was wrong

`pactl` prints `Corked:` *before* `application.name`, so the first version of `measure-idle.sh` counted an empty
line as "one stream playing". Nothing was playing. The flag was corrected on those three samples; the
measurements themselves were valid.

### 4. Samples invalidated by real use

Midway through the "after" idle set, Spotify started playing — the owner was using the machine. Those eight
samples are kept with an `-UNCONTROLLED` label and are not quoted. The run resumed once media was paused.

## Stress

`scripts/stress-control-center.sh`: each cycle opens the Control Center, sweeps ten sections forward and back at
120 ms dwell (shorter than a transition, so every switch retargets mid-flight), and closes mid-transition.

| Run | RSS | Threads | FDs | Result |
|---|---|---|---|---|
| 20 cycles | 172.9 → 181.0 MB, flat after cycle 5 | 33 → 33 | 82 → 82 | clean |
| 50 cycles | 180.0 → 181.4 MB | 33 → 33 | 82 → 82 | clean |
| 100 cycles | 180.5 → 184.3 MB | 33 → **34** | 82 → **101** | investigated ↓ |
| +50 cycles | 183.6 → 184.2 MB | 34 → 34 | 101 → 101, **identical set** | bounded |
| 100 open/close @ 30 ms, 100 @ 10 ms | +0.16 MB | unchanged | unchanged | clean; reopen lands during teardown |

The 100-cycle growth was checked rather than waved through. The new descriptors were PipeWire memfds and the new
thread a PipeWire/Pango helper — consistent with the Audio tab initialising streams on first real use, and not
something the morph can create. A further 50 cycles produced an **empty file-descriptor diff** and no new thread:
one-time lazy initialisation, not a leak.

**Totals:** ~420 cycles, ≈4,600 section switches, ≈420 closes mid-transition, 200 reopen-during-teardown cycles.
No crash, no new coredump (26 → 26, all pre-existing), no stuck or duplicated surface (`niri msg layers`: overlay
layer empty afterwards).

## Not measured

- **GPU memory per process** — still not measurable without privileges (see `03_Performance/README.md`).
  `gt_act_freq_mhz` was sampled as an activity proxy and is in the CSVs.
- **Animation disabled at runtime** — turning motion off means writing `settings.toml` or the plugin-owned
  `motion.toml`. Covered instead by the unit test's motion-disabled case.
- **Settings stress** — see `02_Architecture/animation/motion-settings.md`.
