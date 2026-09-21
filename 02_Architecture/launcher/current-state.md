# Launcher — current state

## What exists

The upstream Noctalia launcher, configured through `[shell.launcher]` in `rice.toml`
(`compact`, `show_icons`, `categories`, `sort_by_usage`, `show_app_actions`) and restyled by Zynith only in small
ways: row corner radius raised to match the shared panel radius (`82fb4b0`), and the panel silhouette/reveal it
inherits from `PanelManager`.

It is reachable from its bar button or `Super+D`. Clicking empty bar space deliberately does **not** open it
(`[bar.default.dead_zone.actions] left = "none"`), which was a Phase 1 fix.

## Cost — the known hotspot

| State | noctalia | niri |
|---|---|---|
| Launcher open (idle) | 3.96 % | 1.65 % |
| Rapid open/close cycling | **7.73 %** | 5.48 % |

This is **the most expensive shell state measured**. The cause is that every open rebuilds the panel's scene:
`create()` constructs the whole tree, and app discovery plus icon resolution happen again. An open, idle launcher
is cheap; constructing it is not.

## Not yet done

The launcher redesign, style variants (the current design must remain selectable), configurability, and the
creation-cost optimization are all **planned, not implemented** — see `06_Reference/future-work.md`. Candidate
approaches for the cost, none yet measured: retaining the scene between opens, keeping the app model resident,
incremental/event-driven discovery, and icon cache lifetime tuning.
