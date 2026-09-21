# Phase 5 — Notifications and the Sound System

**Window:** 2026‑09‑20 03:02 (`phase5` backup) → 14:09 · **Commit:** `803664d`
("osd/notifications/sound: zynith pass").

## Goals

Restyle notifications in the Zynith language without a second notification store, and add an event-driven sound
vocabulary with no daemon, no polling and no per-event subprocess.

## Notifications

`notification_toast.cpp` — app identity leads as an **accent caption above the title** (the grey footer is gone);
card radius ≥ 16·scale to match the OSD and panels. Urgency, actions, grouping, timeout and history are untouched.
Glass comes from a niri layer rule on `^noctalia-notification$` with `background-effect { blur true }`.

## Sound

| Aspect | Decision |
|---|---|
| Assets | Synthesised WAVs in `~/.local/share/zynith/sounds/` (~124 KB), regenerable by `generate.py`. Soft sine blips with raised-cosine envelopes — no samples, nothing copyrighted |
| Playback | **In-process** via Noctalia's `SoundPlayer` on the existing PipeWire loop for volume/mute/notification |
| Lock/unlock | `[hooks] session_locked / session_unlocked` running one-shot `pw-play` — these fire on real logind events, so no polling |
| Master volume | Stays owned by Noctalia Settings (`audio.sound_volume` in `settings.toml`); `rice.toml` sets only `enable_sounds` and the cue paths |

## The mute-cue bug — three layers deep

- **Symptom:** the mute/unmute cue never played.
- **Investigation** found three independent causes stacked:
  1. upstream computed `playFeedback = volumeChanged && !muted`;
  2. a second caller (`application_ui.cpp` mixer callback) passed the default `playFeedback = true`;
  3. a stray volume event consumed the 70 ms cooldown before the mute event arrived.
- **Fix:** all mute paths converge in `AudioOsd::showOutput/showInput`. A mute-state change plays the cue **only on
  unmute** (playing into a muted sink is silence) and **bypasses** the volume cooldown, which was raised to 110 ms.
- **Verification:** recorded the sink monitor with `parec` — a 180 ms burst on unmute versus 40–60 ms volume ticks.
  **VERIFIED** at the time; the same technique is documented in `02_Architecture/notifications/pipeline.md`.

## Key-repeat anti-spam

`binds.kdl` gives hardware adjust keys `cooldown-ms=50` and toggles `repeat=false`, capping how fast
`noctalia msg` can be spawned by a held key.

## Retrospective amendments

| Later phase | Change |
|---|---|
| Phase 6 (`e9e27b0`) | Toast reveal/exit easings switched to the long-tail curves |
| Phase 6 (2026‑09‑21, config) | Notifications were **entirely dead** for a period — not a regression in this code, but a D-Bus ownership conflict with SwayNotificationCenter. See `04_Incidents/postmortems/2026-09-21-notification-ownership.md` |
