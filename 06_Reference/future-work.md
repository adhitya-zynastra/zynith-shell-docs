# Future Work

Status vocabulary: **Planned** (agreed, not started) · **Proposed** (idea, not agreed) · **In progress** ·
**Completed** · **Deferred** · **Rejected**.

Nothing on this page is implemented. Implemented work lives in `01_Phases/`.

## Planned — things I want, not yet built

| Item | Notes |
|---|---|
| **Morph primitive** | ✅ **Done** (Phase 6A) — `MorphTransition` in `src/render/animation/`, with `tests/morph_transition_test.cpp`. See [morph-primitive.md](../02_Architecture/animation/morph-primitive.md) |
| **Control Center morphing** | ✅ **Done** (Phase 6A) — behaviour was already correct from `e9e27b0`; the Control Center now *consumes* the shared primitive instead of implementing it. Visual behaviour deliberately unchanged |
| **Settings morphing** | Preset → preset detail, basic → advanced, as spatial transitions |
| **Launcher redesign** | ✅ **Done** 2026‑09‑25 (`b106c38`) as the Zynith style — [transient-ui.md](../02_Architecture/transient/transient-ui.md). Original note: new polished default: minimal, keyboard-first, cinematic. Reference points are Caelestia and Ryoku/Ryoko (the exact Ryoku reference is **UNKNOWN** and must be identified, not guessed) |
| **Launcher style variants** | ✅ **Done** — `style = zynith | classic`; classic is unchanged. A `custom` style was not built. Original note: the *current* launcher must remain selectable. Architecture should be `launcher.style = zynith \| classic \| custom`, not an irreversible redesign |
| **Launcher configurability** | ✅ **Done in part** — width, height, icon size, density, key hints; transparency/blur/tint stay the shared Glass group. Original note: geometry, appearance, behaviour, layout — see my Phase 6 brief for the full list |
| **Launcher creation cost** | Re-measured 2026‑09‑25: ~66 ms CPU per open+close over 20 cycles, no growth (`tracks-launcher-osd-notify.md`); scene reuse still not investigated. Original note: rapid open/close is the most expensive measured state (7.73 % noctalia + 5.48 % niri). Investigate scene reuse vs. rebuilding, incremental app discovery, icon cache lifetime |
| **Lock screen refinement** | Treat it as one composition rather than widgets placed around a wallpaper: hierarchy, negative space, alignment, focal point |
| **Lock screen power controls** | Sleep/Reboot/Shutdown/Logout. **Security is non-negotiable**: must not bypass authentication, expose protected data, unlock the session, or interfere with PAM or `ext-session-lock`. Destructive actions need confirmation |
| **Lock screen configurability** | Widget visibility/position/alignment/typography, clock and date formats, password-field style |
| **Configurable-shell architecture** | "Everything should be an option": Zynith's design becomes the *default preset*, not the only possibility. Needs a meaningful layout model (named regions + alignment/spacing/order), not raw x/y coordinates |
| **Motion: migrate the niri generator** | ✅ **Done** 2026‑09‑25 — see ADR‑0015 and [motion-settings.md](../02_Architecture/animation/motion-settings.md) |
| **Template post-hook deduplication** | `gtk3` and `gtk4` run the *identical* `post_hook`, so the engine executes the same `gtk/apply.sh` twice per apply. Deduplicating identical post-hook invocations within one apply pass is behaviour-preserving and halves the GTK portion. Do **not** flip `hook_async` — the two are serialised deliberately because they rewrite the same files. Measured context: [postmortem](../04_Incidents/postmortems/2026-09-21-template-fork-storm.md) |
| **Disable templates for absent software** | *User configuration, not code.* 11 of my 21 enabled builtin templates target software that is not installed, and each renders a file and spawns a hook script on every palette change. Turning them off in Appearance → Templates should remove roughly half of the ~2,695 forks per apply |
| **Personalization — later groups** | Motion, Glass, Control Center and Wallpaper Browser done ([personalization.md](../02_Architecture/configuration/personalization.md)); bar, launcher, widgets and OSD groups arrive with their systems |
| **Zynith Settings** | The system-wide settings hub (users, network, devices, display, audio, power, niri, shell and Zynith configuration). **Designed on paper only** — [settings-information-architecture.md](../02_Architecture/configuration/settings-information-architecture.md), ADR‑0017. Whether it extends the current window or is a new app over the same registry is **UNKNOWN** |
| **Responsive layout: more consumers** | Launcher, OSD and notifications should size through `ui::responsive` when they are redesigned, not be retrofitted first. [responsive-layout.md](../02_Architecture/layout/responsive-layout.md) |
| **Glass: remaining consumers** | OSD and notifications moved onto glass 2026‑09‑25 (`b106c38`). Bar, dock, desktop widgets and bar-attached panels still use their own opacity keys. Each moves onto `shell::glass` with its redesign |
| **Personalization deep links** | `settings-open` selects a section, not a group; `Super+Alt+A` relies on Motion being the first group |
| **Runtime checks not yet run** | Tint following a real palette change (needs a wallpaper or `shell_mode` change), and the fragment writer's full-config rollback (needs a deliberately broken niri config). From the second track set: media → Media routing (nothing was playing) and a held shortcut after `repeat=false` |
| **Synchronous `wallpaper-set` over IPC** | One `IpcPollSource dispatch took 1667.2ms` warning at a `wallpaper-set` of a 13 MB JPEG: the IPC handler decodes on the main loop. Pre-existing; not investigated |
| **Audio tab showed no output device once** | After a shell restart, the Control Center's Audio tab read "No output device selected, 0 %" while the bar read 100. Seen once, not investigated — belongs to the audio redesign |
| **Config diagnostics for ranged fields** | Out-of-range and wrong-typed values are clamped or ignored *silently* for every ranged int/float field (`schema/field.h` never uses its `Diagnostics&`). Found in Phase 6A; see the correction in [configurability.md](../02_Architecture/configuration/configurability.md). Upstream parser change, affects every field |
| **Global motion refinement** | Partly addressed: overshoot verified absent, springs critically damped, pace set by preset. **Open idea:** keep short feedback animations crisp under slow presets — not done, because scaling short durations differently would also retime the approved Phase 2 lock choreography (70 ms delay, 20 ms stagger) |

## Proposed — not agreed

| Item | Notes |
|---|---|
| Zynith security and privacy layer | **PROPOSED / NOT IMPLEMENTED.** Intent recorded, no design and no code. Would be a future phase of its own, with enforcement outside the shell process. See `02_Architecture/security.md` |
| Panel scene caching | Would cut launcher creation cost at a memory price; needs measurement before commitment |

## Deferred

| Item | Why |
|---|---|
| Automated lock/unlock testing | Risk of locking me out of my own machine; validated visually instead |
| Making the test count 119/119 | The failing test is unrelated third-party behaviour; changing unrelated infrastructure to improve a count is explicitly against policy |

## Rejected

| Item | Why |
|---|---|
| Decoding every wallpaper at native resolution | Catastrophic for large repositories (ADR‑0010) |
| A permanent global wallpaper cache | Violates bounded-resource rule |
| Disabling `swaync` outright | Breaks the Hyprland fallback session (ADR‑0012) |
| Removing the bar's 1 Hz update | Measured: no improvement. Kept rather than pretending it was an optimization |
