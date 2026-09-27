# Zynith Design Language — Proposal ("Optics")

**Status: PROPOSED (2026‑09‑26).** *Amended the same day:* the sixth batch implemented the foundation parts —
tokens, typography roles, the surface hierarchy, the spatial origin and the motion roles — with deliberate
differences from the numbers below. The surface reveal stays a tween; springs are used only for retargetable
elements, and they are critically damped. See [`design-foundation.md`](design-foundation.md). Screens are
unchanged. Evidence:
[`design-research-2026-09.md`](design-research-2026-09.md). Architecture and order of work:
[`design-roadmap.md`](design-roadmap.md). Numbers are logical pixels at scale 1 and milliseconds at tempo 1. My
`corner_radius_scale` and the shell tempo multiply them as they do today.

## 1. Philosophy

**The desktop is the scene; Zynith is the lens.** The wallpaper is the photograph. The shell is the camera's
instrument layer: it frames, focuses and reads the scene without competing with it. Camera and optics vocabulary
is the organising metaphor: aperture, focus, exposure, readout. It is chosen because it turns into concrete
behaviour, and because no reference uses it. The references are organised around a frame (Caelestia), print
(Ryoku), an island (Clavis), Material (End4) and pills (Imperative).

| Principle | What it means in engineering terms |
|---|---|
| **Everything has an origin** (aperture) | a surface opens *out of* the element that summoned it and closes back into it — the seed's rectangle and radius are the first frame of the surface's clip |
| **One thing in focus** (focal plane) | when a primary surface opens, the rest of the shell recedes; there is never more than one foreground surface |
| **Accent is light, not paint** (exposure) | the palette accent appears as edges, glow and the one current selection; never as large fills |
| **Data is read, not decorated** (readout) | live values use a tracked monospace voice with tabular figures; language uses the UI face |
| **The scene is composed with, not covered** | text on the wallpaper is contrast-corrected and placed in its calm regions |
| **Motion has mass** | spatial motion is a spring with velocity continuity: it arrives fast, settles with ≤ 1.5 % overshoot, and continues from where and *how fast* it was going when retargeted |

## 2. Spatial system

- **Scale:** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64. Within a component use 4–16; between groups 24–32;
  compositional margins (a stage, the lock screen) 48–64. Nothing between the steps.
- **Density** (`compact` / `comfortable` / `spacious`) scales the spacing steps only. It never scales type or radius.
- **Depth order:**
  - scene (wallpaper);
  - ambient (desktop widgets, visualiser);
  - frame (bars);
  - lens (Control Center, launcher, notification centre);
  - transient (OSD, toasts, menus, tooltips);
  - modal (power confirm, lock).
- **Alignment:** each surface section has one text column, and every text block in it shares a left edge. Icons align
  to the text's cap height, not its box.
- **Edges:** a surface either touches its seed (it grew from it) or sits one step (24) away from any other surface.
  No 8 px gaps between unrelated surfaces.

## 3. Geometry

| Family | Radius (scale 1) | Used for |
|---|---|---|
| `surface` | 18 | lens and modal outer shape |
| `plate` | 10 | grouped content inside a lens |
| `control` | 8 | buttons, fields, tiles |
| `pill` | h/2 | chips, the search field, OSD bars — interactive capsules only |
| `stage` | 0 | full-bleed compositions (lock, wallpaper browser) |

- **Concentric rule:** a child inset uniformly from its parent's corner takes `parent − inset` (floored at 4), so
  nested corners share a centre. Otherwise it takes its family radius.
- **Width classes:** S 360, M 560, L 760. A surface picks the largest class ≤ 0.9 × available width; height follows
  content.
- **Icon containers:** 32 / 40 / 48 squares, icons 16 / 20 / 24, radius from the `control` family.
- **Hairline:** 1 px. There are no 2–3 px borders except focus brackets.

## 4. Material

| Level | Fill | Blur | Edge | Shadow |
|---|---|---|---|---|
| `scene` | the wallpaper | — | — | — |
| `ambient` | none | — | — | — (text contrast-corrected, §6) |
| `frame` | surface @ 0.55 | compositor | hairline ink @ 10 % | none |
| `lens` | surface @ 0.72 | compositor | hairline ink @ 12 % + **inner top catch-light** 1 px on-surface @ 8 % | one: y 12, blur 40, black @ 28 % |
| `plate` | surface-container-high @ 0.45 over the lens | none | none | none |
| `signal` | primary @ 0.16 | none | primary hairline @ 0.6 + 12 px glow @ 0.18 | none |
| `scrim` | black @ 0.32 | shell-rendered wallpaper blur where the surface owns the wallpaper | — | — |

Rules:
- Never stack two blurred layers.
- A plate is a *tone* step, not more transparency.
- One shadow per lens.
- `signal` appears once per surface at rest.

## 5. Typography

Faces by role:
- **Display:** Space Grotesk, Light 300.
- **UI:** Inter.
- **Data:** JetBrains Mono.

Until Space Grotesk and Inter are installed, display falls back to Montserrat Light and UI to Montserrat.

| Role | Size / weight | Used for |
|---|---|---|
| `display.xl` | 104 / 300 | the lock clock |
| `display` | 64 / 300 | hero clocks, the one big readout of a surface |
| `headline` | 32 / 400 | a section's primary value (temperature, battery %) |
| `title` | 20 / 500 | surface and section titles |
| `body.lg` | 16 / 400 | primary rows |
| `body` | 14 / 400 | everything else |
| `label` | 12 / 500 | control labels |
| `data` | 12 / 400, JetBrains Mono, UPPERCASE, tracking +0.12 em, tabular | technical readouts and units |
| `micro` | 11 / 500 | tags, secondary counts |

- **Tabular figures** (`tnum`) for any number that changes.
- Bold only for error text.
- Mono only for what is literally data: values, units, keys, paths. Never for language.

## 6. Colour

- **Source:** the existing wallpaper-derived Material palette (m3-tonal-spot). No change.
- **Accent budget:**
  - at rest, one `signal` element per surface (the current selection);
  - keyboard mode adds the focus brackets;
  - accent text only for *live* values;
  - no accent fill larger than a 48 × 48 control;
  - tiles are neutral, and "on" is a `signal`, not a filled tile.
- **Ink on the scene:** text placed on the wallpaper is corrected against the sampled region to a CIE L* distance
  of ≥ 50 (≈ 4.5:1). If the palette cannot reach that, a local radial scrim (radius 24–48, black @ 0.25) sits
  behind the text. This is computed once per wallpaper change, never per frame.
- **Semantics:**
  - `error`: destructive, armed and failed states only;
  - `warning`: battery ≤ 15 % only;
  - there is no "success" colour — success is the absence of error.

## 7. Motion

**Model.** Spatial properties (position, size, radius, clip) are **springs** that keep velocity across a retarget.
Opacity and colour are short tweens. Parameters come from the measurements in the research record: spatial arrival
measured 180–240 ms with ≤ 1 % overshoot, and scene changes ≈ 550 ms. The "reaches 99 %" column was computed from
the spring equations, not estimated. A first draft had `spatial.enter` at ω 26 (≈ 172 ms), which was faster than
anything measured and barely slower than exit; it was retuned to ω 22.

| Role | Kind | Parameters | Reaches 99 % | Overshoot | Used for |
|---|---|---|---|---|---|
| `spatial.enter` | spring | ω 22/s, ζ 0.85 | ≈ 205 ms | ≈ 0.6 % | a surface growing from its seed |
| `spatial.move` | spring | ω 30/s, ζ 1.0 | ≈ 220 ms | 0 | indicators, focus brackets, accordion widths, a lens gliding to a new seed |
| `spatial.exit` | spring | ω 40/s, ζ 1.0 | ≈ 165 ms | 0 | closing into the seed |
| `spatial.scene` | spring | ω 12/s, ζ 1.0 | ≈ 550 ms | 0 | wallpaper reveal, lock rack-focus |
| `hover` | spring | ω 45/s, ζ 1.0 | ≈ 150 ms | 0 | seed lift |
| `press` | spring | ω 60/s, ζ 1.0 | ≈ 110 ms | 0 | press depth |
| `effect.in` / `effect.out` | tween, decelerate / accelerate | 150 / 100 ms | — | — | opacity, colour |

**Rules.**
- **Entrance:** the surface first, content 50 ms later (`effect.in`). The first open staggers up to five content
  groups by 20 ms. The rest arrive together. Never stagger on a retarget.
- **Exit:** content `effect.out`; the surface `spatial.exit`. It is always shorter than the entrance.
- **Morph / shared element:** if a change keeps an object (the selection, the lens, a card becoming a wallpaper),
  that object is animated *through* the change. Replacing it is not allowed.
- **Interruption:** any spatial property can be retargeted on any frame and keeps its current velocity. Close
  during open reverses from the current state.
- **Depth:** on a context switch, outgoing content goes to scale 0.985 and fades (100 ms), and incoming comes from
  1.015 (150 ms, 40 ms later). The container reshapes on `spatial.move`.
- **Blur:** compositor blur is not animated. Only surfaces that render the wallpaper themselves (lock, backdrop)
  animate their blur radius.
- **Tempo:** ω is multiplied by the shell tempo, and tween durations are divided by it. Reduce-motion collapses
  springs to a single frame and keeps 100 ms fades.
- **Idle:** nothing animates or repaints at rest.

## 8. Interaction language

| When | Behaviour |
|---|---|
| Hovering a seed | tone +6 %, scale ≤ 1.02 (`hover`); neighbours never move |
| Pressing | scale 0.97 (`press`); release springs back |
| Keyboard focus | **focus brackets**: four 2 px corner ticks, 6 px long, 3 px outside the target, gliding between targets (`spatial.move`); shown only after a key press, hidden on pointer motion |
| Opening | from the seed (aperture); the rest of the shell recedes (focal plane) |
| Closing | back into the seed; if the seed is hidden (an auto-hidden bar), toward its screen edge |
| Switching context inside a surface | the lens persists and reshapes; content changes with depth |
| Moving to another surface on the same output | the lens glides to the new seed instead of closing and reopening |
| Dragging | 1:1 under the pointer; on release the measured velocity feeds the spring |
| Destructive arm | the brackets close in on the button and take the error colour; the second press confirms (the existing arm/confirm rule) |

## 9. Responsive system

- **16:10 laptop (this machine), 16:9:** width classes pick the size, and anchors keep edge distances.
- **Ultrawide:** the focal element is centred on the *output*; the periphery stays anchored to the edges; stage
  content is capped at 1440 wide.
- **Scale factors:** logical pixels throughout; Wayland handles the device ratio. There is no extra user multiplier
  beyond density.
- **Bars consuming the workspace:** the existing position-reference model (ADR‑0018) stays.
  - *Workspace-relative:* surfaces that belong to the working area (the launcher, a Control Center opened from the
    keyboard).
  - *Output-relative:* compositions that belong to the screen (lock, OSD, centred bars and their panels).

## 10. Reusable primitives

| Primitive | What it is |
|---|---|
| `Spring` | a value + velocity channel in `AnimationManager`: ω, ζ, retarget keeps velocity |
| `MotionRole` | the §7 table as the only way call sites choose motion |
| `SeedMorph` | animates a clip (rect, radius, corner shapes) from a seed rect to a target rect on the existing SDF rect shader |
| `Lens`, `Plate`, `Signal`, `Scrim` | the §4 materials, owned by Glass |
| `FocusBrackets` | one per surface; glides to the focused element |
| `Readout` | label + value + unit as one typographic unit (data voice, tabular figures) |
| `InkOnScene` | contrast-corrected text colour (and fallback scrim) for anything on the wallpaper |
| `ScenePlacement` | the calm region of the wallpaper for a given box, computed once per wallpaper change |
| `FocusAccordion` | a list in which the focused item expands and the others compress to slivers |

## 11. Signature elements

1. **Aperture** — every surface grows out of the exact thing you touched, and returns into it.
2. **Focal plane** — one surface in focus. The lock screen *racks focus* between idle (the clock sharp, the
   wallpaper at 8 px blur) and authenticate (identity sharp, the wallpaper at 24 px blur, the clock receding).
3. **Focus brackets** — keyboard focus as a camera's autofocus point; the same brackets arm destructive actions.
4. **Exposure accent** — the accent is light on an edge, never a painted block.
5. **Readouts** — tracked mono values with steady tabular digits (OSD levels, clock seconds, rates, battery).
6. **Scene composition** — clocks and text sit where the wallpaper is calm, legible on any image.

## 12. What this rules out

- Solid accent tiles.
- Cards inside cards.
- A grid of equal cards as a layout.
- Fades and slides with no origin.
- Tweens that restart at zero velocity.
- Overshoot above 1.5 %, or on shrink.
- Stagger on every change.
- Text restating a control's state.
- Busy states that shift layout.
- Decorative diagrams that carry no information.
- Polling for visual state.

## Amendment — the shared language on screen (Batch 7, 2026‑09‑26)

Batch 7 is the first batch that builds screens **on** the foundation: the Zynith Control Center
([`panel.md`](../control-center/panel.md)) and the lock screen ([`composition.md`](../lockscreen/composition.md)).
What the two surfaces now share, and where each rule lives in code:

| Axis | The rule, as built | Owner |
|---|---|---|
| Geometry | anything you press is a **capsule** (`tokens::pill(height)`): command-bar items and their selection capsule, chips, the lock power capsule, the password field (preset radius 28). Grouped content is a **plate** (`Radius::Plate`). A container around controls is **concentric** with them (the power capsule's radius = item + inset). Lines are **1 px hairlines** (`kHairline`); the focus ring is 2 px | `ui::tokens` |
| Material | the panel is glass (unchanged, ADR‑0016). Inside it, sections are **plates**: a tone step, not more glass, with an edge only when card borders are on. On the lock screen the periphery is **ink on the scene** (text with a shadow, no plate), and the field and the power capsule are the only glass | `tab.cpp` (`applySectionCardStyle`), lock preset |
| Typography | chosen by role: the time is `Display` (light, tabular, display face) in both places; values and positions that change are `Data` (mono, tabular); section headings are `Subtitle`; captions and secondary readouts are `Label` / `Micro` in the muted colour. (Muted `Label` headings were tried first; beside the sections' own bold titles they read as inconsistent, so they were withdrawn the same day) | `ui::type` |
| Colour | the accent budget: in the Control Center the accent is the selection capsule's tint and edge, an active toggle, a playing status and the avatar's focus ring — nothing else. On the lock screen it is only the visualiser. An armed destructive action is the only solid fill (error role) | `ui::color` |
| Motion | one shared object per change: the selection capsule (`ElementMove` spring) travels while the item labels fold and unfold (`MotionValue`s on the same role) and the content morphs (`MorphTransition`, `Morph` role). Interrupting retargets all of them from their current position and velocity. No new engine | `AnimationManager`, `MotionValue`, `MorphTransition` |
| Responsive | the command bar shrinks its items before anything overlaps and folds all labels when they do not fit; the lock widgets are anchored to edges or the centre | `layoutCommandBarNav`, widget `anchor` |

**Still only proposed** (unchanged by Batch 7): `SeedMorph` (panels still reveal as a whole surface rather than
growing from the seed), `FocusBrackets`, the lock screen's rack focus, `InkOnScene` contrast correction (the lock
text relies on a shadow and the palette tint, not on measured contrast), `ScenePlacement`, and `FocusAccordion`.
The Zynith Home now honours §12's rule against a grid of equal cards; the classic Home still is one, by design.
