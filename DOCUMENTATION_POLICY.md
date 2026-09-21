# Documentation Policy

**Version:** 1.6 · **Generated:** 2026-09-21 · **Revised:** 2026-09-21 (Phase 6 completion run) · **Source commit:** `57debbc` · **Last audited phase:** 6

## 1. Canonical source

Markdown under `~/Documents/Dev/ZynithShell/` is the single canonical source. DOCX and PDF in
`99_Reports/generated/` are **build artifacts** produced by `scripts/build-docs.sh`; never edit them by hand.

## 2. Evidence classification

Every non-trivial historical or numeric claim carries one of these tags:

| Tag | Meaning |
|---|---|
| **VERIFIED** | Reproduced directly on this machine, or read out of a file/commit that still exists. Command or path is cited. |
| **RECOVERED** | Reconstructed from a durable artifact (git history, timestamped backup directory, journal, config file) rather than observed live. |
| **INFERRED** | A reasoned conclusion from verified facts. The reasoning is stated so a reader can disagree. |
| **UNKNOWN** | Not establishable from surviving evidence. Stated explicitly rather than guessed. |

Untagged prose is descriptive narrative about the current tree and must be checkable against the source.

## 3. Prohibitions

- Do not invent measurements, dates, versions, file paths, commit hashes or rationales.
- Do not present a planned or proposed design as implemented.
- Do not quietly fill a historical gap; write **UNKNOWN** and say what evidence would settle it.
- Do not promote a measurement into a benchmark table unless its provenance block is complete
  (date, commit, build type, tool, duration, repetitions) — see `03_Performance/README.md`.

## 4. Contaminated measurements

Measurements taken from an **incremental** build that followed a layout change to a widely-included header are
invalid and are recorded as `INVALID / CONTAMINATED` with an explanation, never in authoritative tables.
See `04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md`.

## 5. Cross-phase amendments

When a later phase materially changes something an earlier phase introduced, the earlier phase document receives a
**Retrospective amendments** section linking forward, and `01_Phases/cross-phase-matrix.md` records the pair.
Phase documents are never silently rewritten to match the present.

## 6. Voice and attribution

This documentation is written in **my own voice as the project owner**, in the first person, because it is my
engineering record rather than a report about somebody else's project. Two rules keep that from becoming
inaccurate.

**Attribute work to whoever performed it.** I made the decisions, set the constraints and priorities, tested by
hand, and rejected designs; **Claude Code** — acting as my engineering assistant — did the inspection, wrote the
patches I specified, ran the benchmarks and chased the backtraces. So "I decided", "I rejected", "I observed" and
"I had Claude measure" are all accurate, and "I measured" is not written where Claude took the measurement.

**Do not invent motivation.** First person is for reasoning the evidence supports — from the session record,
commit messages, configuration comments or surviving artifacts. Where the evidence establishes *what* I did but
not *why*, the document states the technical fact and stops; where the reason is genuinely lost, it says so (the
original choice of niri is an example). Style never outranks accuracy.

Not every page is first person. History, rationale, decisions, observations and incidents are; API descriptions,
command references, configuration schemas, file inventories and architecture definitions stay in conventional
technical prose, because a reference page is not a memoir.

Attribution in the *prose* is what this section governs. Attribution in *git metadata* is separate and
deliberately different: commits are authored as the repository owner, with no assistant trailers. See
[`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md).

### How Claude is used, and why it is documented this way

The working arrangement matters to the accuracy of this record, so it is stated rather than implied. I supply the
architecture, requirements, design direction and constraints; Claude does the implementation-heavy work and the
kind of investigation that benefits from an agent repeatedly inspecting, building, running and verifying things —
debugging, regression and stress testing, build validation, repository exploration, tracing lifetimes and
ownership, benchmarking, cross-file refactoring and documentation maintenance.

What I deliberately do **not** do is let it think for me. If I do not understand something, I ask until I do; if
an architectural decision does not make sense, I challenge it; if a benchmark looks suspicious, I make it prove
the number. Two entries in this documentation exist because of exactly that — the
[incremental-build contamination](04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md), where a
suspicious regression turned out to be a broken build, and the
[invalid sharpness metric](04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md), where a number
that had been believed was wrong. A record that presented this as a smooth collaboration would be less useful
than one that shows where the process caught itself.

## 7. When documentation is written

**With the work, not after it.** Since 2026‑09‑21 this is a standing project rule rather than a preference:
every meaningful change to Zynith updates the documentation in the same session, routed to the document that
owns the subject. The loop, the recording checklist, the routing table and the evidence-capture guidance are in
[`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md).

## 8. Audit trail

`scripts/audit-docs.py` re-checks commit hashes, file paths and the documentation version block against the live
repository. Run it before regenerating the report.
