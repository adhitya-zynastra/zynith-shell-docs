# Quickshell for Zynith — study and migration analysis (2026‑10‑02)

**Status:** research record. I want Zynith to become more modular and easier to understand, primarily
Quickshell-oriented, and asked whether that is realistic before anything moves. Claude read the installed Quickshell
type files, the three reference shells and Noctalia's own reasons for leaving Qt, checked what niri offers, and
measured a minimal Quickshell instance on this machine. Nothing was migrated.

## 1. What Quickshell is, on this machine

| Fact | Value | Tag |
|---|---|---|
| Package | `quickshell-0.3.1-2.fc44` (COPR errornointernet/quickshell), `/usr/bin/quickshell` | VERIFIED (`rpm -qi`) |
| License | LGPL‑3.0-only AND GPL‑3.0-only | VERIFIED (`rpm -qi`) |
| Qt | links Qt 6.11 **private API** (`Qt_6.11_PRIVATE_API` in Quick, Gui, Qml, WaylandClient) | VERIFIED (`rpm -qR`) |
| Consequence observed | a second, older build at `/usr/local/bin/quickshell` (2026‑03‑01, built against Qt 6.10) **no longer starts** (`Qt_6.10_PRIVATE_API not found`) and is **first on PATH** | VERIFIED |
| Model | a QML runtime: `ShellRoot`, `PanelWindow` (layer-shell), `PopupWindow`, `FloatingWindow` (xdg), `Variants` (one instance per screen or model item), `Singleton`, `LazyLoader`, `PersistentProperties` (survive reload), live reload on file change, `IpcHandler` + `qs ipc call` | VERIFIED (qmltypes) |

### 1.1 What it provides that Zynith needs

| Need | Quickshell module | Notes |
|---|---|---|
| bars, panels, toasts, OSD, desktop surfaces | `PanelWindow`, `WlrLayershell` (layer, namespace, keyboard focus, exclusion), `Region` masks | per-screen via `Variants` |
| Settings window | `FloatingWindow` | can be a separate instance |
| blur behind surfaces | `Quickshell.Wayland._BackgroundEffect` | niri advertises `ext_background_effect_manager_v1` |
| workspaces | `Quickshell.WindowManager` (`Windowset`, projections) over `ext_workspace_manager_v1` | niri advertises it; niri-specific data (columns, overview state, window layouts) still needs niri IPC |
| session lock | `WlSessionLock`, `WlSessionLockSurface` | ext-session-lock |
| PAM | `Quickshell.Services.Pam` `PamContext`; password passed as a QML string via `respond(string)` | in-process vs subprocess: **UNKNOWN / REQUIRES VERIFICATION** (not in the docs) |
| polkit agent | `Quickshell.Services.Polkit` (`PolkitAgent`, `AuthFlow`) | |
| notifications server | `Quickshell.Services.Notifications` | |
| media | `Quickshell.Services.Mpris` | |
| audio | `Quickshell.Services.Pipewire` (nodes, volume, links, `PwNodePeakMonitor`) | **peak levels only: no FFT spectrum** |
| tray | `Quickshell.Services.SystemTray`, `Quickshell.DBusMenu` | |
| battery, power profiles | `Quickshell.Services.UPower` | |
| Bluetooth, Wi‑Fi | `Quickshell.Bluetooth`, `Quickshell.Networking` | NetworkManager backend; **no secret-agent type found** |
| idle | `IdleMonitor`, `IdleInhibitor` | |
| apps for a launcher | `DesktopEntries` | |
| colour extraction | `ColorQuantizer` | quantisation, not a Material 3 scheme |
| screen capture | `ScreencopyView` | whole outputs only on niri (no `ext-image-copy-capture`) |
| files, processes, sockets | `Quickshell.Io` (`FileView`, `JsonAdapter`, `Process`, `Socket`, `SocketServer`) | |

### 1.2 What it does not provide

FFT spectrum; a niri IPC model (Clavis wrote its own C++ module); clipboard history; a thumbnail cache; Material 3
scheme generation and app templates; config schema and validation; weather, calendar, screen time; brightness
(Clavis shells out to `brightnessctl`); the live-wallpaper renderer and its supervision; Wi‑Fi secret and Bluetooth
pairing agents; niri config generation. Zynith already has native implementations of all of these.

## 2. Measurements

| Measurement | Result | Conditions | Tag |
|---|---|---|---|
| Minimal Quickshell: one 1×1 transparent background-layer `PanelWindow` with one `Text` | config loaded in **0.33 s**; **RSS 117 MB**; 13 threads; 32 fds; **0 CPU ticks over 10 s idle** | 2026‑10‑02, `/usr/bin/quickshell -p <probe>`, run once for 15 s from a scratch directory, then its runtime directory removed | VERIFIED |
| Zynith today (everything) | RSS 128 MB (206 MB in Phase 0), 34 threads | `noctalia msg status` | VERIFIED |
| Noctalia's own claim about its v4 Quickshell shell | ≈ 300 MB per monitor; v5 about one sixth | [Announcing Noctalia v5](https://noctalia.dev/blog/announcing-noctalia-v5); not measured here | (claim) |

So an **empty** Quickshell instance already costs about what the **whole** current shell costs. A full
Quickshell shell's footprint on this machine is **UNKNOWN / REQUIRES VERIFICATION**; INFERRED to be several hundred
megabytes, consistent with Noctalia's figure. That matters on a 15 GB laptop that has already had one
memory-pressure power-off ([Phase 0 §6](phase0-audit-2026-09-26.md)).

## 3. Why Noctalia left Qt, and what that means here

Noctalia v5 is the native rewrite of a Quickshell shell. Its announcement names four reasons: memory (≈ 300 MB per
monitor), **every Qt update required rebuilding the shell** with frequent dependency mismatches, JavaScript and
binding overhead adding up, and inheriting a general-purpose toolkit's assumptions instead of owning the event loop
and renderer. The second reason is already visible on this machine (§1). Moving Zynith to Quickshell means walking
back across that line on purpose. It is worth doing only for what QML is clearly better at, which is **building
and changing UI quickly and declaratively**, and only with the costs designed around.

## 4. Risks of a Quickshell-based Zynith

| Risk | Evidence | Mitigation |
|---|---|---|
| Qt private-API coupling: a Fedora Qt update can break the shell until Quickshell is rebuilt | VERIFIED locally (§1) | keep the packaged build only; remove the stale `/usr/local` one; keep the native shell as a working fallback during migration |
| Memory | §2 | budget gate in the first spike; one UI process, not several; `LazyLoader` for rarely used surfaces; Settings as a separate instance that exits when closed |
| Secrets in JavaScript strings | `respond(string)` takes the password as a QML string; JS/QString memory cannot be wiped the way Phase 1 wipes Noctalia's buffers | **no password entry in QML**: lock, polkit, Wi‑Fi and pairing stay native (Architecture 2.0 §6) |
| Unbounded runtime logs in tmpfs | Ryoku `qsruntime.go` (a 4 GB tmpfs fill) | log level and a janitor in the session unit |
| Native crashes in Quickshell's own modules | Clavis isolated a screencopy crash in a separate process | avoid `ScreencopyView` in the main UI; separate processes for risky work |
| JavaScript doing hot work | all three references keep spectrum, metrics and niri parsing native | rule: no polling and no parsing in QML; hot paths in a C++ QML module |
| Licensing | Quickshell LGPL/GPL; reference shells GPL‑3.0; Noctalia MIT; the private repo's `main` holds a GPL‑3.0 LICENSE | the license decision is still mine (Phase 1 §1) and should be made **before** writing new code |
| Maturity | 0.3.x | pin the version; wrap Quickshell-specific types behind Zynith components |

## 5. What should stay native or external

| Component | Where | Why |
|---|---|---|
| niri | external | the compositor; Zynith only generates validated fragments and uses IPC |
| linux-wallpaperengine | external process, supervised | GPL‑3.0, heavy, crash-prone (CEF); one instance |
| Lock + PAM, polkit prompt, Wi‑Fi secret agent, Bluetooth pairing | **native, separate process** | secrets must be wipeable, non-dumpable, and isolated from plugins and UI crashes |
| Spectrum FFT, system sampler, niri event model | native C++ QML module (in-process) | ≥ 1 Hz hot paths; all references do this |
| Theme generation (Material 3), template engine, hooks | native helper (out of process) | already native; runs user commands, so isolate and bound it |
| Thumbnail cache (WebP, tiers, sessions) | native helper or C++ module | proven design (ADR‑0010); JS cannot match it |
| Config schema, validation, atomic writes | native | one writer per file |
| niri fragment writer | native helper | validate + atomic, already exists |
| PipeWire, NetworkManager, BlueZ, UPower, logind, polkitd, gnome-keyring | system services | consumed, never reimplemented |

## 6. The four options

A — **current** (native C++ monolith). B — **primarily Quickshell/QML** (everything in QML using Quickshell
built-ins, CLIs for the rest, as Caelestia). C — **Quickshell + native helpers** (QML UI and state, C++ QML modules
and small helper programs for what QML cannot do; lock and PAM in QML, as Clavis). D — **hybrid** (QML for UI and
shared state; hot paths in a C++ module; isolation-worthy work in helper processes; **secrets in a separate native
process**, which during migration is the existing shell reduced step by step).

| Criterion | A current | B QML only | C QS + helpers | D hybrid |
|---|---|---|---|---|
| Performance (frame work) | best (own renderer, measured) | worst (JS in hot paths) | good | good |
| Startup | ≈ 0.5 s to wallpaper (measured) | **UNKNOWN**, likely slower | **UNKNOWN** | **UNKNOWN**; secure core starts independently |
| RAM | 128–206 MB (measured) | highest (≈ 300 MB/monitor claimed) | high (≥ 117 MB baseline + content) | high + small native core |
| Idle CPU / wakeups | ≈ 0.3 % idle (measured) | polling-prone | event-driven if disciplined | event-driven by rule |
| Stability | one crash domain | one crash domain + Qt breakage | Qt breakage; lock in UI process | Qt breakage contained to UI; lock survives UI crashes |
| Security | hardened in Phase 1 | passwords in JS | passwords in JS | passwords never in QML |
| Maintainability / understanding | low: 324 k lines, hidden wiring | high for UI, chaos for system code | high | high, with a clear map (2.0 §2) |
| Extensibility | Luau plugins; C++ for anything visual | very high | high | high |
| Development complexity | very high per UI change (C++, 16 min clean builds) | low | medium | medium (two languages, a protocol) |

**Recommendation: D, built in stages, converging on "Quickshell UI + one native data module + a few helper
processes + a native secure core".** B is ruled out by the performance and security evidence. C is D without
the secret boundary, and that boundary is the one thing Phase 1 shows is worth paying for. A stays the shipping
shell until each replacement proves itself.

## 7. Gates for the first spike (before any surface is migrated)

A Quickshell spike (one bar + one panel, on niri, beside the running shell) must show, on this machine:

1. **RAM**: the UI process stays within a budget I set (proposed: ≤ 250 MB with one bar and one panel loaded).
2. **Idle**: ≤ 0.5 % of one core with nothing visible changing; no timers below 1 s when nothing animates.
3. **Startup**: wallpaper and bar visible in ≤ 1 s from spawn.
4. **Frame pacing**: panel open/close at 60 Hz without dropped frames (measured with the existing harnesses in
   `~/.config/zynith/scripts/benchmarks/`).
5. **Qt update drill**: documented recovery when Fedora updates Qt before the COPR rebuilds Quickshell.

If the spike fails 1–3, the answer is to keep the native shell and borrow only the *structure* from this study
(focused panels, multi-bar anchoring, one wallpaper state, settings app), which Architecture 2.0 is written to allow.
