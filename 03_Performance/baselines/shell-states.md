# Shell State Baselines

Source data: `../benchmarks/shell-states.csv` · chart: `../charts/cpu-by-state.png`
**Provenance:** 2026‑09‑21, commit `eaff2b2`, **clean build**, quiet workspace, 3–5 s per sample, single run.

CPU is a percentage **of one core**; the machine has 18 hardware threads.

| State | noctalia CPU | niri CPU | ctxt/s | RSS |
|---|---|---|---|---|
| Idle, bar only | 1.40 % | 0.40 % | 111 | 160.5 MB |
| Control Center open (idle) | 1.00 % | 0.33 % | 112 | 165.2 MB |
| Control Center page transition | 2.28 % | 1.30 % | 150 | 163.8 MB |
| Rapid Control Center switching | 4.00 % | 2.46 % | 213 | 164.1 MB |
| Launcher open | 3.96 % | 1.65 % | 155 | 173.7 MB |
| Rapid launcher open/close | **7.73 %** | 5.48 % | 369 | 170.4 MB |
| Notification visible | 1.31 % | 0.33 % | 134 | 166.3 MB |
| OSD visible | 6.55 % | 6.55 % | 236 | 166.6 MB |
| Wallpaper browser idle | 2.33 % | 0.67 % | 120 | 172.9 MB |
| Carousel moving | 2.00 % | 1.00 % | 128 | 170.6 MB |
| Rapid traversal (66 items/s) | 2.25 % | 0.64 % | 132 | 170.6 MB |
| After browser closes | 1.66 % | 0.33 % | 113 | 167.8 MB |
| All transient UI closed | 1.40 % | 0.40 % | 110 | 167.8 MB |

One wallpaper apply costs **38 ms of shell CPU**.

## Observations a maintainer should know

- **Open panels are nearly free.** An open Control Center costs the same as the bar alone; the shell does no
  steady-state work for a surface that is merely visible.
- **Panel *construction* is the expensive operation.** Rapid launcher cycling is the costliest state measured,
  because every open rebuilds the panel's scene. This is the main remaining optimization target.
- **niri tracks the shell.** Where niri rises it is compositing frames the shell produced. On a busy workspace
  niri's idle figure rises to ~3–6 % purely from the user's own animating windows; that is not shell overhead. The
  0.40 % figure above is from a quiet workspace.
- **GPU sleeps at idle** (`gt_act_freq_mhz` = 0) and only rises during transitions.
- **Idle cost is main-thread only.** A per-thread breakdown showed no background polling hotspot, and an A/B that
  disabled the bar's once-per-second update measured **no improvement**, so it was reverted rather than kept as a
  fake optimization.
