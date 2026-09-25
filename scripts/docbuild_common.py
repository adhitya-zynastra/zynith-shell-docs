"""Shared helpers: discover the documentation set and parse just enough Markdown."""
import os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def meta():
    with open(os.path.join(ROOT, "VERSION.json")) as f:
        return json.load(f)

# Order of the compiled master report.
REPORT = [
    ("Executive Summary",            ["EXECUTIVE_SUMMARY.md"]),
    ("Project",                      ["00_Project/origins.md", "00_Project/overview.md", "00_Project/philosophy.md",
                                      "00_Project/technology-stack.md", "00_Project/repository-map.md"]),
    ("Architecture",                 ["ARCHITECTURE.md", "02_Architecture/system/layers.md",
                                      "02_Architecture/configuration/precedence.md",
                                      "02_Architecture/configuration/configurability.md",
                                      "02_Architecture/configuration/personalization.md",
                                      "02_Architecture/configuration/settings-information-architecture.md",
                                      "02_Architecture/layout/responsive-layout.md",
                                      "02_Architecture/transient/transient-ui.md",
                                      "02_Architecture/layout/coordinate-model.md",
                                      "02_Architecture/animation/motion-language.md",
                                      "02_Architecture/surface/glass.md",
                                      "02_Architecture/animation/lifetime-and-motion.md",
                                      "02_Architecture/animation/motion-settings.md",
                                      "02_Architecture/animation/morph-primitive.md",
                                      "02_Architecture/wallpaper/browser-architecture.md",
                                      "02_Architecture/notifications/pipeline.md",
                                      "02_Architecture/shell/event-model.md",
                                      "02_Architecture/control-center/panel.md",
                                      "02_Architecture/launcher/current-state.md",
                                      "02_Architecture/lockscreen/composition.md",
                                      "02_Architecture/security.md"]),
    ("Project History",              ["01_Phases/Phase_-1/README.md", "01_Phases/Phase_0/README.md",
                                      "01_Phases/Phase_1/README.md", "01_Phases/Phase_1/bugs.md",
                                      "01_Phases/Phase_2/README.md", "01_Phases/Phase_3/README.md",
                                      "01_Phases/Phase_4/README.md", "01_Phases/Phase_5/README.md",
                                      "01_Phases/Phase_6/README.md", "01_Phases/cross-phase-matrix.md"]),
    ("Performance Engineering",      ["03_Performance/README.md", "03_Performance/baselines/shell-states.md",
                                      "03_Performance/baselines/memory-floor.md",
                                      "03_Performance/baselines/idle-conditions.md",
                                      "03_Performance/optimization-log.md",
                                      "03_Performance/benchmarks/phase6a-motion.md",
                                      "03_Performance/benchmarks/tracks-motion-glass.md",
                                      "03_Performance/benchmarks/tracks-wallpaper-layout-cc.md",
                                      "03_Performance/benchmarks/tracks-launcher-osd-notify.md",
                                      "03_Performance/benchmarks/tracks-lock-widgets-motion.md",
                                      "03_Performance/benchmarks/contaminated-measurements.md"]),
    ("Reliability and Incidents",    ["04_Incidents/postmortems/2026-09-20-signal-uaf.md",
                                      "04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md",
                                      "04_Incidents/postmortems/2026-09-21-notification-ownership.md",
                                      "04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md",
                                      "04_Incidents/postmortems/2026-09-21-template-fork-storm.md",
                                      "04_Incidents/known-failures.md"]),
    ("Decision Records",             sorted("05_Decisions/ADRs/" + f
                                            for f in os.listdir(os.path.join(ROOT, "05_Decisions", "ADRs")))),
    ("Maintenance and Reference",    ["06_Reference/maintenance.md", "06_Reference/commands/index.md",
                                      "06_Reference/configuration/noctalia-rice.md",
                                      "06_Reference/configuration/niri.md",
                                      "06_Reference/troubleshooting/index.md",
                                      "06_Reference/future-work.md"]),
    ("Appendix",                     ["GLOSSARY.md", "DOCUMENTATION_POLICY.md", "DEVELOPMENT_WORKFLOW.md",
                                      "CHANGELOG.md"]),
]

FOREWORD = (
    "This is my engineering record of Zynith Shell \u2014 what I built, why I chose each approach, what broke, "
    "and what I could not establish. I made the design decisions, set the constraints and priorities, tested by "
    "hand and rejected what did not work; Claude Code acted as my engineering assistant, inspecting the system, "
    "writing the patches I specified, running the benchmarks, chasing the backtraces and drafting these pages "
    "from the evidence. Work is attributed to whoever performed it. Where a historical fact could not be "
    "established from surviving evidence, it is marked UNKNOWN rather than reconstructed, and a set of "
    "measurements taken from a contaminated build is preserved as invalid rather than deleted."
)

FIGURES = [
    ("07_Assets/diagrams/system-layers.svg",
     "How Zynith is layered, hardware upward \u2014 and where the boundary sits between what I changed "
     "and what stays untouched"),
    ("07_Assets/diagrams/animation-pipeline.svg",
     "One animation engine and one tick: why interrupting a transition retargets it instead of restarting it"),
    ("07_Assets/diagrams/wallpaper-pipeline.svg",
     "Wallpaper resource lifecycle across a browsing session \u2014 what is acquired on open, promoted around "
     "the focus, and released on close"),
    ("07_Assets/diagrams/notification-pipeline.svg",
     "The notification path, and the single D-Bus name whose ownership silently decides whether any of it runs"),
    ("07_Assets/diagrams/configuration-precedence.svg",
     "Configuration precedence \u2014 the merge order that makes settings.toml the last writer, and the reason "
     "Zynith never writes it"),
    ("03_Performance/charts/cpu-by-state.png",
     "Idle cost versus interaction cost, clean build only \u2014 the launcher is the most expensive state and "
     "is the open performance question"),
    ("03_Performance/charts/wallpaper-session-rss.png",
     "Memory across one browsing session: preparing 132 previews costs about 3 MB RSS, and close returns it"),
    ("03_Performance/charts/decodes-vs-traversal.png",
     "Why the decode gate matters: traversal cost stays flat at 18 decodes whether you sweep 20 items or 100"),
    ("03_Performance/charts/optimizations.png",
     "Every measured optimization, before and after \u2014 including the one that measured no improvement and "
     "was reverted"),
    ("03_Performance/charts/desktop-stack-pss.png",
     "Where desktop memory actually goes: the whole stack is 332 MB PSS, and the shell is not the largest part"),
]

SHOTS = [
    ("settings-motion-before.png",
     "Settings \u2192 Appearance before the motion migration \u2014 the Motion group holds two entries, and the "
     "Overridden filter and Reset Page control that ADR-0014 depends on already exist"),
    ("personalization-motion.png",
     "Personalization, opened by Super+Alt+A: one section for Zynith's own customization, landing on Motion"),
    ("personalization-groups.png",
     "Personalization with its four groups: Motion, Glass, Control Center and Wallpaper Browser. Control Center "
     "appearance options moved here from the Control Center section; none is duplicated"),
    ("carousel-1920.png",
     "The responsive carousel at 1920 px: the same five cards and 21\u00b0 step as before the change"),
    ("carousel-3200.png",
     "The same laptop at niri scale 0.6 (logical 3200 px): the card keeps its size and the arc gains a pair "
     "of neighbours"),
    ("cc-routing.png",
     "Bar widgets routed to their Control Center sections \u2014 network, bluetooth, volume, brightness, battery. "
     "Five clicks, one panel open: every switch after the first retargeted in place"),
    ("cc-density.png",
     "Control Center density compact, comfortable and spacious: only the frame rhythm changes. The network "
     "details row is redacted"),
    ("bars-output-centred.png",
     "The Media and Time bars on the output reference: a line at the screen centre runs through the middle of both"),
    ("launcher-no-footer.png",
     "The Zynith launcher after the correction pass: no key-hint footer, no scrollbar beside the results"),
    ("launcher-zynith.png",
     "The Zynith launcher: search bar with a primary hairline, tinted selection with the Enter hint, key-hint footer"),
    ("launcher-classic.png",
     "The classic launcher, kept selectable and unchanged (style = classic)"),
    ("osd-glass.png",
     "The OSD on the shared glass model: accent disc, title over bar, value; muted microphone below"),
    ("notification-stack.png",
     "A burst of six notifications settled at the preset's four visible cards; the rest queue with expiry paused"),
    ("personalization-launcher.png",
     "Personalization's Launcher group: style, geometry, density and hints, with the moved icon/grid/compact toggles"),
    ("glass-tint-compare.png",
     "Glass on the launcher: default (left) and a 0.35 primary tint (right) \u2014 the tint is a palette role, "
     "so it follows the wallpaper"),
    ("glass-blur-compare.png",
     "Glass blur on (left) and off (right): with blur off the wallpaper behind the card stays sharp"),
    ("desktop-current.png",
     "The desktop as it stands at 57debbc \u2014 wallpaper-derived palette, glass surfaces, one shared radius"),
    ("bar.png",
     "The bar after the Phase 6 recomposition: three glass clusters instead of per-widget pills, achieved with "
     "zero lines of C++"),
    ("control-center.png",
     "Control Center with top navigation \u2014 switching sections retargets the open panel rather than "
     "rebuilding it"),
    ("launcher.png",
     "The current launcher, kept as-is. The redesign is planned, and this design must remain selectable"),
    ("wallpaper-browser.png",
     "The wallpaper browser after the spatial correction: a compact control card, and a separate full-width "
     "orbit carousel below it"),
    ("power-menu.png",
     "The modal power menu \u2014 uniformly blurred, with no rectangular card around the orbs"),
    ("notification.png",
     "A notification toast in the Zynith language, with app identity leading as an accent caption"),
    ("osd.png",
     "The volume OSD, whose on-screen hold is a one-shot timer rather than an animation \u2014 worth ~50\u201380 "
     "wakeups per second"),
]

TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+\*)")

def _continuation(lines, i, body):
    """Absorb a wrapped list item's indented continuation lines.

    Markdown allows a list item to wrap across source lines; treating each line as its own
    item split inline spans (a **bold** opened on one line and closed on the next rendered
    its asterisks literally) and broke the bullet.
    """
    while i < len(lines):
        nxt = lines[i]
        if not nxt.strip():
            break
        if not nxt.startswith(("  ", "\t")):
            break
        if nxt.strip().startswith(("- ", "* ", "|", "```", "#", ">")):
            break
        if re.match(r"^\s*\d+\.\s+", nxt):
            break
        body += " " + nxt.strip(); i += 1
    return i, body

def blocks(path):
    """Yield ('h',level,text) ('p',text) ('code',text) ('table',rows) ('li',text) ('rule',)."""
    text = open(os.path.join(ROOT, path)).read()
    lines = text.split("\n")
    i, out = 0, []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            out.append(("code", "\n".join(buf))); i += 1; continue
        if ln.startswith("|") and i + 1 < len(lines) and set(lines[i+1].replace("|", "").strip()) <= set("-: "):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            out.append(("table", rows)); continue
        if ln.startswith("#"):
            lvl = len(ln) - len(ln.lstrip("#"))
            out.append(("h", lvl, ln.lstrip("# ").strip())); i += 1; continue
        if ln.strip().startswith(("- ", "* ")):
            body = ln.strip()[2:]; i += 1
            i, body = _continuation(lines, i, body)
            out.append(("li", body)); continue
        m_ol = re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if m_ol:
            body = m_ol.group(2); i += 1
            i, body = _continuation(lines, i, body)
            out.append(("oli", m_ol.group(1), body)); continue
        if ln.strip().startswith(">"):
            out.append(("quote", ln.strip().lstrip("> ").strip())); i += 1; continue
        if ln.strip() == "---":
            out.append(("rule",)); i += 1; continue
        if ln.strip():
            buf = [ln.strip()]
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not lines[i].startswith(("#", "|", "```", "- ", "* ", ">"))
                   and not re.match(r"^\s*\d+\.\s+", lines[i])):
                buf.append(lines[i].strip()); i += 1
            out.append(("p", " ".join(buf))); continue
        i += 1
    return out

def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s.replace("**", "").replace("`", "").replace("*", "")
