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
- **The shell writes two niri config fragments** (`rice/animations.kdl`, `rice/glass.kdl`). Reviewed for this
  surface: the paths are fixed (config home + a constant name, no user-supplied component); the content is rendered
  from enums and clamped numbers, so no configuration string reaches the KDL; validation runs `niri validate` as an
  **argument vector**, never a shell string; writes are atomic; the writers exist only under niri. Nothing
  privileged.
- **Plugins are trusted code** — there is no sandbox. One plugin remains (`identity`); the Motion plugin, which
  wrote files through the plugin API's unsandboxed `writeFile`/`renameFile`, is retired.
- Shell hooks (`[hooks] session_locked/unlocked`) execute a shell command on real logind events. Anything placed
  there runs with the user's privileges.

## Known weaknesses (stated, not fixed)

| Weakness | Note |
|---|---|
| Plugins are unsandboxed | Inherited from Noctalia's plugin model |
| Hooks execute arbitrary commands | By design; the user owns the config |
| Coredumps may contain sensitive memory | systemd-coredump is enabled; the project generated several during debugging |
| No integrity checking of the local build | A compromised `~/.local/opt/noctalia` would be launched by niri |

## PROPOSED / NOT IMPLEMENTED — the Zynith security and privacy layer

**Nothing in this section exists.** No design document, no code, no configuration, no commit. It is recorded here
so the intent is not lost, and it must not be described as part of Zynith until some of it is real.

What I want eventually is an *optional* network and privacy layer for the desktop — off by default, and visibly
off when it is off. The shape I have in mind:

| Intended capability | Note |
|---|---|
| Protected DNS and malicious-domain blocking | Resolver-level, not a browser extension |
| Per-application network permissions | Which applications may reach the network at all |
| Secure public-Wi-Fi mode | A single toggle that tightens the posture when I am on a network I do not trust |
| Privacy dashboard | What is connecting where, visible rather than inferred |
| Kill switch and leak protection | Fail closed, not open |

The architectural constraints matter more to me than the feature list, because they are what would keep it from
becoming a liability:

- **Linux-native enforcement.** nftables, the resolver and NetworkManager where appropriate — not a shell process
  pretending to be a firewall.
- **Enforcement outside the UI process.** The shell must never be the thing standing between me and the network.
  If the shell crashes — and [it has](../04_Incidents/postmortems/2026-09-20-signal-uaf.md) — enforcement must
  survive it.
- **Least privilege**, event-driven rather than polling, and **auditable**: I should be able to read what it did
  and why.

This belongs to a future Security and Privacy phase. It is **not** part of Phase 6 and it is not started.
