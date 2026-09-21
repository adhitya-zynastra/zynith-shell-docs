# Configurability Architecture

**Status:** design adopted 2026‑09‑21, Phase 6. **Source state at design time:** `57debbc`.
**Evidence:** VERIFIED by reading `src/config/` and `src/shell/settings/` in the patch repository.

## What I wanted

My rule for Zynith going forward is *everything a user reasonably expects to customize should be configurable* —
and the counter-rule that keeps it from becoming unusable: **not every internal variable becomes a slider**. What
I did not want was to start bolting per-feature settings onto the launcher, the lock screen and the Control
Center independently and end up with four small settings universes plus the Motion plugin's fifth.

So before any of the Phase 6 UI work, I had Claude inspect what already exists.

## What already exists (and why I am not replacing it)

Noctalia 5.1 already has a complete, mature configuration system — roughly **14,700 lines** under `src/config/`:

| Component | File | Responsibility |
|---|---|---|
| Typed model | `config_types.h` (1,791 lines) | Every config struct, with defaults as member initialisers |
| Declarative schema | `schema/config_schema.cpp` (2,371 lines) | `field()` / `subTable()` / `enumField()` binding TOML keys to members, with ranges |
| Merge | `config_merge.cpp` | Deep merge of the config directory, then the override layer |
| Validation | `config_validate.cpp` (820 lines) | Range and type checking with diagnostics |
| Origins | `config_origins.cpp` | Which **file and line** defined each key — the basis for override reporting |
| Overrides | `config_overrides.cpp` (2,716 lines) | The GUI write path: `setOverride` / `clearOverride` at a dotted path |
| Migrations | `config_migrations.cpp` (1,008 lines) | Versioned config upgrades |
| Settings UI | `shell/settings/` (59 files) | 22 sections, a registry, and a control factory |

**Decision: Zynith extends this system and never builds beside it.** A new Zynith setting is a field on an
existing config struct, a line in the schema, and an entry in the settings registry — three additions in three
existing files. That is the whole architecture, and it is deliberately boring.

## The precedence fact that shapes everything

This is the part I most wanted settled before writing UI code, because it is exactly the class of problem that
bit me once already with `[shell.animation].speed`.

```
  defaults (member initialisers in config_types.h)
      ↓  overridden by
  ~/.config/noctalia/*.toml        ← merged ALPHABETICALLY. Zynith's design lives here (rice.toml)
      ↓  overridden by
  ~/.local/state/noctalia/settings.toml   ← the GUI's override layer. Always wins.
```

**VERIFIED:** `ConfigService` sets `m_overridesPath = <state-dir>/settings.toml` (`config_service.cpp:557`), and
the settings GUI writes every change through `setOverride()` into that file.

The consequence is unavoidable and worth stating plainly: **the moment a user changes a Zynith-designed setting
in the GUI, that key is pinned in `settings.toml` and my `rice.toml` value stops having any effect on it —
permanently, including across future Zynith updates.**

### Why that is correct, and what it obliges me to build

I considered three ways to resolve it.

- **Move Zynith's design into `settings.toml`.** Rejected outright. It makes Zynith a second writer of a file the
  GUI rewrites wholesale, which is the one boundary this project has never crossed
  ([ADR‑0003](../../05_Decisions/ADRs/ADR-0003-settings-ownership.md)).
- **Introduce a separate Zynith preset layer.** Rejected: a third source of truth for the same keys is how you
  get the `shell.animation.speed` problem back with more moving parts.
- **Treat the layering as the intended semantics.** Adopted.

Under the adopted model the two layers have distinct, honest meanings:

| Layer | Meaning | Written by |
|---|---|---|
| `rice.toml` | **The Zynith preset** — my opinionated defaults for the whole design language | me, by hand |
| `settings.toml` | **The user's deliberate deviations** from that preset | the GUI, only when the user changes something |

Shadowing is then not a bug; it is a user decision being respected. But it obliges two things that must exist for
the model to be usable, and both are buildable because the machinery is already there:

1. **Visibility.** A setting that deviates from the Zynith preset must be identifiable as such.
   `ConfigService::hasEffectiveOverride(path)` already answers exactly this, and `ConfigOriginIndex` already knows
   which file supplied the losing value.
2. **Reset means delete, not rewrite.** "Reset to default" must call `clearOverride(path)` — removing the key from
   `settings.toml` so the value falls back through the merge to the Zynith preset. It must **never** write the
   preset's current value into `settings.toml`, which would silently freeze today's default forever and detach the
   setting from future Zynith changes. `clearOverride` / `clearOverrides` already exist
   (`config_service.h:173-174`).

## The twelve questions, answered

| Concern | Resolution |
|---|---|
| **Ownership** | One owner per key. Defaults: `config_types.h`. Zynith preset: `rice.toml`. User deviations: `settings.toml` (GUI only). No key has two writers |
| **Defaults** | Member initialisers on the config structs — the single place a default is stated |
| **Schema** | Declarative in `schema/config_schema.cpp`; a field that is not in the schema is not loadable, so the schema is the contract |
| **Persistence** | TOML. Zynith's layer hand-edited; the override layer written atomically by `config_overrides.cpp` |
| **Validation** | `config_validate.cpp` against the schema's declared ranges, before application |
| **Runtime application** | Config reload is event-driven (inotify), not polled; subsystems react to the change signal |
| **Migration** | `config_migrations.cpp`, versioned. A renamed or removed Zynith key gets a migration, never a silent drop |
| **Reset / default** | `clearOverride(path)` — **delete the override**, never write the current default |
| **Precedence** | defaults → `~/.config/noctalia/*.toml` (alphabetical) → `settings.toml`. Documented in [`precedence.md`](precedence.md) |
| **Invalid values** | Rejected by validation with a diagnostic carrying the originating file and line; the previous valid value stands |
| **Subsystem boundaries** | Each subsystem owns one config sub-table (`[shell.launcher]`, `[shell.animation]`, …) and reads nothing outside it |
| **UI exposure** | An entry in `settings_registry.cpp` binding a section, group, label, dotted path and control type |

## What becomes configurable, and what does not

The test I am applying, rather than a list I will fail to keep current:

**Expose it** when a reasonable user would want it different and the value is meaningful on its own — geometry,
spacing, padding, margins, radius, opacity, blur, tint, borders, shadows, typography, visibility, layout, motion
behaviour, interaction behaviour, and per-widget behaviour.

**Do not expose it** when it is an implementation detail whose correct value depends on other internals — cache
sizes, decode gates, promotion windows, z-index constants, timer granularity, texture tiers. `kPromotionAhead = 3`
is not a setting; it is a consequence of how the carousel draws. A user cannot reason about it, and exposing it
converts an internal invariant into a compatibility obligation.

Where a preference genuinely exists behind an internal (someone wants sharper previews at higher memory cost),
the right exposure is an intent-level choice — *preview quality: balanced / high* — not the raw pixel tier.

## Consequences I am accepting

- Every new Zynith setting costs three edits in three existing files. That friction is the point: it keeps the
  schema, the validation and the UI from drifting apart.
- The Zynith preset can never override a user's explicit GUI choice. That is correct, and it means shipping a
  changed default only reaches users who have not touched that key.
- `rice.toml` must stay hand-editable and commented, because it is the document that states what Zynith's design
  *is*. It is not a generated file and must not become one.

## Related

- [ADR‑0014](../../05_Decisions/ADRs/ADR-0014-extend-noctalia-config.md) — the decision record for this page
- [ADR‑0003](../../05_Decisions/ADRs/ADR-0003-settings-ownership.md) — why Zynith never writes `settings.toml`
- [`precedence.md`](precedence.md) — the merge order in detail
