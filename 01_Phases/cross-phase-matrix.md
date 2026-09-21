# Cross-Phase Amendment Matrix

When a later phase materially changes something an earlier phase introduced, it is recorded here **and** in the
earlier phase's "Retrospective amendments" section. Phase documents are never rewritten to hide the original design.

| Originally introduced | Phase | Amended by | Commit | Change | Impact |
|---|---|---|---|---|---|
| `ScreenVeil` primitive | 2 | 2.5 | `6de342a` | Reused as the modal power-menu backdrop; `PanelManager` gained `showModalBackdrop()`/`hideModalBackdrop()` | New consumer; no behaviour change for lock/unlock |
| `ScreenVeil` primitive | 2 | 6 | `e9e27b0` | Added `showTint()` — a tint-only mode with no image node | Enabled the live wallpaper backdrop; snapshot mode unchanged for the power menu |
| Lock/unlock timing model | 2 | 6 | `e9e27b0` | Base duration tiers raised (100/200/400 → 130/300/520) and long-tail easings added | Lock choreography uses its **own** constants, so approved timings held; only shared-tier surfaces slowed |
| Motion plugin presets | 3 | 6 | `e9e27b0` | Same tier change — presets and speed semantics unchanged, on-screen result slower/smoother | No config migration needed |
| OSD hold (`kHideDelayMs`) | 4 | 6 | `e9e27b0` | **Pinned at 1400 ms**; it had been derived from the tiers and would have drifted to 1.82 s | Prevented a silent behaviour change |
| OSD/notification easings | 4, 5 | 6 | `e9e27b0` | `EaseOutCubic` → `EaseOutQuint`, `EaseInOutQuad` → `EaseInOutQuint` | Visual only |
| Mute cue logic | 4 | 5 | `803664d` | Converged all mute paths in `AudioOsd::showOutput/showInput`; cooldown 70 → 110 ms | Fixed a three-layer bug |
| Bar composition | 1 | 6 | config only | Per-widget pills → three glass clusters (`capsule = false` + `capsule_group`) | No C++; no measured CPU change |
| Notification toast | 5 | 6 | `e9e27b0` | Reveal/exit easings retuned | Visual only |
| `AnimationManager` | inherited | 6 | `08f5454`, `eaff2b2` | Reentrancy contract; pending additions; dead-marking; allocation-free tick | Every animated surface in the shell depends on this |
| `Signal` | inherited | 6 | `08f5454`, `eaff2b2` | Lifetime contract; deque storage; tombstones | Fixed the shell's only crash |
| `ThumbnailService` | inherited | 6 | `46296d0`, `eaff2b2`, `57debbc` | Idle LRU, decode gate, sessions with ownership tags, `prefetch()` | Shared with control center, settings and file dialogs — changes affect all of them |
| Panel lifecycle | inherited | 6 | `e9e27b0` | `retargetOpen()`; `ModalBackdropMode` | Any panel can now accept a new context without being rebuilt |
