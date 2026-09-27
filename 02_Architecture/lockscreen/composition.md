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

> **Amendment (2026‑09‑26).** The power controls described above were **never on the real lock screen**: a
> `settings.toml` layout saved by the editor in Phase 2 shadowed `lockscreen.toml`, and its `widget_order` did not
> list the new widget. The fourth-batch editor capture that "showed an application window" is why this went
> unnoticed. See *The preset was never live — and the way back* below.

## Zynith composition (fifth batch, 2026‑09‑26)

**Research, again, and what it changed.** The fourth batch kept my single vertical stack. Re-reading the same
references with the question "where does the eye land first?" gave a different answer: in the Material lock screen
the clock *is* the screen and everything else is a margin; Hyprlock setups that read well separate "what time is it"
from "sign in" by distance, not by boxes; Caelestia treats the lock as an atmosphere rather than a form. The brief
also named **Airlock**: I had Claude search for it and it could not identify a lock screen by that name (the nearest
result was *aerial-lock*, a Quickshell `ext-session-lock` client, which was not studied). Nothing below is taken from
it.

My fourth-batch stack gave the visualiser, avatar, time, date and password equal spacing, so the time did not lead,
and the visualiser — the most animated element — sat at the top, pulling the eye away from the clock.

**Composition** (`~/.config/noctalia/lockscreen.toml`, the preset; the editor writes user changes to
`settings.toml`):

```
                                                          ⏻ ⏾ ↻ ⎋    power: its own corner
                          22:27                     ← focal: large, light weight, no seconds
                   Saturday, 26 September           ← one quiet line
                          ( ◉ )
                       M.S. Adhitya                 ← who is signing in …
                    (  ••••••••••  )                ← … directly above where they authenticate
   ♪ media                                  ☁ 24°   ← periphery: small glass tiles, low emphasis
 ▁▂▃▅▃▂▁▂▃▅▆▅▃▂▁▂▃▂▁▂▃▅▃▂▁▂▃▅▆▅▃▂▁▂▃▂▁▂▃▅▃▂▁▂▃▅▆   ← ambient horizon, primary → tertiary, only while audio plays
```

| Decision | Setting |
|---|---|
| The time is the one focal element: larger, **light** weight, no seconds (a ticking seconds field is motion competing with the clock) | clock `format = "{:%H:%M}"`, new clock `weight = "light"` |
| The date is secondary: small, on-surface-variant | second clock widget, `weight = "regular"` |
| Identity sits directly on the password — one authentication group | identity `cy = 716`, login box `cy = 826`, `compact` layout, no unlock hint |
| The visualiser becomes a horizon: full width, bottom edge, no background, hidden when silent | `audio_visualizer`, `anchor = "bottom"`, `show_when_idle = false` |
| Media and weather are the periphery, bottom corners, glass at 0.30, 16 px radius (the outer-surface radius) | `anchor = "bottom_left"` / `"bottom_right"`, `hide_when_no_media = true` |
| Power leaves the composition for the top-right corner | `session_actions`, `anchor = "top_right"` |
| The wallpaper stays the picture: slightly more blur, a palette tint for legibility, never a capture of the desktop | `blurred_desktop = false`, `blur_intensity = 0.16`, `tint_intensity = 0.44` |

Every widget carries an `anchor`, so on another output size each keeps its distance from its edge or from the centre
instead of scaling ([`responsive-layout.md`](../layout/responsive-layout.md)). Every colour is a palette role.

**Code change for this:** the desktop/lock clock widget gained a `weight` setting (`light` / `regular` / `bold`,
default `bold` = the previous look), offered by the widget editor for digital clocks.

**Security boundary — unchanged.** `LockSurface`, the PAM conversation, `ext-session-lock-v1`, the login box's
password path and the `session_actions` widget are unchanged from `e521a86`. The composition is configuration plus
one generic clock setting. Two lock-adjacent changes were made, neither on the authentication path:
the login box's *editor settings schema* gained `anchor` (placement metadata that placement already read), and the
widget controller gained a reset command (below).

### The preset was never live — and the way back

**Finding (2026‑09‑26).** When I had Claude open the lock screen editor on an empty workspace, it showed my Phase 2
composition, not this preset: visualiser at the top, `HH:MM:SS`, media and weather as a centre strip, no identity
and no power controls. The cause is ownership. The editor saves its whole snapshot, `widget_order` included, as
`settings.toml` overrides. That table has existed since at least 2026‑09‑20 (it is in the `phase3b` backup). An
override `widget_order` replaces the preset's, and **a widget missing from the order is dropped**. So every widget
added to `lockscreen.toml` since Phase 2 has been invisible on the real lock screen — including the fourth batch's
power controls.

**What was changed.** `noctalia msg lockscreen-widgets-reset` clears only the `[lockscreen_widgets]` overrides; the
reload rebuilds from `lockscreen.toml`. It refuses while the editor is open, since the editor's exit would write
the old snapshot back, and while the session is locked. The shadowing and the reset are covered by
`zynith_config_ownership_test`.

**What was not done.** The reset was **not run**. It discards the saved Phase 2 layout, and choosing between that
layout and this preset is my decision, not the assistant's. Until I run it, the lock screen shows the Phase 2
layout — with this batch's `anchor` and `weight` keys merged in by the editor's exit during the test.

## "Aperture" composition (Batch 7, 2026‑09‑26)

**References, for ideas only.** Hyprlock setups separate "what time is it" from "sign in" by distance, not boxes.
The Material lock screen makes one clock the whole screen and pushes everything else to the margins. Caelestia
treats the lock as an atmosphere. Airlock still could not be identified (see the fifth batch). Nothing was copied:
no layout, asset or code.

**The composition.** One focal point, a quiet periphery, and the wallpaper as the picture:

```
                                                      ( ⏾ ⎋ ↻ ⏻ )   power: one glass capsule, top right
                    Saturday, 26 September          ← eyebrow above the time, small, muted
                     22:27                          ← focal: display face, light, tabular figures
                                                    ← negative space: the wallpaper
                            ( ◉ )
                     (   ••••••••   )               ← identity directly above a glass capsule field
   ♪ track · artist                        ☁ 24°    ← periphery written on the scene: no plates
 ▁▂▃▅▃▂▁▂▃▅▆▅▃▂▁▂▃▂▁▂▃▅▃▂▁▂▃▅▆▅▃▂▁▂▃▂▁▂▃▅▃▂▁▂▃▅▆▅   ← ambient horizon, only while audio plays
```

| Decision | Setting (`lockscreen.toml`) |
|---|---|
| The date moves **above** the time as an eyebrow line: the eye lands on the time and the date reads as its caption, rather than one more row of a stack | date clock `cy = 372`, `face = "interface"`, `weight = "regular"`, `on_surface` + shadow (quiet by size, not by colour — see below) |
| The time is set in the shell's **display** face, light, with **tabular figures** so the minute change does not shift the digits | time clock `face = "display"`, `tabular = true`, `weight = "light"`, box 760 × 200 |
| A deliberate gap between the time and the authentication group | identity `cy = 770`, field `cy = 872` |
| The password field is a **glass capsule** — a lens on the wallpaper, not a slab | `input_opacity = 0.26`, `input_radius = 28`, `center_password_text`, no hint, no login button; Caps Lock warning kept |
| Media and weather are **written on the scene** (text with a shadow, no plates) in the bottom corners | `background = false`, `shadow = true`, `hide_when_no_media = true` |
| Power is **one capsule** in the top-right corner | `session_actions` (restyled, below) |
| The visualiser stays the ambient horizon | unchanged from the fifth batch |

All colours are palette roles, and every widget is anchored (centre, bottom corners, top right).

### Code changes

| Change | Where | Notes |
|---|---|---|
| Clock `face` = `custom` (default, the widget's `font_family`) / `display` / `interface`, and `tabular` (default off) | `DesktopClockWidget`, factory, widget settings registry, `en.json` | Uses the `ui::type` faces, so a clock follows `[shell]` fonts without naming one; tabular figures via the `font_spec` feature suffix (Batch 6). Offered in the widget editor for digital clocks |
| `session_actions`: one glass capsule (surface 0.30, hairline, concentric radius) holding clear 38 px items; hover is a tone step; an armed action is the **only solid fill** (error role) | `desktop_session_actions_widget.cpp` | Styling only: the arm/confirm logic, the 4 s window, the refusal of `lock`/`command` rows and of custom command strings are unchanged |
| The editor saves only a **real** edit | `LockscreenWidgetsController::exitEdit` | It saved on every exit before, so opening and closing the editor froze the whole preset into `settings.toml`. That was how the Phase 2 override was born |
| `lockscreen-widgets-reset` keeps what it discards | `ConfigService::stashOverrideTable` | Writes `settings.toml.lockscreen_widgets.stash` next to `settings.toml` (never read as configuration) |
| `lockscreen-widgets-restore` | new IPC | Puts the stashed overrides back through the normal validated override commit |
| A crash on a config reload while locked | `LockscreenWidgetsHost` | See the [postmortem](../../04_Incidents/postmortems/2026-09-26-lock-reload-crash.md) |

**Security boundary — unchanged.** `LockSurface`, the login box's password path, the PAM conversation,
`ext-session-lock-v1` and the lock/unlock lifecycle have no changes in this batch; `git diff` shows no edit to
`lock_surface.cpp`, `lock_screen.cpp` or `lockscreen_login_box.*`. The login box is styled only through its existing
preset keys. The lock host fix touches widget bookkeeping (attach, detach and frame ticks of the widgets around the
field), not authentication.

### Making it live, and what the editor showed

> **Amendment to "What was not done" above.** On 2026‑09‑26 at 14:27 I had Claude run
> `noctalia msg lockscreen-widgets-reset` on the Batch 7 binary. The Phase 2 layout was not discarded: it is in
> `~/.local/state/noctalia/settings.toml.lockscreen_widgets.stash`, and `noctalia msg lockscreen-widgets-restore`
> puts it back. `settings.toml` has no `[lockscreen_widgets]` table since, so the lock screen follows
> `lockscreen.toml`.

**First editor capture** (on a verified-empty workspace): the time, the identity group, the glass field, the corner
periphery and the power capsule rendered as designed. But the eyebrow date was **nearly invisible**:
`on_surface_variant` on the light upper part of my wallpaper. The real lock adds blur and a 0.44 palette tint,
which would help, but that is not a reason to depend on it. The date is now `on_surface` with its shadow: quiet by
size, not by colour. Re-captured: legible.
- Full composition (editor, half size): [`lock-aperture-editor.png`](../../07_Assets/screenshots/lock-aperture-editor.png).
- The focal group: [`lock-aperture-focal.png`](../../07_Assets/screenshots/lock-aperture-focal.png).
- The power capsule: [`lock-power-capsule.png`](../../07_Assets/screenshots/lock-power-capsule.png).

**Editor exit without an edit:** both runs left `settings.toml` byte-identical (hash compared before and after) and
without a `[lockscreen_widgets]` table. This confirms the dirty-only save.

**Not verified:** the real lock screen. It was not locked by automation (standing rule). The editor draws the same
widgets but not the lock's blur, tint, password states, fade choreography or the unlock bridge. The reload-while-locked
crash fix is described in the postmortem and was not exercised at runtime.

