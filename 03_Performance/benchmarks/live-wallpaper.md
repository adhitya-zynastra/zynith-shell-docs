# Live wallpaper measurements (2026‑09‑27)

Subject: [live wallpapers](../../02_Architecture/wallpaper/live-wallpapers.md), branch `feature/live-wallpaper`
(`1ba8cec` over `956765a`). All numbers below were taken by Claude.

**Conditions.** Fedora 44, niri 26.04, Intel Arc iGPU, one output eDP-1 1920×1200 @ 60 Hz. linux-wallpaperengine
built from upstream `b016d7d` (Release), `--fps 30 --silent --layer background --disable-mouse --scaling fill`.
Steam library: one folder, 560 Workshop items, 45 GB. The desktop was in use (Noctalia running, static wallpaper
and backdrop surfaces present); later runs were taken with the session locked. CPU % is of one core, from
`/proc/<pid>/stat` utime+stime over the stated window. VERIFIED unless marked otherwise.

## Renderer cost (standalone, before any Zynith code)

| wallpaper | kind | processes | RSS | CPU | SIGTERM → exit |
|---|---|---|---|---|---|
| 1334736987 "mount fuji in autumn sunrise" | scene | 1 | 225 MB | ~5 % (6 s window) | 0.12 s, rc 0 |
| 1214148605 "Animated Forest Snow 4k" | video | 1 | 359 MB | 79 % (5 s window) | 0.32 s |
| 1081733658 "Customizable Module Visualizer" | web | 10 (CEF) | ~1.3 GB summed | ~100 % summed | 5.2 s, then CEF abort ("pure virtual method called") |

The video figure is software decoding: the renderer configures libmpv without `hwdec`. The web run left its CEF
profile directory in `/tmp` (`/tmp/dd39e50d-…`, removed by hand); that observation is why the supervisor now gives
the child a private `TMPDIR` and deletes it after exit.

> **Amended 2026‑10‑02:** the reason given above is wrong.
>
> - linux-wallpaperengine *does* set `hwdec=auto`, but through libmpv's render API it never told mpv which display
>   it renders for, so mpv could not open a VA-API device for its OpenGL interop.
> - It fell back to `vaapi-copy`, which copies every frame back to RAM (this 1080p item), or to software decoding
>   (the 4K item above).
> - A local renderer patch passes the Wayland display (`~/linux-wallpaperengine`, branch
>   `zynith/vaapi-wayland-display`, f89e82c). See the [optimization log](../optimization-log.md), O‑14:
>   - the 4K video drops from **≈ 98 % to 13.9 %** of a core;
>   - a 1080p video drops from **37.1 % to 13.1 %**.

## Discovery

| step | first run | warm (runs 2–3) |
|---|---|---|
| Steam layout (roots, `libraryfolders.vdf`, assets) | 5.2 ms | 0.3–0.6 ms |
| 560 × `project.json` → catalog | 154.9 ms | 46.4–51.3 ms |

Result: 560 items, 539 renderable, 560 with a preview; 21 presets excluded. Runs on the provider's worker thread;
not measured inside the shell yet.

## Thumbnail source decode (cold, before the WebP cache)

120 items sampled, `decodeRasterImage` on the author preview:

| format | n | median | max |
|---|---|---|---|
| GIF (first frame) | 47 | 0.5 ms | 1.7 ms |
| JPEG | 74 | 12.4 ms | 19.4 ms |

Preview long edge: median 733 px, max 1600 px. The 64-card prefetch window therefore costs well under a second of
worker time on first browse (INFERRED from these per-image costs, not measured end to end).

## Supervisor (scratch harness against the real renderer, shell not involved)

| scenario | result |
|---|---|
| scene start → stop | *running* after 1509 ms (the 1.5 s grace); exit 710 ms after `stop()`, requested, rc 0; process group empty; scratch dir removed |
| web start → stop | 8 processes in the group at start; SIGKILL at 2080 ms (the 2 s deadline); group empty; CEF profile (in the scratch dir) removed |
| video, external `kill -9` | exit observed after 41 ms, reported as not requested |
| missing assets folder | exit during startup after 269 ms, rc 1, output tail `Cannot find a valid assets folder, resolved to "/nonexistent/assets"` |
| id `999999999999` / `../etc` / preset 3084897312 | rejected before any process: not installed / not a Workshop id / preset message |

No `linux-wallpaper` process remained after the run; `$XDG_RUNTIME_DIR/zynith/live-wallpaper/` was empty.

## Build notes

- The first incremental build after the `WallpaperConfig` layout change produced crashing config tests
  (`config_schema_roundtrip`: `std::bad_alloc`; `config_wallpaper_precedence`, `config_override_mutation`: SIGSEGV).
  After `meson compile --clean` (974 s at `-j 10`, niced) all three passed — the ADR‑0013 lesson recurring; those
  runs are not evidence of anything.
- Full suite after the clean build: 130 / 131, the one failure being the known `upower_charge_limit_integration`.

## In-shell transitions (2026-09-27, unlocked session, owner present)

**Method.** `transbench.py` (scratch) drives transitions over IPC and measures what is *on screen*: a 48×48 crop of
the empty focused workspace sampled with `grim` every ~17 ms (pixels hashed and averaged in memory, never stored).
**Blank** = samples showing niri's empty background (flat 64,64,64); **first visible** = first sample after the
request that differs from the old wallpaper and is not blank. Process/handover events come from the shell log.
A second sampler counted distinct `linux-wallpaper` process groups every 20 ms. "Stable" is omitted for animated
wallpapers (the crop never settles). Wallpapers: scene 1334736987 / 1350400986, video 1214148605, web 1081733658.

### Before (commit 1ba8cec + log markers)

| transition | n | first visible ms (min/med/max) | blank ms (min/med/mean/max) |
|---|---|---|---|
| static → live (scene) | 5 | 787 / 800 / 811 | 0 / 0 / 0 / 0 |
| live → static | 5 | 4 / 145 / 173 | 0 / 21 / 14 / 31 — a grey flash in 3 of 5 |
| scene → scene | 8 | (old wallpaper disappears at ~70 ms) | 756 / 785 / 800 / 874 (p95 874) |
| scene → video | 3 | — | 559 / 602 / 607 / 660 |
| video → scene | 3 | — | 970 / 1002 / 1011 / 1061 |
| scene → web | 2 | — | 1129 / 1209 / 1209 / 1289 |
| web → scene | 2 | — | 2413 / 2602 / 2602 / 2792 |

Dominant cost of every live→live blank: renderer startup inside linux-wallpaperengine (spawn → first frame
~750–880 ms for a scene), plus the old renderer's exit (40–150 ms scene, ~300 ms video, 2 s SIGKILL for web,
which ignores SIGTERM). Steam discovery, IPC and the shell's own work were each < 60 ms (spawn at +51–58 ms after
the request). The live→static flash: a fresh static surface starts transparent (`transition_on_startup`) and the
renderer exited ~40 ms after SIGTERM, so niri's grey showed through the first frames.

### Changes

1. **Poster frame.** During a switch the shell's own wallpaper surface comes back above the old renderer showing
   the *new* item's preview (opaque on its first frame, `Wallpaper::setTransientImage`, runtime-only); the old
   renderer is stopped only once the poster is on screen (`Wallpaper::settled()`); the new renderer later draws
   over it. Static → live transitions the static wallpaper to the poster while the renderer starts.
2. **Live → static** stops the renderer only after the static wallpaper's transition-in has finished.
3. **Stop grace** 2 s → 1 s (bounded by the web renderer; nothing that exits cleanly is cut short).

### After (same method, clean build)

| transition | n | first visible ms (min/med/max) | blank ms |
|---|---|---|---|
| static → live (scene) | 6 | 84 / 266 / 549 (poster) · live over it at ~820–1009 | **0** (all) |
| live → static | 5 | 154 / 180 / 215 | **0** (all) — flash gone |
| scene → scene | 6 | 23 / 116 / 145 (poster) · live ~0.93–1.03 s | **0** (all) |
| scene ↔ video | 1+1 | 100 / 5 | **0** |
| scene → web / web → scene | 1+1 | 113 / 90 | **0** · live reached at 1668 / 1925 ms (was 1367 / 2871) |

Total request → *live* frame is unchanged for scenes (renderer startup, outside Zynith); request → *new wallpaper
visible* dropped from ~0.8–2.9 s to ~0.1–0.25 s, and the blank interval is 0 in all 21 samples.

### Lifecycle checks (in shell)

| check | result |
|---|---|
| one-renderer invariant | max 1 process group over every sample: 1036 samples during carousel/rapid/crash, plus every transition run |
| carousel, 3 items, 10 s | rotated 3× in collection order at 11.8 s spacing (interval + startup) |
| rapid navigation, 6 selects 150 ms apart | settled on the last selection, nothing pending |
| crash (`kill -9`, uptime < 30 s) | static restored, error surfaced (message shows the renderer's last output line — cosmetic) |
| shell restart while live | renderer died with the shell (PDEATHSIG), live resumed on start, 1 renderer |
| persistence | `state.toml [wallpaper_live]` holds only ids; survived restarts |
| palette | `palette_source` switched to the item preview on each live start, cleared on live → static |
