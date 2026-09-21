# Lock Screen

## Composition

Configured in `~/.config/noctalia/lockscreen.toml` (179 lines). Elements: wallpaper, visualiser, avatar/name,
time, date, password field, media, weather. The identity is deliberately **generic** — no hard-coded name, avatar
or location — because the configuration is meant to be shareable.

## Behaviour Zynith added (Phase 2)

| Element | Behaviour |
|---|---|
| Password row | Starts at opacity 0 while still keyboard-focused; fades in when there is text, an attempt in flight, or an error; fades out again if emptied |
| Status text | "Authenticating…" and failure messages render **inside the pill** as its placeholder with the input's invalid styling; the separate label shows only the Caps Lock warning |
| Entrance | Widgets fade in top-to-bottom by on-screen position (70 ms delay, 20 ms stagger, 210 ms ease-out, base values) |
| Exit | Pill fades first, then widgets recede; the exit **returns its end time** and the unlock is scheduled from it |
| Unlock bridge | A `ScreenVeil` per output, prepared with the lock background's exact source/blur/tint, fades out after the unchanged `unlock()`; a 2 s one-shot timer guarantees removal |

## Why the veil exists

niri refuses compositor actions while the session is locked (`allowed_when_locked`), so `DoScreenTransition` can
bridge *into* the lock but not out of it. The veil is drawn by the shell itself, on the unlocked side.

## Security

PAM, credential handling, the failure path, fingerprint logic and `ext-session-lock-v1` usage are **untouched**.
The only change to the sequence is that `unlock()` is deferred by the exit animation's real duration (0 ms when
animations are disabled). See `02_Architecture/security.md`.

## Testing policy

Automated lock/unlock cycling is **deliberately not performed** — the risk of locking the owner out of a
daily-driver machine outweighs the coverage. Validation is visual plus the timing arithmetic that made the unlock
timer derive from the animation schedule.

## Planned

Recomposition as a single deliberate composition, power controls (sleep/reboot/shutdown/logout) with confirmation
for destructive actions, and per-element configurability. None implemented.
