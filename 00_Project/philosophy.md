# Philosophy

My motto for this project is *FAST. OPTIMIZED ASF. PERFORMANCE GODLY. STABLE ASH.* Stripped of the enthusiasm,
it means one thing: push performance hard, but never at the cost of a desktop that breaks. These are the working
principles it turned into.

## 0. The reason any of this exists: control

Underneath the priority order is a simpler commitment, and it is the reason I left Windows rather than tuning it:
I want to know what is running on my machine, know **why** it is running, and be able to remove or change it. See
[`origins.md`](origins.md).

Every principle below is a consequence of that. Event-driven construction is not asceticism — it is a refusal to
have processes waking up for reasons I cannot name. "Never become a second owner" is the same instinct applied to
configuration files. Reversibility exists so that a decision I make today is not a decision I am stuck with.
And the project is documented to this depth because a system I cannot explain is not one I control, whether the
opaque part is a vendor's telemetry service or my own code six months from now.

## 1. Priority order, applied literally

**Correctness → stability → security → responsiveness → resource efficiency → maintainability → configurability
→ aesthetics.** This was tested twice and honoured both times:

- When a performance-motivated design (copying callables in dispatch, later: not copying them) collided with
  lifetime safety, safety won and the performance was recovered a different way (ADR‑0011).
- When the wallpaper browser's memory-efficient lazy loading produced visible loading gaps, the *user-visible
  correctness* of the browser outranked the smaller memory number (ADR‑0010).

## 2. Configuration first, code last

Anything expressible as configuration is configuration. The Phase 6 bar redesign contains zero lines of C++. Code
is reserved for behaviour with no configuration surface.

## 3. Measure, then claim

No optimization is recorded as an improvement without a before/after. Two honest outcomes are documented as such:
removing the bar's 1 Hz update measured **no** improvement and was reverted; the live backdrop measured within
noise and is recorded as a correctness fix, not a performance one.

## 4. Event-driven by construction

No polling, no daemons, no per-frame subprocesses. Where a timer exists it has a stated reason and a measured cost.
The animation settings are a *panel* rather than a *service* purely because services arm a resident timer.

## 5. Never become a second owner

`settings.toml` has one writer: the Noctalia GUI. Hyprland's configuration has one owner: my Hyprland
setup, which this project does not touch. The packaged Noctalia stays installed. Each of these is a boundary the project does not cross, even when
crossing it would be convenient.

## 6. Reversibility

Every change is undoable: a config block to delete, a drop-in file to remove, or a fallback binary to run. Backups
are taken before each phase (`~/.config/rice-backups/`), which is also what made the project's history recoverable
for this documentation.

## 7. Defaults are opinions, not restrictions

I settled on this during Phase 6 and adopted it as a design principle going forward: the polished Zynith look
should be the *default preset*, with meaningful properties exposed as configuration. This is **aspiration, not
current state** — most of the configurability work is still in `06_Reference/future-work.md`.
