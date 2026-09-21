# Motion Settings — One Surface, One Owner

**Status:** in progress, Phase 6. **Implemented at:** config model and settings UI landed; niri generation
still owned by the Motion plugin (see *What is not done yet*).

## What I wanted

Phase 3 gave motion a UI by building a Luau plugin panel (`Super+Alt+A`). It worked, and I said at the time that
it was the wrong long-term shape — motion belongs in the one customization surface users already know, not in a
plugin panel of its own. This is that correction.

## The problem, stated precisely

The main settings surface **already** exposed two motion keys, under Appearance → Motion:

| Setting | Config path | Registry |
|---|---|---|
| Animations enabled | `shell.animation.enabled` | `settings_registry.cpp:592` |
| Animation speed | `shell.animation.speed` | `settings_registry.cpp:597` |

The Motion plugin writes **the same two keys** into `~/.config/noctalia/motion.toml`, where its header claims to
be their "sole owner". Both statements cannot be true, and the precedence between them is not symmetrical:

```
  ~/.config/noctalia/motion.toml     ← the plugin writes here
        ↓  overridden by
  ~/.local/state/noctalia/settings.toml   ← the main settings UI writes here. Always wins.
```

So dragging the Animation Speed slider in main settings **permanently detaches speed from the Motion plugin**.
The plugin's panel would keep showing its own number while the shell used a different one.

**VERIFIED at the time of writing:** `settings.toml` contains no `shell.animation` table, so the conflict is
**latent, not active** — the plugin's value (`speed = 0.64` under the Cinematic preset) is what the shell uses.
It would become active the first time anyone touches that slider. This is the same failure shape as the original
`[shell.animation].speed` precedence problem from Phase 3, and finding it latent rather than live was luck.

## The fix

Rather than teach two surfaces to coexist, make one of them the home. Following
[ADR‑0014](../../05_Decisions/ADRs/ADR-0014-extend-noctalia-config.md), motion is now modelled in the main config
schema and exposed in the main settings surface.

`ShellConfig::AnimationConfig` gained the compositor-side model that previously lived only in the plugin's
`motion.json`:

| Field | Key | Type | Default |
|---|---|---|---|
| `preset` | `shell.animation.preset` | enum: instant / fast / default / smooth / cinematic | `smooth` |
| `niriOpen` | `shell.animation.niri_open` | int %, 0–200 | 100 |
| `niriClose` | `shell.animation.niri_close` | int %, 0–200 | 100 |
| `niriMovement` | `shell.animation.niri_movement` | int %, 0–200 | 100 |
| `niriOverview` | `shell.animation.niri_overview` | int %, 0–200 | 100 |

All five are registered in Appearance → Motion beside the two that were already there, so "how fast does the
desktop feel" is one group rather than two surfaces that can disagree.

Design points worth stating, because they are decisions rather than mechanics:

- **The preset is the shape; the trims adjust it.** A trim is a percentage of the preset's baseline, with 100
  meaning the preset unmodified. This preserves the Phase 3 property that **Smooth is the approved Phase 2
  baseline and is not altered** — a user who wants faster window opens trims `niri_open`, and the lock/unlock
  choreography that was approved against Smooth keeps its timings.
- **One table, not two.** The compositor keys are namespaced `niri_*` inside `shell.animation` rather than split
  into a separate `[shell.motion]` table. Splitting them would have recreated the two-owners problem at a
  different address.
- **`shell.animation.speed` keeps its existing meaning** — the direct multiplier for Noctalia's own surfaces. It
  is deliberately *not* redefined as a derived value, because it is an existing user-facing slider and silently
  changing what a shipped setting means is its own kind of breakage.
- **Defaults match the plugin's defaults**, so a user who has never opened either surface sees no behaviour
  change from this work.

### Files changed

| File | Change |
|---|---|
| `src/config/config_types.h` | `MotionPreset` enum + `kMotionPresets[]`; five fields on `AnimationConfig` |
| `src/config/schema/ranges.h` | `kMotionTrimRange{0, 200, 5}` |
| `src/config/schema/config_schema.cpp` | Five schema bindings in `shellAnimationSchema()` |
| `src/shell/settings/settings_registry.cpp` | Five entries in Appearance → Motion |
| `assets/translations/en.json` | Labels, descriptions, and the five preset option names |

A note for whoever changes this next: `AnimationConfig` is in `config_types.h`, which is widely included, and this
change altered its layout. Per [ADR‑0013](../../05_Decisions/ADRs/ADR-0013-clean-build-for-measurement.md) that
requires `meson compile --clean` before the binary is run or measured — which is exactly the mistake that
produced hours of invalid data once already.

## What is not done yet

**The Motion plugin still generates `~/.config/niri/rice/animations.kdl`.** The config model and the UI have
moved, but the generator has not, so at the time of writing the plugin remains the thing that turns a preset and
four trims into niri KDL, validates it with `niri validate`, and swaps it atomically.

That generation step is the plugin's one genuinely irreplaceable capability, and moving it has a real design
question behind it: the shell would become a writer of niri's configuration directory, which is a new
responsibility and a new precedence surface. Until that is resolved the migration is **incomplete**, and the
honest description of the current state is: *the settings live in the main surface; the generator does not.*

Recorded as remaining work in [`future-work.md`](../../06_Reference/future-work.md) rather than described as
finished.
