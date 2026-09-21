# Why Zynith Exists

**Evidence basis:** my own account, written 2026‑09‑21. Everything on this page is **RECOVERED** from that
account rather than from artifacts — the design period it describes predates the first backup this project took,
and nothing from it survives on disk. Dates in it are approximate and are marked where that matters.

Every other page in this set explains *what* Zynith is and *how* it works. This one explains why I bothered,
because that is the part that stops making sense to a future reader first.

## It started with not wanting to use Windows any more

The honest origin is frustration rather than ambition. I do not think Windows is bad software, and I am not
interested in the tribal version of this argument — it works, and it does several things well. What wore me down
was a question of control.

I chose the hardware. I paid for the machine. And then the operating system was the thing deciding what ran in
the background, what updated, what started with the system, what sent telemetry, what occupied storage, and which
services existed at all. Most of those decisions have defensible reasons behind them — security, compatibility,
update infrastructure, enterprise requirements. I still did not like the direction, because the effect
accumulates: a decent CPU, a fast SSD, 16 GB of RAM and a capable GPU, gradually spent on a software stack that
keeps adding to itself.

What I wanted was narrower than "a faster computer":

- to know what is running,
- to know **why** it is running,
- to be able to remove it if I do not need it,
- and to be able to change it if I do not like it.

That is where open source stopped being an abstraction for me. Not because proprietary software is evil and open
source is automatically better — that framing is its own kind of nonsense — but because being able to read the
thing you are running, build it yourself, replace a component or simply learn from how someone else solved a
problem is a genuinely different relationship with your own machine. If I do not like something, I should at
least have the *possibility* of changing it.

That principle is the root of the priority order in [`philosophy.md`](philosophy.md), and of why the whole system
is layered so that any layer can be removed.

## Fedora, and why I stopped distro-hopping

Fedora was the first distribution I properly settled on, after the obligatory tour through Arch, Debian, Ubuntu,
and an unreasonable number of desktop environments, window managers and compositors. I stayed because of the
balance: current software and room to experiment, without the system needing constant attention.

That mattered for a practical reason. I am a CS student — university, coursework, AI/ML, web development and a
steady supply of side projects I did not need to start. My main laptop cannot be a science experiment. I wanted
freedom *and* reliability, and that combination is the single constraint that shaped Zynith more than any other:
it is why the Fedora package stays installed, why Hyprland stays working, why every change is reversible, and why
`niri validate` runs before anything is applied.

## Hyprland, and how this actually started

A friend suggested I try Hyprland. That is the specific moment this project traces back to.

Hyprland was the first thing that showed me a desktop did not have to be "here is a desktop, change the
wallpaper" — it could be "here is a compositor, tell it how you want your desktop to behave." Window rules,
keybindings, workspaces, animations, gaps, tiling, IPC, plugins. I could keep changing things until the desktop
was mine rather than someone else's default.

This is also why Hyprland is still installed. It is described elsewhere in this documentation as a fallback
session, which is true and is the engineering reason, but it is not the whole reason: it is what got me into this
in the first place, and I did not stop liking it the day I switched to niri.

## Why I built my own instead of downloading someone's

I looked at a lot of other people's setups, and many of them are extraordinary — bars, launchers, dynamic
wallpapers, glass panels, visualisers, custom notification systems, lock screens, dashboards.

I want to be clear that I have no objection to using someone else's dotfiles. If a setup does what you want, use
it; building everything yourself does not make anyone a more legitimate Linux user. I would have done exactly
that if I had found something that matched what I wanted and worked properly on Fedora.

That was the problem. The setups I found most interesting were built around Arch or around a specific package
ecosystem, depended on long tool chains, or were customised deeply enough that porting them meant rebuilding half
of them anyway. At the point where I would be rewriting most of it, writing the thing I actually wanted became
the cheaper option.

## Where it stopped being a rice

A rice answers "make my desktop look like this." I found I cared about a different question: "make my desktop
*behave* like this."

A wallpaper browser, a launcher, a control center, a notification system, a lock screen, a bar and a pile of
scripts can all look good individually and still not be a system, because they disagree about how things should
work. What I wanted was cohesion: the wallpaper drives the palette, the palette drives the shell, the shell uses
one visual language, animations are related to each other, settings control the actual system rather than being
unrelated toggles, temporary UI is genuinely temporary, and resources have clear lifetimes.

And the part that turned it into an engineering project rather than a styling one: **I did not want a desktop
that spends a meaningful fraction of the machine drawing a clock.** That is the sentence behind every measurement
in [`03_Performance/`](../03_Performance/README.md).

## When it became serious

**Approximately four to five months before the live implementation work** — so around April or May 2026;
**the exact date is UNKNOWN** and nothing survives from that period — I stopped treating this as a side
experiment. That is when I started writing requirements, designing the architecture, planning interactions,
studying how other people had implemented similar systems, and reading about the things that actually decide
whether a shell is any good: configuration ownership, resource ownership, process lifetimes, event-driven
design, animation orchestration, caching, GPU textures, CPU wakeups, memory, and what happens when an object is
destroyed while something else still holds a reference to it.

That last one is not a coincidence. It became the project's most serious incident
([the use-after-free](../04_Incidents/postmortems/2026-09-20-signal-uaf.md)) months later.

The numbered phases documented in [`01_Phases/`](../01_Phases/) cover the **live implementation** window of
2026‑09‑19 to 2026‑09‑21. They are not the start of the project; they are the point at which the design was far
enough along to build against a real machine.

## Discovering niri

I spent a long time building around Hyprland, because that is what I knew. While researching compositors more
seriously I found niri, and that changed the plan.

niri already did several of the things I had been sketching for myself. Not all of them — it was never "this is
my finished shell" — but enough that the question changed from *how do I build this* to *why am I rebuilding what
the compositor already does well*. The scrolling window model was what caught my attention first; the compositor
architecture and the way it handles workspaces and window movement matched how I wanted to work.

That was a relief, honestly, because the alternative was accidentally spending years writing my own compositor.
Then I started using Noctalia on top of it, and the shape of the project settled:

| Layer | Responsibility |
|---|---|
| **niri** | compositor foundation — tiling model, workspaces, window movement, layer-shell |
| **Noctalia** | shell foundation — one native process drawing the chrome, with one animation clock |
| **Zynith** | architecture, design language, interaction model, resource policy, and the UI work on top |

This corrects an earlier statement in this documentation. Until this page existed, the README recorded that my
reasons for adopting niri were not recoverable. They are recorded here now.

## What I am actually aiming at

Not the prettiest rice. There are people doing remarkable work in that category and I am not competing with them.

What I want is a Linux desktop I enjoy using every day: something that feels like it belongs on my machine, that
I understand, that I can change, that does not fight me, that does not need absurd resources to look good, and
that can be customised heavily without becoming unmaintainable — where the compositor, shell, UI, animations,
configuration and resource management feel like parts of one system rather than a collection of neighbours.

I want it to feel alive when I am interacting with it and to disappear when I am working.

The underlying reason is the same one this page started with. I could have used someone else's rice, or stayed
on a stock desktop, or stayed with Hyprland — all completely reasonable. Building my own means that when I catch
myself thinking *why doesn't it work like this*, I do not have to stop at wishing. I can go and find out why,
and if I still do not like the answer, I can change it.

## A note on where I am in this

I am learning most of this while building it. I did not arrive knowing how Wayland shells work and decide to make
one; I am a CS student working it out, and a large amount of the time went into questions like *what owns this
object*, *why is this callback still alive*, *why is this process waking up*, and *how does Wayland actually do
this*.

That is worth stating plainly because it explains the shape of this documentation. The postmortems record what I
initially suspected as well as what was actually true, and the performance pages keep the measurements that
turned out to be invalid, because in a project where the author is learning, the wrong first answer is part of
the record — and the reason the second answer can be trusted.
