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

I was also running a **Hyprland + JaKooLit** configuration (`~/.config/hypr`), which is why
SwayNotificationCenter and a `swaync.service` user unit were on the machine at all. That unit later caused the
Phase 6 notification outage: one of this project's significant incidents was lying in wait in the environment
before the project started.

## Resource baseline before Zynith

**UNKNOWN.** No CPU, RSS, wakeup or GPU measurement was taken before the project began, and nothing in the
surviving artifacts records one. The earliest trustworthy numbers are Phase 6 clean-build measurements
(`03_Performance/`). Any "before Zynith" performance claim would be fabrication.

What *can* be said (INFERRED): the shell binary in use was the distribution build with the same feature set, so
idle cost was probably similar in order of magnitude — but this is reasoning, not data, and it is not used
anywhere in the performance tables.

## What motivated the project

**RECOVERED** from my initial brief to Claude (session record, 2026‑09‑19). The desktop worked; it just looked
like nothing in particular. I wanted a dark glass/blur aesthetic with a wallpaper-derived palette, my Hyprland
keybindings ported to niri, a redesigned launcher and bar, and per-application transparency — and I wanted it
built *live* on the real machine, with validation and backups at each step, rather than by pasting in someone
else's rice and inheriting problems I could not explain.

That last point is the reason this documentation exists at all. A copied rice is not something you can maintain;
I wanted to be able to say why every line is there.

Explicit constraints I set in that brief and held to throughout: keep Hyprland intact as a fallback, back up
before changing anything, validate configuration before applying, never blindly copy a published rice.

## Screenshot

**UNKNOWN** — no screenshot of the pre-Zynith desktop survives. Screenshots in `07_Assets/screenshots/` all
postdate Phase 6.
