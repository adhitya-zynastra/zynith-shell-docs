# What the Idle Baseline Requires

**Recorded:** 2026‑09‑21, Phase 6 completion run, clean build `ccfe125`.

The documented idle figure for the shell is **~1.4 % of one core**. Reproducing it needs conditions that were
never written down, and not knowing them cost me a false alarm during this run. Two measurements, sixty seconds
apart, on the same clean build:

| Condition | noctalia | niri |
|---|---|---|
| Settings window **open** | **7.76 %** | 11.94 % |
| Settings window **closed** | **2.46 %** | 5.23 % |

## Finding 1 — an open Settings window costs about 5.3 % of a core

I had left the Settings window open from a screenshot attempt. That alone accounted for the difference: closing it
dropped the shell from 7.76 % to 2.46 % and niri from 11.94 % to 5.23 %.

This is not a defect — a visible, interactive, 370-control window is doing real work — but it is a large enough
resident cost that **no idle measurement is valid with Settings open**, and it is worth knowing that the Settings
window is by some distance the most expensive surface in the shell to leave sitting on screen.

## Finding 2 — the baseline assumes silence

The remaining 2.46 % against a 1.4 % baseline is the **bar's CAVA `audio_visualizer` widget**. `rice.toml` places
it inside the time cluster (`members = ["clock", "audio_visualizer"]`), so whenever audio plays it animates every
frame. **VERIFIED at measurement time:** `pactl list sink-inputs` showed Zen uncorked and playing, Spotify corked.

So the honest statement of the baseline is: *~1.4 % of one core, with no audio playing and no panel open.* An
active audio visualiser roughly doubles it. That is the widget working as designed — it is a per-frame
visualiser — but it means an idle number taken while music plays is measuring the visualiser, not the shell.

## Consequence for this run

The palette-apply CPU comparison taken during this pass is recorded as **UNCONTROLLED** rather than quoted: the
before-figure (165 ms at `57debbc`) and the after-figures (240–320 ms at `ccfe125`) were taken under different
audio conditions, and I did not control for it. The **fork counts are unaffected by any of this** and are
consistent across both an incremental and a clean build, three runs each, which is why the −18 % result rests on
them alone.

What would settle the CPU question: check out `57debbc`, clean build, and measure both commits back to back with
audio stopped and no panel open. Not done in this pass.

## Checklist before quoting an idle number

1. No Settings window, Control Center, launcher or wallpaper browser open.
2. No audio playing — `pactl list sink-inputs | grep Corked` should show no `Corked: no`.
3. Clean build (ADR‑0013), and the binary's version string free of `-dirty`.
4. Workspace quiet — niri composites the user's own animating windows, which is not shell cost (T‑10).
