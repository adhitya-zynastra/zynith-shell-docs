# `~/.config/zynith/` — Zynith's own configuration

Zynith 2.0's configuration root. Map of the directory: `~/.config/zynith/README.md`.

| File | Written by | Read by | Notes |
|---|---|---|---|
| `zynith.toml` | Settings → Zynith UI, or by hand | native shell (at start and on `surfaces-sync`) and Zynith UI | `[surfaces]`: which visible surfaces Zynith draws (`"zynith"`) or the native shell still does (`"native"`) |
| `appearance.toml` | Zynith Settings | Zynith UI | tint, accent, contrast, surface opacity, blur, edges, radius, font scale |
| `animation.toml` | Zynith Settings | Zynith UI | speed, style (fluid · crisp · calm), reduced motion |
| `experience.toml` | Zynith Settings, Control Panel | Zynith UI | profile, adaptive, `[overrides]` |
| `bars.toml` | Zynith Settings | Zynith UI | one `[[bar]]` per bar: edge, anchor, offset, margin, thickness, length, visibility, layer, widgets, style |
| `panels.toml` | Zynith Settings | Zynith UI | `[panels]`, `[launcher]`, `[control_panel]` modules, `[osd]` |
| `notifications.toml` | Zynith Settings | Zynith UI | location, density, grouping, DND, sound, lock redaction |
| `wallpaper.toml` | Zynith Settings | Zynith UI → `rice/wallpaper.kdl` | folder, overview `live` or `poster`, lock |
| `widgets.toml` | by hand for now (seeded from the native layout) | Zynith UI | `[[widget]]`: type, output, cx, cy, width, height, rotation, flip, reference, settings |
| `window.toml` | Zynith Settings | Zynith UI → `rice/layout.kdl` | behaviour |
| `shell.json` | (Stage 1) | nothing since the migration | kept only as the source of the one-time migration |
| `plugin-grants.toml` | `noctalia msg plugins grant\|revoke` | native shell (Luau host) | `[grants] "author/plugin" = ["exec", …]`. Plugins can never write it ([ADR‑0021](../../05_Decisions/ADRs/ADR-0021-plugin-capabilities.md)) |
| `templates/palette.json` | hand-written | native theme engine (template `zynith_palette` in `rice.toml`) | Renders `~/.local/state/zynith/palette.json` for the UI |
| `scripts/` | hand-written | me, Claude | helpers, benchmarks, manual tests |

## `shell.json` keys that change something outside the UI

- **`window.behaviour`**: `config` (default) · `scrolling` · `tiling-like`. The main UI instance writes
  `~/.config/niri/rice/layout.kdl` from it, after `niri validate`; see the [niri reference](niri.md).
- **`notifications.server`**: `false` by default. When `true`, the UI owns `org.freedesktop.Notifications`, but
  only if no other process does. The native shell owns it today.
- **`experience.profile`**: `auto` follows the hardware recommendation and power (`experience.adaptive`), or names
  a profile: performance · balanced · enhanced · max.

## State the UI keeps (`~/.local/state/zynith/`)

| File | What |
|---|---|
| `palette.json` | the live palette (generated) |
| `launcher.json` | launch counts and times, for ranking. Nothing else |

The notification history is held in memory only and is never written.
