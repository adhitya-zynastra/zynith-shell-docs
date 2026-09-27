# Live Wallpapers

Current as of branch `feature/live-wallpaper` (over `956765a`). Decision record:
[ADR-0019](../../05_Decisions/ADRs/ADR-0019-live-wallpapers-by-reference.md). Measurements:
[live-wallpaper benchmark](../../03_Performance/benchmarks/live-wallpaper.md).

## Why this exists

I wanted Steam Wallpaper Engine Workshop wallpapers as live desktop wallpapers for the Zynith showcase, inside the
Wallpaper browser I already use rather than as a separate tool. The constraint I set before any code was written:
browsing must stay as cheap as browsing static wallpapers, the 45 GB Workshop library must stay where Steam keeps
it, and only one live renderer may ever run. Claude surveyed the existing wallpaper code, the upstream
linux-wallpaperengine source and the library on disk, measured the renderer, and implemented the design below.

## Shape

```
Wallpaper panel (Static | Live tab)
   │  select / favourite / collection / carousel controls — never a command line
   ▼
LiveWallpaperController                   src/shell/wallpaper/live/live_wallpaper_controller.*
   ├── LiveWallpaperProvider (interface)  src/shell/wallpaper/live/live_wallpaper_provider.h
   │     └── WallpaperEngineProvider      …/wallpaper_engine_provider.*   discovery · previews · launch spec
   │           └── catalog functions      …/wallpaper_engine_catalog.*    Steam layout · project.json (unit-tested)
   ├── LiveRendererProcess                …/live_renderer_process.*       the one external renderer
   ├── Wallpaper (static backend)         setOutputExternallyManaged() hand-over
   └── ConfigService                      state.toml [wallpaper_live] · palette source override
```

The static wallpaper system is unchanged apart from being told, through the hook upstream already had for mpvpaper
plugins, when an output is owned by an external renderer.

## Where the content comes from

linux-wallpaperengine resolves a bare Workshop id only inside four hard-coded roots under `$HOME`
(`~/.local/share/Steam`, `~/.steam/steam`, the Flatpak and Snap roots) and finds its assets the same way. Steam can
keep Workshop content in any library folder, listed in `libraryfolders.vdf`. So the provider resolves the location
itself:

```
Steam roots ([wallpaper.live] steam_root, else the four standard ones; symlinks collapse)
  → library folders   (each root + every "path" in steamapps/libraryfolders.vdf or config/libraryfolders.vdf)
     → <lib>/steamapps/workshop/content/431960/<workshop id>     wallpapers
     → <lib>/steamapps/common/wallpaper_engine/assets             engine assets (first found)
```

and launches the renderer with the **absolute item folder** in `--bg` and an explicit `--assets-dir`. Nothing is
copied. On this machine there is one library; the layout resolves in under 6 ms.

**Discovery** reads every item's `project.json` on a worker thread (560 items: 155 ms first run, ~47 ms warm) and
keeps the catalog in memory for the shell's lifetime. `refresh(false)` re-walks only when a Workshop content folder's
mtime changed (Steam adds or removes a folder there on subscribe/unsubscribe). The folder name is the Workshop id —
253 of 560 `project.json` files carry no `workshopid` field. Kinds: 375 scene, 142 video, 22 web, 21 **presets**.
Presets (`"dependency"` on another item) are listed as unsupported: their files are referenced relative to their
own folder, which the renderer does not mount.

## Thumbnails

Every item ships an author preview (`preview.jpg` 289, `preview.gif` 270, `preview.png` 1 — none missing). The Live
tab hands those files, in place, to the shell's `ThumbnailService`: worker-thread decode, then a WebP per size in
`~/.cache/noctalia/thumbnails` keyed on *path + size + mtime + target size*. That is the persistent cache the static
browser already uses — no second cache was invented. A thumbnail is regenerated only when Steam updates the item's
preview. GIF previews contribute their first frame (the carousel never animates). Cold decode: GIF first frame
0.5 ms median, JPEG 12.4 ms median (previews are ~733 px on the long edge).

No renderer is ever launched for a thumbnail. linux-wallpaperengine's `--screenshot` renders a real surface for N
frames; it is the fallback I would use for an item without a preview, and no such item exists here, so it is not
implemented.

Memory: the static browser makes its whole collection resident at the 384 px tier for the session (see
[browser architecture](browser-architecture.md) for why a bounded window failed there). The Live tab instead
prefetches only the **64 cards around the focus** (~24 MB), because the requirement for live wallpapers was bounded
memory over a library of hundreds; cards further out decode on arrival from the WebP cache. Whether fast sweeps
over a cold cache show placeholders is measured in the benchmark page.

## Renderer lifecycle

`LiveRendererProcess` supervises exactly one child:

- fork/exec with everything prepared before `fork()`; the child gets its **own process group** (CEF's helpers share
  it and are signalled together), **`PR_SET_PDEATHSIG`** (dies with the shell) and a private **`TMPDIR`** under
  `$XDG_RUNTIME_DIR/zynith/live-wallpaper/`, removed after exit — linux-wallpaperengine's CEF otherwise leaves a
  profile directory in `/tmp` on every web launch (observed).
- exit is observed through a **pidfd** on the main poll loop, output through a pipe (kept as a 4 KB tail for error
  messages, logged at debug). No polling.
- **Started** = still alive after a 1.5 s grace (the renderer prints no readiness line; failures abort in ~270 ms).
- **Stop** = SIGTERM to the group, SIGKILL at 2 s. Web renderers take ~5 s and end in a CEF abort anyway.
- At shutdown: TERM, 400 ms, KILL, reap.

`pidfd_open` is called through `syscall()`: Fedora 44's glibc 2.43 `<sys/pidfd.h>` declares it without C linkage
guards, so a C++ translation unit links against a mangled symbol that does not exist (the first build failed on it).

Invocation built by the provider (one process covers every output):

```
linux-wallpaperengine --fps 30 --silent --layer background --disable-mouse --assets-dir <assets>
    --screen-root <connector> --bg <canonical item folder> --scaling fill   (repeated per output)
cwd = the renderer's own directory (it mounts its cwd into its virtual filesystem as a fallback root)
```

## Ownership and hand-over

| Transition | Order |
|---|---|
| Static → Live | start renderer · wait for the grace · release static surfaces · palette → preview |
| Live → Live | stop old · wait for exit · start new · (static surfaces stay released; niri's empty background shows in the gap) |
| Live → Static | restore static surfaces + palette · then stop the renderer |
| startup failure | static stays/returns · falls back once to the last wallpaper that ran |
| crash while running | static returns immediately · one automatic restart if it had run ≥ 30 s (at most every 5 min) |
| output change | removed outputs go back to static · renderer restarted on the new set |

Both surfaces live on the **background** layer. With no niri `place-within-backdrop` rule for
`linux-wallpaperengine`, a live wallpaper behaves exactly like the static `noctalia-wallpaper` surface, including
being drawn per workspace in the overview; niri's backdrop keeps Zynith's blurred `noctalia-backdrop`. Zynith does not
edit the niri config for this. Pointer input is off by default (`--disable-mouse`): with it on, the renderer's
surface takes input across the whole output, unlike the click-through static surface.

## Palette

While a live wallpaper is up, `ConfigService::setPaletteSourceOverride()` points `getPaletteWallpaperPath()` at the
item's preview. Every palette consumer — theme generation, template apply (GTK/niri/app colour files), the
`wallpaper_changed` hook — already reads that path, and the override fires the same wallpaper-change callback a
static change does. The theme service decodes the image at 112×112, extracts, frees and memoizes per
(path, mtime, scheme). The override is runtime-only (never written to `settings.toml`) and is cleared on
Live → Static. The greeter sync deliberately keeps the static image.

My own idea was a temporary snapshot of the live wallpaper, colours extracted, snapshot freed; I left the final
choice of algorithm to Claude. Claude chose the preview instead: a screen capture contains whatever windows are on
screen — wrong colours, and private content in a file — and an off-screen frame needs a second renderer, while the
author preview is a still of the same wallpaper that already exists on disk.

## Carousel

Cycles through the **Zynith live collection only** (never the Workshop library), sequential or shuffled, on a
one-shot timer re-armed after each successful switch. A rotation is an ordinary switch — stop, wait, start — so two
renderers never overlap. It is suspended while the session is locked (same gate as static automation) and skips
items that can no longer be launched.

## Persistence

`~/.local/state/noctalia/state.toml`, table `[wallpaper_live]` — identifiers only:

| key | value |
|---|---|
| `mode` | `live` / `static` — written only once a renderer is verified, so a failed selection never replaces a working one |
| `provider` | `wallpaper-engine` |
| `current` | Workshop id |
| `favorites`, `collection`, `recent` | comma-separated Workshop ids (recent: 16, newest first) |
| `category` | last Live tab category |
| `carousel`, `carousel_interval`, `carousel_order` | bool, seconds, `sequential` / `shuffle` |

`[wallpaper_panel] tab` remembers the last browser tab.

## Configuration — `[wallpaper.live]` (rice.toml)

| key | default | meaning |
|---|---|---|
| `renderer` | `linux-wallpaperengine` on PATH | executable (`~` expanded) |
| `steam_root` | standard roots | Steam root to search; library folders are always followed |
| `fps` | 30 | 1–144 |
| `volume` | 0 | 0 = `--silent`, else 1–100 |
| `scaling` | `fill` | `fill` · `fit` · `stretch` · `default` |
| `mouse` | false | pointer input for interactive wallpapers |
| `fullscreen_pause` | true | pause while a window is fullscreen |

## IPC

`noctalia msg wallpaper-live-set <id>` · `wallpaper-live-stop` · `wallpaper-live-status` (JSON) ·
`wallpaper-live-next` · `wallpaper-live-carousel on|off [seconds] [sequential|shuffle]` ·
`wallpaper-live-collection add|remove <id>` · `wallpaper-live-favorite add|remove <id>`.

## Known limitations

- Live → Live shows niri's empty background during the stop + start gap.
- Video wallpapers decode in software: linux-wallpaperengine configures libmpv without `hwdec`. That is a renderer
  change (outside Zynith).
- The overview backdrop and the lock screen keep the static wallpaper.
- The renderer keeps running behind the lock screen (the carousel pauses; the renderer does not).
- Web wallpapers are expensive (~1.3 GB across 10 processes); they are allowed, not hidden.
- Live mode applies to every output; the static browser's monitor selector has no Live counterpart.
