# Glossary

Written for a developer joining the project, not for a Wayland expert.

| Term | Meaning in this project |
|---|---|
| **Wayland** | The display protocol. Clients draw their own windows; the compositor arranges and composites them. There is no X server. |
| **Compositor** | The process that owns the screen. Here: **niri**. It composites surfaces, applies blur, handles input routing and window management. |
| **niri** | A scrollable-tiling Wayland compositor, configured in KDL. Provides window animations, `layer-rule` blur, screencopy, and `ext-session-lock`. |
| **Noctalia** | The desktop shell Zynith patches — a native **C++** application (5.x is a rewrite; it is *not* QML). Draws bar, panels, notifications, OSD, lock screen and wallpaper. |
| **Zynith** | This project: a patch series over Noctalia + a configuration layer + two plugins. |
| **layer-shell** | The Wayland protocol that lets a client place a surface as desktop furniture (bar, panel, wallpaper, overlay) rather than as a window. Every Zynith surface is one. |
| **Surface** | A Wayland drawing target. A panel, a toast and the wallpaper are each a surface. |
| **Exclusive zone** | Screen area a layer surface reserves so windows do not overlap it — how the bar pushes windows down. |
| **D-Bus** | The session IPC bus. Relevant here because `org.freedesktop.Notifications` can be owned by exactly one process. |
| **PipeWire** | The audio (and video) graph. Zynith plays cues in-process on its loop and reads the spectrum for the bar visualiser. |
| **systemd user unit** | A service managed per-login-session. `swaync.service` is one, and it had to be made session-conditional. |
| **zram** | A compressed RAM-backed swap device. 8 GiB here, lzo-rle, ~2.8:1 in practice. |
| **Signal / ScopedConnection** | Zynith's observer primitive (`src/ui/signal.h`). `ScopedConnection` disconnects on destruction. Its dispatch rules are safety-critical — see ADR‑0011. |
| **AnimationManager** | The single animation engine. Drives every animated property from one tick. Components never run their own frame clock. |
| **MotionService** | Holds the global animation `enabled` flag and `speed` (0.05–4.0). Every base duration is divided by speed. |
| **Tombstone** | Marking an entry *dead* instead of erasing it, so an in-flight dispatch keeps stable indices and never destroys a callable that is currently running. |
| **Reentrancy** | Code being re-entered while already executing — e.g. an animation setter that starts another animation. Both `Signal` and `AnimationManager` define explicit reentrancy contracts. |
| **UAF (use-after-free)** | Touching memory after its owner was destroyed. The project's most serious incident was one. |
| **GPU texture** | An image uploaded to the GPU. Lives in GPU memory, so it does **not** appear in process RSS — which is why 132 wallpaper previews cost ~3 MB RSS but 53 MB of texture bytes. |
| **Thumbnail tier** | Zynith holds two representations of a wallpaper: **preview** (384 px, whole collection) and **display** (768 px, promotion window). |
| **Promotion** | Upgrading a card from the preview tier to the display tier when it enters the focus window. |
| **Session cache** | A `ThumbnailService` session opened by the wallpaper browser; entries acquired during it are tagged and dropped when it closes. |
| **Decode gate** | `pauseDecodes()/resumeDecodes()` — while the carousel moves, a cache miss records intent instead of queueing work, so a fling decodes what it lands on. |
| **Morph transition** | Planned motion model where A *transforms into* B instead of A disappearing and B appearing. **Not implemented.** |
| **Event-driven** | Work happens in response to an event. The opposite is **polling** — doing work on a timer to check whether anything changed. Zynith forbids polling as a design rule. |
| **Wakeup** | The kernel scheduling a sleeping process. Approximated here by context-switch counts; fewer is better at idle. |
| **PSS / RSS** | PSS divides shared pages among sharers; RSS counts them fully for every process. Stack totals use PSS, per-process trends use RSS. |
| **Retarget** | Changing a running animation's destination while keeping its current value/velocity, instead of restarting from the initial state. |
| **Layer rule** | A niri configuration block matching a layer surface by namespace, used to apply blur to Zynith's notification and backdrop surfaces. |
| **Rice** | Community term for a heavily customised desktop. `rice.toml` is Zynith's design layer. |
