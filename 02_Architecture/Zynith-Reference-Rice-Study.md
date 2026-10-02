# Reference Rice Study — architecture (2026‑10‑02)

**Status:** research record. The September study ([design research](design/design-research-2026-09.md)) covered
look and motion. This pass is about **structure**: how each project divides UI, state, system access and helper
processes. I asked for the source trees to be read, not only the videos. Claude read them; the findings below cite
files. **No code was copied.** All three trees are **GPL‑3.0**, and Zynith's code base (Noctalia) is MIT, so ideas
may be reused but code may not be pasted in.

Material in `~/Videos/Downloaded/`:

| Item | What it is | Compositor | Read |
|---|---|---|---|
| `quickshell/` | **Clavis Shell** (StatIndet), Quickshell/QML + native C++ modules, last commit 2026‑09‑18 | **niri** | source + docs |
| `caelestia/` | caelestia-dots/shell, Quickshell/QML + C++ plugin, last commit 2026‑03‑01 | Hyprland | source |
| `ryoku-arch/` | Ryoku, a full Arch distribution; shell is Quickshell/QML with a Go control daemon | Hyprland | source + docs |
| 6 videos | showcase recordings (Caelestia ×2, End‑4, Imperative, Ryoku, a Hyprland daily driver) | — | studied in September; no source for End‑4 / Imperative here |

Also on this machine: `~/.config/quickshell/` (an older Caelestia clone plus an end‑4-style overview from the
Hyprland era; not used by Zynith) and `~/linux-wallpaperengine` (the live renderer, GPL‑3.0).

## 1. Clavis — UI in QML, system work in separate programs

**Idea.** Strict layering inside the shell, and system work split into separate programs with machine protocols.

**How** (`AGENTS.md`, `docs/architecture/`):
- `Modules/` (features: Bar, Keystone, Sidebars, Launcher, Lock, Wallpaper, ControlCenter…), `Services/` (long-lived
  state and system interaction, one singleton per domain), `Widgets/` (presentation only), `Common/` (tokens,
  sizes, paths, pure helpers), `core/` (native C++ QML modules: niri IPC client and window/workspace/output models,
  Cava spectrum, weather, media palette, lyrics, gamma).
- Rule: **presentation components may not create processes or run commands.**
- Two sibling programs own system concerns: `keytop` (system metrics; Clavis consumes its JSONL stream and must
  not re-implement its parser) and `key-cli` (recording, clipboard, keyboard-lock backend, JSON with
  `schemaVersion`).
- Services use Quickshell's built-ins wherever they exist (`Quickshell.Networking`, `.Bluetooth`,
  `.Services.UPower`, `.Mpris`, `.Notifications`, `.Pam`, `WlSessionLock`); the spectrum is native (`Clavis.Cava`).
- Settings is a route table as data (`Common/settings-routes.json`: id, title, icon, page, path, aliases).
- niri config ownership (`config-isolation.md`): Clavis writes only its own fragments (`clavis/effects.kdl`,
  `cursor.kdl`, `layer-rules.kdl`, `binds.kdl`), **only when I click "set up"**, never at startup; candidate config
  validated with real `niri validate`; flock; backups; no automatic reload.
- Wallpaper (`wallpaper-backends.md`): the desktop wallpaper and the **overview wallpaper are two independent
  surfaces**; the overview one gets `place-within-backdrop` and the workspace `background-color` is made
  transparent. Resolution order for the overview: per-output overview → global overview → per-output desktop →
  global desktop.
- Lock (`lock-snapshot-crash.md`): a Quickshell screencopy bug crashed the shell; they moved the pre-lock capture
  into a **short-lived separate Quickshell process** to isolate it.

**Why it works.** Each kind of code has one home, so "where does this belong" has an answer. System parsing lives
in one tested program instead of in JavaScript in every widget. Crash-prone native code is isolated.

**Learn:** the four-folder rule and "presentation never spawns"; versioned machine protocols; opt-in, validated
niri fragments; separate desktop and overview wallpaper surfaces; isolate risky native work in its own process.

**Do not copy:** the three-repository split (heavy for a one-person project); its Material/Apple-island look (the
September study already rejected the island as a borrowed pattern).

## 2. Caelestia — one scene per monitor, demand-counted audio

**Idea.** The whole shell is a frame around the screen: one full-screen layer window per monitor
(`modules/drawers/Drawers.qml`) holds the bar and every panel as "drawers", with an input mask cut to what is open.

**How.** `services/Visibilities.qml` maps each screen to which drawers are open. Config is one JSON file watched and
saved by `FileView` + `JsonAdapter` (`config/Config.qml`, `shell.json`) with typed per-area config singletons.
The C++ plugin (`plugin/src/Caelestia/Services/`) does audio capture, Cava and beat tracking behind a
**`ServiceRef` reference count**: the audio service runs only while a visible consumer holds a reference. Network
goes through `nmcli` (`services/Nmcli.qml`); system usage is polled.

**Why it works.** One window makes cross-panel motion trivial (everything shares one coordinate space and one
shadow). The reference count makes "no visible spectrum → no spectrum work" structural.

**Learn:** demand counting for expensive producers (Zynith's spectrum and sampler should look exactly like this);
typed config singletons over one file.

**Do not copy:** one full-screen surface per monitor. Any animation damages a full-output buffer, and the September
study rejected it for that reason. CLI polling (`nmcli`, 0.5–1 s timers) where D-Bus exists.

## 3. Ryoku — UI processes hold no logic; a daemon owns state

**Idea.** QML is only a view. A Go control plane (`ryoku/shell/ipc/`, `ryoku-shell daemon`) supervises the
Quickshell components, owns wallpaper, clipboard, lock, the polkit agent and the GNOME keyring prompter, and serves
one Unix socket.

**How.** `statestream.go`: QML singletons `subscribe <topic>` and receive a full JSON state frame, then a frame on
every change; **byte-identical frames are suppressed** so an unchanged value never wakes a binding. Intent goes the
other way with `call <topic>.<method>`. Settings ("Ryoku Hub") is a separate Quickshell app with its own Go data
plane (`ryoku/hub/`). Shared look comes from one QML module (`ryoku/ui`, `Ryoku.Ui` tokens) used by shell, settings
and apps. Per-domain config files (`shell.json`, `visualizer.json`, `widgets.json`) are watched for live retuning.
`qsruntime.go` documents an operational hazard: Quickshell keeps per-instance logs in `$XDG_RUNTIME_DIR`
(tmpfs, i.e. RAM) and never removes them; one warning storm filled 4 GB, so the daemon prunes them. Live video
wallpapers use their own tiny shared-memory renderer (`ryoku/shell/livewall/livewall.c`), and the palette comes
from one sampled frame (`ipc/theming.go`).

**Why it works.** State has one owner and one transport. The UI can be restarted or reloaded without losing state,
and it never polls. Settings being its own app keeps the shell small.

**Learn:** the subscribe/call contract with change suppression; Settings as a separate app; one token module for
every surface; a poster frame for palette and stills.

**Do not copy:** a whole extra runtime (Go) for a one-person project unless a native helper is needed anyway; the
distribution-level scope (installer, package updates, agent OS).

## 4. Patterns across all three

| Concern | Clavis | Caelestia | Ryoku | Synthesis for Zynith |
|---|---|---|---|---|
| UI technology | QML | QML | QML | QML is the common choice for **UI** |
| Hot data (spectrum, metrics, niri model) | native C++ modules + external CLI | native C++ plugin | Go daemon | **never in JavaScript** |
| Where state lives | QML service singletons | QML singletons | daemon, streamed | one owner per domain; surfaces only read |
| System access | Quickshell built-ins + CLIs with JSON | `nmcli`, Hyprland IPC, polling | daemon | D-Bus/native, no CLI parsing |
| Panels | separate surfaces (sidebars, keystone, spotlight) | drawers in one surface | separate surfaces per module | separate surfaces |
| Settings | in-shell window with route table | in-shell | **separate app** | separate app, route table |
| Expensive producers | — | `ServiceRef` refcount | daemon topics | demand counting |
| Compositor config | opt-in validated fragments | — (Hyprland) | Lua config generated by Hub | validated fragments, one owner per key |
| Secrets | Quickshell `PamContext` in the shell | same | daemon owns polkit + keyring prompts | native, out of the UI process |
| Crash isolation | risky capture in a separate process | none | daemon survives UI reloads | separate processes for secrets and renderers |

The strongest shared lesson is not "use QML". It is that **all three keep heavy or system-level work out of the
QML/JavaScript layer**, and the two newer ones (Clavis, Ryoku) push it into separate processes with explicit
protocols.
