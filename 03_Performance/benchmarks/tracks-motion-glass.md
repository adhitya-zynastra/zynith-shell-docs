# Motion, Zynith Corner and Glass — Validation Record

**Date:** 2026‑09‑25. **Implementation:** `aaa69b0` (glass) → `f5cad71` (motion) → `8c2b4eb` (Zynith Corner).
**Binary tested:** one clean build (`meson compile --clean`, 998 targets, zero failures) of the tree that became
`8c2b4eb`; the committed tree is byte-identical to it. The two intermediate commits were **not** built on their
own.

This was an implementation-first pass, so validation aimed at catching regressions rather than at a full campaign.

## Tests

| Suite | Result |
|---|---|
| Full suite | **122 / 123** — only `upower_charge_limit_integration`, unrelated and pre-existing |
| `niri_config_fragments_test` (new) | pass — incl. **byte-exact** match with the plugin's last output |
| `glass_surface_test` (new) | pass |
| `zynith_config_ownership_test` (new) | pass — reset deletes the override from `settings.toml` |
| `morph_transition_test`, `signal_dispatch_test`, `animation_reentrancy_test` | pass — lifetime protections intact after the `ColorSpec` layout change |

## Runtime checks on the live desktop

Changes were driven through `rice.toml` — the Zynith preset layer — and every one was reverted; `rice.toml` was
compared byte-for-byte with its pre-test copy afterwards. `settings.toml` was never written by any test.

| Check | Result |
|---|---|
| Migration: generated `animations.kdl` vs the plugin's | body **identical** (diff empty); only the header changed |
| `glass.kdl` generated, full config valid | yes; `blur` moved out of `config.kdl` into the include; `noctalia.kdl` still last |
| Leftover candidate temp files | none |
| 8 edits in ~0.3 s ending on the **original** value | **0 installs** — intermediate values never written |
| 8 edits in ~0.3 s ending on a **new** value (1.25) | **exactly 1 install**, `slowdown 0.8` = 1/1.25 |
| Animations off | `animations { off }`, niri valid; back on restores the original body exactly |
| `Super+Alt+A` command (`settings-open zynith-corner`) | opens Zynith Corner on the Motion group with correct current values |
| Plugin retired | disabled through `noctalia msg plugins disable` (the shell's own path), files removed, backed up |
| Glass tint on the launcher | fill patch mean **(26, 29, 24) → (46, 51, 39)**, toward the palette's primary |
| Glass blur off | wallpaper sharp behind the card (visual; see `glass-blur-compare.png`) |
| 100 × launcher + Zynith Corner open/close | RSS +12.9 MB then **+0.24 MB** (plateau), threads 34 → 34, fds 100 → 100, same pid |
| Coredumps this boot | none |
| Stuck surfaces | none (overlay layer empty) |

## Performance — interleaved A/B, matched pace

A = `a147fc1`, B = this work. The two binaries interpret `speed` differently (direct vs global), so A ran with
`speed = 0.64` and B with `speed = 1.0 × Cinematic` — both a shell pace of 0.64. The shell was stopped before each
edit, so no writer ever saw the A value; niri's `slowdown` read 1.0 in every round.

| | A | B |
|---|---|---|
| Idle, shell | 2.39 · 2.63 % | 2.62 · 2.45 % |
| Launcher open/close (the main glass consumer here) | 173.0 · 176.0 ms | 176.0 · 176.5 ms |

**No regression.** Two media streams were playing in every round, so the absolute idle figures include the bar's
visualiser (see `03_Performance/baselines/idle-conditions.md`); the condition was the same in both arms, which is
what an A/B needs. Raw data: `tracks-motion-glass-ab.csv`.

## Measurements rejected

- **Edge-energy "sharpness" behind the launcher.** It ranked blur-off *below* blur-on — impossible. The sample box
  overlapped launcher text, whose edges dominate. Not used; the visual comparison is the evidence instead.
- **"Tint follows a light palette."** Switching to light mode gave an identical colour, because this desktop pins
  `shell_mode = "dark"`: the toggle never changed the shell's palette. Not a failure of the tint, and not evidence
  of anything.

## Not tested, and why

- **Tint following a real palette change at runtime.** The only ways to change the shell's palette here are
  changing the wallpaper or `shell_mode`, and I will not touch either on the owner's desktop for a test. Covered by
  `glass_surface_test`, which swaps the palette under the same spec.
- **Full-config rollback.** Exercising it means deliberately breaking the live niri config. Implemented and
  reasoned through; not run.
- **Reset through the GUI.** Would write `settings.toml`. Covered by the ownership test against a real
  `ConfigService` in a temp directory.
- **GPU memory** — still not measurable without privileges.
