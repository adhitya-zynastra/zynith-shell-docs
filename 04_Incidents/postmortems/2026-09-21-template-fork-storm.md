# Postmortem — A palette change spawns ~2,700 processes

| | |
|---|---|
| **Severity** | Medium — no visible failure; a large, repeated, mostly wasted system cost |
| **Found** | 2026‑09‑21, Phase 6 completion run, while investigating the known GTK apply cost |
| **Measured at** | `57debbc`, clean build, running shell (pid 227326, started 05:20, binary from the 05:08 clean build) |
| **Status** | Diagnosed and classified. Dominant cause is **user configuration**; one safe architectural optimization identified, not yet implemented |

## What I observed

Nothing, on screen. This one was already on my list as a known cost — "~156 ms per palette change spent writing
GTK CSS that fails, plus an emacs hook exiting 127" — and the goal for this run was to find out precisely what
was Zynith's fault, what was Noctalia's, and what was mine.

## What I initially suspected

That it was mostly the GTK template: a synchronous hook writing a file to a path that does not exist
(`~/.config/gtk-3.0/noctalia.css` is genuinely absent — it is the one standing warning in the documentation
audit), plus an emacs hook failing. In other words, two bad templates.

That was wrong in scale. It is not two templates; it is twenty-one, and the cost is not milliseconds of writing.

## What Claude investigated

I had Claude read the template catalog and the apply path, then measure the real cost on the running clean build
rather than trusting the earlier figure. Measuring it correctly took two attempts, and the first one is worth
recording because it would have understated the problem:

- `noctalia msg templates-apply` returns in ~24 ms because the message is **asynchronous** — it queues the apply
  and returns before any of the work happens. Timing that call measures nothing.
- `templates-apply` also uses the **forced** path, which deliberately bypasses the service's
  `sameInputs` deduplication (`template_apply_service.cpp:201`). So it is the worst case, not the normal one.

The honest measurement is a **genuine palette change** with the dedup guard in play. I used two
`theme-mode-toggle` calls — dark → light → dark — which is two real palette applies and leaves the desktop exactly
where it started. Process creation was counted from `/proc/stat`'s `processes` counter, shell CPU from
`/proc/<pid>/stat`.

## What the evidence showed

| Measurement | Value |
|---|---|
| Idle baseline | ~4 forks/second |
| **Forks per genuine palette change** | **2,695** |
| **Shell CPU per palette change** | **165 ms** |
| Forks per forced `templates-apply` | 2,826 |
| Peak *direct* children of the shell | 5 |
| Shell thread count, before and after | 40 (unchanged) |

Only five direct children at peak, with the thread count flat, means the ~2,700 processes are **grandchildren** —
the per-template `bash` hook scripts and everything they in turn spawn (`sed`, `grep`, `command -v`, `mkdir`,
`gsettings`, …). The 165 ms figure corroborates the previously documented ~156 ms, so that number was right; what
nobody had measured was the process storm behind it.

The multiplier is the enabled template list. From `settings.toml`, **21 builtin templates are enabled**, and
checking each one's target binary on this machine:

| Installed (10) | **Not installed (11)** |
|---|---|
| alacritty, btop, cava, gtk3, gtk4, hyprland, kcolorscheme, kitty, niri, starship | **emacs, foot, ghostty, helix, labwc, mango, qt, scroll, sway, umbriel, wezterm** |

So **more than half of every palette apply renders files and spawns hook scripts for software that is not on this
machine.** The emacs entry is the clearest case: it uses `output_path_dynamic`, so it spawns a shell *just to
compute the path it will write to* (`emacs/output-path.sh` walks `~/.config/doom`, `~/.config/emacs`,
`~/.emacs.d` — none exist), and then its `apply.sh` exits 127 because emacs is absent.

## Root cause and classification

This is what the investigation was for, so the split is stated precisely:

| Layer | Responsibility | Verdict |
|---|---|---|
| **Zynith code** | none — Zynith does not touch the template system | **not at fault** |
| **Noctalia code** | the template engine executes each template's `post_hook` as a shell script; `gtk3` and `gtk4` both invoke the *same* `assets/templates/gtk/apply.sh`, and both are pinned `hook_async = false` | **contributes**; the double invocation is genuinely redundant |
| **User configuration** | 21 enabled templates, 11 for absent software | **dominant cause, and mine to fix** |
| **External hooks** | `emacs/apply.sh` exits 127; `gtk/apply.sh` calls `gsettings list-schemas` (208 schemas, ~4 ms) | **external**; the 127 is correct behaviour for a missing program |

The honest conclusion is that I had been blaming the GTK template for a cost that is mostly my own enabled-template
list. The missing `noctalia.css` is real, but it is a symptom of the same thing, not the cause of the 165 ms.

## Fix

**Not yet applied — this is user configuration and deleting it is not mine to do unilaterally.** The recommended
change is to disable the 11 templates for software that is not installed, from the settings GUI (Appearance →
Templates), which should remove roughly half the per-apply process storm. It is reversible from the same screen.

One **safe architectural optimization** was identified and is recorded as future work rather than implemented in
this pass: `gtk3` and `gtk4` execute the identical `post_hook` command string, so the engine runs the same script
twice per apply. Deduplicating identical post-hook invocations within a single apply pass is behaviour-preserving
(the script already rewrites both `gtk.css` files in one run — that is *why* the two are synchronous) and would
halve the GTK portion without introducing the race that making them async would.

Two things were explicitly **not** done: the user's template configuration was not modified or deleted, and
`hook_async` was not flipped to `true` — the comment in `builtin.toml` states the two invocations are serialised
deliberately because they drive the same script, and making them concurrent would race on the same output files.

## Verification

The measurement method was verified before the numbers were trusted: an idle control window recorded ~4 forks/s
against 2,695 for a single apply, direct-child and thread counts confirmed the forks are hook grandchildren rather
than shell threads, and the theme mode was confirmed restored to `dark` afterwards.

## Engineering lesson

**An asynchronous IPC call is not a measurement surface.** The first attempt timed `noctalia msg templates-apply`
at 24 ms and would have concluded the apply was cheap; the call returns before the work starts. Anything measured
through `msg` needs a settle window and a counter that survives the call, not a stopwatch around it.

And the one I did not expect: **the default-enabled template list is a per-apply tax proportional to software you
do not own.** Nothing warns about it, the cost is invisible because it is asynchronous, and it scales with a list
most people will never revisit after install.
