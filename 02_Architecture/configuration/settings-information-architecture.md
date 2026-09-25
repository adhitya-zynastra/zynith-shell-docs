# Settings Information Architecture — Now and Later

**Written:** 2026‑09‑25. **Decision:** [ADR‑0017](../../05_Decisions/ADRs/ADR-0017-personalization-and-zynith-settings.md).

This page exists to keep two things from being confused: the customization area Zynith has **today**, and the
system-wide settings application Zynith is **eventually** meant to have.

## Now: Personalization

Customization of the desktop shell lives in **Personalization**, a section of the existing settings window (the one
Noctalia provides, opened with `settings-open`). `Super+Alt+A` opens it directly.

| Group | Contains |
|---|---|
| Motion | animations on/off, speed, preset, niri trims |
| Glass | transparency, opacity, blur, blur strength, tint, borders, shadow |
| Control Center | density, top navigation, hover-open, width |
| Wallpaper Browser | carousel on/off, card size |

It was briefly called **Zynith Corner** (`8c2b4eb`). That name was retired on 2026‑09‑25 because it named a brand
rather than what the section holds, and because a branded area would have had nowhere sensible to go once a real
Zynith settings application exists. "Appearance" was not available — Noctalia already has an Appearance section —
and "Personalization" describes appearance *and* behaviour customization, which is what the groups actually are.

**Personalization is not "Zynith Settings".** It is one category of customization options inside the current
settings window. The code deliberately contains no Zynith branding at this level: the section is
`SettingsSection::Personalization`, id `personalization`.

### How a surface's options are split

A surface's options are split by kind, so each key has exactly one control in the window:

- **Appearance and behaviour** of a shell surface — how it looks, how it moves, how dense it is — goes in
  Personalization.
- **Function** of a feature — which Control Center tabs exist, its shortcuts, its sidebar modes, where it is
  placed — stays in that feature's own section.

When an option moves between sections it is moved, never copied. Moving Control Center density, top navigation,
hover-open and width into Personalization removed them from the Control Center section in the same change.

## Later: Zynith Settings

The intended end state is **Zynith Settings** — one system-wide settings application and hub, in the sense of
Windows Settings, a phone's Settings app, or the settings hubs of modern Linux desktops and shells. It is expected
to hold system information, users, network, applications, devices, display, audio, power, system configuration,
niri configuration, shell configuration and Zynith's own configuration.

The rule that shapes it now: **niri-specific and Zynith-specific settings must end up reachable from Zynith
Settings, not from disconnected applications.** Nothing built today may become a second, competing hierarchy.

```
Zynith Settings                       (future — not built)
├── System          info, users, updates
├── Network
├── Devices         display, audio, input, power
├── Applications
├── Personalization                   ← exists today, as a section of the current settings window
│   ├── Motion
│   ├── Glass
│   ├── Control Center
│   └── Wallpaper Browser
├── Shell           the remaining shell-feature sections
└── Compositor      niri configuration (today: the Niri section + generated fragments)
```

The expected migration is that the current settings window **grows into** Zynith Settings rather than being
replaced by it, so Personalization is carried over as a category with its groups intact. Whether that is literally
the same window extended, or a new application reusing the same registry, is **UNKNOWN** and will be decided when
that work starts. Either way the registry — one entry per key, with section, group, path and control — is the
piece that survives.

## What was deliberately not built

No Zynith Settings application, no system pages (users, network, devices), and no second settings window. This
page and ADR‑0017 are the only artefacts of the future architecture, by design.
