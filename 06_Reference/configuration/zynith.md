# `~/.config/zynith/` — Zynith's own configuration

Zynith 2.0's configuration root. Map of the directory: `~/.config/zynith/README.md`.

| File | Written by | Read by | Notes |
|---|---|---|---|
| `shell.json` | the Zynith UI's `Config` service (only writer); the Settings app goes through it | Zynith UI (Quickshell) | Missing keys fall back to defaults, and a missing file is created with them. Sections: `experience`, `bars`, `panels`, `window`, `launcher`, `wallpaper`, `notifications`, `osd` |
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
