# Coordinate Model — Output, Workspace, Bars and Panels

**Written:** 2026‑09‑25 (fourth batch). **Decision:** [ADR‑0018](../../05_Decisions/ADRs/ADR-0018-position-reference.md).

## The problem it fixes

My desktop has three bars: the main bar on the left edge (reserves 40 px), a media bar at top centre and a time bar at
bottom centre (both reserve nothing). The two centred bars — and every panel opened from them — sat **20 px to the
right of the screen centre**, and `Shift+Super+E` opened the Control Center against the left bar.

Both were one mistake each, not arithmetic errors:

- **Centring.** A layer-shell surface with `exclusive_zone = 0` is placed by the compositor inside the area left
  after other surfaces' reservations. The time bar was therefore centred between the left bar and the right edge:
  (40 + 1920) / 2 = 980. Its attached panels used the same zone, so they matched the bar — and were off-centre with
  it. The model was implicit; nothing let me say which centre I meant.
- **Shortcut anchoring.** A panel opened without a source bar attached to the *first enabled bar* in `bar.order`,
  which is the left bar.

## The model

Two coordinate spaces, chosen explicitly:

| Reference | Meaning | Layer-shell | Centre on this laptop |
|---|---|---|---|
| `workspace` (default) | the area left after other surfaces reserve space | `exclusive_zone = 0` | 980 |
| `output` | the whole output | `exclusive_zone = -1` | 960 |

`PositionReference` (`src/config/config_types.h`) is used by:

| Surface | Key | Notes |
|---|---|---|
| Bar | `[bar.<name>].reference` | Only for a bar that reserves no space (`barUsesOutputReference`); a reserving bar needs its zone |
| Panel attached to a bar | inherits the bar's | `PanelManager` gives the attached panel the bar's exclusive zone, so bar and panel always agree |
| OSD | `[osd].reference` | So an OSD over a screen-centred bar lines up with it |
| Desktop / lock-screen widgets | always output | positioned by absolute output coordinates (`exclusive_zone = -1`), unchanged |
| Floating centred panels (launcher) | always output | already `-1` when centred, unchanged |
| Notifications | always workspace | they must avoid bars on their edge; unchanged |

**Default is `workspace`**, the previous behaviour, so nothing moves unless configured. The Zynith preset sets
`reference = "output"` for the Time and Media bars and the OSD.

## Panel anchoring

A panel opened **from a bar** attaches to that bar and inherits its reference — unchanged. A panel opened **without
one** (shortcut, IPC) now resolves, in order:

1. `[shell].panel_anchor_bar` — the existing global override, which forces every panel to one bar;
2. the panel's own anchor — `[control_center].anchor_bar` for the Control Center;
3. the first enabled bar — the previous behaviour.

`Shift+Super+E` therefore opens the Control Center at the Time bar, bottom centre, once
`[control_center] anchor_bar = "Time"` is set — no hard-coded position.

## Caveats

- `rice.toml` can only *add* a key to a bar defined in `settings.toml` (deep merge). If a bar is later deleted in the
  GUI, a partial `[bar.<name>]` table left in `rice.toml` would define a default bar of that name.
- Floating (non-centred) panels anchored at the pointer compute output coordinates from the bar's margins
  (`surfaceOriginForOutputLocal`), which is exact for output-reference bars and off by the external reservation for
  workspace bars — as before; their layer surface is offset by the same amount, so they still line up.
