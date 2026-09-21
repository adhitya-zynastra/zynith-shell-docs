# Executive Summary

**Zynith Shell** is a desktop environment for Fedora 44 built on the niri Wayland compositor and a locally patched
Noctalia 5.1.0 shell. It was developed live on the owner's daily-driver laptop between **2026‑09‑19** and
**2026‑09‑21**, in seven numbered phases, and is documented here at commit **`57debbc`**.

## What exists

A dark, glass, wallpaper-derived desktop where the entire chrome — bar, panels, notifications, OSD, lock screen,
wallpaper — is drawn by **one shell process** costing about **1.4 % of one core at idle**, with the whole desktop
stack (shell + compositor + audio + portals) at **332 MB PSS**.

The implementation is deliberately layered: a **configuration layer** (`rice.toml`, `rice/*.kdl`) carries the
design, two **Luau plugins** carry settings UI, and a **17-commit patch series** over pristine Noctalia carries
only behaviour that configuration cannot express. The Fedora package stays installed as a fallback, and Hyprland
remains a working alternate session.

## What was engineered, beyond appearance

- **A wallpaper browser** that prepares an entire collection as 384 px previews on open, promotes a
  direction-aware window around the focus to 768 px, and releases everything when it closes. Traversing 20, 50 or
  100 wallpapers costs an identical **18 decodes**, and the focused card renders with no perceptible upscaling.
- **A single animation system** with a three-tier duration hierarchy and long-tail easings, retargeting rather than
  restarting on interruption.
- **Lifetime-safe shared primitives.** The project's one serious failure — a use-after-free that took down the
  desktop chrome — was fixed structurally, with a regression test that fails against the old implementation.

## What this documentation is careful about

Every measurement carries provenance, and a set of numbers is explicitly marked **invalid**: an incremental build
after a header layout change produced a binary that crashed at startup and inflated every CPU reading taken from
it. Those figures are preserved in `03_Performance/benchmarks/contaminated-measurements.md` so they are never
mistaken for data. Where history cannot be recovered — most importantly, **any pre-project resource baseline** —
the documentation says **UNKNOWN** rather than estimating.

## What is not done

Morph transitions, the launcher redesign and its style variants, lock-screen recomposition and power controls, the
broad configurability architecture, folding settings into one surface, and the GTK template cost. All are listed as
**planned** in `06_Reference/future-work.md`; none is described as complete anywhere in this set.

## State at the time of writing

| | |
|---|---|
| Commit | `57debbc`, working tree clean, clean build |
| Tests | 118 / 119 — the single failure is third-party and pre-dates the project |
| Validation | `niri validate` ✓ · `noctalia config validate` ✓ |
| Stability | No crashes since the lifetime fixes, across ~40 apply cycles, 14 browse sessions and 40+ panel transitions |
