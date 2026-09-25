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

Automated lock/unlock cycling is **deliberately not performed** — the risk of locking me out of a
daily-driver machine outweighs the coverage. Validation is visual plus the timing arithmetic that made the unlock
timer derive from the animation schedule.

## Planned

Recomposition as a single deliberate composition, power controls (sleep/reboot/shutdown/logout) with confirmation
for destructive actions, and per-element configurability. None implemented.

## Recomposition and power controls (fourth batch, 2026‑09‑25)

**Research.** Before changing anything I had Claude look at current lock screens: Hyprlock configurations (a
widget-per-element model — time, avatar, blurred input field), Caelestia's Quickshell lock screen (session lock with
a fluid, organic treatment), and Android 14's Material lock screen (one large clock as the focal point, date and
weather as one small secondary line, shortcuts pushed into the bottom corners). What I took from them is hierarchy,
not layout: one vertical axis, one dominant element, secondary information quiet, actions out of the axis.

**Finding.** My composition already follows that axis — visualiser, identity, `HH:MM:SS`, date, password pill, then
media and weather as one low strip — so it was kept. What it lacked was power controls and an answer to a failed
password.

| Change | Where | Notes |
|---|---|---|
| **Power controls** — suspend, logout, reboot, shutdown as a new `session_actions` widget | bottom-right corner, `lockscreen.toml` | Icon-only glass discs, low emphasis, placeable anywhere with the lock screen editor; `vertical` and `show_labels` settings |
| Logout / reboot / shutdown **arm first** | the widget | First press turns the button to the error role and shows "Press again to …"; a second press within 4 s runs it. The arm lapses on a one-shot event-loop timer. Suspend runs at once |
| **Failed password shake** | `LockSurface::shakeLoginPanel` | ~360 ms damped horizontal shake of the pill, after PAM has already answered |

**Security boundary.** The widget calls the existing `SessionActionRunner` built-in handlers (logind via
`systemctl`/`loginctl` argv). It refuses `lock`, `lock_and_suspend`, `command` rows and any row with a custom command
string — the power menu may run shell strings; the lock screen will not. It is given the runner only by the lock screen
host, so it cannot exist on the desktop; the desktop editor does not offer it. PAM, `ext-session-lock-v1`, the
password path and the lock/unlock lifecycle are unchanged. The existing login box's own session row (regular layout
only) is untouched and still off in my preset.

**Not tested by running a real lock**, by standing rule (lockout risk on a daily-driver machine). The composition was
checked in the lock screen editor, which renders the same widgets without locking; see the validation record.
