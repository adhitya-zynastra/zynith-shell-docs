# Zynith 2.0 — the owner's corrections, 2026‑10‑03

I compared the Zynith bars with the native ones and found that hidden "smart" bars did not come back at the edge,
left a frosted patch where they had been, and that the workspaces looked inconsistent. I asked that every
pre-migration setting have a place, that the wallpaper change animate, and that the surfaces take their look from
the reference rices. Claude did the work below; commits are on `feature/zynith-ui` and `feature/zynith-core`.

## What was wrong, and why

| Symptom | Cause | Fix |
|---|---|---|
| A hidden smart bar did not return when the pointer reached the top or bottom centre | When a bar finished hiding, its window stopped updating at the same moment its input region switched to the edge strip, so the switch was never committed. The region stayed the bar's own rectangle, 4 px short of the screen edge. The strip was also only as wide as the bar (≈ 35 px for an empty media bar) | The input region follows where the bar is going; a hidden bar's surface touches the edge; the strip is `reveal_length` wide (480 px), and a workspace switch shows the bar briefly (the native `show_on_workspace_switch`) — `d4e7dd4` |
| A frosted block stayed where a hidden bar had been | The compositor blur request kept the bar's rectangle after the bar slid away (the earlier no-update state had hidden this) | The blur region is dropped while the bar is away — `a5a4704` |
| Workspaces: tall pill, medium pills, small and tiny dots | A faithful copy of the native widget | One geometry for every style: uniform cells, filled = occupied, ring = empty, one active marker that stretches between workspaces (Caelestia's trailing indicator), merged backgrounds for runs of occupied ones; five styles, every size, colour, label and motion a setting — `171cc13` |

## Every native option has a place

- **Bars:** thirteen native options had no equivalent (content scale, text weight, widget colours, bar-wide capsule
  thickness, radius, border and foreground, opposite-edge margin, centring reference, panel overlap, concave edge
  corners, contact shadow). All exist now and are on Settings → Bars — `78ec2ae`.
- **Native panels:** a hot corner or a native key asked the native shell for its Control Center or launcher even
  though Zynith draws them. The native panel manager now hands any panel whose surface Zynith owns to the UI
  (`event panel …`), and opens its own only when the UI is not running — `547685c`.
- **Launcher:** the native launcher's calculator is libqalculate (units, currencies); Zynith's was a small
  evaluator. The native providers are now reachable (`launcher-providers`, `launcher-query`, `launcher-activate`),
  so "100 usd to inr" and every plugin provider answer in the Zynith launcher. Prefixes, global search, usage
  sorting, icon size and origin badges are settings — `4e5b8ea`.
- **Notifications and OSD:** edge margins, layer, keep-dismissed, the remaining screen positions; OSD horizontal
  placement and side margin.

## The wallpaper change

- The palette now cross-fades over ≈ 650 ms instead of snapping (`[animation] palette_ms`).
- A new wallpaper grows as a circle from where it was chosen, over the old one and under the windows, then hands
  over to the native wallpaper — the Imperative transition measured in the design research (≈ 550 ms, ease-out) —
  `ae5be76`. Settings → Wallpaper also shows the native transition effects.

## Not verified

- Hover reveal and the reveal layer's stacking against the native wallpaper by eye: no pointer injection, and the
  reveal was checked from its own pixels. **UNKNOWN** until I look.
- A load failure during this work started the last commit automatically — the fixed fallback worked.
