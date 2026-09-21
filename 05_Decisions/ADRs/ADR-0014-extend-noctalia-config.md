# ADR-0014 — Extend Noctalia's configuration system; treat `settings.toml` as the user's deviation layer

**Status:** Accepted · **Date:** 2026‑09‑21 (Phase 6) · **Evidence:** VERIFIED by source inspection at `57debbc`

## Context
Phase 6's remaining scope — launcher styles, lock-screen composition, Control Center behaviour, motion — is mostly
*configurable surface*. I needed a configuration architecture before writing any of it, or I would end up with
four feature-specific settings systems plus the Motion plugin's, and no coherent story about precedence.

Two facts from inspecting the source decided this:

1. Noctalia already has a complete config system — typed model, declarative schema, merge, validation, origins
   tracking, an override write path, versioned migrations, and a 22-section settings UI. Roughly 14,700 lines.
2. The settings GUI writes `~/.local/state/noctalia/settings.toml` (`config_service.cpp:557`), which sits **above**
   `~/.config/noctalia/*.toml` in the merge. So anything a user changes in the GUI permanently shadows Zynith's
   `rice.toml` value for that key.

Fact 2 is the same shape as the `[shell.animation].speed` precedence problem I hit in Phase 3, and I did not want
to discover it a third time after building three subsystems on top of it.

## Decision
1. **Zynith extends the existing configuration system and never builds beside it.** A new setting is a field on a
   config struct, a line in `schema/config_schema.cpp`, and an entry in `settings_registry.cpp`.
2. **The two layers get distinct meanings.** `rice.toml` is *the Zynith preset*; `settings.toml` is *the user's
   deliberate deviations from it*. Shadowing is the intended semantics, not a defect.
3. **Reset means delete.** "Reset to default" calls `ConfigService::clearOverride(path)`, removing the key from
   `settings.toml` so the value falls back to the Zynith preset. It must never write the preset's current value
   into the override layer.
4. **Deviations must be visible.** `hasEffectiveOverride(path)` plus `ConfigOriginIndex` already provide this.

## Why
I considered moving Zynith's design into `settings.toml` and rejected it: that makes Zynith a second writer of a
file the GUI rewrites wholesale, which is the one boundary this project has never crossed (ADR‑0003). I considered
a separate Zynith preset layer and rejected it too — a third source of truth for the same keys reproduces the
precedence problem with more moving parts.

Treating the existing layering as the intended semantics costs nothing to build, because the machinery
(`hasOverride`, `hasEffectiveOverride`, `clearOverride`, origin tracking) is already there. It also gives the
honest answer to "why did my Zynith default stop applying": because you changed it, and that is being respected.

Point 3 is the part that is easy to get wrong and expensive to discover later. A "reset" that writes the current
default into `settings.toml` looks identical to the user on the day they click it, and silently freezes that key
at today's value forever — detaching it from every future Zynith change. Deleting the override is the only
behaviour that keeps the preset live.

## Alternatives
- *Move Zynith's design into `settings.toml`* — rejected: two writers, last-writer-wins, ADR‑0003.
- *A third Zynith-preset config layer* — rejected: another source of truth for the same keys.
- *A per-feature settings system per subsystem* — rejected: this is what the decision exists to prevent.

## Consequences
- Every new setting costs three edits in three existing files. The friction is deliberate — it keeps schema,
  validation and UI from drifting.
- A shipped change to a Zynith default only reaches users who have not touched that key. Correct, and worth
  stating in release notes when a default changes.
- `rice.toml` must remain hand-written and commented; it is the statement of what Zynith's design *is*, and must
  never become a generated file.
- Internal invariants (cache tiers, promotion windows, z-index constants) stay unexposed. Exposing one converts it
  into a compatibility obligation; where a real preference exists behind it, the exposure is intent-level
  ("preview quality: balanced / high"), not the raw constant.
