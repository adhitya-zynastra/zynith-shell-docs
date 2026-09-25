# Transient UI — Launcher, OSD, Notifications, Audio Feedback

**Written:** 2026‑09‑25 (third three-track batch, `b106c38`). **Validation:**
[`tracks-launcher-osd-notify.md`](../../03_Performance/benchmarks/tracks-launcher-osd-notify.md).

These four systems appear briefly and often. The batch made them one family visually (glass, accent disc,
wallpaper palette) without making them one subsystem: each keeps its own lifecycle, and no central event framework
was added.

```
 keys / IPC / D-Bus / PipeWire / logind
        │
        ├── LauncherPanel ───── PanelManager surface (built on open, destroyed on close)
        ├── *Osd feeders ─────► OsdOverlay (one primitive, OsdContent per event)
        ├── NotificationManager ► NotificationToast (one layer surface per output, cards inside)
        └── AudioOsd / NotificationManager ► SoundPlayer (in-process PipeWire, one stream per cue)
                        │
              shell::glass + palette roles + AnimationManager
```

## What I found before building anything

I had Claude inspect each system first. Most of the requested architecture already existed, and was left alone:

| Asked for | Already true |
|---|---|
| One shared OSD primitive fed by event-specific sources | `OsdOverlay` + `OsdContent`; volume, microphone, brightness, keyboard backlight, layout, lock keys, media, privacy, Wi‑Fi, Bluetooth, power profile, caffeine, night light, DND |
| OSD temporary, retargeting, no idle wakeups | surfaces created on `show()`, destroyed once every instance is idle; a new event updates content and restarts one hold; the hold is an event-loop timer (`40c1936`) |
| Launcher resources only while open | the scene tree is built in `create()` and destroyed by `PanelManager` after `onClose()`; async icon textures are trimmed and providers reset on close |
| No launcher indexing loop | the desktop-entry index is shared, inotify-driven, with a stat-only check on open |
| Audio and OSD from one normalized event | `AudioOsd` shows the OSD and plays the cue from the same PipeWire state change, with a cooldown |
| No sound daemon; bursts do not stack | `SoundPlayer` is in-process and refuses to restart a cue that is still playing |

## Launcher

`[shell.launcher].style = "zynith" | "classic"`. **Zynith is the default; Classic is the previous launcher and is
unchanged** — every Zynith path is behind the style flag, and the classic row paddings, gaps and icon sizes resolve to
the same values as before.

The Zynith style:
- **Search bar** — a taller, frameless input inside a tinted card with a search glyph and a primary hairline. It is
  always the focused element, so it carries the focus colour.
- **Selection** — a primary-tinted fill with a hairline primary edge and a `↵` glyph, instead of a solid primary
  block. Text never sits on solid primary, so the selection stays legible on any wallpaper-derived palette.
- **Key hints** — a footer of keycaps: navigate, open, Shift+Enter actions, F6 categories (when enabled), Esc.
- **Geometry** — `width` (640), `height` (540), `icon_size` (32), `density` (the shared `LayoutDensity`), `key_hints`.

Style is read in `create()`, and the scene is rebuilt on every open, so a style change lands on the next open. Icon
size and density also update live through `syncLauncherViewLayout`.

**Transparency, blur and tint are not launcher keys.** They are the shared Glass group (ADR‑0016: one owner per
property). A per-launcher opacity would give opacity two owners.

**Search** runs synchronously per keystroke through the existing providers. Measured at **0.23–0.28 ms per query**
over 80 applications (debug log `[launcher] query: N result(s) in X ms`), so I had Claude add no debounce, no worker
and no index: none would pay for itself.

## OSD

The OSD's surface decisions now come from `shell::glass::panelSurface()` — palette tint, border colour and the blur
gate — like every other translucent surface. `[osd].background_opacity` and `[osd].border` remain the single owners of
its fill alpha and border switch. The on-screen hold, previously a hard-coded 1.4 s, is `[osd].duration_ms`
(600–5000, default 1400).

**Event sources not added**, and why: Caps Lock / Num Lock already feed the OSD (`LockKeysOsd`); nothing new was
needed. A screenshot event has no source in the shell. Media track changes already feed `MediaOsd`.

## Notifications

Refined rather than redesigned: the card takes its tint and border colour from glass (critical keeps its Error
border), a glyph fallback sits on the same accent disc the OSD uses, and the preset caps visible cards at four
(`[notification].max_visible = 4` in `rice.toml`; overflow queues with expiry paused and follows).

**Bug fixed:** the card clamped its corner radius to 16 px, but the blur region used the unclamped radius — about
7 px with this rice's corner scale — so compositor blur showed as small squares outside the card's rounded corners.
Both now use one `toastCardRadius()`.

## Audio feedback

- **Microphone mute cue plays both ways.** The existing rule "play the mute cue only on unmute" is right for the
  speakers — a cue on a muted sink is silence — but wrong for the microphone: muting the mic does not silence the
  speakers, and a mic going mute is exactly the state worth confirming.
- **Burst coalescing is `SoundPlayer`'s.** I first had Claude add a 750 ms notification-cue window in
  `NotificationManager`; reading `SoundPlayer::playBuffer` showed a still-playing cue is already never restarted, so
  the new window duplicated a mechanism and was reverted before commit. What was added is a debug line per cue
  (`sound "x": playing (N stream(s) active)` / `still playing, not restarted`) so the behaviour is observable.
- Lock/unlock cues stay the `pw-play` hooks in `rice.toml`: one short process per real logind event, and moving them
  would have meant touching the lock path, which this batch does not.

## Amendment — 2026‑09‑26 (`e521a86`)

- **Key hints removed.** The footer was clutter at this size; `key_hints` is gone and the Zynith launcher also hides
  its scrollbar (scrolling unchanged).
- **Cue retrigger replaces cue dropping.** `SoundPlayer` now rewinds a still-playing cue instead of ignoring the
  new request, with retriggers ≥150 ms apart coalesced — one stream per cue, in step with the newest event. The
  "skipped/late" notification sounds I reported were dropped plays; stream start-up measured at 20 ms.
- **Mute cue before the mute.** `PipeWireService::setMuted` calls an injected hook; the application plays the cue
  and the mute is applied when it drains (event, not delay). A newer request cancels a pending mute.

## Settings

Personalization gained four groups, by ADR‑0017's split (appearance/behaviour here, function in the feature's own
section): **Launcher** (style, width, height, icon size, density, key hints, plus the moved show-icons / app-grid /
compact toggles), **OSD** (orientation, scale, opacity, border, duration — position, offsets, monitors and event
kinds stay in OSD), **Sounds** (shell sounds, volume, the three cue files — moved from Services → Audio, where
overdrive stays), **Notifications** (scale, opacity, border — placement, history and actions stay in Notifications).

## Security

No new command execution, paths or IPC. Notification text is rendered as before. The launcher launches through the
existing provider path. No network, no telemetry, no privileges.

## Known limitations

- Caps Lock, Num Lock, media and keyboard-layout OSD events were not triggered at runtime (see the validation record).
- The launcher's category row and grid tiles keep the classic look in the Zynith style.
- Volume ticks: 11 volume events 60 ms apart produced 7 cues — the existing cooldown, left as it was.
