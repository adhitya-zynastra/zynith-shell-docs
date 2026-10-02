# ADR-0020 — Quickshell built-ins are adopted after measurement; NetworkManager is read natively

**Status:** Accepted, implemented (`feature/zynith-ui` `b136894`) · **Date:** 2026‑10‑02

## Context

[Architecture 2.0 §4.1](../../02_Architecture/Zynith-Architecture-2.0.md) assigned each domain to a Quickshell
built-in where one exists. For example, it gave network state to `Quickshell.Networking`. The table was drawn up
from what the built-ins can *do*. Nobody had measured what they cost while idle, in the places where I actually
use this laptop.

The Stage 1 prototype idled at 0.23 % of a core with 7–9 wakeups/s. Claude bisected it by running each service
alone in its own Quickshell instance:

- `Network` alone: **68 wakeups/s and ≈ 0.4 % of a core**;
- every other service: 0–1 wakeups/s.

The cause is the environment, not a defect. On campus, NetworkManager tracks 40 access points, and each one
updates its signal strength on every background scan. `Quickshell.Networking` follows all of them, because its
model exposes every network with live properties. The bar shows one icon.

## Decision

1. **Network state comes from Zynith.Native's `NetworkState`.**
   - It always watches only NetworkManager's own object and the access point in use.
   - The list of nearby networks, and the per-access-point signals behind it, exists only while something holds
     it with `retain()`/`release()`. Today that is the Wi‑Fi panel.
   - Actions go straight to NetworkManager: enable or disable Wi‑Fi, scan, activate a saved connection, add and
     activate a new one, deactivate.
   - Passwords never reach the UI. For a new secured network, NetworkManager asks the secret agent, which is still
     the native shell.
2. **A built-in is adopted only after its idle cost has been measured here.** The method is one service per
   instance, 15–30 s each, counting CPU ticks and voluntary context switches across all threads. Wherever a
   built-in models a large collection to show a small state, it is a candidate for a narrow native reader with a
   demand-counted list.
3. **Interim transport.** The clipboard history and the native shell's switches (night light, stay awake, DND) are
   reached through `noctalia msg` until the helper protocol in §4.2 exists. The UI calls it only on demand: when
   a panel opens, or after an action. It never calls it on a timer.

## Consequences

- The prototype idles at **0.03 %** of a core with 2 wakeups/s. Before this change it was 0.23 % with 7–9
  wakeups/s. See the [optimization log](../../03_Performance/optimization-log.md) O‑10.
- One more native class to maintain: about 400 lines of QtDBus. It is written against NetworkManager's stable
  D-Bus API, not Quickshell internals.
- **Untested so far:** turning Wi‑Fi off and on, and connecting to a network through `NetworkState`. Either would
  have cut the connection I was using. What *was* verified:
  - the state readout (connected, kind, strength);
  - the on-demand list: 4 networks while the panel was open, 0 and no consumers after it closed;
  - that the `WirelessEnabled` write is permitted, using a no-op (setting it to its current value).
- Bluetooth was measured the same way: 0 wakeups/s while idle. Discovery runs only while the Bluetooth panel is
  open, so `Quickshell.Bluetooth` stays.
