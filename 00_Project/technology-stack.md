# Technology Stack

All versions **VERIFIED** on 2026‑09‑21 via `rpm -q` / `uname -r` / `niri --version` on the target machine.

## Platform

| Component | Version | Role |
|---|---|---|
| Fedora Linux | 44 | Host distribution |
| Linux kernel | 7.2.5-200.fc44.x86_64 | DRM/KMS, i915 driver, zram |
| niri | 26.04 | Scrollable-tiling Wayland compositor; owns window management, layer-shell, animations, screenshots |
| Noctalia | 5.1.0 (Fedora RPM `noctalia-5.1.0-1.fc44`) as the patch base | Desktop shell: bar, panels, notifications, OSD, lock screen, wallpaper |
| Mesa | 26.2.2-6.fc44 | OpenGL ES / EGL on Intel Arc |
| PipeWire | 1.6.9-1.fc44 | Audio graph; shell sound playback and the CAVA spectrum feed |
| WirePlumber | 0.5.17-1.fc44 | PipeWire session manager |
| libdrm | 2.4.134-1.fc44 | DRM userspace |
| sdbus-c++ | 2.2.1-2.fc44 | D-Bus binding used by Noctalia and its tests |
| SwayNotificationCenter | 0.12.6-1.fc44 | **Installed but excluded from the niri session** — see incident report |
| Hyprland | 0.56.2-2.fc44 | Fallback session, untouched |
| kitty | 0.47.1 | Terminal |
| btop | 1.4.7 | System monitor |

## Languages and build

| Item | Detail |
|---|---|
| Shell source | C++23 (`-std=c++23`), built with GCC (`g++ 16.1.1` per btop's banner; compiler flags in `meson.build`) |
| Build system | Meson + Ninja, `--buildtype=release`, `-Db_lto=false`, `-Dtests=enabled` |
| Allocator | jemalloc (`-DNOCTALIA_USE_JEMALLOC=1`) |
| Plugin language | Luau (`plugin_api` ≤ 30) |
| Configuration | TOML (Noctalia), KDL (niri) |
| Documentation toolchain | python-docx, reportlab, matplotlib (installed user-local for this documentation set) |

## Notable third-party code vendored in the Noctalia source tree

**VERIFIED** from `meson.build` include paths: Luau (VM/Compiler/Ast), `material_color_utilities` (palette
generation), `fzy` (fuzzy matching for the launcher), `wuffs` (image decoding).

## Hardware target

| Item | Value |
|---|---|
| CPU | Intel Core Ultra 5 125H — 14 cores / 18 threads, 400–4500 MHz |
| GPU | Intel Arc Graphics (Meteor Lake‑P), i915 driver, GuC/HuC firmware loaded |
| RAM | 15 GiB |
| Swap | 8 GiB zram, lzo-rle |
| Display | eDP‑1, 1920×1200 @ 59.999 Hz, scale 1, 300×190 mm |
| Storage | NVMe 953.9 GB (SAMSUNG MZAL81T0HDLB) |

Every performance number in `03_Performance/` was taken on this machine; none of it transfers unchanged to
other hardware, particularly the GPU-dependent figures.
