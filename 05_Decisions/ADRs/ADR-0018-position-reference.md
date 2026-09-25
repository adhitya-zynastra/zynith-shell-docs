# ADR-0018 — Positions name their coordinate space

**Status:** Accepted, implemented · **Date:** 2026‑09‑25

## Context
With a reserving left bar and two non-reserving centred bars, "centred" meant two different things depending on a
layer-shell detail — the exclusive zone — that no setting exposed. The centred bars and their panels sat 20 px right
of the screen centre, and I read that as a geometry bug. It was a coordinate-space choice made implicitly.

## Decision
1. A position's coordinate space is explicit: **`workspace`** (the compositor's usable area) or **`output`** (the
   whole screen), as `PositionReference`.
2. It is a property of the **bar**, and panels attached to a bar **inherit it**. A panel and its bar can never
   disagree about where "centre" is.
3. The OSD gets the same key, because it is the other surface that is centred near a bar.
4. **Default `workspace`** — the behaviour before this decision. Nothing moves on upgrade; the preset opts in.
5. No pixel compensation anywhere. The fix is choosing the zone the compositor already honours.
6. Panels opened without a source bar use a per-panel anchor bar (`[control_center].anchor_bar`) before falling back
   to the first bar.

## Alternatives
- *Always centre on the output* — rejected: it would silently move every existing non-reserving bar, and a bar that
  should avoid a docked panel would overlap it.
- *Offsetting centred surfaces by half the reserved width* — rejected: a compensation that breaks as soon as a second
  reserving surface appears.
- *A global "panel anchor bar" only* — already existed and forces every panel to one bar, which breaks clicking the
  media bar to get the media section at the top.

## Consequences
- Only non-reserving bars can use `output`; the setting is hidden while `reserve_space` is on.
- Notifications stay workspace-relative, deliberately.
