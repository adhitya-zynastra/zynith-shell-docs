# Postmortem — Notifications silently dead (D-Bus name ownership)

| | |
|---|---|
| **Severity** | High — no notifications and no notification sounds, for an unknown period |
| **Reported** | 2026‑09‑21 by the project owner |
| **Status** | Resolved |

## Symptom

Incoming notifications did not appear and their sound cues did not play. The shell was otherwise healthy, and
Phase 5's notification code was unchanged and previously verified working.

## Diagnosis

One command settled it:

```
$ busctl --user list | grep -i notif
org.freedesktop.Notifications   148597 swaync   adhitya :1.348  user@1000.service
```

**SwayNotificationCenter** owned `org.freedesktop.Notifications`, not Noctalia. D-Bus grants a well-known name to
exactly one process, so every notification in the session went to swaync and Noctalia never saw one.

`swaync` was started by a **systemd user unit** shipped with the package:

```ini
# /usr/lib/systemd/user/swaync.service
Type=dbus
BusName=org.freedesktop.Notifications
ConditionEnvironment=WAYLAND_DISPLAY
[Install] WantedBy=graphical-session.target
```

It was enabled for the owner's **Hyprland** setup and started in *any* graphical session, including niri.

## Root cause

An environment-level ownership conflict, not a shell bug: two notification servers installed, one of them enabled
session-agnostically.

## Fix

A drop-in that excludes it from the niri session only, so the Hyprland fallback keeps its notification daemon:

```ini
# ~/.config/systemd/user/swaync.service.d/10-skip-under-niri.conf
[Unit]
ConditionEnvironment=!XDG_CURRENT_DESKTOP=niri
```

```sh
systemctl --user daemon-reload
systemctl --user stop swaync.service
```

Noctalia claims the name on its next start.

## Verification

- `busctl --user list` shows **noctalia** owning `org.freedesktop.Notifications`
- single toast, 5-notification burst (stacked correctly), critical urgency — all render
- sound confirmed independently of audible output: recording the sink monitor during a notification captured a
  peak of 1228 and ~178 ms of non-silence

## Lessons

- A "shell bug" that contradicts a previously verified subsystem should prompt an **ownership check** of the
  relevant D-Bus name before any code is read.
- Dual-session setups (niri + Hyprland) need session-conditional units, not enable/disable toggles, or fixing one
  session breaks the other.
