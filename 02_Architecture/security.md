# Security — Current State

This documents **only what exists**. It is not a design for a future security system.

## Session lock

- Authentication is **PAM**, through Noctalia's `PamAuthenticator`. Zynith changed **nothing** in
  `tryAuthenticate()`'s credential handling or `handleAuthResult()`'s failure path. **VERIFIED** — the patch
  README lists these as explicit non-changes and the diffs confirm it.
- The lock uses the `ext-session-lock-v1` protocol. Zynith's only change to the lock/unlock *sequence* is that the
  unchanged `unlock()` call is **deferred** by the exit animation's real duration (0 ms when animations are off).
- Fingerprint logic is untouched.
- The password field is presentational: hidden until typing, with errors rendered inside the pill. No change to
  what is stored or compared.

## Screen privacy

- `rice/rules.kdl` sets `block-out-from "screen-capture"` for KeePassXC and GNOME Secrets, so password managers do
  not appear in screencasts or screenshots. **VERIFIED** in the live config.
- The lock screen composition is deliberately generic: no hard-coded name, avatar or location.

## Process and IPC surface

- One shell process, no setuid, no daemon added by Zynith.
- Noctalia owns `org.freedesktop.Notifications` and `org.kde.StatusNotifierWatcher` on the session bus.
- The Motion plugin writes files (`motion.json`, `motion.toml`, `animations.kdl`) through the plugin API's
  unsandboxed `writeFile`/`renameFile`. **Plugins are trusted code** — there is no sandbox. Only two plugins exist,
  both written for this project.
- Shell hooks (`[hooks] session_locked/unlocked`) execute a shell command on real logind events. Anything placed
  there runs with the user's privileges.

## Known weaknesses (stated, not fixed)

| Weakness | Note |
|---|---|
| Plugins are unsandboxed | Inherited from Noctalia's plugin model |
| Hooks execute arbitrary commands | By design; the user owns the config |
| Coredumps may contain sensitive memory | systemd-coredump is enabled; the project generated several during debugging |
| No integrity checking of the local build | A compromised `~/.local/opt/noctalia` would be launched by niri |

## PROPOSED / NOT IMPLEMENTED

A Zynith privacy/security subsystem has been mentioned as a future direction. **No design, no code, no
configuration exists.** It must not be described as part of the system until it does.
