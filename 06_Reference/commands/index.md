# Command Reference

## Shell control (`noctalia msg <verb>`)

Verbs used throughout this project. `noctalia msg --help` lists the full set.

| Verb | Purpose |
|---|---|
| `panel-open <id> [context]` | Open a panel. Ids used here: `control-center`, `launcher`, `wallpaper`, `session`. (`settings-open personalization` opens Personalization.) Context selects a section, e.g. `control-center bluetooth` |
| `panel-toggle <id> [context]`, `panel-close [id]` | Toggle / close |
| `config-reload` | Re-read `~/.config/noctalia/*.toml` |
| `config validate`, `config export full` | Validate; print the **effective** config after precedence |
| `wallpaper-get [connector]`, `wallpaper-set [connector] <path>` | Read / set the wallpaper |
| `wallpaper-next`, `wallpaper-previous`, `wallpaper-random` | Cycle |
| `volume-up`, `volume-down`, `brightness-up`, `brightness-down` | Trigger the OSD path |
| `bar-hide`, `bar-show`, `bar-toggle` | Bar visibility |
| `desktop-widgets-{show,hide,toggle}`, `dock-{show,hide,toggle}` | Surfaces |
| `color-scheme-get`, `color-scheme-set <source> …` | Palette source |

### Verbs Zynith added for the Zynith UI

Each prints JSON (or `ok`) for the UI to read; none is polled.

| Verb | Purpose |
|---|---|
| `weather-status` | What the shell already fetched: now (temperature, feels like, humidity, wind and direction, UV), the days (with sunrise and sunset) and every forecast hour |
| `screen-time [days]` | Total, per app, per hour (today) or per day |
| `charge-limit [on\|off]` | The battery's charge limit (UPower's preset), health and capacity; or turns the preset on or off |
| `brightness-status`, `brightness-rescan` | Every display's brightness (backlight or DDC/CI); look for DDC monitors again |
| `calendar-events [days]` | The synced calendars' coming events |
| `effects-status` | EasyEffects' output and input profiles and the active ones (`effects-profile-set` applies one) |
| `wallpaper-live-library`, `wallpaper-favorites`, `wallpaper-favorite` | The live library and favourites |
| `clipboard-pin`, `clipboard-image`, `clipboard-entry-text`, `clipboard-paste` | The clipboard panel |
| `settings-schema [section]` | The native settings registry: the sections, or one section's settings (kind, value, bounds or options, path, whether overridden) |
| `settings-set {"path": [...], "value": …}`, `settings-reset {"path": [...]}` | Change one native setting as the native Settings window would (a validated ConfigService override in `settings.toml`); refused while locked |

## Zynith UI (`~/.local/src/noctalia-lockfade/zynith-ui/ui/zynith-ui …`)

| Command | Purpose |
|---|---|
| `start`, `restart`, `status`, `log` | Run it; a failed load starts the last commit from a snapshot instead |
| `cmd control`, `cmd launcher [prefix]`, `cmd wallpaper`, `cmd close` | Keybinding socket: panels |
| `cmd action <action>` | Any action a bar gesture can name, e.g. `panel-toggle control-center audio` |
| `ipc panelRect` | Where the open panel sits (for captures cropped to it) |
| `settings [route]` | The Settings window |

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
