# Phase 1 — Hardening, Performance, Reliability (2026‑09‑26)

**Status:** in progress. Baseline: [`phase0-audit-2026-09-26.md`](phase0-audit-2026-09-26.md), which is authoritative
where it conflicts with the original master specification. I asked for this phase as a pasted brief; Claude is the
engineering assistant carrying it out, and each result below says who did what and how it was checked.

## 1. Git and GitHub

| Step | What was done | Verified |
|---|---|---|
| Inspect | one local branch (`master`), no remote, no tags or stashes. Identities in history: `lockfade <none>` ×9 (a tool placeholder), `pristine <none>` ×1 (the Noctalia 5.1.0 import), `M.S.Adhitya` ×6, `ZynAstra` ×12. **Six commit messages carried `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` trailers**; no commit had an AI author or committer | `git log --format=fuller --all` |
| Secret scan | tracked + untracked files and every added line in history, for private keys and GitHub, AWS, Slack, Google and API tokens; my home path, e-mail, name and Wi‑Fi name. **Nothing found.** Largest blobs are upstream assets; the pack is 22 MB | pattern scan over `git log -p --all` and the tree |
| Checkpoint | the uncommitted Batches 5–7 (42 modified files, 21 new) committed as one checkpoint | clean `git status` afterwards |
| Identity | the GitHub account's e-mail is `adhitya.senthil22@gmail.com`: the repository's own "Initial commit", made by GitHub, carries it and GitHub links it to the account `adhitya-zynastra`. The API that lists account e-mails needed a scope the token does not have, so this is the evidence used | GitHub API |
| Rewrite | backup branch `backup/pre-identity-rewrite` (local only). `git filter-branch` on `master` set author and committer to `M.S. Adhitya <adhitya.senthil22@gmail.com>` on all 29 commits and removed only the six `Co-Authored-By: Claude …` lines (and the blank line each left behind) | the sequence of trees is identical (hash of all tree ids before = after); commit count, order, author dates and subjects identical; empty diff against the backup; zero AI mentions in messages |
| Repository-local identity | `user.name "M.S. Adhitya"`, `user.email adhitya.senthil22@gmail.com` (the global config is unchanged) | `git config --local` |
| Remote and push | `origin` = `github.com/adhitya-zynastra/Zynith-Shell` (private, owned by the account). Pushed as a **new branch `master`**; no force-push, `main` untouched | on GitHub: 29 commits, all authored and committed by `adhitya-zynastra`, no co-author, repository still PRIVATE |

**Open for me — the license.** The repository's `main` holds one commit, a **GPL‑3.0** `LICENSE` that GitHub
created. The code is Noctalia, whose `LICENSE` is **MIT** ("Copyright (c) 2026 noctalia-dev"). The two histories
were deliberately not merged: choosing Zynith's license, and how the MIT notice is kept, is my decision. Until then
the code lives on `master`.

**Commit hashes changed.** Every hash cited in this documentation before today refers to the pre-rewrite history.
The backup branch keeps those objects resolvable locally. The mapping is in §9.

## 2. Plan (ordered by risk)

| # | Item | Kind | Physical tests needed from me |
|---|---|---|---|
| 1 | Core dumps of the shell (lock password material) | security | — |
| 2 | Plugin auto-update → notify-only | security | — |
| 3 | Locked-state lifecycle and password buffers | security | real lock/unlock, wrong passwords |
| 4 | Theme templates: capability-aware, failures isolated | reliability | — |
| 5 | Plugin catalog fetch off the startup path | reliability | — |
| 6 | Spectrum: demand-driven lifecycle, measured before/after | performance | — |
| 7 | Shared sampler audit | performance | — |
| 8 | Typography: brand font, fonts installed, CJK/Hangul fallback | foundation | — |
| 9 | One agent per responsibility (Wi‑Fi, Bluetooth) | ownership | Wi‑Fi password prompt, wrong password, pairing |
| 10 | Bounded stress pass and failure isolation | reliability | — |
| 11 | Manual test checklist; documentation | — | the checklist itself |

Reference research done for this phase:
- Caelestia's visualiser (`plugin/src/Caelestia/Services/cavaprovider.cpp`, `modules/background/Visualiser.qml`):
  the audio-analysis service runs only while a visible consumer holds a reference (`ServiceRef`), hides when
  windows cover the desktop, and emits values only when they change. This informs item 6.
- Nothing relevant to plugin updates or lock buffers in the three reference trees.

## 3. Security

### 3.1 Core dumps — commit `e1df05f`

**Launch path.** niri's `spawn-sh-at-startup` execs `~/.local/opt/noctalia/bin/noctalia` in a systemd user
scope. The core limit is `unlimited` and cores go to `systemd-coredump`, which keeps them on disk. The PAM helper
is a re-exec of the same binary (`/proc/self/exe pam-helper`) and receives the password over a pipe.

**Mechanism chosen: `PR_SET_DUMPABLE 0`** at startup, in the shell and in the PAM helper
(`src/security/process_hardening.*`). Alternatives rejected:

| Option | Why not |
|---|---|
| `RLIMIT_CORE = 0` | inherited across `exec`: every application launched from the shell would lose its core dumps |
| system-wide `coredump.conf` / `core_pattern` | not narrow; out of scope by instruction |
| non-dumpable only while locked | leaves password remnants in memory after unlock exposed to a later crash; also the polkit and Wi‑Fi prompts |

**Scope, verified by test:** the kernel resets dumpability on `exec`, so executed programs are unaffected.
`ZYNITH_ALLOW_COREDUMP=1` opts out for a debugging session.

**Side effects, and what replaces them:**
- A non-dumpable process refuses same-user `ptrace` (`gdb -p`), and its `/proc/<pid>/{fd,maps,environ}` become
  root-owned. `noctalia msg status` therefore now reports the shell's own `pid`, `rssKb`, `threads`, `fds`,
  `cpuTicks` and `dumpable`.
- Fatal signals (SEGV, BUS, FPE, ILL, ABRT) write a backtrace to the shell log and stderr on an alternate stack,
  then re-raise. Frames of the executable print as offsets for `addr2line -Cfe`.

**Verified.**
- `process_hardening_test`: non-dumpable after the call; the opt-out works; an `exec`'d child is dumpable; self
  resources are readable; a deliberate SIGSEGV logs `[FATAL] … signal 11 (SEGV)` plus a backtrace, dies of
  SIGSEGV and leaves **no** core.
- Mutation: removing the `prctl` call fails two checks.
- **Before building it** I had Claude check that PipeWire still accepts a non-dumpable client (PipeWire looks at
  `/proc/<pid>/root`): a small test client saw 24 nodes either way.
- Live, after install: `dumpable: false`; `/proc/<pid>/fd` owned by root from outside; the NetworkManager agent,
  polkit agent, MPRIS, WirePlumber mixer, tray watcher, sounds and the spectrum stream all came up.

**Not verified:** the PAM helper path runs only on a real unlock (manual checklist).

### 3.2 Plugin updates — commit `385994a`

`[plugins] auto_update` had three modes (`none`, `official`, `all`); the default `all` fetched every enabled git
source at startup and every 6 h and **materialised new plugin code** for enabled plugins. New mode **`notify`**,
now the default:
- fetches and compares exactly as before;
- never materialises code, and never moves a source's `HEAD`;
- reports pending updates as one notification per new set ("Plugin updates available … nothing was installed").

`all` and `official` remain explicit opt-ins, and manual updates (Settings → Plugins, `noctalia msg plugins update
<source>`) are unchanged. The first check moved from login to **3 minutes after startup**, and checks are skipped
while the session is locked.

**Verified live:** no fetch during startup; at +3 min, "source 'official': installed plugins are current" (and
community); the plugin directory is unchanged. `config_schema_roundtrip` covers the new default, parsing `"notify"`,
and Notify's scope (every enabled git source). **Not verified:** the notification itself, because no update is
pending upstream.

### 3.3 Locked state and password buffers — commit `89bb4a2`

| Path | Before | After |
|---|---|---|
| Lock screen's master copy | wiped (`size()` bytes) on submit, escape, unlock, teardown | wiped over its **whole capacity**; buffer reserved at lock so typing never reallocates |
| Each lock surface's copy (one per output) | replaced **by value on every keystroke**; old buffers freed unwiped; never wiped on destruction | wiped before replacement and on destruction; the by-value argument wiped on every exit |
| The password field's text | freed unwiped on replace, clear and destruction | password mode reserves its buffer, and wipes on `setValue`, clear and destruction (upstream already kept no undo history in password mode) |
| PAM worker copy and helper | wiped after use (upstream) | unchanged, now full-capacity via the shared helper |
| Logging | no key text logged (verified: the keyboard logs only bind/release/keymap) | unchanged |
| Lock widgets on config reload | rebuilt under the live lock (the 2026‑09‑26 crash) | deferred to unlock |
| Plugin network checks | ran regardless | skipped while locked |

`security::wipeString` uses `sodium_memzero` over the full capacity. It is tested: bytes left past `size()` by an
earlier, longer value are zeroed, and the buffer is kept.

**Audited, left as is (documented):**
- The weather, location and media services keep refreshing while locked. The lock shows weather and media, so
  that work is visible.
- The system-monitor sampler keeps its 1 s cadence under the lock: the bar under the lock is not visible, but the
  sampler is shared and cheap.
- Rendering stops when outputs are blanked, because frame callbacks stop.

**Not verified at runtime:** everything on the real lock path (manual checklist).

## 4. Reliability — theme templates, commit `956765a`

**Root causes** (verified on this machine):
1. `~/.config/gtk-3.0` and `~/.config/gtk-4.0` are **symlinks into `~/.mydotfiles/com.ml4w.dotfiles.stable/`,
   which no longer exists**: the GTK outputs can never be written.
2. Emacs is not installed; its hook exits 127.
3. Ten of the 21 enabled built-in templates target absent applications. For those, the engine created their config
   directories, wrote a theme file and ran their hook on every apply.
4. Every hook ran even when its output was byte-identical, as on the first apply of every session.

**Fix (engine, generic):**
- `requires_command` on a template: none on `PATH` → the entry is skipped entirely, logged once per session. The
  built-in templates declare it for all 18 applications they theme; GTK and Qt/KDE colour schemes stay ungated.
- An output directory that cannot exist is skipped with one warning per session naming the cause, e.g.
  "`~/.config/gtk-3.0` is a symlink to a missing target (`../.mydotfiles/…`)". It no longer fails the apply.
- A post-hook runs only when at least one of its outputs was rendered **and changed**. Forced applies
  (`templates-apply`, the theme CLI) still re-run every hook.

**Measured** (system-wide fork counter from `/proc/stat` around the event; I was using the machine):

| Event | Before | After |
|---|---|---|
| `templates-apply` (forced, current palette) | 2,663–2,665 forks, **4 warnings** per apply | 2,151–2,360 forks (the forced path intentionally still runs hooks for installed apps), **0 warnings** |
| Shell restart = the session's first apply | 2,513 / 2,533 forks | **245 / 298 / 342** (≈ −90 %) |

Tests: `template_capability_test` — an absent app gets no output, no directory and no hook; any alternative
command counts; a dangling output directory neither fails the apply nor creates the missing target; an entry after
a skipped one still applies; an unchanged output skips its hook unless forced. Mutation: disabling the
`requires_command` skip fails three checks.

**For me to decide:** GTK theming will stay off until the dangling symlinks are replaced by real directories:
`rm ~/.config/gtk-3.0 ~/.config/gtk-4.0 && mkdir ~/.config/gtk-3.0 ~/.config/gtk-4.0`. Removing a symlink deletes
no data, but GTK applications would then start following the palette.
