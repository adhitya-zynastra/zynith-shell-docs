# Development Workflow — Documentation Is Part of Zynith

**Status:** standing rule, adopted 2026‑09‑21, after documentation v1.2. It applies to all future Zynith work
and does not expire at the end of a phase.

I wrote the first version of this documentation set *after* Phases −1 through 6 were already finished. It worked,
but only because backups, commit messages and session records happened to survive — and several things did not
survive, which is why this set contains genuine **UNKNOWN** entries that no amount of later effort can fill.

That is the whole argument for this page. Documentation written months later is archaeology. Documentation
written alongside the work is a record.

## The loop

```
PLAN → IMPLEMENT → BUILD → TEST → DEBUG → BENCHMARK → DOCUMENT → VERIFY → COMMIT
```

`DOCUMENT` is not the last step and it is not optional. Work is not finished when the code compiles and the
tests pass; it is finished when someone else could understand it six months from now.

## What to record

For meaningful work, as much of this as applies:

| | |
|---|---|
| Intent | What I wanted, and **why** I wanted it |
| Behaviour | What it did before, what it does now |
| Approach | The architecture or implementation path taken |
| Surface | Important files changed; dependencies, packages or libraries involved; configuration changes |
| Evidence | Testing performed, benchmarks, resource usage |
| Reality | Bugs hit, approaches that failed, fixes, limitations |
| Forward | Known follow-up work |
| Provenance | Relevant commit IDs |

**Use judgement.** A config tweak or a one-line CSS fix does not need a report. A compositor lifecycle change, a
new subsystem, a major UI system, a performance optimization, a crash investigation or an architecture change
does. The goal is not more pages — it is never losing the engineering history.

## Where it goes

Not everything into one changelog. Route the change to the document that owns the subject:

| Kind of work | Update |
|---|---|
| Implementation | the relevant phase document |
| Architecture change | `02_Architecture/` **and** an ADR |
| New design decision | a new ADR in `05_Decisions/ADRs/` |
| Performance work | `03_Performance/` (log, benchmarks, charts) |
| Bug, crash or outage | `04_Incidents/` |
| Configuration change | `06_Reference/configuration/` |
| New feature | phase document **and** the relevant architecture or reference page |
| Change to something an earlier phase introduced | the earlier phase's *Retrospective amendments* **and** `01_Phases/cross-phase-matrix.md` |

## Capturing evidence

Claude is explicitly authorised to collect documentation evidence while working, and should, when it preserves
something text cannot:

- **Before/after screenshots** for visually significant UI work — the single most useful artifact, and the thing
  this project most conspicuously lacks for Phases −1 through 5.
- **Short recordings** for animation, motion or interaction work, where behaviour over time is the point.
- **Raw measurements and their conditions** for performance work — never a summarised number alone.
- Terminal output, logs, diagrams, charts, configuration snapshots and code excerpts as they help.

Do not capture material purely to enlarge the record.

## Preserving history

The rules that already govern this set continue to apply, and they matter more when writing in the moment,
because that is when the temptation to tidy is strongest:

- A failed approach is **documented as a failed approach**, not quietly dropped.
- An invalid benchmark is **marked invalid** and kept, not deleted (see
  `03_Performance/benchmarks/contaminated-measurements.md`).
- A wrong assumption is recorded alongside what turned out to be true.
- Architecture changes **amend** history; they never rewrite it.
- Anything not establishable is **UNKNOWN**.

Evidence outranks appearance. A record that only contains successes is a marketing document, and I will not
trust it in six months.

## Keeping the generated report current

Markdown is canonical; DOCX and PDF are artifacts. At a substantial milestone — not after every commit:

```sh
~/Documents/Dev/ZynithShell/scripts/build-docs.sh     # audit → charts → diagrams → DOCX + PDF
```

Then verify internal references, confirm the audit passes, and record the documentation commit. If the work
produced no meaningful documentation change, do not regenerate a 79-page report to prove it.

## Performance work specifically

Performance is a first-class requirement in Zynith, so measurements carry a full provenance block: hardware,
build state, commit, workload, duration, tool, the before and after values, an interpretation, and the
limitations. **A measurement from a build that was not cleanly rebuilt after a header layout change is not
evidence** (ADR‑0013), and a suspicious number is investigated rather than published.

## The question that ends a task

Before declaring any meaningful Zynith work complete:

> *Did I preserve enough that another developer — including me, six months from now — could understand what just
> changed and why?*

If not, the work is not finished yet.
