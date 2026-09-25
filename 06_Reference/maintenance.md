# Maintenance Guide

Every command here was run on this machine during the project. Paths are absolute.

## Build

```sh
cd ~/.local/src/noctalia-lockfade/source
# first time only
meson setup ../build --prefix="$HOME/.local/opt/noctalia" --buildtype=release -Dtests=enabled -Db_lto=false

cd ~/.local/src/noctalia-lockfade/build
nice -n 15 meson compile -j 12 noctalia     # ~1-3 min incremental
meson install --quiet
```

## Clean build — **mandatory** after changing a widely-included header

```sh
cd ~/.local/src/noctalia-lockfade/build
meson compile --clean && nice -n 15 meson compile -j 12   # ~10 min, 986 targets
meson install --quiet
```
Skipping this after a layout change produced a startup crash and hours of invalid measurements — ADR‑0013.

## Restart the shell

```sh
kill $(pgrep -x noctalia | head -1); sleep 2
setsid -f "$HOME/.local/opt/noctalia/bin/noctalia" >/tmp/zyn.log 2>&1
# debug logging:
setsid -f env NOCTALIA_LOG_LEVEL=debug "$HOME/.local/opt/noctalia/bin/noctalia" >/tmp/zyn.log 2>&1
```
If the shell will not start, niri's `spawn-at-startup` fallback means logging out and in gives you the packaged
`/usr/bin/noctalia` instead of no desktop.

## Validate

```sh
niri validate                                   # niri config
~/.local/opt/noctalia/bin/noctalia config validate
~/.local/opt/noctalia/bin/noctalia config export full   # effective config after precedence
```

## Tests

```sh
cd ~/.local/src/noctalia-lockfade/build
meson test                       # 120 tests; 119 expected to pass
./signal_dispatch_test           # lifetime contract — MUST pass
./animation_reentrancy_test      # tick contract — MUST pass
```
`upower_charge_limit_integration` is a known unrelated failure (`04_Incidents/known-failures.md`).

## Verify the lifetime guarantees after touching `signal.h` or `animation_manager.*`

1. Clean rebuild (ADR‑0013).
2. `./signal_dispatch_test && ./animation_reentrancy_test`.
3. Confirm the Signal test still *fails* against the old implementation if you changed its semantics — a test that
   passes both ways proves nothing.
4. Exercise the field path: open the wallpaper browser, apply wallpapers while scrolling, toggle Light/Dark
   mid-transition. Watch `coredumpctl list`.

## Debug a crash

```sh
coredumpctl list | tail
coredumpctl info <pid>                       # module list + per-thread backtraces
coredumpctl dump <pid> -o /tmp/core
gdb -q -batch -ex "thread 1" -ex "bt 12" ~/.local/opt/noctalia/bin/noctalia /tmp/core
journalctl -b -1 -k | grep -iE 'segfault|i915|drm|oom'   # previous boot
```

## Performance measurement

```sh
# process CPU over a window, as % of one core
python3 - <<'PY'
import time
p=open('/proc/'+__import__('subprocess').run(['pgrep','-x','noctalia'],capture_output=True,text=True).stdout.split()[0]+'/stat')
PY
```
The full harness used for this documentation is described in `03_Performance/README.md`; it samples
`/proc/<pid>/stat`, `/proc/<pid>/task/*/status` and `smaps_rollup`, and drives input through a temporary uinput
device.

## Change configuration

| Want to change | Edit | Then |
|---|---|---|
| Bar layout, panel geometry, OSD/notification placement, palette | `~/.config/noctalia/rice.toml` | `noctalia msg config-reload` |
| Window glass, blur, per-app opacity, layer rules | `~/.config/niri/rice/rules.kdl` | `niri validate && niri msg action load-config-file` |
| Keybindings | `~/.config/niri/rice/binds.kdl` | same |
| Animation presets/speed | Motion panel (`Super+Alt+A`) | it validates and writes atomically |
| Lock screen | `~/.config/noctalia/lockscreen.toml` | reload |
| Anything already set in `settings.toml` | the Noctalia **GUI** | — (never hand-edit that file) |

## Recover from a broken build

```sh
cd ~/.local/src/noctalia-lockfade/source
git status --short          # what is uncommitted
git stash push -u           # park it
git checkout <last-good>    # e.g. 57debbc
cd ../build && meson compile --clean && meson compile -j 12 && meson install --quiet
```

## Regenerate this documentation

```sh
~/Documents/Dev/ZynithShell/scripts/build-docs.sh
```
