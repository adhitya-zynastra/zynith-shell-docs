# `~/.config/noctalia/rice.toml` — the Zynith design layer

276 lines, hand-written, the main file to edit. Sections below are the ones Zynith actually uses; the schema is
`src/config/schema/config_schema.cpp`.

| Section | What it controls | Notes |
|---|---|---|
| `[audio]` | `enable_sounds`, `volume_change_sound`, `mute_sound`, `notification_sound` | `sound_volume` is **not** here — the GUI owns it |
| `[hooks]` | `session_locked`, `session_unlocked` → one-shot `pw-play` | fires on real logind events |
| `[theme]` | `source = "wallpaper"`, `wallpaper_scheme = "m3-tonal-spot"`, `mode = "dark"` | rejected schemes are documented in-file |
| `[shell]` | `font_family`, `corner_radius_scale`, translucency | |
| `[shell.panel]` | `transparency_mode = "glass"`, placements, `floating_offset`, `shadow` | |
| `[shell.session]` | `modal = true`, action list with shortcuts, `variant = "destructive"` | `modal` is a Zynith-added key |
| `[shell.launcher]` | `compact`, `show_icons`, `categories`, `sort_by_usage`; `style` (zynith/classic), `width`, `height`, `icon_size`, `density`, `key_hints` | the last six are Zynith-added; see `transient-ui.md` |
| `[bar.default]` | geometry, opacity, border, `capsule = false`, lane lists | **the bar's look** |
| `[[bar.default.capsule_group]]` | the `time` / `status` / `sys` clusters | each needs explicit `fill`/`opacity`/`padding` once `capsule = false` |
| `[widget.*]` | per-widget overrides (`clock`, `network`, `media`, …) | e.g. `[widget.network] show_label = false` |
| `[widget.<name>.actions]` | per-widget click/scroll actions (`left`, `right`, `middle`, `scroll_up`, …) | Zynith sets `[widget.clock.actions] left = "panel-toggle control-center home"`; upstream opens the calendar tab |
| `[notification]`, `[osd]` | placement, opacity, scale; `[osd].duration_ms` (Zynith-added); `[notification].max_visible = 4` (Zynith preset) | fill tint/border colour/blur come from `[shell.glass]` |
| `[control_center]` | `width`, `style`, `top_nav`, `hover_open`, `hover_open_delay_ms`, `density` | all but `width` are Zynith-added; `density` = `compact` / `comfortable` / `spacious`; `style = "zynith"` with `top_nav = true` gives the command bar and the Zynith Home (Batch 7, `control-center/panel.md`) — `classic` is the previous panel. Script: `noctalia msg control-center-style-set zynith|classic` |
| `[wallpaper]` | `carousel`, `carousel_card_width`, `transition`, `transition_duration` | `carousel` is read at panel construction — restart to switch. `carousel_card_width` (400–1400, default 760) is the *preferred* focused-card width; see `responsive-layout.md` |
| `[bar.<name>].reference`, `[osd].reference` | `workspace` (default) or `output` | Zynith-added; see `coordinate-model.md`. The preset puts the Time and Media bars and the OSD on `output` |
| `[control_center].anchor_bar` | bar a shortcut-opened Control Center attaches to | Zynith-added; preset `"Time"` |
| `[backdrop]`, `[hot_corners.*]` | overview backdrop, corner actions | |
| `[shell.animation]` | `enabled`, `speed`, `preset`, `niri_open/close/movement/overview` | The Zynith motion preset. Speed is **global**: shell = 0.8 × preset × speed, niri slowdown = 1/speed. Generates `niri/rice/animations.kdl` |
| `[shell.glass]` | `opacity` (custom mode only), `blur`, `blur_strength`, `tint`, `tint_role`, `tint_strength`, `border_role`, `border_opacity` | The shared surface model. `blur_strength` generates `niri/rice/glass.kdl` and affects windows too |

Both tables — and the Control Center and wallpaper-browser keys above — are also editable in **Personalization**
(`Super+Alt+A`); a change made there lands in `settings.toml` as a user override, and Reset removes it so the
value here shows through again. Until 2026‑09‑25 `[shell.animation]`
was forbidden in this file because the Motion plugin owned it through `motion.toml`; that arrangement is retired
(ADR‑0015).

After editing: `noctalia msg config-reload` (or `Super+Alt+R`). Check the result with
`noctalia config export full`, which shows values *after* precedence.

## `~/.config/noctalia/lockscreen.toml` — keys added by Zynith

The lock preset (`02_Architecture/lockscreen/composition.md`). Widget settings live under
`[lockscreen_widgets.widget.<id>.settings]`.

| Widget | Key | Values | Since |
|---|---|---|---|
| any | `anchor` | `center`, `top`, `bottom`, `left`, `right`, `top_left`, … | fourth batch (`responsive-layout.md`) |
| `clock` (digital) | `weight` | `light` / `regular` / `bold` (default) | fifth batch |
| `clock` (digital) | `face` | `custom` (default: the widget's `font_family`) / `display` / `interface` — the shell's type faces | Batch 7 |
| `clock` (digital) | `tabular` | `true` / `false` (default) — equal-width digits | Batch 7 |
| `session_actions` | `vertical`, `show_labels` | booleans | fourth batch |

**Ownership.** The editor writes a changed layout to `settings.toml` (`[lockscreen_widgets]`), which then shadows
this file. Since Batch 7 it writes only when something changed.

| Command | Effect |
|---|---|
| `noctalia msg lockscreen-widgets-reset` | clears the `settings.toml` layout so this file applies; keeps the discarded table in `settings.toml.lockscreen_widgets.stash` |
| `noctalia msg lockscreen-widgets-restore` | puts the stashed layout back |

Both refuse while the editor is open or the session is locked.

