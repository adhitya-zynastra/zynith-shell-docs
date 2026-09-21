# ADR-0002 — Patch Noctalia locally instead of forking or reimplementing

**Status:** Accepted · **Date:** 2026‑09‑19 (Phase 2) · **Evidence:** VERIFIED — base commit `a176ada`
"noctalia 5.1.0 pristine (Fedora SRPM)", install prefix `~/.local/opt/noctalia`, spawn fallback in `config.kdl`.

## Context
I needed behaviour the packaged shell does not expose (lock transitions, modal power menu, carousel, panel
retargeting). Writing a shell from scratch was never in scope, and forking outright would have made me the owner
of every upstream fix I subsequently failed to merge.

## Decision
I chose to patch rather than fork. Keep the Fedora `noctalia` package installed and untouched. Maintain a small git repository whose first commit is
the pristine 5.1.0 source, apply Zynith changes as reviewable commits on top, build to a user-local prefix, and
have niri spawn the local build **with a fallback to `/usr/bin/noctalia`**.

## Alternatives
- *Fork upstream* — rejected: no upgrade path, and the diff would stop being reviewable.
- *Configuration only* — insufficient; some behaviour has no configuration surface.
- *Patch the RPM* — rejected: every `dnf update` would fight the change.

## Consequences
- A broken local build degrades to the packaged shell rather than to no desktop.
- Upstream updates require rebasing the patch series; the patch README documents this.
- **Corollary that has held throughout:** anything expressible as configuration *is* configuration. The Phase 6 bar
  redesign is zero lines of C++.
