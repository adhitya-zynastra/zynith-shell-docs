# Design Foundation — Architecture Assessment and Roadmap

**Status: PROPOSED (2026‑09‑26).** *Amended the same day:* the sixth batch carried out the foundation of Stages 1
and 2, and the data half of Stage 3's origin work, without Stage 0's separate spikes. Tabular figures and the
spring were proven directly with tests and measurements instead. See [`design-foundation.md`](design-foundation.md)
for what is consumed and what is only defined. Surface work (Stages 3–5) is Batch 7. Evidence:
[`design-research-2026-09.md`](design-research-2026-09.md). Target language:
[`design-language.md`](design-language.md).

The question is not "what to redesign next". It is the smallest foundation under which a much richer language can
be built *once*, instead of five screens each redesigned in isolation. The fifth batch showed the cost of the
second approach: a restyled Control Center inside an unchanged structure, reverted within the hour.

## 1. Assessment by system

| System | Verdict | Why |
|---|---|---|
| Config layering, registry, Personalization, ownership rules | **KEEP** | preset → overrides → reset works and is tested; new tokens slot in as keys |
| Position reference, `anchor_bar`, centring rule (ADR‑0018) | **KEEP** | the responsive model the language assumes |
| Widget system (anchors, placement, editor) | **KEEP** | `ScenePlacement` and `InkOnScene` are additions, not replacements |
| Renderer: SDF rect (concave corners, insets, shadows), blur program, shell-rendered wallpaper | **KEEP** | already able to draw `SeedMorph` clips, lens shadows and animated wallpaper blur |
| niri generators (`animations.kdl`, `glass.kdl`) | **KEEP** | compositor motion and blur stay owned in one place |
| `AnimationManager` | **REFINE** | keep it as the frame clock; add a `Spring` channel (value + velocity, ω/ζ, velocity-keeping retarget) and bezier curves. The ten fixed easings stay for effects |
| `MorphTransition` | **REFINE** | generalise into `SeedMorph`: a clip rect + radius + corner shapes animated by springs, with velocity carried across retargets |
| `Style` tokens | **REFINE** | extend: spacing 24–64, a type ramp by role with display faces, radius families + concentric rule, motion roles, accent budget. Existing names stay as aliases while call sites migrate |
| Glass | **REFINE** | from one level to the material levels (`frame`, `lens`, `plate`, `signal`, `scrim`) with a catch-light edge and one shadow spec; it stays the single owner (ADR‑0016) |
| `PanelManager` | **REFINE** | seed-aware open/close (the seed rect is known from the click or anchor); a lens that glides to a new seed on the same output instead of rebuilding |
| Bar system | **REFINE** | bar widgets expose their rectangles as seeds and get the hover/press language; bar layout itself unchanged |
| Text rendering | **REFINE** | tabular figures (Pango font features) and per-role faces |
| Control Center — tab framework, services, sections' data | **KEEP** | the content is right; its presentation is not |
| Control Center — Home layout and card styling | **REBUILD** | the equal-card grid is the structure that limits it (35 identical card applications) |
| Launcher — providers, index, lifecycle | **KEEP** | measured fast (0.23–0.28 ms per query) |
| Launcher — view layer | **REBUILD** | a stock list with a category row; rebuild the presentation on `Lens`, `Readout`, `FocusBrackets` |
| OSD, notifications | **REFINE** | move onto `SeedMorph` (OSD grows from the source widget if visible, otherwise from its edge) and the material levels |
| Lock screen — composition | **REFINE** | a new composition using rack-focus and `InkOnScene`, **after** I decide the `settings.toml` layout question |
| Wallpaper browser | **REFINE** | `FocusAccordion` for browsing; a reveal from the chosen card in the shell-rendered wallpaper |
| Power menu | **REFINE** | `SeedMorph` + `FocusBrackets` arming |
| Island-bar + wide attached panel presentation | **REBUILD** | concave flares beside a 160 px island do not read; `SeedMorph` replaces the flare for panels wider than their bar |
| ext-session-lock, PAM, `LockSurface` authentication, the password path, `session_actions` safety | **DO NOT TOUCH** | security boundary |
| IPC semantics, `settings.toml` ownership, config migrations | **DO NOT TOUCH** | stability and ownership |
| Sound pipeline, PipeWire, notification D-Bus ownership | **DO NOT TOUCH** | stable, recently fixed |
| niri config validation and atomic writes | **DO NOT TOUCH** | a broken compositor config is the worst failure on this machine |

**Considered and rejected for now: one scene per monitor** (the Caelestia and Ryoku architecture). It would make
bar and panel one shape with one shadow. But Zynith's surfaces submit full-buffer damage. A full-output surface
would repaint 1920 × 1200 for every animated pixel, and bar, panel, OSD and notification lifetimes are separate
today for good reasons. `SeedMorph` gets most of the visual benefit inside the panel surface, which already
overlaps the bar region. I will revisit this only if partial damage exists and a measurement shows the cost is
acceptable.

## 2. Roadmap

Primitives before screens. Five stages; each ends with a visual review by me before the next begins.

### Stage 0 — Feasibility spikes (no user-visible change)
- **Objective:** turn every UNKNOWN the language depends on into a measurement.
- **Spikes:**
  - a spring channel prototype with unit tests (settle time and overshoot against the §7 table);
  - a `SeedMorph` clip on one panel behind a flag;
  - whether niri composites `ext-background-effect` blur under surface opacity (can a blurred lens fade?);
  - Pango tabular figures;
  - repaint cost of a larger panel surface;
  - font installation (Space Grotesk, Inter) — my decision.
- **Affected systems:** none shipped.
- **Dependencies:** none.
- **Risks:** low.
- **Validation:** a written go/no-go per primitive, with numbers.

### Stage 1 — Tokens and materials
- **Objective:** the §2–§6 vocabulary exists in code and Glass.
- **Affected systems:** `Style`, Glass, text rendering, the config schema (new keys in the preset).
- **Visual goal:** existing screens change *consistently and subtly* — radii, spacing steps, one shadow spec,
  catch-light, accent budget — with no layout changes.
- **Architectural goal:** one source of truth for every value; old token names become aliases.
- **Dependencies:** Stage 0 (fonts, tabular figures).
- **Risks:** a wide header change (ADR‑0013: clean build); many call sites.
- **Unchanged:** every layout, every behaviour.
- **Validation:** token tests; before/after captures of each surface on the same wallpaper; config validate;
  suite 124/125.

### Stage 2 — Motion foundation
- **Objective:** springs and motion roles are the only way motion is chosen.
- **Affected systems:** `AnimationManager`, `MorphTransition`, call sites (44 × `EaseOutCubic` and the rest).
- **Visual goal:** the same transitions, now with velocity continuity and asymmetric grow/shrink.
- **Architectural goal:** call sites name a *role*. Tempo and reduce-motion apply in one place.
- **Dependencies:** Stage 0 spring spike.
- **Risks:** subtle timing regressions (the approved Phase 2 lock choreography must not change); CPU per frame.
- **Unchanged:** niri's own springs; lock choreography timings (pinned by test).
- **Validation:**
  - unit tests of the spring maths;
  - **frame-capture measurement with the research method**: the measured curves must fit their role within
    RMS 0.05;
  - a rapid-retarget capture must show no velocity discontinuity;
  - open/close CPU no worse than today's 80–86 ms per cycle.

### Stage 3 — Signature primitives on one surface
- **Objective:** `SeedMorph`, focal plane, `FocusBrackets`, the `signal` material and `Readout`, proven end to end on
  **the Control Center only**.
- **Affected systems:** `PanelManager`, bar seeds, Control Center presentation (Home rebuilt), Glass.
- **Visual goal:** the Control Center grows out of the widget I clicked, the shell recedes, keyboard focus shows as
  brackets, the Home tab has one focal readout instead of a grid of equal cards.
- **Architectural goal:** the primitives are generic; nothing in them names the Control Center.
- **Dependencies:** Stages 1–2.
- **Risks:** surface-size and clip interplay with the existing attached reveal; hover-open and click-open paths;
  the coordinate model.
- **Unchanged:** routing, anchor bar, position references, hover intent, section data.
- **Validation:** frame captures of open/close/retarget; coordinate-model checks from the fourth batch re-run;
  CPU and fds over 20 cycles; my review.

### Stage 4 — Recompose the other surfaces
- **Objective:** apply the primitives surface by surface, each starting from a written composition, in this order:
  1. launcher (view rebuilt);
  2. OSD and notifications;
  3. wallpaper browser (`FocusAccordion`, reveal);
  4. power menu;
  5. lock screen (after the `settings.toml` layout decision; authentication untouched).
- **Dependencies:** Stage 3 accepted.
- **Risks:** scope; each surface is its own review.
- **Unchanged:** providers, feeders, D-Bus, authentication.
- **Validation:** per surface — captures, measured motion against the roles, resource cycles, no real lock
  (editor only).

### Stage 5 — Composing with the scene
- **Objective:** `InkOnScene` and `ScenePlacement` for desktop widgets and lock text.
- **Visual goal:** legible, deliberately placed text on light, dark and busy wallpapers.
- **Architectural goal:** analysis runs once per wallpaper change, off the frame path.
- **Dependencies:** Stage 1.
- **Risks:** mis-placement on unusual images; always overridable by the user's placement.
- **Validation:** a fixed set of test wallpapers (light, dark, busy, centred subject); contrast ≥ 4.5:1 measured
  from captures.

## 3. Risks and trade-offs

| Risk | Mitigation |
|---|---|
| Springs read as "bouncy" or gamer-like | overshoot only on growth, capped at 1.5 % (measured references sit at ≈ 1 %); shrink never overshoots |
| Performance: more animated properties, shadows and clips; full-buffer repaint per surface | keep surfaces tight; Stage 0 measures a larger surface; every stage re-runs the open/close CPU and idle checks |
| Fonts are not installed | fallbacks defined; installing fonts is my decision |
| Compositor blur cannot be animated | the focal plane is designed scrim-first; animated blur only where the shell renders the wallpaper |
| Scope creep: screens before primitives | the order above; Stage 3 is one surface |
| Rebase cost against upstream Noctalia | primitives are additive (new channel, new roles); upstream files change at call sites only |
| Taste | a visual review by me closes every stage; the classic styles stay selectable until a stage is accepted |

## 4. What is deliberately not copied

- Caelestia's frame-and-drawer silhouette and Material defaults.
- Ryoku's paper-and-ink palette, kanji glosses, dither and poster ornaments, and the seal.
- Clavis's island.
- Imperative's skewed carousel and lens-circle lock.
- End4's cookie shapes.
- Polling for visual state (Caelestia polls every 0.5–1 s).

The ideas taken are general ones:
- surfaces with an origin;
- one container carried through a change;
- velocity-preserving springs and asymmetric grow/shrink;
- contrast correction on the wallpaper;
- an accent budget;
- semantic motion roles.
