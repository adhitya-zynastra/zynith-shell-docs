# System Layers

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Applications          kitty · Zen · VS Code · Spotify · …                 │
├───────────────────────────────────────────────────────────────────────────┤
│ Shell (Zynith)        bar · panels · notifications · OSD · lock screen ·  │
│                       wallpaper — one process: noctalia                   │
├───────────────────────────────────────────────────────────────────────────┤
│ Compositor            niri 26.04 — window management, layer-shell,        │
│                       window animations, blur/background-effect,          │
│                       screencopy, ext-session-lock                        │
├───────────────────────────────────────────────────────────────────────────┤
│ Display protocol      Wayland + wlr/ext protocols (layer-shell,           │
│                       screencopy, session-lock, data-control, …)          │
├───────────────────────────────────────────────────────────────────────────┤
│ Graphics              Mesa 26.2.2 → EGL / OpenGL ES 3.2 → i915            │
├───────────────────────────────────────────────────────────────────────────┤
│ Kernel                Linux 7.2.5 — DRM/KMS, i915 (GuC/HuC), zram         │
├───────────────────────────────────────────────────────────────────────────┤
│ Hardware              Intel Core Ultra 5 125H · Arc iGPU · eDP-1 1920×1200│
└───────────────────────────────────────────────────────────────────────────┘
```

## Responsibilities, and why the boundary sits where it does

| Layer | Owns | Explicitly does **not** own |
|---|---|---|
| **niri** | Where windows go, window open/close/resize animation, which surface is focused, exclusive zones, blur of layer surfaces, screenshots | Any shell chrome. niri draws no bar, no menu, no notification. |
| **noctalia (Zynith)** | Every piece of chrome, as Wayland **layer-shell** surfaces. One process, one GPU context, one event loop. | Window management. The shell asks niri for actions over IPC (`niri msg`) rather than implementing them. |
| **PipeWire** | Audio graph. The shell plays cues **in-process** on the PipeWire loop (no `paplay` per sound) and reads the spectrum for the bar visualiser. | — |
| **systemd (user)** | Service lifecycle for session daemons. Used by Zynith only to *exclude* SwayNotificationCenter from the niri session. | — |

**Why one shell process:** every panel is a layer-shell surface created by the same process, sharing one
`AnimationManager`, one `ThumbnailService`, one texture manager and one Wayland connection. This is the reason a
lifetime bug in a shared primitive (see `04_Incidents/`) could take down the entire desktop chrome at once, and
also the reason the whole shell idles at ~1.4 % of one core.

## Process inventory at idle

**VERIFIED** 2026‑09‑21 by PSS accounting over `/proc/*/smaps_rollup`:

| Process | PSS | RSS |
|---|---|---|
| pipewire | 99.6 MB | 108.4 MB |
| noctalia | 98.6 MB | 161.6 MB |
| niri | 56.8 MB | 105.8 MB |
| wireplumber | 19.8 MB | 36.1 MB |
| xdg-desktop-portal-{gnome,gtk,base} | 35.1 MB | 89.6 MB |
| **desktop stack total** | **332.3 MB** | **573.9 MB** |

The remainder of system memory use is application processes, not the desktop. See
`03_Performance/baselines/memory-floor.md`.
