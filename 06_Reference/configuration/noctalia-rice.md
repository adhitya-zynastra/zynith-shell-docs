# `~/.config/noctalia/rice.toml` — the Zynith design layer

246 lines, hand-written, the main file to edit. Sections below are the ones Zynith actually uses; the schema is
`src/config/schema/config_schema.cpp`.

| Section | What it controls | Notes |
|---|---|---|
| `[audio]` | `enable_sounds`, `volume_change_sound`, `mute_sound`, `notification_sound` | `sound_volume` is **not** here — the GUI owns it |
| `[hooks]` | `session_locked`, `session_unlocked` → one-shot `pw-play` | fires on real logind events |
| `[theme]` | `source = "wallpaper"`, `wallpaper_scheme = "m3-tonal-spot"`, `mode = "dark"` | rejected schemes are documented in-file |
| `[shell]` | `font_family`, `corner_radius_scale`, translucency | |
| `[shell.panel]` | `transparency_mode = "glass"`, placements, `floating_offset`, `shadow` | |
| `[shell.session]` | `modal = true`, action list with shortcuts, `variant = "destructive"` | `modal` is a Zynith-added key |
| `[shell.launcher]` | `compact`, `show_icons`, `categories`, `sort_by_usage` | |
| `[bar.default]` | geometry, opacity, border, `capsule = false`, lane lists | **the bar's look** |
| `[[bar.default.capsule_group]]` | the `time` / `status` / `sys` clusters | each needs explicit `fill`/`opacity`/`padding` once `capsule = false` |
| `[widget.*]` | per-widget overrides (`clock`, `network`, `media`, …) | e.g. `[widget.network] show_label = false` |
| `[notification]`, `[osd]` | placement, opacity, scale | |
| `[control_center]` | `width`, `top_nav`, `hover_open`, `hover_open_delay_ms` | last three are Zynith-added |
| `[wallpaper]` | `carousel`, `transition`, `transition_duration` | `carousel` is read at panel construction — restart to switch |
| `[backdrop]`, `[hot_corners.*]` | overview backdrop, corner actions | |

| `[shell.animation]` | `enabled`, `speed`, `preset`, `niri_open/close/movement/overview` | The Zynith motion preset. Speed is **global**: shell = 0.8 × preset × speed, niri slowdown = 1/speed. Generates `niri/rice/animations.kdl` |
| `[shell.glass]` | `opacity` (custom mode only), `blur`, `blur_strength`, `tint`, `tint_role`, `tint_strength`, `border_role`, `border_opacity` | The shared surface model. `blur_strength` generates `niri/rice/glass.kdl` and affects windows too |

Both tables are also editable in **Zynith Corner** (`Super+Alt+A`); a change made there lands in `settings.toml` as
a user override, and Reset removes it so the value here shows through again. Until 2026‑09‑25 `[shell.animation]`
was forbidden in this file because the Motion plugin owned it through `motion.toml`; that arrangement is retired
(ADR‑0015).

After editing: `noctalia msg config-reload` (or `Super+Alt+R`). Check the result with
`noctalia config export full`, which shows values *after* precedence.
