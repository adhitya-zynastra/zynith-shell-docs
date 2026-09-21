# Future Work

Status vocabulary: **Planned** (agreed, not started) · **Proposed** (idea, not agreed) · **In progress** ·
**Completed** · **Deferred** · **Rejected**.

Nothing on this page is implemented. Implemented work lives in `01_Phases/`.

## Planned — requested by the owner, not yet built

| Item | Notes |
|---|---|
| **Morph primitive** | A reusable geometry/property interpolation on the existing `AnimationManager` — source/target geometry, radius, opacity, scale, clipping. Must be interruptible and retargetable; must not become a second animation engine |
| **Control Center morphing** | Content region morphs between sections while the shell, backdrop and navigation stay stationary. The panel-retarget work (`e9e27b0`) is the prerequisite and is done |
| **Settings morphing** | Preset → preset detail, basic → advanced, as spatial transitions |
| **Launcher redesign** | New polished default: minimal, keyboard-first, cinematic. Reference points are Caelestia and Ryoku/Ryoko (the exact Ryoku reference is **UNKNOWN** and must be identified, not guessed) |
| **Launcher style variants** | The *current* launcher must remain selectable. Architecture should be `launcher.style = zynith \| classic \| custom`, not an irreversible redesign |
| **Launcher configurability** | Geometry, appearance, behaviour, layout — see the owner's brief for the full list |
| **Launcher creation cost** | Rapid open/close is the most expensive measured state (7.73 % noctalia + 5.48 % niri). Investigate scene reuse vs. rebuilding, incremental app discovery, icon cache lifetime |
| **Lock screen refinement** | Treat it as one composition rather than widgets placed around a wallpaper: hierarchy, negative space, alignment, focal point |
| **Lock screen power controls** | Sleep/Reboot/Shutdown/Logout. **Security is non-negotiable**: must not bypass authentication, expose protected data, unlock the session, or interfere with PAM or `ext-session-lock`. Destructive actions need confirmation |
| **Lock screen configurability** | Widget visibility/position/alignment/typography, clock and date formats, password-field style |
| **Configurable-shell architecture** | "Everything should be an option": Zynith's design becomes the *default preset*, not the only possibility. Needs a meaningful layout model (named regions + alignment/spacing/order), not raw x/y coordinates |
| **One primary settings surface** | Fold the Motion panel's functionality into the main settings experience, preserving presets, speed, advanced controls, validation and atomic writes. `Super+Alt+A` may deep-link to that section instead of opening a separate system |
| **GTK template / hook cost** | ~156 ms per palette change is spent writing GTK CSS that fails (`~/.config/gtk-3.0/noctalia.css` is missing) and spawning an emacs hook that exits 127 every time. Skip unchanged writes, avoid spawning hooks whose tools are absent |
| **Global motion refinement** | The owner still reports the desktop feeling slightly too fast after the 130/300/520 retune |

## Proposed — not agreed

| Item | Notes |
|---|---|
| Zynith privacy/security subsystem | **PROPOSED / NOT IMPLEMENTED.** No design exists. See `02_Architecture/security.md` |
| Panel scene caching | Would cut launcher creation cost at a memory price; needs measurement before commitment |

## Deferred

| Item | Why |
|---|---|
| Automated lock/unlock testing | Risk of locking the owner out of their own machine; validated visually instead |
| Making the test count 119/119 | The failing test is unrelated third-party behaviour; changing unrelated infrastructure to improve a count is explicitly against policy |

## Rejected

| Item | Why |
|---|---|
| Decoding every wallpaper at native resolution | Catastrophic for large repositories (ADR‑0010) |
| A permanent global wallpaper cache | Violates bounded-resource rule |
| Disabling `swaync` outright | Breaks the Hyprland fallback session (ADR‑0012) |
| Removing the bar's 1 Hz update | Measured: no improvement. Kept rather than pretending it was an optimization |
