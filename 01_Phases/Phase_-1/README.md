# Phase −1 — The System Before Zynith

**Window:** everything before 2026‑09‑19 18:23 (the timestamp of `~/.config/rice-backups/20260919-182322-pre-rice/`,
the first backup Zynith took). **Evidence:** that backup directory, `rpm` metadata, and the surviving
`~/.config/niri/config.kdl.save`.

## Hardware (VERIFIED, unchanged since)

| Item | Value |
|---|---|
| CPU | Intel Core Ultra 5 125H — 14 cores / 18 threads, 400–4500 MHz |
| GPU | Intel Arc Graphics (Meteor Lake‑P), i915, GuC 70.53.0 / HuC 8.5.4 |
| RAM | 15 GiB |
| Swap | 8 GiB zram (lzo-rle) |
| Display | eDP‑1 — 1920×1200 @ 59.999 Hz, scale 1, 300×190 mm, no VRR |
| Storage | NVMe 953.9 GB + two removable USB devices |

## Software stack (VERIFIED via `rpm -q`)

Fedora Linux 44 · kernel 7.2.5‑200.fc44 · Wayland session · niri 26.04 · Noctalia 5.1.0 (distribution package,
unpatched) · Mesa 26.2.2 · PipeWire 1.6.9 · WirePlumber 0.5.17 · kitty 0.47.1 · Hyprland 0.56.2 ·
SwayNotificationCenter 0.12.6.

## Desktop as configured before the project

**RECOVERED** from `rice-backups/20260919-182322-pre-rice/`:

- `niri/config.kdl` — **635 lines**, essentially the stock niri template (its comments still carry the upstream
  wiki URLs) with `spawn-at-startup "noctalia"` added. For comparison the current `config.kdl` is **130 lines**,
  because Zynith moved rules/binds/animations into `rice/*.kdl` includes.
- `settings.toml` — 325 lines of Noctalia GUI state.
- `kitty.conf` (35 lines), `alacritty.toml` (4 lines).
- `niri/noctalia.kdl` — 32 lines, the generated palette export (already present: Noctalia was already theming niri).

The user also ran a **Hyprland + JaKooLit** configuration (`~/.config/hypr`), which is why
SwayNotificationCenter and a `swaync.service` user unit existed on the machine. That unit later caused the
Phase 6 notification outage — the pre-existing environment is directly responsible for one of the project's
significant incidents.

## Resource baseline before Zynith

**UNKNOWN.** No CPU, RSS, wakeup or GPU measurement was taken before the project began, and nothing in the
surviving artifacts records one. The earliest trustworthy numbers are Phase 6 clean-build measurements
(`03_Performance/`). Any "before Zynith" performance claim would be fabrication.

What *can* be said (INFERRED): the shell binary in use was the distribution build with the same feature set, so
idle cost was probably similar in order of magnitude — but this is reasoning, not data, and it is not used
anywhere in the performance tables.

## What motivated the project

**RECOVERED** from the project owner's initial brief (session record, 2026‑09‑19): the desktop was functional but
visually stock — the owner wanted a dark glass/blur aesthetic with a wallpaper-derived palette, their Hyprland
keybindings ported to niri, a redesigned launcher and bar, per-application transparency, and to do it *live* on the
real machine with validation and backups at each step rather than by copying someone else's rice.

Explicit constraints from that brief, honoured throughout: keep Hyprland intact as a fallback, back up before
changing anything, validate configuration before applying, never blindly copy a published rice.

## Screenshot

**UNKNOWN** — no screenshot of the pre-Zynith desktop survives. Screenshots in `07_Assets/screenshots/` all
postdate Phase 6.
