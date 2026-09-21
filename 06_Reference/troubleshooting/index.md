# Troubleshooting Database

Format per entry: **Symptom → Cause → Diagnosis → Fix → Verification → Related**.
Every entry here was an actual failure on this machine.

---

## T‑01 · No notifications appear, and no notification sound

- **Cause:** another process owns `org.freedesktop.Notifications`. On this machine it was SwayNotificationCenter,
  started by a systemd user unit from the Hyprland setup.
- **Diagnosis:** `busctl --user list | grep -i notif` — if the owner is not `noctalia`, that is the whole problem.
- **Fix:**
  ```sh
  mkdir -p ~/.config/systemd/user/swaync.service.d
  printf '[Unit]\nConditionEnvironment=!XDG_CURRENT_DESKTOP=niri\n' \
    > ~/.config/systemd/user/swaync.service.d/10-skip-under-niri.conf
  systemctl --user daemon-reload && systemctl --user stop swaync.service
  # restart the shell so noctalia claims the name
  ```
- **Verification:** `busctl --user list` shows noctalia; `notify-send test hello` produces a toast; record the sink
  monitor with `parec` to prove the cue played.
- **Related:** `04_Incidents/postmortems/2026-09-21-notification-ownership.md`, ADR‑0012.

---

## T‑02 · An edit to `rice.toml` appears to do nothing

- **Cause:** `~/.local/state/noctalia/settings.toml` (written by the settings GUI) overrides
  `~/.config/noctalia/*.toml`.
- **Diagnosis:** `noctalia config export full` shows the *effective* value; compare with your file. Then
  `grep -n '<key>' ~/.local/state/noctalia/settings.toml`.
- **Fix:** change it in the Noctalia **GUI**, or remove the conflicting block from `settings.toml` yourself —
  Zynith tooling deliberately never writes that file.
- **Known live instance:** the bar's `end` widget list, `thickness` and `font_family` are set in `settings.toml`,
  which is why the CPU/RAM/temp cluster and notification bell do not appear even though `rice.toml` lists them.
- **Related:** `02_Architecture/configuration/precedence.md`, ADR‑0003.

---

## T‑03 · btop shows no CPU box

- **Cause:** `shown_boxes` in `~/.config/btop/btop.conf` does not include `cpu`. btop persists box toggles on exit,
  so a stray keypress can remove it permanently.
- **Diagnosis:** `grep '^shown_boxes' ~/.config/btop/btop.conf`
- **Fix:** set `shown_boxes = "cpu proc mem net"`. Change nothing else in that file.
- **Verification:** run btop; the CPU box shows the model name, per-core bars and load averages.

---

## T‑04 · Shell crashes on startup in an unrelated constructor right after a header change

- **Cause:** mixed struct layouts from an incremental build (ABI skew).
- **Diagnosis:** did you just change a widely-included header's layout? If yes, suspect the build before the code.
- **Fix:** `meson compile --clean && meson compile -j 12 && meson install --quiet`
- **Also:** discard every measurement taken from that binary.
- **Related:** `04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md`, ADR‑0013.

---

## T‑05 · Clicking a wallpaper card does nothing (keyboard Enter works)

- **Cause:** z-order. Cards carry a depth-derived z-index and `WallpaperTile` is itself an `InputArea`; if the
  carousel's hit-test overlay is below them, each card swallows the press with no handler attached.
- **Diagnosis:** instrument `CarouselView::onPointerPress` — if it never fires, the press is not reaching the view.
- **Fix:** the overlay's z-index must exceed the maximum card z (`kOverlayZIndex 5000` vs `kFocusZIndex 1000`).
- **Related:** `01_Phases/Phase_6/README.md` (6e).

---

## T‑06 · Applying a wallpaper changes nothing on screen until the browser closes

- **Cause:** the modal backdrop was a **frozen screencopy** covering the live desktop.
- **Fix:** `Panel::ModalBackdropMode::Live` → `ScreenVeil::showTint()` (tint only, no image node).
- **Verification:** on a workspace where the wallpaper is visible, apply and watch the desktop behind the open
  browser change.
- **Related:** `04_Incidents/postmortems/` and ADR‑0007.

---

## T‑07 · Focused wallpaper looks soft / low resolution

- **Cause:** the card is drawing the preview tier (384 px) instead of the display tier (768 px) — either promotion
  is not reaching the tile, or the promoted decode has not landed.
- **Diagnosis:** compare the tile's `frameW` against the texture width. The focused frame is 753.6 px, so the
  texture must be ~768.
- **Fix:** ensure the promotion window covers the focus, that changing the window forces bound tiles to
  re-evaluate, and that the decode gate opens when the settle *begins*.
- **Related:** `04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md`.

---

## T‑08 · Hovering the clock does not open the Control Center

- **Cause:** the hover-intent timer armed only on the `clock` widget, but the Zynith bar puts the clock and the
  audio visualiser in one capsule group — with audio playing, the centre of that cluster is the *visualiser*.
- **Fix:** widgets record their capsule group; resting anywhere on the group containing the clock arms the intent.
- **Verification:** hover the centre of the time cluster for ~350 ms with music playing.

---

## T‑09 · Carousel scrolls the wrong way / not at all with a synthetic input device

- **Cause:** a positive `REL_WHEEL` is scroll-**up**; at offset 0 it clamps and nothing moves. Also, a horizontal
  `ScrollView` ignores the vertical axis unless `setCrossAxisWheel(true)` is set.
- **Note:** this was a *test-harness* error that briefly looked like a shell bug. Verify wheel direction before
  filing anything.

---

## T‑10 · Idle CPU looks far too high

- **Check, in order:** (1) is the build clean? (T‑04) (2) is the workspace quiet — niri composites the user's own
  animating windows, which is not shell cost (3) is a debug log level enabled? `NOCTALIA_LOG_LEVEL=debug` logs
  per-frame and inflates everything.
