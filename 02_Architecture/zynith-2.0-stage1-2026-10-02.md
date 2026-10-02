# Zynith 2.0 — implementation record: Stage 1 and the migration (2026‑10‑02)

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
| Clipboard | Centred panel over the native shell's encrypted history. The shell gained `clipboard-history` (previews of at most 240 bytes), `clipboard-select` and `clipboard-remove`; a full payload leaves the shell only by going back onto the clipboard | `09974ee`; native `a2bf7b6` |
| Window behaviour | `window.behaviour` → `~/.config/niri/rice/layout.kdl` (as configured · scrolling · tiling-like), validated by niri before an atomic rename ([niri reference](../06_Reference/configuration/niri.md)). Tiling-like adds a centre-visible-columns bind (`Mod+Ctrl+C`); expand and centre-one-column were already in `binds.kdl` | `46770bd`, `51f1347` |
| Notifications | Server, popups, in-memory history and Do Not Disturb. **Off** (`notifications.server`), and it never takes `org.freedesktop.Notifications` from another owner. Tested on a private D-Bus session (`tools/notify-test.sh`) | `5c5f93f` |
| Wallpaper | Centred panel: images from the wallpaper folder and live wallpapers from the collection (new native `wallpaper-live-list`), applied through the core, so desktop, overview, lock screen and palette follow. Applying was **not** exercised, because it would have changed my wallpaper | `3695532`; native `4f68939` |
| Live wallpaper integration | Renderer patch: video wallpapers decode on the GPU without a copy (4K: ≈ 98 % → 13.9 % of a core; optimization log O‑14). Local branch of `~/linux-wallpaperengine`, not upstream | renderer f89e82c |
| Plugin security (native) | Luau capability permissions, decision 4 ([ADR‑0021](../05_Decisions/ADRs/ADR-0021-plugin-capabilities.md)); `dusk/identity` declared and granted `exec, files` | native `54204d2` |
| Network | Native `NetworkState` instead of `Quickshell.Networking` ([ADR‑0020](../05_Decisions/ADRs/ADR-0020-measure-builtins-before-adopting.md)) | `b136894` |
| Quick Settings | Volume, microphone, brightness (native `Backlight`: sysfs read, logind write), Wi‑Fi, Bluetooth, DND, night light, stay awake, microphone, power profile. The shell's own switches are read from its status | `9aa9f91`; native `f09531b` |
| Settings | Separate instance: Home, Experience, Appearance, Bars, Window behaviour, About | `3bad9da` |
| Native core in the UI | `NiriState` (one event-stream connection, emits only on change); `AudioSpectrum` (passive PipeWire monitor, demand-counted, sleeps on silence) | `43ed17d`, `133143c`, `e381281` |

### Decisions taken while building

These are implementation choices. They are not on the architecture's decision list.

- **The UI talks to the native shell over its IPC socket directly** (`CoreClient`, `7061d00`), not through
  `noctalia msg` processes. Each process had cost ≈ 60 ms of CPU; see the optimization log, O‑11.
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
- **Live-reload findings, recorded for whoever continues.**
  - A new QML file is visible to other files only after a second reload: Quickshell scans the directory once
    per reload.
  - A changed native plugin needs a restart, because a loaded plugin is not replaced.
  - A plain JS array as a `Repeater` model rebuilds every delegate on each change. That restarted every
    notification's entrance and timeout until the lists moved to `ScriptModel`.
- **The window-behaviour default is "as configured".** `shell.json` held `"scrolling"`, a default the prototype had
  written itself and that nothing had ever applied. Claude migrated it to `"config"` before switching the generator
  on, so my window behaviour did not change. My hand-written `layout {}` already matched the Tiling-like preset.
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

## Measured after the second batch

Prototype idle with nothing open: **0.03–0.05 % of a core once settled** (0.20 % in the first minute after a start),
2–4 wakeups/s, PSS 75–77 MB (Performance profile, after `b136894`; final run at 14:44 with every panel present). The live renderer, measured for reference in the same session: 4.95 % of a core and 201 MB RSS while
unlocked. **Its cost while the session is locked is UNKNOWN.** Measuring it needs a real lock, which I do myself:
`~/.config/zynith/scripts/tests/locked-renderer-cost.sh` walks through it. Whether to pause the renderer while
locked will be decided from that number.

## The migration (evening of 2026‑10‑02)

That evening I told Claude to stop gating and start the real migration: Quickshell draws every normal visible
surface, and the native shell becomes the engine behind them. I asked for implementation first and measurement
afterwards. Claude did the work below; what is on my screen changed with it.

### What changed hands

The handover switch is new: `~/.config/zynith/zynith.toml [surfaces]`. The native shell reads it and steps aside
per surface, and Settings → Zynith UI flips it back.

| Surface | Now drawn by | How the native one stepped aside | Keys |
|---|---|---|---|
| Bars | Zynith: my three native bars, recreated in `bars.toml`. A left rail, a time bar at the bottom and a media bar at the top; the last two hide while windows are open | native gate in `Bar::syncInstances` (`407729d`) | — |
| Launcher | Zynith: calculator `=`, windows `>`, wallpapers `@`, emoji `:`, session `!` | keybindings | `Mod+D`, `Mod+Alt+E` |
| Notifications | Zynith, as the only owner of `org.freedesktop.Notifications` | `[notification] enable_daemon = false` (rice.toml) | `Mod+Shift+N` |
| Control Panel | Zynith; replaces Home and Quick Settings | keybinding | `Mod+Shift+E` |
| Clipboard, wallpaper, session menu | Zynith | keybindings | `Mod+Alt+V`, `Mod+W`, `Ctrl+Alt+P` |
| OSD | Zynith: volume, microphone, brightness, keyboard layout | `[osd] enabled = false` (rice.toml) | brightness keys → `zynith-ui cmd brightness` |
| Desktop widgets | Zynith: my twelve widgets, recreated from the native layout in `widgets.toml` | `[desktop_widgets] enabled = false` (rice.toml) | — |
| Overview wallpaper | **live** (my new decision; the poster stays as the fallback) | generated `rice/wallpaper.kdl` | — |

- **Still native:**
  - the lock screen (see below);
  - the dock, which the earlier decision keeps out of the critical path;
  - the window switcher, screenshot annotation and the native Settings GUI (`Mod+T`).
- **Zynith Settings** opens from the Control Panel's gear and from the launcher.
- **Startup:** the Zynith UI starts with niri from `config.kdl`.
- **Rollback:**
  - set a surface back to `"native"` in `zynith.toml`;
  - re-enable its rice.toml switch where it has one;
  - restore the keybinding from `~/.config/rice-backups/*-zynith-ui-*`.

### Foundations built for it

- **Configuration lives in `~/.config/zynith/*.toml`.**
  - It is read and written by a native `ConfigFile` type: TOML, atomic writes, live reload.
  - The Stage 1 `shell.json` was migrated once.
  - See the [configuration reference](../06_Reference/configuration/zynith.md).
- **Wallpaper-aware tokens.**
  - Surfaces lean toward the wallpaper's colour (`appearance.toml` tint), not grey.
  - Accent, contrast, edges, radius, text size and motion speed and style are all settings.
- **A keybinding socket (`CommandServer`).** `zynith-ui cmd …` reaches the UI in about 20 ms; `quickshell ipc`
  took about 100 ms. If the UI is not running, it falls back to the native panel.
- **Desktop-widget layout from the native shell.** It was read once, never written, so my composition carried
  over.
- **Native additions:** `weather-status`, `surfaces-sync`, and `windowList()`/`focusWindow()` on `NiriState`.

### What went wrong

- **Notification server across live reloads.** It survived a reload but the new UI generation did not attach to
  it, so for a moment notifications would have gone nowhere. Fixed by remembering ownership across reloads
  (`PersistentProperties`). Claude verified it: a notification sent after four reloads was delivered.
- **Two `FileView` pitfalls again.**
  - Emoji did not load until the file's path was set on first use.
  - A `for` statement is not allowed as a bare QML handler expression.
- **I locked the session during the OSD handover.** Claude stopped before writing anything, built Settings and
  desktop widgets in the meantime, and finished the handover after I unlocked. No configuration was written while
  I was locked.

### Not done yet

- **Lock screen UI in Quickshell.** This needs my decision. The session lock and PAM must stay native, but only the
  client holding the lock can draw on the lock surfaces, so QML cannot draw them from the UI process. The way that
  keeps both rules is a small native lock client that renders a Qt Quick (QML) interface with PAM in C++, the
  `zynith-secure` role from the architecture.
- **Live wallpaper on the lock screen.** The lock surface is opaque and belongs to the lock client, so this belongs
  with the item above.
- **A Zynith workspace/overview surface.** niri's overview is the compositor's own; a Zynith one would need window
  thumbnails through screencopy.
- **Measurement:** the full performance, stress and lifecycle pass, deliberately after the migration.

## Functional parity pass (night of 2026‑10‑02 → 2026‑10‑03)

Next I set a new floor: every migrated surface must keep what the native one could do, and then be better. I
added three things while it ran. The wallpaper carousel had to stay an option, with real motion. Nothing could be
hard-coded. And every bar widget menu had to work, whatever I choose to keep. Claude audited each native surface
against its QML replacement, then rebuilt what was missing. The commits are on `feature/zynith-ui` (`42be15a` …
`e574f67`) and `feature/zynith-core` (`bebce09`, `9a8d8c6`).

### The audit's gaps, and what closed them

| Surface | Missing after the migration | Now |
|---|---|---|
| Wallpaper browser | Installed/Favourites/Recent/Collection tabs, carousel rotation, static favourites, sort, per-screen | All of it, filtered from held state and refreshed by native change events (no delays). A carousel layout after the native arc, with choreography, beside a grid layout |
| Desktop widgets | The editor: nothing could be added, moved, resized or configured | An editor over the wallpaper itself (`Mod+Alt+W`): move with grid and centre guides, scale, rotate, lasso, duplicate, flip, layer order, hide, undo, copy/paste, a schema inspector, a live picker. Five new kinds (calendar, system, volume, session, button), an analog clock, visualizer wave and rings |
| Launcher | App actions, categories, pinned apps, auto-paste, `/calc`-style prefixes, my usage history | All carried over; native usage counts imported once |
| Clipboard | Pin, image preview, paste into the previous window, live refresh | Two panes: filters, pins, the selected entry whole (images as a data URI, nothing on disk), Enter pastes |
| Notifications | Queue beyond `max_popups`, persistent history, per-app filters | Queue, `[[filter]]` rules, history in a 0600 file, progress, inline reply, stack tags, swipe; history sections and collapsible groups |
| OSD | Lock keys, keyboard backlight, track changes, privacy, Wi-Fi/Bluetooth/profile/caffeine/night light/DND | Every native OSD event is forwarded to the UI (`OsdOverlay::show`), so all fourteen kinds show |
| Bars | 14 of the 34 native widget kinds; per-widget settings; gestures; capsule groups; named instances | The whole catalogue under native names and keys; `[widget.<name>]` and `.actions`; groups with accordions; per-bar corners, border, shadow, font, empty-space actions; Settings → Bars edits all of it |

My native bar configuration was carried over faithfully. `settings.toml` (the GUI's) overrides `rice.toml`, so the
effective left bar was the GUI's: the `g1` accordion, the status capsule and the clock variants. The hand
translation in the migration had dropped theme-mode, clipboard and the accordion; they are back. The previous
`bars.toml` is in `~/.config/rice-backups/20261003-005305-zynith-bars-native-import/`.

### Native additions

- **Change events to the UI** (`zynith::notifyUi`): the shell connects to the UI's socket without blocking and
  writes `event wallpaper | clipboard | lock on/off | osd {json}`. The UI no longer asks on a timer.
- **IPC:** `wallpaper-live-library`, `wallpaper-favorites`, `wallpaper-favorite`, `clipboard-pin`,
  `clipboard-image`, `clipboard-entry-text`, `clipboard-paste`.
- **`uiOwns()`** caches `zynith.toml` by modification time; OSD events ask it on every volume step.

### Motion

`Motion` now carries Material 3's expressive and emphasized curves (the family Caelestia and end-4 use, read from
their source in `~/.config/quickshell`), by role. `Anim` and `Glide` replace ad-hoc animations. One finding: my
machine runs the Performance profile while power saver is on, and that profile turned springs off, so focus
moves *jumped*. Lighter profiles now shorten motion instead of removing it.

### What went wrong

- **The UI failed to load twice**, each time for a few minutes, from QML errors that only show at load (a
  property named `left`, a missing import, capitalised property names, a read-only `implicitHeight`). Bars and
  notifications were gone meanwhile. `zynith-ui start` now detects a failed load and runs the last commit from a
  snapshot instead.
- **Every live reload removed the UI's socket.** Qt unlinks a local server's path when it closes, and the old
  generation closes after the new one listens. Keybindings then fell back to the native panels, which is probably
  why I found myself in the native wallpaper browser. The server now listens on a private name and renames it into
  place.
- **A niri layer rule for blur was wrong.** It blurred the whole surface, margins included, and overrode the
  Experience profile. It is removed; surfaces request blur for their own region, which niri honours.
- **Two captures showed my terminal**, before Claude switched to privacy-blurred and region-only captures. Both
  were deleted immediately.

### Not verified

- Pointer gestures in the desktop editor (drag, scale, rotate, lasso) and in the carousel (drag, fling): no input
  injection tool is installed. Keyboard and IPC paths were exercised.
- Plugin launcher providers (Luau): none of my enabled plugins has one, and the bridge is deferred.
- The lock screen in QML, and the live lock wallpaper, are next.

## Next

1. **The stage gate:** whether the prototype starts replacing native surfaces on my desktop (architecture Stage 3:
   one surface at a time, each with a parity checklist and a rollback). That is my decision.
2. The helper protocol (§4.2), to replace the interim `noctalia msg` calls.
3. Pausing the live renderer while locked, if the measurement shows a cost.
4. Panel cost in Balanced (≈ 1.6× native).
5. Desktop widgets (not started).

Still open from §18: removing the stale `/usr/local/bin/quickshell` needs my `sudo`, and the capability model for
Luau plugins is tracked as deferred.
