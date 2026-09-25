# Performance Engineering

Resource discipline is not a side quest in Zynith; it is most of what distinguishes it from a themed desktop.
I care about CPU, GPU, RAM, cache, swap and zram, thread count, wakeups, IPC, filesystem I/O and GPU textures,
and I set the engineering constraints that follow from that: event-driven by construction, bounded lifetimes, no
unnecessary daemons, no polling, no second animation engine, no per-frame shell scripts, no redundant IPC. Where
Zynith spends something, I want to be able to say what it bought.

The other half of the discipline is evidential. I had Claude measure everything that is claimed here, and the
rule below is what keeps the numbers worth reading — including in the cases where measuring proved me wrong and
an "optimization" was reverted.

## Provenance rule

A number may appear in an authoritative table only with a complete provenance block:
**date · commit · build type · machine · tool · sample duration · repetitions**. Everything here was measured on
the machine described in `00_Project/technology-stack.md`, so figures do not transfer to other hardware —
especially GPU-dependent ones.

**Build type is not optional.** Measurements from an incremental build that followed a layout change to a
widely-included header are invalid; see `benchmarks/contaminated-measurements.md`.

## Method

| Quantity | How it was taken |
|---|---|
| Process CPU | `utime + stime` from `/proc/<pid>/stat`, sampled over a fixed wall-clock window, expressed as a percentage **of one core** (the machine has 18 threads, so 1.4 % ≈ 0.08 % of total capacity) |
| Context switches | sum of `voluntary_ctxt_switches + nonvoluntary_ctxt_switches` across `/proc/<pid>/task/*/status` |
| RSS | `VmRSS` from `/proc/<pid>/status` |
| PSS | `Pss` from `/proc/<pid>/smaps_rollup` — used for the stack total, because RSS double-counts shared pages |
| GPU | `/sys/class/drm/card1/gt_act_freq_mhz` sampled at 4 Hz. A **proxy for activity only**: `intel_gpu_top` needs privileges not available, and per-process GPU memory was **not measurable** |
| Decode / cache counters | `ThumbnailService::Stats` (decodes, idle hits, evictions, peak idle bytes), logged once per browse session at debug level |
| Input | a temporary uinput virtual device (absolute pointer + wheel + keyboard) so wheel/click/key timings are reproducible; removed after each run |

## What is deliberately absent

- **Pre-Zynith baselines.** Nothing was measured before the project started, so there is no honest
  "before the project" column anywhere in this documentation. See `01_Phases/Phase_-1/README.md`.
- **GPU memory per process** — not measurable with available privileges.
- **Frame timing / jank statistics** — no instrumentation exists for it.

## Index

| File | Contents |
|---|---|
| `baselines/shell-states.md` + `benchmarks/shell-states.csv` | CPU, context switches and RSS for 14 shell states |
| `baselines/memory-floor.md` | PSS breakdown of the desktop stack and the realistic floor |
| `baselines/idle-conditions.md` | **Read before quoting an idle figure** — what the ~1.4 % baseline assumes |
| `benchmarks/wallpaper-session.csv` | Memory and decode behaviour across browse sessions |
| `benchmarks/optimizations.csv` | Before/after for each optimization, with the measurement that justified it |
| `benchmarks/template-apply.csv` | Cost of a palette change: process forks, shell CPU, enabled-template inventory |
| `benchmarks/tracks-motion-glass.md` + `tracks-motion-glass-ab.csv` | Motion/Zynith Corner/Glass validation, matched-pace A/B |
| `benchmarks/phase6a-motion.md` + `phase6a-*.csv` | Motion refactor: interleaved A/B, stress, and two measurement mistakes |
| `benchmarks/contaminated-measurements.md` | Numbers that must never be used |
| `optimization-log.md` | Narrative: what was optimized, why, and what it cost |
| `charts/` | Generated PNGs (`scripts/generate-charts.py`) |
