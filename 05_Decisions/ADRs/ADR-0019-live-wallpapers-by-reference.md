# ADR-0019 — Live wallpapers: Zynith selects and supervises, Steam keeps the content

**Status:** Accepted, implemented (branch `feature/live-wallpaper`) · **Date:** 2026‑09‑27

## Context
I wanted Steam Wallpaper Engine Workshop wallpapers as live desktop wallpapers for the Zynith showcase, integrated
into the existing Wallpaper browser as a first-class **Static / Live** choice rather than a separate tool.
linux-wallpaperengine (built from upstream at `~/linux-wallpaperengine`, commit `b016d7d`) renders them on
Wayland. The Workshop library on this machine is 560 items and ~45 GB.

Three things shaped the design, all measured or read by Claude on 2026‑09‑27 before any code was written:

- **A live wallpaper is a full renderer.** At 30 fps on the Intel Arc iGPU, 1920×1200: a scene wallpaper ~225 MB RSS
  and ~5 % of one core; a 4K video ~360 MB and ~79 % (libmpv without hardware decoding); a web wallpaper
  10 processes, ~1.3 GB and roughly one full core. SIGTERM exits a scene in 0.12 s, a video in 0.32 s and a web
  wallpaper in 5.2 s (ending in a CEF abort).
- **Every item ships its own preview** (`preview.jpg` / `.gif` / `.png`, all 560 present, ≤ 1 MB each).
- **linux-wallpaperengine resolves ids only in four hard-coded home-relative Steam roots** and accepts an absolute
  item folder in `--bg`; assets are found the same way unless `--assets-dir` is given.

## Decision
1. **Reference, never copy.** Zynith persists *provider id + Workshop id* in `state.toml [wallpaper_live]`. The
   provider resolves the canonical folder at use time — Steam roots → `libraryfolders.vdf` library folders →
   `steamapps/workshop/content/431960/<id>` — and passes the absolute folder plus an explicit `--assets-dir`.
   Workshop content is never copied, moved or modified; Zynith is the selector, Steam the asset store.
2. **Provider abstraction.** `LiveWallpaperProvider` owns discovery, metadata, previews and the renderer
   invocation; `WallpaperEngineProvider` is the first. The UI and the controller never see a command line.
3. **Exactly one renderer.** `LiveRendererProcess` supervises one child: own process group, `PR_SET_PDEATHSIG`,
   pidfd + output pipe on the main poll loop (no polling), SIGTERM → SIGKILL after 2 s. A switch stops the old
   renderer, waits for its exit, then starts the next. The carousel is an ordinary switch on a timer.
4. **Browsing never renders.** The Live tab shows the authors' preview images through the existing
   `ThumbnailService` (worker decode, persistent WebP cache keyed on path + size + mtime). No renderer is launched to
   produce a thumbnail.
5. **Ownership by hand-over, not by stacking.** Live mode releases the static surfaces through the upstream hook
   `Wallpaper::setOutputExternallyManaged()`; the static wallpaper stays up until the new renderer has survived a
   1.5 s startup grace, and comes back *before* the renderer is stopped on Live → Static or on any failure.
6. **Palette from the preview.** While a live wallpaper is up, `ConfigService::setPaletteSourceOverride()` points
   the palette at the item's preview (runtime-only, never persisted). The existing theme path decodes it at
   112×112, extracts, frees and memoizes — no screen capture, no extra render.
7. **Same layer as the static wallpaper.** `--layer background` without a niri `place-within-backdrop` rule, so a
   live wallpaper behaves exactly like `noctalia-wallpaper` does today, including in the overview. niri's backdrop
   stays with Zynith's own blurred `noctalia-backdrop`.

## Alternatives
- *Copy or symlink selected items into a Zynith folder* — rejected: duplicates up to 45 GB, goes stale on every
  Workshop update, and breaks on unsubscribe.
- *Pass bare Workshop ids to the renderer* — rejected: misses Steam library folders on other drives.
- *Launch the renderer (or `--screenshot`) to produce carousel thumbnails* — rejected: a full GPU renderer per card,
  and every item already has an author preview.
- *Screen-capture the live wallpaper for the palette* (my first idea, raised during the work) — rejected after
  discussion: a capture includes whatever windows are on screen (wrong colours, and private content), and an
  off-screen render needs a second renderer. The preview is the author's own still of the wallpaper.
- *Overlap old and new renderer during a switch for a seamless cut* — rejected: doubles GPU and memory cost for a
  transition that happens every few minutes at most.
- *Render Workshop presets* by launching their base item with `--set-property` — rejected: presets reference files
  in their own folder, which the renderer does not mount; they are listed as unsupported instead of rendered wrong.

## Consequences
- Switching between two live wallpapers shows niri's empty background for the stop + start gap (measured in
  `03_Performance/benchmarks/live-wallpaper.md`).
- Live mode costs whatever the renderer costs; the shell side is idle (no timers except the carousel's one-shot).
- The overview backdrop and the lock screen keep using the static wallpaper.
- Documentation: [live wallpapers](../../02_Architecture/wallpaper/live-wallpapers.md).
