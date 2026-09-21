# Phase 1 — Bugs

## B1‑01 · A `sed` edit removed the wrong `font_family`

- **Symptom:** after an edit intended to change the shell font, a desktop widget lost its font instead.
- **Root cause:** the substitution matched the *first* `font_family` key in `settings.toml`, which belonged to a
  desktop widget rather than the shell-level section.
- **Fix:** the widget's line was restored by hand and the correct shell-level key removed. **RECOVERED** from the
  session record; the current `settings.toml` is consistent.
- **Lesson, since applied everywhere:** never edit TOML with positional regex. Later phases parse section
  context explicitly (the Motion plugin's override scanner does exactly this).

## B1‑02 · Invalid colour roles rejected by the validator

- **Symptom:** `noctalia config validate` refused the configuration.
- **Cause:** `surface_container_high` and `outline_variant` are not valid Noctalia colour roles; only the core
  Material‑3 roles exist.
- **Fix:** use `surface_variant`. This constraint is now recorded in `00_Project/overview.md` and
  `06_Reference/configuration/noctalia-rice.md`.

## B1‑03 · Clicking empty bar space opened the launcher

- **Symptom:** stray clicks on the bar opened the launcher.
- **Fix:** `[bar.default.dead_zone.actions]` — `left = "none"`, `middle = "none"`, scroll bound to workspace
  switching. The launcher is reachable only from its own button or `Super+D`. **VERIFIED** in `rice.toml`.
