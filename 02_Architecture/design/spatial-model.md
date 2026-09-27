# Spatial Model ("Optics") — Origins, Edges, Direction

**Implemented 2026‑09‑26 (sixth batch).** Code: `src/shell/spatial/spatial_origin.h` (types),
`spatial_model.*` (functions), plumbing in `panel_manager.*` and `bar.cpp`. Tests: `spatial_model_test`.

"Optics" is not branding here. It is one engineering question, asked of every transient surface: **where did it
come from, which way does it travel, and what is its relationship to the rest of the interface?**

## What already existed, and stays

| System | Role in the model |
|---|---|
| Position references (ADR‑0018): output vs workspace | the coordinate spaces surfaces are placed in |
| `anchor_bar`, open-near-click, the centring rule | how `PanelManager` places a panel — unchanged |
| Widget `anchor` (responsive placement) | how persistent widgets keep edge distances |
| Attached-panel reveal direction | the direction rule the model reuses |
| `MorphTransition`, now also `MotionRect` | how a shared element travels between states |

No second positioning system was created. The model adds **meaning** on top of the existing coordinates.

## Origin

```
Origin { kind, sourceBar, sourceId, rect, edge }
kind:  BarWidget | BarArea | Command | Surface | None
rect:  output-local logical px — the same space as PanelOpenRequest's anchor — captured at request time
edge:  the screen edge the origin sits on (from the bar's position)
```

| Opened by | Origin recorded |
|---|---|
| A bar widget: a click, or resting on the clock (hover-open) | `BarWidget`, bar name, the widget's config name (or type), **the widget's own rectangle**, the bar's edge — one helper serves both paths |
| An empty part of a bar (dead-zone gesture) | `BarArea`, bar name, a 1 × 1 point at the pointer, the bar's edge |
| IPC `panel-toggle` / `panel-open`, which is also what keybindings run (Shift+Super+E, the launcher key) | `Command` — no spatial source |
| Internal opens (a Control Center card opening a section, the dock's launcher button) | `None` (unchanged call sites) |

`PanelManager` records the origin of every open request (`openOrigin()`) and logs it next to the existing "opened"
line, for example `origin bar-widget Time/clock @ 880,1170 160x30 edge=bottom reveal=up`.

**The origin is semantic, not a hard-coded coordinate.** It names the bar and widget. The rectangle is a snapshot
for geometry, not a position anything is pinned to.

## Direction

`revealDirection(edge)` is the attached-panel rule (`attached_panel::revealDirection`), **reused rather than
re-derived**, and a test checks the two agree for every bar position:
- from a bottom bar a surface rises;
- from a left bar it moves right;
- and so on.

## Depth

Depth is the surface hierarchy ([`surface-hierarchy.md`](surface-hierarchy.md)): scene 0 → floating 5, backed by
the layer-shell layer.

## What the model enables, and what it does not do yet

**Enabled:** a transient surface can know:
- its originating bar, widget or command;
- its coordinate space;
- the direction away from its origin's edge;
- its depth;
- its lifetime policy.

**Not done (Batch 7):**
- no surface yet derives its entrance *geometry* from the origin rectangle (the Control Center growing out of the
  clock widget, the OSD out of the volume widget);
- the OSD and notifications do not record origins: they are not panels and are not opened through
  `PanelOpenRequest`. The launcher is a panel and records `Command` when opened by IPC or a keybinding;
- the dock's launcher button still opens with `None`.
