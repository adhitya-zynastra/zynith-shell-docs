# Zynith 2.0 — Stage 1 implementation record (2026‑10‑02)

This is the record of what was built for [Zynith 2.0](Zynith-Architecture-2.0.md). The architecture document
describes the target; this page describes what exists. On 2026‑10‑02 I accepted the architecture and told Claude
to start building it: Quickshell/QML for the UI, native C++ for the core, niri as the compositor. The first
target was a prototype that runs **beside** the native shell and takes none of its exclusive roles. Claude
wrote, ran and measured the code below. I made the decisions listed in the architecture document's §18.

## Where it lives

| What | Where | State |
|---|---|---|
| Prototype UI | branch `feature/zynith-ui`, worktree `~/.local/src/noctalia-lockfade/zynith-ui/ui` | pushed |
| Native QML module `Zynith.Native` | `ui/native/` (CMake), built to `~/.local/src/noctalia-lockfade/build-zynith-native` | pushed |
| Prototype config | `~/.config/zynith/shell.json`, written only by the prototype's `Config` service | live |
| Palette bridge | Noctalia template `zynith_palette` in `rice.toml` → `~/.local/state/zynith/palette.json` | live |
| One wallpaper state in the native shell | branch `feature/wallpaper-state`, commit `67f09d4` | **installed 2026‑10‑02** |
| Benchmarks | [Stage 1 spike](../03_Performance/benchmarks/zynith-ui-spike-2026-10-02.md) | — |

The prototype is started and stopped with `ui/zynith-ui start|stop|restart|status|log`.

- `zynith-ui ipc <method>` calls into it: `panel <id>`, `launcher`, `close`, `profile <name>`, `status`, `stats`, `apps <query>`.
- `zynith-ui settings` opens the Settings app.

**Rollback:** `zynith-ui stop`. The prototype owns no session role and writes nothing outside `~/.config/zynith`
and `~/.local/state/zynith`.

## What exists

| Area | Built | Commits |
|---|---|---|
| Tokens and visual language | `Theme` (semantic roles from the live palette, fallback map), `Type` (Inter, Space Grotesk, Tabler glyphs), `Metrics`, `Motion` (native roles scaled by the profile) | `7d82442`, `d10c01c`, `41728bc` |
| Experience profiles | `ExperiencePolicy`: one table of every quality and cost knob for Performance, Balanced, Enhanced and Max, plus per-knob overrides in `shell.json`. `Hardware` recommends a profile, and the choice stays mine | `7d82442` |
| Adaptive selection | Automatic mode follows power: at most Balanced on battery; Performance while power saving is on or the battery is low (below 20 %, cleared above 25 %). A chosen profile is never changed | `127f3b8` |
| Bars | Any number, from config. Edge + anchor + offset geometry; always / autohide / smart visibility; widgets per section from a registry | `7d82442`, `43ed17d` |
| Widgets | workspaces, clock, media, visualizer, audio, network, battery, quick | `7d82442`, `133143c` |
| Panels | One router per output with history. Home, Media, System, Network, Bluetooth; in-surface navigation; a surface stays warm for a profile-defined time and idle while hidden | `da26550`, `5f10738` |
| Launcher | Centred surface, fuzzy search over desktop entries, keyboard navigation, ranking by recent use. Apps are spawned by niri | `f5b1984` |
| OSD | volume, mute, keyboard layout; off by default while the native OSD runs | `9b10bdc` |
| Settings | Separate instance: Home, Experience, Appearance, Bars, Window behaviour, About | `3bad9da` |
| Native core in the UI | `NiriState` (one event-stream connection, emits only on change); `AudioSpectrum` (passive PipeWire monitor, demand-counted, sleeps on silence) | `43ed17d`, `133143c`, `e381281` |

### Decisions taken while building

These are implementation choices. They are not on the architecture's decision list.

- **Apps from the launcher are spawned by niri, not by the shell.**
  - Quickshell sets its own environment (`QSG_RENDER_LOOP`, `QML_IMPORT_PATH`, `QS_*`). An app started by the shell
    would inherit it.
  - Claude checked that a niri-spawned process runs in the requested directory and does not see
    `QML_IMPORT_PATH`.
  - Other compositors fall back to `Quickshell.execDetached`.
- **Quickshell's crash handler is disabled for the prototype.**
  - That handler relaunches a crashed instance under a rewritten command line and opens a report window. The
    relaunched copy is invisible to the launcher.
  - See the [reload-crash postmortem](../04_Incidents/postmortems/2026-10-02-zynith-ui-reload-crash.md).
- **Names that shadow Qt types are avoided in services.**
  - A singleton called `Palette` silently resolved to QtQuick's own type.
  - `Network` and `Bluetooth` collide with Quickshell modules unless those modules are imported under an alias.
- **The launcher's surface is not tied to a bar.** Panel geometry gained a `center` placement whose top stays
  fixed while the list grows.

## One wallpaper state (native shell)

Decision 3 of the architecture requires that the desktop, overview, lock screen and palette all derive from **one**
wallpaper state.

- `WallpaperState` (`67f09d4`) answers, per output, what still image stands for the wallpaper: the live poster, or
  the static path. The overview backdrop and the lock screen ask it, and it owns the palette source.
- Claude clean-built it: 130/131 tests pass, the remaining failure being the known `upower_charge_limit_integration`.
- I had Claude install it on 2026‑10‑02 after backing up the running binary to
  `~/.local/opt/noctalia/bin/noctalia.pre-wallstate-20261002`.

| Check | Result |
|---|---|
| Installed binary | `noctalia v5.1.0 (67f09d46bf0e)`. The previous one (`1ba8cec-dirty`) is a strict subset of it: both live-wallpaper commits are ancestors |
| Overview backdrop in Live mode | **VERIFIED**. Mean colour of the backdrop's corner: (16, 32, 62). The poster's corner is (12, 39, 87); the static wallpaper's is (150, 151, 153) |
| Palette source in Live mode | **VERIFIED**: `wallpaper-live-status` reports the poster as `palette_source` |
| Lock screen in Live mode | **UNTESTED**. Lock testing is not automated on this machine; it needs my own lock and unlock |

## Measured

The details and raw output are in the [spike benchmark](../03_Performance/benchmarks/zynith-ui-spike-2026-10-02.md).
These figures are from the same-conditions re-run under TuneD `powersave`:

- **Startup:** bar visible in 575–648 ms.
- **Memory:** PSS 77–79 MB idle.
- **Idle CPU:** 0.10 % in Performance and 0.65 % in Balanced, against the native shell's 2.7–2.8 % in the same minutes.
- **Panel open + close:** at parity with the native Control Center in Performance; **≈ 1.6×** in Balanced. This is
  the regression still open.

## What went wrong

- **The prototype crashed on live reload,** six times before the cause was found: a teardown-order bug in
  `NiriState`. Fixed in `e381281`. See the
  [postmortem](../04_Incidents/postmortems/2026-10-02-zynith-ui-reload-crash.md).
- **The first spike figures were wrong in two ways.** The crash-relaunched copies lowered the measured PSS, and the
  native panel reference came from a different power profile. Both are recorded in
  [contaminated-measurements.md](../03_Performance/benchmarks/contaminated-measurements.md). The spike script
  now records the platform profile and counts stray instances.
- **A screenshot caught application content.** During launcher verification, a capture was taken after a second
  toggle had already closed the launcher, so it showed my terminal. Claude deleted it at once. The later captures
  were crops of the surface only and were deleted after inspection.

## Next

From the architecture's list, in the order Claude is taking them:

1. Clipboard history.
2. The window-behaviour generator: `shell.json` → a generated niri fragment, including the honest Tiling-like
   preset.
3. Pausing the live renderer while locked.
4. Notifications and Quick Settings for the cut-over.
5. Wallpaper browsing in the new UI.

Still open from §18: removing the stale `/usr/local/bin/quickshell` needs my `sudo`, and the capability model for
Luau plugins is tracked as deferred.
