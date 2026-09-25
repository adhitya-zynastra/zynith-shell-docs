# ADR-0015 — The shell owns niri animation generation; the Motion plugin is retired

**Status:** Accepted (decision), **implementation deferred to Phase 6B** · **Date:** 2026‑09‑21 (Phase 6A)
**Evidence:** VERIFIED by source inspection at `ccfe125` and by reading the installed plugin.

## Context

Phase 6 moved the motion *model* into the main settings surface — `shell.animation.preset` plus four `niri_*`
trims. The *generator* did not move: the Motion plugin still turns those choices into
`~/.config/niri/rice/animations.kdl`. That leaves two sources of truth for the same thing, which is the problem
this phase exists to eliminate.

Four facts decide it.

**1. The plugin cannot react to the main settings.** It is a *panel*, not a service — deliberately, because
Noctalia plugin services arm an unconditional 1 s timer ([ADR‑0005](ADR-0005-motion-plugin-as-panel.md)). It runs
only while open or on commit. So if a user changes the preset in Settings → Appearance → Motion, the plugin is
not running and `animations.kdl` is never regenerated. **The settings and the generator cannot be in different
places.** Either the generator moves to the shell, or the settings move back to the plugin — and the owner has
explicitly rejected a separate `Super+Alt+A` animation universe.

**2. The shell already writes niri configuration.** I previously recorded moving generation into the shell as "a
new responsibility and a new precedence surface". **That was wrong, and this ADR corrects it.** Noctalia's
builtin template catalogue contains a `niri` entry (`assets/templates/builtin.toml:162`) that renders
`assets/templates/niri/niri.kdl` and applies it via `niri/apply.sh` — which is how `~/.config/niri/noctalia.kdl`,
the palette export Zynith depends on keeping last in the include order, is produced. Writing niri config is the
established mechanism, not a new one.

**3. The infrastructure already exists.** `writeTextFileAtomic()` (`src/config/atomic_file.h`) provides the
atomic swap. `ConfigService::addReloadCallback()` plus `lastChange().shell` provides an event-driven trigger that
skips reloads which did not touch the shell section — no polling, no timer.

**4. The derivation is fully recovered.** From the plugin's `panel.luau`: preset factors (instant 3.0, fast 1.6,
default 1.25, smooth 1.0, cinematic 0.8) applied to baselines (workspace 380, movement 420, overview 400 spring
stiffness; open 360 ms, close 240 ms; screenshot 260; recent/exitConfirm/configNotif 600/600/800), with
`spring(base, f) = max(1, round(base·f²))` and `duration(base, f) = max(1, round(base/f))`, and `slowdown = 1/speed`.
This also explains the observed `motion.toml` value: `0.8 × 0.8 (cinematic) × 1.0 × 1.0 = 0.64`. ✓

## Decision

1. **The shell becomes the sole generator** of `~/.config/niri/rice/animations.kdl`, derived from
   `shell.animation` on config reload, written atomically and validated with `niri validate` before the swap.
2. **The Motion plugin is retired as a settings surface.** Its panel becomes a pointer to
   Settings → Appearance → Motion, or is removed; `Super+Alt+A` is repointed or dropped.
3. **`motion.json` and `motion.toml` cease to be sources of truth.** `shell.animation` in the Noctalia config is
   the single source, with the precedence already established in
   [ADR‑0014](ADR-0014-extend-noctalia-config.md): defaults → `rice.toml` (Zynith preset) → `settings.toml`
   (user deviations).
4. **The `shell` trim is dropped.** In the plugin's model `[shell.animation].speed` was *derived*
   (`0.8 × preset × shell_trim × speed`). In the main settings it is a *direct* user-facing slider, and it has
   shipped that way. Redefining a shipped control's meaning is its own kind of breakage, so the direct meaning
   wins and the redundant trim goes — the phase brief explicitly allows dropping fields the architecture makes
   redundant.
5. **niri's `slowdown` follows `shell.animation.speed`** (`1/speed`), as it did in the plugin. One speed control
   governs both halves of how fast the desktop feels.

## Why the implementation is deferred rather than rushed

Implementing the generator *without* retiring the plugin recreates the dual-writer problem in a worse form: two
programs writing the same file, one on every config change and one whenever the user opens a panel. Retiring the
plugin means modifying `~/.local/share/noctalia/plugins/motion/`, which is the owner's environment rather than
this repository, and that belongs in the same change as a working replacement.

Shipping half of this onto a daily-driver desktop — a compositor-config writer racing a plugin — is precisely
what "do not leave half-built architecture behind" forbids. The decision is settled here; the migration is one
coherent piece of Phase 6B work.

## Consequences

- Once implemented, `animations.kdl` gains a generated-by header naming the shell, and hand edits to it are lost
  on the next config change. That is already true of the plugin-generated file.
- A `niri validate` failure must leave the previous file untouched — generate to a temporary, validate, then
  rename. Never a partial write.
- Rapid consecutive changes must coalesce, or a slider drag spawns a validate per frame. The reload callback
  already fires per reload rather than per keystroke, but this needs checking under a drag before shipping.
- Users with an existing `motion.json` lose nothing: the same preset and trim names exist in `shell.animation`,
  and a one-time migration can read the old file if one is present.

## Alternatives

- *Keep the plugin as generator, have it read Noctalia config* — **impossible**: a panel does not run when the
  main settings change (fact 1).
- *Move the settings back into the plugin* — rejected by the owner; a separate animation settings universe is the
  thing this phase removes.
- *Generate via the template system* — rejected: templates are palette-driven, and animation settings are not
  palette data. Wrong trigger.
