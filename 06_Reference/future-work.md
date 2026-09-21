# Future Work

Status vocabulary: **Planned** (agreed, not started) · **Proposed** (idea, not agreed) · **In progress** ·
**Completed** · **Deferred** · **Rejected**.

Nothing on this page is implemented. Implemented work lives in `01_Phases/`.

## Planned — things I want, not yet built

| Item | Notes |
|---|---|
| **Morph primitive** | Extract the Control Center's bespoke section-transition logic (`layoutTabContainers`) into a shared, interruptible, retargetable primitive on the existing `AnimationManager` — **a refactor with a behaviour-preservation obligation**, not a new feature. Acceptance criteria are the six properties already met today, audited in [control-center/panel.md](../02_Architecture/control-center/panel.md). Must not become a second animation engine |
| **Control Center morphing** | *Behaviourally already done* — `e9e27b0`'s `retargetOpen()` keeps the outer surface stable, transitions only the content region over ~34 px, is direction-aware, and continues an interrupted switch from the outgoing content's real offset (96.7 → 58.3 ms CPU, 643 → 398 context switches per navigation). What remains is making it *the morph primitive's first consumer* rather than its implementation |
| **Settings morphing** | Preset → preset detail, basic → advanced, as spatial transitions |
| **Launcher redesign** | New polished default: minimal, keyboard-first, cinematic. Reference points are Caelestia and Ryoku/Ryoko (the exact Ryoku reference is **UNKNOWN** and must be identified, not guessed) |
| **Launcher style variants** | The *current* launcher must remain selectable. Architecture should be `launcher.style = zynith \| classic \| custom`, not an irreversible redesign |
| **Launcher configurability** | Geometry, appearance, behaviour, layout — see my Phase 6 brief for the full list |
| **Launcher creation cost** | Rapid open/close is the most expensive measured state (7.73 % noctalia + 5.48 % niri). Investigate scene reuse vs. rebuilding, incremental app discovery, icon cache lifetime |
| **Lock screen refinement** | Treat it as one composition rather than widgets placed around a wallpaper: hierarchy, negative space, alignment, focal point |
| **Lock screen power controls** | Sleep/Reboot/Shutdown/Logout. **Security is non-negotiable**: must not bypass authentication, expose protected data, unlock the session, or interfere with PAM or `ext-session-lock`. Destructive actions need confirmation |
| **Lock screen configurability** | Widget visibility/position/alignment/typography, clock and date formats, password-field style |
| **Configurable-shell architecture** | "Everything should be an option": Zynith's design becomes the *default preset*, not the only possibility. Needs a meaningful layout model (named regions + alignment/spacing/order), not raw x/y coordinates |
| **Motion: migrate the niri generator** | *Partially done.* The motion config model and its settings UI now live in the main surface (`shell.animation.preset` + four `niri_*` trims, Appearance → Motion). The Motion plugin still owns generating `~/.config/niri/rice/animations.kdl` — validating with `niri validate` and swapping atomically. Moving that makes the shell a writer of niri's config directory, which is a new responsibility and a new precedence surface; unresolved. See [motion-settings](../02_Architecture/animation/motion-settings.md) |
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
