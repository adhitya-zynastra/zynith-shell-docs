# Executive Summary

If you have ten minutes and you are about to inherit this project, read this page and then
[`06_Reference/maintenance.md`](06_Reference/maintenance.md).

## What Zynith is, and why I built it

**Zynith Shell** is my desktop environment for Fedora 44, built on the niri Wayland compositor and a locally
patched Noctalia 5.1.0 shell. The design work began roughly four to five months earlier; the **live
implementation** documented in these phases ran on my daily-driver laptop between **2026‑09‑19** and
**2026‑09‑21**, with **Claude Code as my engineering assistant**. It is documented here at commit **`c5dd72d`**.

I started it because I wanted a machine I actually control — one where I know what is running, know why, and can
change it. That began as frustration with Windows deciding what my hardware spent itself on, went through Fedora
and Hyprland, and turned into an engineering project at the point where I stopped asking how my desktop should
*look* and started asking how it should *behave*. I did not download someone else's rice, not out of principle
but because the setups I liked were built for other distributions and other package ecosystems; by the time I had
ported one, I would have rebuilt most of it. The full account is in
[`00_Project/origins.md`](00_Project/origins.md).

What I wanted concretely: a dark, glassy, wallpaper-derived desktop that I can explain line by line, that keeps
Fedora's stability underneath it, and that does not spend a noticeable fraction of the machine sitting still.

## The architecture, in one paragraph

Everything is deliberately layered so that each layer can be removed independently. A **configuration layer**
(`rice.toml`, `rice/*.kdl`) carries the design language; two **Luau plugins** carry settings UI; and a
**15-commit patch series** over pristine Noctalia carries only the behaviour that configuration cannot express.
The Fedora package stays installed as a fallback and Hyprland remains a working alternate session, so no single
bad build can leave me without a desktop. The result is a desktop whose entire chrome — bar, panels,
notifications, OSD, lock screen, wallpaper — is drawn by **one shell process** costing about **1.4 % of one core
at idle**, with the whole desktop stack (shell + compositor + audio + portals) at **332 MB PSS**.

## What I actually engineered, beyond appearance

- **A wallpaper browser** that prepares an entire collection as 384 px previews when it opens, promotes a
  direction-aware window around the focus to 768 px, and releases everything when it closes. Traversing 20, 50 or
  100 wallpapers costs an identical **18 decodes**, and the focused card renders with no perceptible upscaling.
- **A single animation system** with a three-tier duration hierarchy and long-tail easings, which retargets rather
  than restarting when an animation is interrupted.
- **Lifetime-safe shared primitives**, arrived at the hard way. The project's one serious failure — a
  use-after-free that took down the entire desktop chrome — was fixed structurally rather than patched around, and
  carries a regression test that fails against the old implementation.

## The problems that actually cost me time

| Problem | What it really was | Where |
|---|---|---|
| Shell vanished, machine powered off | Use-after-free in `Signal::emit` — dispatch iterated a snapshot while disconnect erased | [postmortem](04_Incidents/postmortems/2026-09-20-signal-uaf.md) |
| Startup crash + hours of bad CPU numbers | Incremental build mixed two `Signal::State` layouts; every measurement from that binary was an artifact | [postmortem](04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md) |
| Notifications completely dead | SwayNotificationCenter owned the D-Bus name — an environment conflict, not a shell bug | [postmortem](04_Incidents/postmortems/2026-09-21-notification-ownership.md) |
| Wallpapers looked soft when focused | Memory-efficient preview tier was being drawn where the display tier belonged | [postmortem](04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md) |

## What I took away from it

Three things changed how I worked for the rest of the project. **A shared primitive must state its lifetime
contract in its header** — the use-after-free was possible because `Signal` was half tombstoning and half erasing,
and each half was defensible alone. **A binary you did not clean-build is not evidence** — I spent hours reasoning
about a performance regression that existed only in a skewed build. And **when a subsystem that was verified
working goes dead, check ownership before reading code** — the notification outage was one `busctl` command away
the entire time.

## Current state

| | |
|---|---|
| Commit | `c5dd72d`, working tree clean, clean build plus recorded incremental rebuilds |
| Tests | 123 / 124 — the single failure is third-party and pre-dates the project |
| Validation | `niri validate` ✓ · `noctalia config validate` ✓ |
| Stability | No crashes since the lifetime fixes, across ~40 apply cycles, 14 browse sessions and 40+ panel transitions |

## What is not done

The launcher redesign and its style variants, lock-screen recomposition and power controls, the broad
configurable-shell layout model, the GTK template cost, and **Zynith Settings** — the system-wide settings hub, which
is designed on paper ([settings-information-architecture.md](02_Architecture/configuration/settings-information-architecture.md))
and not built. All are listed as **planned** in [`06_Reference/future-work.md`](06_Reference/future-work.md); none is
described as complete anywhere in this set. (Until 2026‑09‑25 this list also named morph transitions and folding
settings into one surface; those are done — see the Phase 6 amendments.) The Zynith security and privacy layer is **future architecture only** — nothing of it is implemented.

## How to inherit this

Every measurement in these pages carries provenance, and a set of numbers is explicitly marked **invalid** and
quarantined in `03_Performance/benchmarks/contaminated-measurements.md` so it can never be mistaken for data.
Where history cannot be recovered — most importantly, **any pre-project resource baseline** — the documentation
says **UNKNOWN** rather than estimating. If you are picking this up: start from
[`02_Architecture/configuration/precedence.md`](02_Architecture/configuration/precedence.md), because the fastest
way to break Zynith is to become a second writer of a file that already has an owner.
