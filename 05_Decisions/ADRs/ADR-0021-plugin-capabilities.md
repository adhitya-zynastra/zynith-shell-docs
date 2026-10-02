# ADR-0021 — Luau plugins get declared and granted capabilities, never secrets

**Status:** Accepted, implemented (`feature/zynith-core` `54204d2`) · **Date:** 2026‑10‑02

## Context

On 2026‑10‑02 I decided to keep Luau for plugins and improve its security model rather than move to QML plugins.
The decision named what that means:

- capability-based permissions, with explicit capabilities for exec, network, files and notifications;
- no unrestricted shell execution;
- notify-only updates;
- a failing plugin must not take the UI down;
- plugins kept away from secrets.

Before this change, every plugin could call every function in the `noctalia` table. That included:

- `runAsync` with a shell string (`/bin/sh -c`);
- `http` and `download`;
- reading and writing any file I can access;
- reading the clipboard;
- reading any environment variable.

Updates were already notify-only (Phase 1, `385994a`). A failing plugin was already contained: calls run under
`pcall` with a time budget.

Claude counted what is installed: 91 community plugins are on disk. Only one is enabled: my own `dusk/identity`
lock-screen widget. That plugin calls `getenv("USER")`, `fileExists` on avatar paths outside its folder, and
`runAsync({"getent", "passwd", user})`.

## Decision

1. **Declared ∩ granted.**
   - A plugin lists what it needs in `plugin.toml` (`capabilities = ["exec", "files"]`).
   - The grants live in `~/.config/zynith/plugin-grants.toml`, written only through
     `noctalia msg plugins grant | revoke`.
   - The effective set is the intersection. A plugin that declares more in an update gains nothing until it is
     granted, and a grant does nothing for a plugin that does not declare it.
2. **Seven capabilities:**

   | Capability | Covers |
   |---|---|
   | `exec` | run a program from an argv table |
   | `shell` | run a shell string |
   | `network` | `http`, `httpStream`, `download` |
   | `files` | anything outside the plugin's own folder and data folder |
   | `notifications` | sending notifications |
   | `clipboard` | reading or setting the clipboard |
   | `env` | any environment variable beyond a plain set: `HOME`, `USER`, `LANG`, `LC_*`, `XDG_*` and a few more |
3. **Some locations are closed whatever the grants.**
   - *Never readable:* `~/.ssh`, `~/.gnupg`, keyrings, password stores, cloud and Git credentials, browser
     profiles, the shell's encrypted clipboard store and notification history, and `/proc/<pid>/` (other
     processes' environments).
   - *Never writable:* places where a write becomes code execution or a change to permissions: shell startup
     files, `~/.local/bin`, autostart, systemd user units, the niri/Hyprland/noctalia/zynith configuration (the
     grants file included), and other plugins' code.
   - Paths are judged after symlinks are resolved, so a link inside the plugin folder that points at `~/.ssh` is
     refused.
4. **A refusal is a script error that names the fix**, for example
   `runAsync needs the 'exec' capability: declare it in plugin.toml, then noctalia msg plugins grant <id> exec`.
   It is logged once per plugin and capability, and the plugin host contains it like any other error.
5. **`shell` is separate from `exec`.**
   - The §14 target was "no `/bin/sh -c`". A capability that has to be declared *and* granted is the
     enforceable version of that.
   - Shell strings stand out, and no plugin gets them by default.
6. **Migration.** I had Claude declare `exec` and `files` in `dusk/identity`'s `plugin.toml` (the original is
   backed up in `~/.config/rice-backups/20261002-plugin-capabilities/`). It granted the same two in the new grants
   file before the shell restarted, so the widget never ran ungranted.

## What this is not

**It is not a sandbox.** A plugin that may run programs (`exec` or `shell`) can do anything I can: it could run
`noctalia msg plugins grant` itself, or start a shell from an argv table. Granting `exec` means trusting the
plugin with my user account, and the capability makes that trust explicit and visible.

Without `exec` and `shell`, there is no route from `files` or `network` to code execution. That follows from the
never-writable locations above and from a plugin having no IPC access.

## Verification

- `tests/plugin_capabilities_test.cpp` covers the policy:
  - own folders, secrets, `/proc`, a symlink escape and protected writes;
  - environment allow-listing;
  - declared ∩ granted, and grants surviving a reload from disk.
- `tests/plugin_capability_gates_test.cpp` drives the real Luau bindings:
  - with nothing granted, seven gated calls are refused while plain calls and the plugin's own files still work;
  - after granting `exec files env`, those work, while `shell` (not granted), `network` (not granted) and
    `~/.ssh` stay closed.
- `tests/plugin_process_test.cpp` now declares and grants what its plugin uses.
- Full suite: 132 of 133, the remaining failure being the known `upower_charge_limit_integration`.
- `noctalia msg plugins capabilities` on the installed shell reports
  `dusk/identity declared exec, files · granted exec, files · effective exec, files`.
- **Untested live:** the identity widget itself under enforcement. It runs only on the lock screen, which is not
  automated on this machine. It needs my next lock.

## Consequences

- Any community plugin I enable later fails loudly until I grant what it declares. A plugin that declares nothing
  (every community plugin today) can only draw and use its own folder.
- The Settings UI does not show capabilities yet; that belongs to the 2.0 Settings → Privacy & security page.
  Until then, `noctalia msg plugins capabilities [id]` is the view.
