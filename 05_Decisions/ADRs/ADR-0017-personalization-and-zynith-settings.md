# ADR-0017 — Personalization now, Zynith Settings later

**Status:** Accepted; Personalization implemented, Zynith Settings not started · **Date:** 2026‑09‑25

## Context
The first three-track batch (`8c2b4eb`) added a settings section called **Zynith Corner** to hold the Motion and
Glass groups. In the next batch I asked for the Control Center and wallpaper browser options to be exposed as well,
and for the section to be renamed: a branded name described nothing about what was inside it, and I want the
system-wide settings application to be the thing that carries the Zynith name when it exists.

Two facts constrained the name. Noctalia already has an **Appearance** section (theme, fonts, colours), so that
name was taken. And the new groups are not only visual — hover-open, card size and density are behaviour and
layout — so a purely visual name would mislead.

## Decision
1. The section is **Personalization** (`SettingsSection::Personalization`, id `personalization`). No Zynith branding
   at this level of the code or UI.
2. **Split a surface's options by kind.** Appearance and behaviour of a shell surface (motion, glass, density,
   width, hover-open, carousel size) go in Personalization; the *function* of a feature (Control Center tabs,
   shortcuts, sidebar modes, placement) stays in that feature's own section.
3. **Move, never copy.** A key has one control. Moving Control Center top navigation, hover-open, hover delay and
   width into Personalization removed them from the Control Center section in the same change.
4. **Zynith Settings is the future system-wide hub** — users, network, devices, display, audio, power, niri
   configuration, shell and Zynith configuration. It is documented
   ([settings-information-architecture.md](../../02_Architecture/configuration/settings-information-architecture.md))
   and not built. Personalization is expected to become one category inside it.
5. No new settings window, no Control-Center-specific settings application.

## Why
Point 3 matters most. The configuration layering (ADR‑0014) is only sane while every key has one owner and one
control; two controls for one key is how a UI starts lying about the current value.

Point 4 is written down now, before any of it exists, so that each track that adds options has one place to put
them and does not grow its own settings screen that would later have to be merged or deleted.

## Alternatives
- *Keep "Zynith Corner"* — rejected by me: the name says nothing about the contents.
- *"Appearance"* — taken by Noctalia's existing section, and too narrow for behaviour options.
- *"Customization"* — viable. I asked for a generic name based on the contents; Claude proposed Personalization,
  the name Windows and several Linux desktops use for the same category, in this batch. Whether "Customization"
  would have been clearer is **UNKNOWN**.
- *Leaving Control Center layout options in the Control Center section and adding only density there* — rejected:
  it would have split one surface's appearance options across two sections.
- *Building a Zynith Settings shell now* — out of scope by instruction.

## Consequences
- The `Super+Alt+A` bind and every documentation reference changed from `zynith-corner` to `personalization`. The
  old id stops working; there is no alias. Nothing outside this desktop used it.
- The generated niri fragments' header comments name the new path, which rewrote `rice/animations.kdl` and
  `rice/glass.kdl` once with unchanged bodies.
- Whether Zynith Settings will be this window extended or a new application reusing the registry is **UNKNOWN**.
