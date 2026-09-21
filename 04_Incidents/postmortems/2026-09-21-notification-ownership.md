# Postmortem — Notifications silently dead (D-Bus name ownership)

| | |
|---|---|
| **Severity** | High — no notifications and no notification sounds, for an unknown period |
| **Reported** | 2026‑09‑21, by me, during ordinary use |
| **Status** | Resolved |

## What I observed

Notifications simply stopped arriving, and their sound cues stopped with them. Nothing else about the shell was
unwell — the bar, panels and OSDs all worked — and I could not tie the failure to anything I had changed.

## What I initially suspected

A Zynith regression in the Phase 5 notification work, since that is the code I had touched most recently in that
area. That suspicion was wrong in an instructive way: the Phase 5 toast code was unchanged from the state in
which I had verified it working, which should have been the first clue that the problem was not in the shell at
all.

## What Claude investigated

I asked Claude to find out why notifications were dead before changing any notification code. It checked the
ownership of the D-Bus name first, and one command settled it:

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

I had enabled it for my **Hyprland** setup, and it starts in *any* graphical session, including niri.

## What the evidence showed

D-Bus grants a well-known name to exactly one process. swaync had claimed it, so every notification in the
session was being delivered to a daemon I was not looking at, and Noctalia never saw one. Nothing was broken in
the sense I had assumed; the notifications were being delivered correctly to the wrong program.

## Root cause

An environment-level ownership conflict, not a shell bug: two notification servers installed, one of them enabled
session-agnostically. This is a direct consequence of my decision to keep Hyprland installed as a fallback
([ADR‑0001](../../05_Decisions/ADRs/ADR-0001-niri-as-compositor.md)) — the fallback brought its own notification
daemon with it.

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

## Engineering lesson

- A "shell bug" that contradicts a previously verified subsystem should prompt an **ownership check** of the
  relevant D-Bus name before any code is read. I had a working subsystem and a dead symptom; that combination
  means something outside the code changed hands.
- Dual-session setups (niri + Hyprland) need **session-conditional units**, not enable/disable toggles. Disabling
  swaync outright would have fixed niri by breaking my fallback session, which defeats the reason the fallback
  exists.
- More generally: keeping a fallback session is not free. I still think it is worth the cost, but the cost is
  real and it arrived as a silent outage rather than as an error message.
