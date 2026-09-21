# Phase 3 — Motion System and the Animation Settings Panel

**Window:** 2026‑09‑19 20:07 (`phase2-anim` backup) → 2026‑09‑20 02:06 (`phase3b` backup).
**Deliverable:** a Luau plugin panel at `~/.local/share/noctalia/plugins/motion/`, not a C++ change.

## Purpose

Give motion a single source of truth and a UI, without adding a background service.

## The architectural decision that shaped it

Noctalia plugin **services** arm an unconditional 1 s repeating timer even when they do nothing. A **panel** does
not: it exists only while open. Since the motto forbids resident polling, the animation settings were built as a
*panel* (`Super+Alt+A`), and all of its work happens on open or on commit.
See `05_Decisions/ADRs/ADR-0005-motion-plugin-as-panel.md`.

## Data flow

```
   motion.json            ← single source of truth (plugin data dir)
        │  on commit
        ├──► ~/.config/noctalia/motion.toml     [shell.animation] enabled / speed
        └──► ~/.config/niri/rice/animations.kdl → `niri validate` → atomic replace
                                                  (rollback on validation failure)
```

Presets: Instant / Fast / Default / Smooth / Cinematic, plus a global speed and advanced percentage-based controls.
**Smooth is the validated Phase 2 baseline and was not altered** — a constraint the owner set explicitly so the
approved lock/unlock choreography kept its timings.

## Precedence protection

`motion.toml` is the **sole owner** of `[shell.animation]`. Because `~/.config/noctalia/*.toml` merges
alphabetically, `rice.toml` would win if it ever defined that table — so `rice.toml` carries a comment forbidding
it, and the plugin scans `rice.toml` line-by-line (stripping comments, tracking section headers) to detect a
conflict and warn. An earlier version of that scanner matched the *comment* itself and produced a false positive;
rewriting it to parse sections fixed it. **RECOVERED** from the session record; the current scanner logic is in
`panel.luau`.

## Bugs

| ID | Symptom | Root cause | Fix |
|---|---|---|---|
| B3‑01 | A Luau ternary always produced the string branch | `draft.enabled and nil or "…"` — `nil` is falsy, so the `or` branch always ran | `(not draft.enabled) and "…" or nil` |
| B3‑02 | Override warnings appeared after every change | The effective-value check raced the asynchronous config reload | Deterministic file scan after commit; effective comparison only when the panel opens |
| B3‑03 | Disabling the plugin left a stale `motion.json` | `onExit` did not reset state | `onExit` atomically writes the defaults back |

## Limitations

- The panel is a second settings surface. The project owner has since stated that this was the wrong long-term
  shape and that it should fold into one primary customization surface — recorded as planned work in
  `06_Reference/future-work.md`, not done.

## Retrospective amendments

| Later phase | Change |
|---|---|
| Phase 6 (`e9e27b0`) | The **base** duration tiers the plugin scales (`animFast/animNormal/animSlow`) were raised 100/200/400 → 130/300/520 and long-tail easings added. The plugin's presets and speed semantics are unchanged, but their on-screen result is slower and smoother |
