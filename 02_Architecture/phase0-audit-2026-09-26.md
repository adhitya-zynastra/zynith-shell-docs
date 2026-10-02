# Phase 0 Audit — Zynith as it actually runs (2026‑09‑26)

**Status:** audit record. Read-only: nothing in the shell or my configuration was changed by it. I wrote a
"master implementation prompt" that describes Zynith 1.0 and asked for its Phase 0 first. I had Claude inspect the
repository, configuration and running session instead of trusting the prompt or older documents. Where the prompt
describes something that is not true of this machine, this page says so.

Evidence tags: **VERIFIED** (read in source, measured, or observed in this session), **INFERRED**, **UNKNOWN**.

## 1. What Zynith is, concretely

| Prompt assumption | Reality | Tag |
|---|---|---|
| A Quickshell/QML shell | **One native C++ process**: Noctalia 5.1.0 (≈ 370 k lines, GPL‑3.0) with Zynith as a patch series on top — 7.0 k lines committed over 91 files (`a176ada` → `e521a86`) plus Batches 5–7 uncommitted (42 changed files, +2.0 k/−0.3 k, 19 new files). No Quickshell anywhere | VERIFIED |
| Reference videos in `videos/downloaded/` | `~/Videos/Downloaded/`: the same 6 videos and 3 source trees studied on 2026‑09‑26; nothing new | VERIFIED |
| A central state layer may be missing | Services are already shared singletons inside the process: one `SystemMonitorService` sampler (bar, Control Center, desktop widgets), one `MprisService` (bar, Control Center, lock), one `NotificationManager`, one `ThemeService`, one `ThumbnailService`. GPU/temperature probes are reference-counted (`retain`/`release`) and sample only while displayed | VERIFIED |
| matugen-based theming | The shell derives the palette itself (Material Color Utilities, `ThemeService`); `matugen` and `wallust` are installed but unused by Zynith | VERIFIED |
| Top bar: a thin top-edge centred island | Three island bars: a left rail (`default`), an auto-hidden top media pill (`Media`), a bottom time pill (`Time`). The prompt's direction is **a design decision for me**, not a fact | VERIFIED |
| Space Grotesk / Inter / Sora | Not installed. Montserrat (interface fallback) and JetBrains Mono are | VERIFIED |

## 2. Ownership map

| Layer | Owner | Notes |
|---|---|---|
| Compositor, windows, workspaces, input, outputs | niri 26.04 | Zynith generates only `rice/animations.kdl` and `rice/glass.kdl` (validated, atomic — ADR‑0015/0016) and `noctalia.kdl` (palette) |
| Shell UI, services, theme, wallpaper, lock UI, notifications server, tray watcher, polkit agent, NM secret agent, IPC | the shell process | D-Bus names owned: `org.freedesktop.Notifications`, `org.kde.StatusNotifierWatcher`, `dev.noctalia.Mpris`, `dev.noctalia.Debug` |
| Authentication | PAM via `src/auth` (upstream), `ext-session-lock-v1` | untouched by Zynith |
| Audio / network / Bluetooth / power / secrets | PipeWire + WirePlumber, NetworkManager, BlueZ, UPower + power-profiles, gnome-keyring | consumed over their APIs/D-Bus, not CLI parsing |

## 3. Files: configuration, generated, cache, state

| Category | Files |
|---|---|
| **Source configuration** (hand-edited) | `~/.config/noctalia/rice.toml`, `lockscreen.toml`, `palettes/`; `~/.config/niri/config.kdl`, `rice/binds.kdl`, `rice/rules.kdl` |
| **Generated** (shell-owned, overwritten) | `~/.config/niri/noctalia.kdl`, `rice/animations.kdl`, `rice/glass.kdl`; template outputs (kitty, starship `~/.cache/noctalia/starship-palette.toml`, GTK, …) |
| **User state / overrides** (Settings window) | `~/.local/state/noctalia/settings.toml` (+ `.lockscreen_widgets.stash`) |
| **Runtime state** (shell-owned) | `~/.local/state/noctalia/`: `notification_history.json` (64 KB), `clipboard/`, `screen_time.json`, `usage_counts.json`, `recently_used.json`, `wallpaper_shuffle.json`, `state.toml`, plugin caches |
| **Cache** | `~/.cache/noctalia/`: thumbnails (9.2 MB), weather/location JSON, avatar, logs |
| **Stray** | `~/.config/niri/monitor.kdl` (0 bytes since 10:24, not included), `config.kdl.save` (27 KB, 2026‑09‑19) |

The categories are already separate. The one blur is that `settings.toml` mixes my GUI choices with editor-saved
layouts (the lock-widget snapshot). Batch 7 made that reversible, not separate.

## 4. Subsystem classification (A–H)

| Class | Subsystems |
|---|---|
| **A — working, Zynith-owned** | motion roles and springs; design tokens and type roles; Glass surface model and niri generators; wallpaper carousel/browser with session thumbnails; `MorphTransition`; Zynith Control Center; lock composition preset and `session_actions`; bar position reference and attachment; Personalization section; Zynith launcher style |
| **B — working, needs refactoring** | Control Center sections other than Home (bespoke cards and titles); 67 raw `animate()` sites not on motion roles; the theme template engine (fails on every apply, §6); lock-widget rebuilds on reload while locked (crash fixed, risk class open); bars/dock/desktop widgets still on their own opacity keys rather than Glass; the bar spectrum's continuous redraw (§5) |
| **C — external, keep** | niri; the Noctalia core (config, panels, renderer, Wayland layer, MPRIS, notifications server, PipeWire/WirePlumber, NM, BlueZ, UPower, logind, PAM, polkit agent, tray); gnome-keyring |
| **D — external, wrap** | plugin catalogs fetched by git from remote sources at startup and every 6 h, with auto-update of installed plugins by default (§7); weather and IP-location over HTTP |
| **E — compatibility layer** | the Fedora `noctalia` package (fallback); Hyprland session config (fallback, never touched); the `dusk/identity` Luau plugin providing the lock identity widget |
| **F — broken** | GTK 3/4 template outputs cannot be written and the Emacs template hook exits 127 on every palette change (documented defect); Hangul text renders blank (documented); `upower_charge_limit_integration` test (third-party) |
| **G — dead / unused** | `matugen`, `wallust`, `swww` installed but unused by Zynith (`hyprpaper` may serve the Hyprland fallback — UNKNOWN); 11 of 21 built-in templates target software that is not installed; `monitor.kdl`, `config.kdl.save` |
| **H — duplicate** | **`nm-applet`** runs beside the shell's network UI and both are registered NetworkManager secret agents (plus GDM's greeter agent, which is normal); **`blueman-applet` + `blueman-tray`** beside the shell's Bluetooth UI and pairing agent — their notifications appear in the shell's history. Which agent answers a Wi‑Fi password or pairing request is UNKNOWN |

## 5. Performance baseline (this session)

| Measurement | Result | Conditions |
|---|---|---|
| Startup to UI | ≈ 0.52 s (`initServices` 343 ms, `initUi` 175 ms) | boot at 17:18:48; a git fetch of both plugin catalogs follows ≈ 5 s later |
| Idle, nothing open, **no audio playing** | **3 ticks / 10 s** (≈ 0.3 % of one core), measured twice | Batch 7 clean build, 14:51 |
| Idle while audio plays (4 streams) | **shell 6.2 %, ≈ 400 wakeups/s; niri 9.7 %** over 30 s | 19:3x; the bar's spectrum redraws at frame rate. niri's share includes browser compositing and is not attributed |
| Shell footprint | RSS ≈ 206 MB; 33 threads; ≈ 83 fds | stable over 40 Control Center cycles (Batch 7) |
| Control Center open → switch → close | 84–90 ms CPU per cycle | Batch 7 |
| Repeating timers while idle | notification-history cleanup 60 s; screen-time tick 5 s; plugin auto-update 6 h; location 6 h; system monitor sampler 1 s (a consumer is always on screen) | from source |

**The single largest steady-state cost is the bar spectrum during playback** (≈ 20× the quiet idle). Everything
else idles well.

## 6. Stability (this session)

- Three shell crashes on 2026‑09‑26, before the Batch 7 fixes
  ([postmortem](../04_Incidents/postmortems/2026-09-26-lock-reload-crash.md)). None since the 14:48 install.
- **A second power-off at 17:17:57** (boot `4f05138e…` ended without a shutdown sequence). The shell did not crash
  (no core dump). In the two minutes before:
  - at 17:16:08 a local-LLM app (Alpaca, flatpak) ended with an **8.4 GB memory peak** on this 15 GB machine;
  - the shell logged machine-wide stalls (a 660 ms main-loop dispatch, 183–349 ms buffer swaps);
  - Cloudflare WARP reported "hung daemon" at 17:17:53.
  Lock and unlock at 17:14 had worked normally. The cause of that power-off is **UNKNOWN**; memory pressure is
  plausible (INFERRED), not shown.

## 7. Security-sensitive areas

| Area | Finding | Tag |
|---|---|---|
| Lock / PAM / `ext-session-lock` | untouched by Zynith. The PAM path copies the password and clears the copy (`secureClear`). The text field's own buffer was not audited | VERIFIED / UNKNOWN |
| Core dumps | the shell never disables dumping (`PR_SET_DUMPABLE`). A crash while the lock screen holds a typed password is written to `/var/lib/systemd/coredump/` | VERIFIED (risk INFERRED) |
| Polkit agent | the shell is the only agent (`polkit_agent = true`); it draws administrator prompts, so spoofing resistance matters | VERIFIED |
| Secret agents | two NM secret agents for one user (shell + `nm-applet`) and two Bluetooth UIs | VERIFIED |
| Plugins | Luau code inside the shell process; catalogs fetched from remote git; **auto-update scope defaults to `All`** (startup + every 6 h) and my config does not override it | VERIFIED |
| Hooks and templates | user-configured shell commands on lock/unlock; template post-hooks run bash scripts on every palette change | VERIFIED |
| IPC | `noctalia msg` socket in `/run/user/1000` (directory 0700): any process running as me can drive the shell | VERIFIED |
| Personal data at rest | notification history (contents), clipboard history, screen time, launcher usage — kept in plain files | VERIFIED |
| Lock screen content | shows my name, avatar, current track and weather while locked (my choice in the preset) | VERIFIED |

## 8. Reference matrix (32 components)

Source of the reference column: [`design-research-2026-09.md`](design/design-research-2026-09.md) (videos v1–v6,
source trees Caelestia, Clavis, Ryoku). "—" means the references do not show it.

| # | Component | Strongest reference idea | Zynith today | Gap → synthesis |
|---|---|---|---|---|
| 1 | Top bar | Caelestia: bar as part of a screen frame, edges as gesture zones | three glass islands | origin: surfaces should grow from the bar; the island vs. top-edge direction is my decision |
| 2 | Centre island | Clavis Keystone: one object that becomes notification/OSD/media | Time pill (hover-open) | a Keystone-like shared object for transient feedback |
| 3 | Workspace indicators | — (only glimpsed) | bar workspaces widget | not researched |
| 4 | Dashboard | Caelestia: pulled from the edge (M1), horizontal pager (M2) | Control Center command bar + Home stage (Batch 7) | contextual state (load / battery) |
| 5 | Launcher | — | keyboard-first; apps, `calc`, `win`, `wall`, session, emoji, plugins, dmenu | settings search, network commands, workspaces, prefix-free calculator; research before building |
| 6 | Notifications | Clavis Keystone | glass toasts, actions, DND, history | grouping by app |
| 7 | Notification history | End4 rigid ≈ 80 ms sidebar (M9) | Control Center section | — |
| 8 | OSD | Clavis Keystone | unified glass OSD | origin from the source widget |
| 9 | Media | Imperative seed-grown popover, surface first (M10) | one MPRIS service → bar, Control Center, lock | artwork cache is `/tmp` only |
| 10 | Lock screen | Imperative idle ↔ authenticate (M6); Ryoku typography | "aperture" preset (editor-verified) | the two-state rack focus; contrast correction |
| 11 | Power menu | Caelestia session rail | modal session panel; lock capsule | — |
| 12 | Wallpaper picker | Ryoku accordion (M5) | orbit carousel + compact menu | — |
| 13 | Wallpaper transition | Imperative circular reveal from the chosen card (M7) | backdrop crossfade | seed reveal |
| 14 | Dynamic theme | Ryoku `Ink.legible` (L* correction), accent clamp | shell-derived Material palette, animated transition, templates | contrast correction; fix broken templates |
| 15 | Settings | Ryoku Hub | Noctalia settings + Personalization | Zynith Settings is paper-only (ADR‑0017) |
| 16–20 | Network, Bluetooth, Audio, Brightness, Battery/power | Imperative bar-pill popovers | Control Center sections, bar routing, OSD | duplicates with the applets (§4 H) |
| 21 | System monitor | Caelestia Performance tab | one shared sampler; demand-driven GPU probes | spectrum cost (§5) |
| 22 | Clipboard | — | clipboard panel + history | not researched |
| 23 | Overview | niri's own | backdrop for niri overview | — |
| 24–28 | Context menus, tooltips, empty/loading/error states | Clavis rules: "busy states never shift layout", "no supporting text unless needed" | exist per component; no shared rule | adopt the Clavis rules as written UI rules |
| 29 | Keyboard navigation | — (not visible in video) | roving nav, Ctrl+Tab, keyboard-first launcher | — |
| 30 | Animation | Clavis semantic roles; Ryoku tempo multiplier and reduced motion | motion roles + springs (Batch 6) | migrate remaining call sites |
| 31 | Startup / login | Ryoku NieR-style login (v3) | GDM; `src/shell/greeter` exists upstream, unused | a decision, not a gap |
| 32 | Shutdown / logout | — | session panel | — |

**Not done in this audit:** new open-source research (the prompt's 0C). The prompt's own rule 0J is to research
before each subsystem. Candidates, all **unread**: launchers (walker, anyrun, vicinae, fuzzel); notification daemons
(swaync, mako); telemetry (btop, Mission Center); other niri shells.

## 9. Architectural weaknesses (ranked)

1. **Duplicate agents** (NetworkManager secrets, Bluetooth) — undefined behaviour at the moment a password is
   needed.
2. **Plugin auto-update of third-party code by default**, plus a startup network fetch.
3. **Core dumps of a process that holds a lock password.**
4. **Always-animating spectrum** during playback: ≈ 6 % shell CPU plus compositor cost, all day when music plays.
5. **Template engine failing on every palette change** (wasted forks, log noise, a stale GTK theme).
6. **Lock-widget rebuilds under a live lock** — the crash is fixed, the risk class remains.
7. **Multi-monitor, suspend/resume, hotplug and real lock/unlock have never been tested**: no second display, and
   lock automation is excluded by my rule. These need me at the machine.
8. Uncommitted Batches 5–7 (≈ 5 k lines) — one disk failure from being lost.

## 10. Recommended order

1. **Commit Batches 5–7** after I have used them (they are tested; the risk is losing them).
2. **Hardening quick wins, small and measurable:**
   - decide the applets (disable `nm-applet` / blueman autostart, or the shell's agents);
   - disable core dumps for the shell;
   - set plugin auto-update to notify-only;
   - turn off the dead templates;
   - cap or pause the spectrum when nothing is visible, then re-measure.
3. **A guided test session with me at the machine:** real lock/unlock, wrong passwords, suspend/resume, lid,
   display blanking, shell restart while locked, and an external monitor if one is available.
4. **Design decisions I owe:** top-edge vs. island bars; font installation (Inter is packaged; Space Grotesk and
   Sora are not).
5. Then the prompt's Phase 3 work in order of gap size, each preceded by its own research (0J): launcher → contextual
   dashboard → notification grouping → Keystone-style transient object → lock two-state.

## Retrospective amendments

- **2026‑10‑02**: two statements above are wrong, found by the
  [current architecture audit](Zynith-Current-Architecture.md). Noctalia 5.1.0 is **MIT**, not GPL‑3.0 (§1; its
  `LICENSE` reads "MIT License, Copyright (c) 2026 noctalia-dev"). The clipboard history is **encrypted at rest**,
  not a plain file (§7; `index.enc`, `src/security/encrypted_file_store`). Notification history, screen time and
  usage counts are plain files as stated.
