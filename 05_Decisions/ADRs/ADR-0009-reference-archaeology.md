# ADR-0009 — Read reference shells for ideas, import no code

**Status:** Accepted · **Date:** 2026‑09‑20 (Phase 6)

## Context
Caelestia (`~/.config/quickshell/caelestia`) and ZynAku (`~/Documents/Projects/Rice/ZynAku_Shell`) are present on
the machine and solve similar interaction problems in QML/Quickshell.

## Decision
Read them as reference archaeology for *interaction and motion principles*; implement the equivalent behaviour
inside Zynith's existing C++ architecture. Import no code, no architecture, and no dependencies.

## What was actually taken
- Caelestia's `WallpaperList.qml`: the idea of a **path with attributes sampled along it**, an **odd visible count
  derived from screen geometry**, a bounded `cacheItemCount`, and starting at the currently-applied wallpaper.
- ZynAku's `WallpaperPicker.qml`: a centred highlight with a virtualised horizontal list.

## What was not taken
No QML, no Quickshell dependency, no file, and not Caelestia's flat `PathLine` geometry — Zynith uses an elliptical
orbit because the brief called for a curved trajectory.

## Consequences
Zynith stays a C++/TOML system with no Qt/QML runtime. Where a reference idea is used, the ADR or the source
comment says so explicitly rather than presenting it as original.
