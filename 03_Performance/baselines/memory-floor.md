# Memory: the Real Floor

**Measured 2026‑09‑21, clean build, PSS via `/proc/*/smaps_rollup`.** PSS is used rather than RSS because RSS
double-counts shared pages and would overstate the stack by ~70 %.

| Process | PSS (MB) | RSS (MB) |
|---|---|---|
| pipewire | 99.6 | 108.4 |
| **noctalia (the shell)** | **98.6** | **161.6** |
| niri (the compositor) | 56.8 | 105.8 |
| wireplumber | 19.8 | 36.1 |
| xdg-desktop-portal-gnome | 19.5 | 42.1 |
| pipewire-pulse | 10.4 | 18.0 |
| xdg-desktop-portal-gtk | 10.0 | 28.4 |
| xdg-desktop-portal | 5.6 | 19.1 |
| gnome-keyring, dbus-broker, session plumbing | ~9.6 | ~30 |
| **Desktop stack total** | **332.3** | **573.9** |

## Interpretation

At the time of measurement the system reported ~5.7 GB in use. The desktop stack is **332 MB PSS** of that; the
remainder is applications — Zen ≈ 1.4 GB across processes, VS Code ≈ 600 MB, Spotify ≈ 520 MB, kitty 427 MB.

An aspiration of "~1.5 GB total desktop" is therefore already met several times over **by the desktop itself**;
what sits above that line is the user's application set. The realistic floor for this stack is **≈ 300–350 MB
PSS**, and pushing below it means removing PipeWire or the xdg portals rather than tuning Zynith. Noctalia is not
even the largest component — PipeWire is.

## zram

8 GiB zram device, `lzo-rle`. At one measurement 1.5 GB of swapped pages compressed to 555 MB (≈2.8:1); a later
sample showed 145 MB in use. Behaviour is healthy and **no change was made** to swap or zram configuration.

## Threads and descriptors

Constant across every stress run: **33–34 threads**, **83 file descriptors**. No growth was observed across 14
wallpaper browse sessions, 40+ control-center transitions and repeated launcher cycling.
