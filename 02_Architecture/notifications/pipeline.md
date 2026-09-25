# Notification Pipeline

> **2026‑09‑25 (`b106c38`):** card appearance moved onto the glass model, blur-radius fix, burst cap preset and
> cue behaviour — see [`transient-ui.md`](../transient/transient-ui.md). The pipeline below is unchanged.

```
 Application (notify-send, browser, …)
        │  org.freedesktop.Notifications  (D-Bus, session bus)
        ▼
 ONE owner of the bus name  ←── this is the single point of failure
        │
        ▼
 Noctalia NotificationManager  ── history store, grouping, urgency, DND, timeouts
        │                    └── SoundPlayer → PipeWire (in-process, no helper process)
        ▼
 notification_toast.cpp  → layer-shell surface "noctalia-notification"
        │
        ▼
 niri layer-rule: background-effect { blur true }   → glass toast
```

## The ownership constraint

D-Bus grants `org.freedesktop.Notifications` to exactly one process. On this machine
**SwayNotificationCenter** was installed as a *systemd user unit* (`swaync.service`, `Type=dbus`,
`BusName=org.freedesktop.Notifications`, `WantedBy=graphical-session.target`) from my Hyprland setup. It
started in every graphical session, including niri, claimed the name first, and Noctalia therefore never received a
single notification — no toast and no sound.

The fix is a systemd drop-in rather than disabling the unit, because the Hyprland fallback session still wants it:

```ini
# ~/.config/systemd/user/swaync.service.d/10-skip-under-niri.conf
[Unit]
ConditionEnvironment=!XDG_CURRENT_DESKTOP=niri
```

Full incident report: `04_Incidents/postmortems/2026-09-21-notification-ownership.md`.

## Sound

Cues are synthesised WAVs in `~/.local/share/zynith/sounds/` (regenerable via `generate.py` — no samples, nothing
copyrighted) played **in-process** by Noctalia's `SoundPlayer` on the existing PipeWire loop. Lock/unlock use
`[hooks]` with one-shot `pw-play`, because those fire on real session events from logind.

Anti-spam measures, all **VERIFIED** in source: volume steps carry a 110 ms cooldown; the mute cue plays on
*unmute* only (playing into a muted sink is silence) and bypasses that cooldown; hardware keys in `binds.kdl` use
`cooldown-ms=50` for adjust keys and `repeat=false` for toggles, capping `noctalia msg` spawns.

## Verification recipe

```sh
busctl --user list | grep org.freedesktop.Notifications     # must show noctalia
notify-send "probe" "hello"                                 # toast within ~1 s
# audio evidence, independent of speakers being audible:
parec -d "$(pactl get-default-sink).monitor" --raw --format=s16le --rate=48000 --channels=1 > /tmp/n.raw &
notify-send "sound" "cue"; sleep 2; kill %1
python3 -c "import struct;d=open('/tmp/n.raw','rb').read();s=struct.unpack(f'<{len(d)//2}h',d[:len(d)//2*2]);print('peak',max(map(abs,s)))"
```
Last run (2026‑09‑21): peak 1228, ~178 ms of non-silence. **VERIFIED**.
