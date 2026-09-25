# Changelog

Commit hashes refer to `~/.local/src/noctalia-lockfade/source`. Dates are git author dates (local time).
Entries are grouped by kind, as required by the documentation policy.

## Wallpaper, Responsive Layout and Control Center — 2026‑09‑25

### Architecture
- `ui::responsive` — extent resolution, fit count and density spacing; no engine, nothing per frame — `b49ec4e`
- Carousel geometry extracted to `carousel_geometry.h`; the focused card is sized from a preference and the arc fits as many cards as are genuinely visible — `b49ec4e`
- "Zynith Corner" renamed **Personalization**; Control Center and Wallpaper Browser groups; future Zynith Settings hub documented, not built (ADR‑0017) — `c5dd72d`

### Features
- `[wallpaper].carousel_card_width` (400–1400, default 760); wider outputs gain neighbours rather than bigger cards — `b49ec4e`
- `[control_center].density` (compact / comfortable / spacious) — `09990f8`
- Ctrl+Tab / Ctrl+Shift+Tab / Ctrl+PgUp / Ctrl+PgDn cycle Control Center sections — `09990f8`
- Clock click opens the Control Center at Home (`[widget.clock.actions]` in `rice.toml`; preset, not code)
- niri `mod-key "Super"` stated explicitly; native Mod+drag move/resize documented and verified

### Fixed
- A clock click after hover-open toggled the panel shut once both routes opened Home; it now confirms the open — `09990f8`
- The first responsive carousel counted occluded slivers as visible cards; caught at runtime and fixed before commit — `b49ec4e`
- Holding a `noctalia msg` shortcut re-spawned it on every key repeat (seen: 13 wallpaper-panel toggles in 5 s); 17 binds now `repeat=false`

### Tests
- `responsive_layout_test`; suite 123 / 124

## Motion, Zynith Corner and Glass — 2026‑09‑25

### Architecture
- Shared glass surface model (`shell::glass`); `ColorSpec` gains a live palette-role tint; custom transparency mode — `aaa69b0`
- Shell generates `niri/rice/animations.kdl` and `rice/glass.kdl`: validated, atomic, coalesced, full-config rollback (ADR‑0015) — `f5cad71`
- Global speed model: shell = 0.8 × preset × speed, niri slowdown = 1/speed (ADR‑0015 amendment) — `f5cad71`
- Zynith Corner settings section with Motion and Glass groups; entries moved, none duplicated — `8c2b4eb`

### Fixed
- Motion trims could be set to 0 %, which divides by zero in the niri derivation; floor is now 50 % — `f5cad71`
- Panels requested compositor blur behind an opaque fill (Solid mode); no longer — `aaa69b0`

### Removed
- Motion plugin, `motion.toml`, `motion.json` (backed up); `Super+Alt+A` now opens Zynith Corner

### Tests
- `niri_config_fragments_test` (byte-exact against the plugin), `glass_surface_test`, `zynith_config_ownership_test`; suite 122 / 123

## Phase 6A — 2026‑09‑25

### Architecture
- `MorphTransition` — shared, retargetable transition leg over `AnimationManager`; no new engine — `a147fc1`
- Control Center section navigation consumes it; visual behaviour unchanged — `a147fc1`
- ADR‑0015: shell to own niri animation generation, Motion plugin to be retired (decided, not implemented)

### Tests
- `morph_transition_test`; suite now 119 / 120

### Documentation
- Correction: out-of-range config values are clamped silently, not reported (`configurability.md`)

## Phase 6 — 2026‑09‑20 → 2026‑09‑21

### Fixed
- **Use-after-free in `Signal::emit`** that crashed the whole shell during wallpaper apply — `08f5454`
- **Carousel clicks did nothing** (cards sat above the hit-test overlay) — `e9e27b0`
- **Applying a wallpaper was invisible** behind the open browser (frozen screencopy backdrop) — `e9e27b0`
- **Control Center replayed its opening animation** on navigation from a bar widget — `e9e27b0`
- **Hover→Control Center failed** when the pointer rested on the visualiser half of the time cluster — `e9e27b0`
- **Focused wallpaper rendered from the preview tier** (1.96× upscale) — `57debbc`
- **Notifications and their sounds were dead** — swaync owned the D-Bus name (environment fix, no commit)
- **btop showed no CPU box** — its own `shown_boxes` (environment fix, no commit)

### Architecture
- `Panel::retargetOpen()` — an open panel takes a new context in place instead of being rebuilt — `e9e27b0`
- `Panel::ModalBackdropMode` + `ScreenVeil::showTint()` — live (non-freezing) backdrops — `e9e27b0`
- `CarouselView` — orbit-path carousel over the existing `VirtualGridAdapter` — `99ac272`, `46296d0`
- Browser split into a compact control card + full-width band on one undecorated surface — `46296d0`
- `ThumbnailService` sessions with ownership tags, decode gate, `prefetch()`, two quality tiers — `eaff2b2`, `57debbc`
- `Signal`/`AnimationManager` reentrancy and lifetime contracts — `08f5454`, `eaff2b2`

### Performance
- Decode gate: carousel movement **54.4 % → 3.96 %** CPU — `46296d0`
- Thumbnail idle set: 20 forward + 20 back **36 → 23** decodes — `46296d0`
- Panel retarget: **96.7 → 58.3 ms** CPU and **643 → 398** context switches per navigation — `e9e27b0`
- Plugin registry: **6 → 0** manifest loads per wallpaper apply — `eaff2b2`
- Allocation-free dispatch (no `std::function` copy per callback) — `eaff2b2`
- Eager previews: traversing 20/50/100 wallpapers each costs **18 decodes** — `57debbc`

### Configuration
- `[wallpaper] carousel`, `[control_center] top_nav / hover_open / hover_open_delay_ms`,
  `[widget.network] show_label`, bar `capsule_group` clusters, clock `font_scale`
- New: `~/.config/systemd/user/swaync.service.d/10-skip-under-niri.conf`

### Documentation
- Patch README extended with the carousel, session cache, quality tiers and measurements
- This documentation set created (2026‑09‑21)

## Phase 5 — 2026‑09‑20 · `803664d`
**Features:** Zynith notification toast (accent app caption, unified radius); sound vocabulary (volume, mute,
notification, lock, unlock, screenshot). **Fixed:** mute cue never played (three stacked causes).
**Architecture:** in-process `SoundPlayer` on the PipeWire loop; `[hooks]` for lock/unlock.

## Phase 4 — 2026‑09‑20 · `40c1936`
**Features:** OSD layout (icon disc, title, gliding bar), rounded card ends.
**Performance:** on-screen hold moved from `animateTimer` to `TimerManager` — removed ~50–80 wakeups/s while visible.

## Phase 3 — 2026‑09‑19/20 · Motion plugin
**Features:** presets, global speed, advanced controls; generates `motion.toml` + `animations.kdl` with validation
and atomic replace. **Architecture:** implemented as a panel, not a service, to avoid a resident 1 s timer.

## Phase 2 — 2026‑09‑19 · `bf0a376` → `4289b62`
**Features:** lock/unlock transitions, hidden-until-typing password pill, errors inside the pill, unlock veil,
modal power menu with circular actions. **Architecture:** `ScreenVeil` primitive. **Fixed:** unlock timer now
derives from the real exit schedule. **Security:** PAM and `ext-session-lock` untouched.

## Phase 1 — 2026‑09‑19 · configuration only
**Features:** dark glass window rules, wallpaper-derived `m3-tonal-spot` palette, ported keybindings, flush bar.
**Architecture:** `config.kdl` reduced 635 → 130 lines with `rice/*.kdl` includes. **Fixed:** stray bar clicks
opening the launcher; invalid colour roles; a mis-targeted `sed` edit.

## Phase 0 — 2026‑09‑19 · inspection only
Baseline snapshot at `~/.config/rice-backups/20260919-182322-pre-rice/`; no functional change.

## Documentation

- **1.4** (2026‑09‑21) — Records the commit-attribution rule: documentation commits are authored as the
  repository owner from the repository's own `.git/config`, with no assistant trailers and no command-line
  identity override, and already-pushed commits are never rewritten. Git metadata carries the owner's project
  identity; Claude's role stays documented in the prose, where it is useful. `DEVELOPMENT_WORKFLOW.md`,
  `DOCUMENTATION_POLICY.md` §6 and `CLAUDE.md` updated; no other content changed.
- **1.3** (2026‑09‑21) — Documentation becomes part of the development loop rather than a later phase. Adds
  `DEVELOPMENT_WORKFLOW.md` (the standing rule: what to record, where each kind of change is routed, what
  evidence to capture, and the question that ends a task), plus `CLAUDE.md` in this repository and at
  `~/.local/src/noctalia-lockfade/` so the rule is picked up when working on either side. Policy gains §7.
  Nothing in the existing set was rewritten.
- **1.2** (2026‑09‑21) — Added `00_Project/origins.md`, the account of why the project exists: leaving Windows
  over questions of control, settling on Fedora, Hyprland as the entry point, why I built rather than downloaded,
  and the point at which a rice became a shell. Three corrections follow from it: my reasons for choosing niri
  are **recorded** rather than unrecoverable (the previous version stated the opposite), Hyprland's retention has
  a second and non-engineering reason, and the numbered phases are now explicitly the *live implementation*
  window rather than the start of the project, which began roughly four to five months earlier with no surviving
  artifacts. Policy §6 gains the working arrangement with Claude and why it is stated.
- **1.1** (2026‑09‑21) — Voice and attribution pass over the existing set: converted the project history,
  rationale, decision records and incident reports to first person as the owner's engineering record, made the
  human/AI division of labour explicit where the evidence establishes it, restructured the four postmortems into
  an observed → suspected → investigated → evidence → root cause → fix → verification → lesson chronology, added
  the design-history narrative behind the wallpaper resource model, recorded the proposed security layer as
  future architecture, and rewrote the figure captions to state why each figure matters. No technical claim was
  changed; no implementation file was touched. Policy §6 now governs voice and attribution.
- **1.0** (2026‑09‑21) — Initial documentation set at source commit `57debbc`.

## Breaking changes
None to date. Every change is reversible by removing a config block, a drop-in file, or by running the packaged
`/usr/bin/noctalia`.
