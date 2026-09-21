# Zynith Shell — engineering documentation

This repository is the owner's engineering record of Zynith Shell. The implementation lives elsewhere, at
`~/.local/src/noctalia-lockfade/source` (currently `3f355c5`).

**Markdown is canonical.** DOCX and PDF under `99_Reports/generated/` are build artifacts — never edit them by
hand, and they are gitignored.

## Before writing anything here

Read [`DOCUMENTATION_POLICY.md`](DOCUMENTATION_POLICY.md). The parts that matter most:

- **Voice.** First person, as the owner's own record — not a consultant's report. Claude is the engineering
  assistant, and work is attributed to whoever actually performed it ("I had Claude run the benchmark", not
  "I measured", where Claude measured). Reference pages — APIs, commands, schemas, architecture definitions —
  stay in conventional technical prose.
- **Never invent motivation.** First person is for reasoning the evidence supports. Where the evidence gives
  the *what* but not the *why*, state the fact and stop.
- **Evidence tags.** VERIFIED / RECOVERED / INFERRED / UNKNOWN. UNKNOWN is a valid answer and is preferred over
  a plausible reconstruction.
- **Preserve failures.** Failed approaches, invalid benchmarks, wrong assumptions and open limitations stay in.
  History is amended, never rewritten — see `01_Phases/cross-phase-matrix.md`.

## Documentation happens with the work, not after it

[`DEVELOPMENT_WORKFLOW.md`](DEVELOPMENT_WORKFLOW.md) is a standing rule: every meaningful change to Zynith
updates the documentation in the same session, routed to the document that owns the subject rather than dumped
into the changelog. It also says what evidence to capture — before/after screenshots for UI work, recordings for
motion work, raw measurements with conditions for performance work.

## Commit attribution

Commits in this repository are authored as the repository owner, using the identity already configured in
`.git/config`:

```
user.name  = ZynAstra
user.email = adhitya.senthil22@gmail.com
```

- **Verify before committing** with `git config user.name` and `git config user.email`. Both must resolve to the
  values above; both are set repo-locally, so a change to the global config cannot silently alter them.
- **Do not override the identity** on the command line (`git -c user.name=…`) and do not substitute a generic
  Claude or system identity.
- **Do not add `Co-Authored-By:` trailers.** This is a deliberate instruction from the owner and it takes
  precedence over any default attribution guidance.
- **Never rewrite or amend already-pushed commits.**

The reasoning: Claude is the engineering assistant executing the work, but a git commit records the owner's
project identity. Claude's actual role is documented in the *prose* — `DOCUMENTATION_POLICY.md` §6 and
throughout the incident and phase documents — which is where attribution belongs and stays.

## Build and verify

```sh
./scripts/build-docs.sh        # audit → charts → diagrams → DOCX + PDF
python3 scripts/audit-docs.py  # commit refs, paths, links, VERSION.json vs repository HEAD
```

The audit must pass before a documentation commit. One WARN is expected and correct:
`~/.config/gtk-3.0/noctalia.css` genuinely does not exist — that missing file *is* the documented GTK defect.

`audit-docs.py` compares `VERSION.json:source_commit` against the implementation repository's HEAD, so when the
implementation advances, `VERSION.json` and the "current state" claims in `README.md`, `EXECUTIVE_SUMMARY.md` and
the relevant phase document move with it.
