# ADR-0006 — Shell sounds play in-process on the PipeWire loop

**Status:** Accepted · **Date:** 2026‑09‑20 (Phase 5)

## Context
I wanted cues for volume, mute/unmute, notifications, lock and unlock, and screenshots — and I was not prepared
to spawn a process every time someone touches a volume key, which is the usual way this gets implemented.

## Decision
Volume, mute and notification cues play **in-process** through Noctalia's `SoundPlayer` on the existing PipeWire
loop. Lock/unlock use `[hooks]` with a one-shot `pw-play`, because they fire on real logind session events rather
than on UI interaction. Assets are synthesised WAVs (~124 KB total) regenerable by `generate.py`.

## Alternatives
- *`paplay`/`pw-play` per cue* — rejected for interactive events: a held volume key would fork a process per step.
- *A resident sound daemon* — rejected: another always-on process for a few short sounds.

## Consequences
- Cue latency is a buffer, not a process spawn.
- Anti-spam belongs in the shell: a 110 ms volume cooldown, and hardware keys rate-limited in `binds.kdl`.
- The master volume stays owned by the Noctalia GUI (ADR‑0003), so `rice.toml` only sets paths and the enable flag.
