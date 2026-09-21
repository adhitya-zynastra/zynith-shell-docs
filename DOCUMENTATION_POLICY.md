# Documentation Policy

**Version:** 1.0 · **Generated:** 2026-09-21 · **Source commit:** `57debbc` · **Last audited phase:** 6

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

## 6. Audit trail

`scripts/audit-docs.py` re-checks commit hashes, file paths and the documentation version block against the live
repository. Run it before regenerating the report.
