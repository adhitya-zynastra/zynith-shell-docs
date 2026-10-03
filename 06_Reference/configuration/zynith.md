# `~/.config/zynith/` — Zynith's own configuration

Zynith 2.0's configuration root. Map of the directory: `~/.config/zynith/README.md`.

| File | Written by | Read by | Notes |
|---|---|---|---|
| `zynith.toml` | Settings → Zynith UI, or by hand | native shell (at start and on `surfaces-sync`) and Zynith UI | `[surfaces]`: which visible surfaces Zynith draws (`"zynith"`) or the native shell still does (`"native"`) |
| `appearance.toml` | Zynith Settings | Zynith UI | tint, accent, contrast, surface opacity, blur, edges, radius, font scale |
| `animation.toml` | Zynith Settings | Zynith UI | speed, style (fluid · crisp · calm), reduced motion |
| `experience.toml` | Zynith Settings, Control Panel | Zynith UI | profile, adaptive, `[overrides]` |
| `bars.toml` | Settings → Bars | Zynith UI | `[[bar]]`: edge, anchor, offset, margin, thickness, length, visibility, layer, reserve, screens, enabled, style (opacity, radius or `radius_top_left`…, border, `border_color`, `border_width`, shadow, padding, spacing, `font_family`, `font_scale`, `hover_highlight`, `capsule*`), `widgets` (start/center/end), `[bar.actions]` (empty space), `[[bar.group]]`. `[widget.<name>]`: a widget's settings in the native keys (`type` when the name is not a kind) and `[widget.<name>.actions]`: left right middle back forward scroll_up/down/left/right hover → an action (`hover` runs after `hover_delay` ms; resting anywhere on a capsule group counts) |
| `panels.toml` | Zynith Settings | Zynith UI | `[panels]`; `[launcher]` width, rows, position, density, layout (list · grid), categories, actions, auto_paste, terminal; `[control_panel]` modules (header shortcuts levels audio media monitor power calendar weather screen_time system notifications clipboard), width, spacing, module_style (plain · cards), session_button, anchor_bar (a bar id), shortcuts (native ids plus `custom:<name>`), shortcut_size (compact · regular · wide), shortcut_columns, shortcut_labels, tile_sizes, `[control_panel.custom.<name>]` (label, detail, icon, action, more, close), levels, mixer_apps, calendar_week_numbers, calendar_events, week_start, weather_forecast (daily · hourly), screen_time_range (1 · 3 · 14); `[osd]` duration, margin, position (top · bottom), hidden kinds |
| `notifications.toml` | Zynith Settings | Zynith UI | location, density, grouping, DND, sound, lock redaction, max_popups (the rest queue), history_persist, history_retention_hours, show_app_name, show_actions, monitor, `[[filter]]` (match, match_content, show_popup, save_history, play_sound, bypass_dnd, timeout_ms, urgencies) |
| `wallpaper.toml` | Zynith Settings | Zynith UI → `rice/wallpaper.kdl` | folder, browser `layout` (carousel · grid) and `card_width`, overview `live` or `poster`, lock |
| `widgets.toml` | the desktop editor (`Mod+Alt+W`) | Zynith UI | `[[widget]]`: type (clock label sticker audio_visualizer weather media_player calendar sysmon volume session_actions button), output, cx, cy, width, height, rotation, flip, hidden, reference, settings (native keys; `anchor` keeps an edge's distance) |
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
| `launcher.json` | launch counts and times, pinned apps, and whether the native history was imported |
| `wallpapers.json` | images applied recently (the shell keeps no such list for static wallpapers) |
| `notifications.json` | the notification history (mode 0600), when `history_persist` is on |

The notification history is written only when `history_persist` is on (the default, as the native shell kept it),
to a file only I can read; turning it off removes the file.
