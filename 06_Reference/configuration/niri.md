# `~/.config/niri/` — compositor configuration

## `config.kdl` (130 lines)

The entry point. Two things matter more than the rest:

```kdl
spawn-at-startup "sh" "-c" "~/.local/opt/noctalia/bin/noctalia || exec /usr/bin/noctalia"
include "rice/rules.kdl"
include "rice/binds.kdl"
include "rice/animations.kdl"
include "noctalia.kdl"        // generated palette — MUST be last
```

1. The **spawn fallback** is why a broken local build cannot leave the user without a shell.
2. **Include order is precedence.** Later nodes win, so the generated palette include stays last.

The stock 635-line configuration is preserved verbatim at `config.kdl.save`.

## `rice/rules.kdl` (144 lines)

Window rules (corner radius, clip, per-app opacity, blur, floating behaviour, privacy block-out) and layer rules.
Two layer rules matter:

```kdl
layer-rule { match namespace="^noctalia-backdrop"; place-within-backdrop true }
layer-rule { match namespace="^noctalia-notification$"; background-effect { blur true } }
```

## `rice/binds.kdl` (198 lines)

Keybindings ported from the owner's Hyprland configuration. Hardware keys use `cooldown-ms=50` (adjust) and
`repeat=false` (toggles) to cap how fast a held key can spawn `noctalia msg`.

## `rice/animations.kdl` (71 lines) — generated

Written by the Motion plugin: `niri validate` first, then an atomic replace. Do not hand-edit; the next commit
from the panel will overwrite it.

## `noctalia.kdl` (32 lines) — generated

Palette export from Noctalia. Regenerated whenever the wallpaper or theme changes.

## Applying changes

```sh
niri validate && niri msg action load-config-file
```
niri also live-reloads on file change (mtime polling), but validating first avoids a broken config being loaded.
