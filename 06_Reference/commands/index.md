# Command Reference

## Shell control (`noctalia msg <verb>`)

Verbs used throughout this project. `noctalia msg --help` lists the full set.

| Verb | Purpose |
|---|---|
| `panel-open <id> [context]` | Open a panel. Ids used here: `control-center`, `launcher`, `wallpaper`, `session`. (`settings-open zynith-corner` opens Zynith Corner.) Context selects a section, e.g. `control-center bluetooth` |
| `panel-toggle <id> [context]`, `panel-close [id]` | Toggle / close |
| `config-reload` | Re-read `~/.config/noctalia/*.toml` |
| `config validate`, `config export full` | Validate; print the **effective** config after precedence |
| `wallpaper-get [connector]`, `wallpaper-set [connector] <path>` | Read / set the wallpaper |
| `wallpaper-next`, `wallpaper-previous`, `wallpaper-random` | Cycle |
| `volume-up`, `volume-down`, `brightness-up`, `brightness-down` | Trigger the OSD path |
| `bar-hide`, `bar-show`, `bar-toggle` | Bar visibility |
| `desktop-widgets-{show,hide,toggle}`, `dock-{show,hide,toggle}` | Surfaces |
| `color-scheme-get`, `color-scheme-set <source> …` | Palette source |

## Compositor (`niri msg …`)

| Command | Purpose |
|---|---|
| `niri validate` | Validate the KDL configuration — always before loading |
| `niri msg action load-config-file` | Reload |
| `niri msg outputs` | Output list, modes, scale |
| `niri msg action focus-workspace <n>` | Used in testing to reach a quiet workspace |

## Diagnostics

```sh
busctl --user list | grep -i notif           # who owns the notification name
coredumpctl list | tail                      # recent crashes
journalctl -b -1 -k | grep -iE 'segfault|i915|drm|oom'   # previous boot, kernel view
systemctl --user is-active swaync.service    # must be inactive under niri
pactl list sink-inputs | grep -E 'Corked|application.name'
grep '^shown_boxes' ~/.config/btop/btop.conf
```

## Build and test

See `06_Reference/maintenance.md` — that file is the authoritative copy of the build, clean-build, test and
recovery commands.

## Documentation

```sh
~/Documents/Dev/ZynithShell/scripts/build-docs.sh     # audit + charts + diagrams + DOCX + PDF
~/Documents/Dev/ZynithShell/scripts/audit-docs.py     # audit only
```
