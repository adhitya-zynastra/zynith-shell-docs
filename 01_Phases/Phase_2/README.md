# Phase 2 — Lock Screen, Transitions, Modal Power Menu

**Window:** 2026‑09‑19 19:38 → 21:49 (git author dates).
**Commits:** `bf0a376` → `7d030fb` → `44e678e` → `6058aa6` → `6de342a` → `4289b62`.
This is where Zynith stopped being configuration and became a **patch series**. The base commit `a176ada`
("noctalia 5.1.0 pristine (Fedora SRPM)") was created first so every later diff is reviewable against the
distribution source.

## Goals

1. A lock screen that is beautiful but *restrained*, with an identity that is generic (no hard-coded name/avatar).
2. Visual lock/unlock **transitions** — the session lock previously snapped.
3. A centred, modal power menu.

Non-goals, stated by the owner: do not touch PAM, do not change the `ext-session-lock` protocol usage, keep the
Fedora package untouched, keep the patch minimal and documented.

## Architecture

### Password presentation (`bf0a376`)

The password row starts at opacity 0 while still keyboard-focused, and fades in when the field has text, an attempt
is in flight, or an error exists. Status text moved *inside* the pill as its placeholder ("Authenticating…",
"Incorrect password") using the input's own invalid styling — the separate status label now shows only the Caps
Lock warning.

### Entrance and exit choreography

`playEntrance()` fades lock widgets in top-to-bottom by on-screen position (70 ms delay, 20 ms stagger, 210 ms
ease-out, base values). `playExit()` fades the pill first, then the widgets recede, and **returns the time at which
the last fade ends**.

### The unlock timing bug and its fix (`7d030fb`, `44e678e`)

The owner challenged a hard-coded `kExitDurationMs = 380` against the arithmetic of the individual fades. The
investigation established that Noctalia divides every base duration by `[shell.animation].speed`, so at speed 0.8
a 304 ms base *is* 380 ms on screen. The fix made the unlock timer **derive** from the schedule
`playExit()` reports rather than duplicating a constant, so the session unlocks exactly when the last fade ends —
and 0 ms when animations are disabled.

### The unlock veil (`6058aa6`) — and why it exists

niri refuses compositor actions while the session is locked (`allowed_when_locked`), so `DoScreenTransition` could
bridge *into* the lock but not out of it. The solution was a new primitive, `ScreenVeil`
(`src/shell/veil/screen_veil.{h,cpp}`): a short-lived, full-screen, click-through layer surface that draws a
blurred texture under a palette tint and fades on the shell's own `AnimationManager`. At authentication success a
veil per output is prepared with the lock background's exact source/blur/tint; after the unchanged `unlock()` it
fades out, revealing the live desktop. A 2 s one-shot timer guarantees removal.

> `ScreenVeil` outlived its original purpose: Phase 2.5 reused it as the power menu's modal backdrop, and Phase 6
> extended it with a tint-only mode for the wallpaper browser. See retrospective amendments.

### Modal power menu (`6de342a`, `4289b62`)

`shell.session.modal` (a Zynith-added config key) switches the session panel to circular glyph buttons with labels
below, over a dimmed blurred snapshot of the desktop. `4289b62` then removed the rectangular card, shadow **and the
compositor blur region** so the entire screen stays uniformly blurred — the owner had specifically rejected the
"rectangular wallpaper region" around the orbs. Destructive actions (Shut Down) use the wallpaper-derived `error`
role rather than a hard-coded red.

## Timing model (still in force)

Every duration in the patch is a **base** value that Noctalia divides by `[shell.animation].speed`. The values were
approved at speed 1.6 and halved when the desktop moved to 0.8, so on-screen timings were unchanged. This is why
later phases could retune global speed without breaking the approved lock choreography.

## Security

PAM (`PamAuthenticator`), `tryAuthenticate()`'s credential handling, `handleAuthResult()`'s failure path,
fingerprint logic and the `ext-session-lock-v1` usage are **untouched**; only presentation and a deferred
`unlock()` call were changed. **VERIFIED** — `README.md` in the patch repo lists these as explicit non-changes and
the diffs confirm it.

## Retrospective amendments

| Later phase | Change |
|---|---|
| Phase 2.5 (`6de342a`) | `ScreenVeil` reused for the modal backdrop; `PanelManager` gained `showModalBackdrop()`/`hideModalBackdrop()` |
| Phase 6 (`e9e27b0`) | `ScreenVeil` gained `showTint()` (no image node) and `Panel::ModalBackdropMode`; panel reveal easing changed to `EaseOutQuint` |
| Phase 6 (`08f5454`) | The `AnimationManager` that drives these transitions was rewritten for reentrancy safety |

## Limitations

- Lock-screen power controls do not exist (planned; `06_Reference/future-work.md`).
- Automated lock/unlock testing is deliberately avoided on the owner's machine to avoid lockout risk, so the
  transitions are validated visually and by timing arithmetic, not by an automated test.
