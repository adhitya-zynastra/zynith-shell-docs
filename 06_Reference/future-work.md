# Future Work

Status vocabulary: **Planned** (agreed, not started) · **Proposed** (idea, not agreed) · **In progress** ·
**Completed** · **Deferred** · **Rejected**.

Nothing on this page is implemented. Implemented work lives in `01_Phases/`.

## Planned — things I want, not yet built

| Item | Notes |
|---|---|
| **Morph primitive** | A reusable geometry/property interpolation on the existing `AnimationManager` — source/target geometry, radius, opacity, scale, clipping. Must be interruptible and retargetable; must not become a second animation engine |
| **Control Center morphing** | Content region morphs between sections while the shell, backdrop and navigation stay stationary. The panel-retarget work (`e9e27b0`) is the prerequisite and is done |
| **Settings morphing** | Preset → preset detail, basic → advanced, as spatial transitions |
| **Launcher redesign** | New polished default: minimal, keyboard-first, cinematic. Reference points are Caelestia and Ryoku/Ryoko (the exact Ryoku reference is **UNKNOWN** and must be identified, not guessed) |
| **Launcher style variants** | The *current* launcher must remain selectable. Architecture should be `launcher.style = zynith \| classic \| custom`, not an irreversible redesign |
| **Launcher configurability** | Geometry, appearance, behaviour, layout — see my Phase 6 brief for the full list |
| **Launcher creation cost** | Rapid open/close is the most expensive measured state (7.73 % noctalia + 5.48 % niri). Investigate scene reuse vs. rebuilding, incremental app discovery, icon cache lifetime |
| **Lock screen refinement** | Treat it as one composition rather than widgets placed around a wallpaper: hierarchy, negative space, alignment, focal point |
| **Lock screen power controls** | Sleep/Reboot/Shutdown/Logout. **Security is non-negotiable**: must not bypass authentication, expose protected data, unlock the session, or interfere with PAM or `ext-session-lock`. Destructive actions need confirmation |
| **Lock screen configurability** | Widget visibility/position/alignment/typography, clock and date formats, password-field style |
| **Configurable-shell architecture** | "Everything should be an option": Zynith's design becomes the *default preset*, not the only possibility. Needs a meaningful layout model (named regions + alignment/spacing/order), not raw x/y coordinates |
| **One primary settings surface** | Fold the Motion panel's functionality into the main settings experience, preserving presets, speed, advanced controls, validation and atomic writes. `Super+Alt+A` may deep-link to that section instead of opening a separate system |
| **Template post-hook deduplication** | `gtk3` and `gtk4` run the *identical* `post_hook`, so the engine executes the same `gtk/apply.sh` twice per apply. Deduplicating identical post-hook invocations within one apply pass is behaviour-preserving and halves the GTK portion. Do **not** flip `hook_async` — the two are serialised deliberately because they rewrite the same files. Measured context: [postmortem](../04_Incidents/postmortems/2026-09-21-template-fork-storm.md) |
| **Disable templates for absent software** | *User configuration, not code.* 11 of my 21 enabled builtin templates target software that is not installed, and each renders a file and spawns a hook script on every palette change. Turning them off in Appearance → Templates should remove roughly half of the ~2,695 forks per apply |
| **Global motion refinement** | I still find the desktop slightly too fast after the 130/300/520 retune |

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
