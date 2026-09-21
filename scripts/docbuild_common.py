"""Shared helpers: discover the documentation set and parse just enough Markdown."""
import os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def meta():
    with open(os.path.join(ROOT, "VERSION.json")) as f:
        return json.load(f)

# Order of the compiled master report.
REPORT = [
    ("Executive Summary",            ["EXECUTIVE_SUMMARY.md"]),
    ("Project",                      ["00_Project/overview.md", "00_Project/philosophy.md",
                                      "00_Project/technology-stack.md", "00_Project/repository-map.md"]),
    ("Architecture",                 ["ARCHITECTURE.md", "02_Architecture/system/layers.md",
                                      "02_Architecture/configuration/precedence.md",
                                      "02_Architecture/animation/lifetime-and-motion.md",
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
                                      "03_Performance/optimization-log.md",
                                      "03_Performance/benchmarks/contaminated-measurements.md"]),
    ("Reliability and Incidents",    ["04_Incidents/postmortems/2026-09-20-signal-uaf.md",
                                      "04_Incidents/postmortems/2026-09-21-incremental-build-abi-skew.md",
                                      "04_Incidents/postmortems/2026-09-21-notification-ownership.md",
                                      "04_Incidents/postmortems/2026-09-21-wallpaper-quality-regression.md",
                                      "04_Incidents/known-failures.md"]),
    ("Decision Records",             sorted("05_Decisions/ADRs/" + f
                                            for f in os.listdir(os.path.join(ROOT, "05_Decisions", "ADRs")))),
    ("Maintenance and Reference",    ["06_Reference/maintenance.md", "06_Reference/commands/index.md",
                                      "06_Reference/configuration/noctalia-rice.md",
                                      "06_Reference/configuration/niri.md",
                                      "06_Reference/troubleshooting/index.md",
                                      "06_Reference/future-work.md"]),
    ("Appendix",                     ["GLOSSARY.md", "DOCUMENTATION_POLICY.md", "CHANGELOG.md"]),
]

FIGURES = [
    ("07_Assets/diagrams/system-layers.svg",            "System layers, hardware upward"),
    ("07_Assets/diagrams/animation-pipeline.svg",       "Animation pipeline: one engine, one tick"),
    ("07_Assets/diagrams/wallpaper-pipeline.svg",       "Wallpaper session pipeline"),
    ("07_Assets/diagrams/notification-pipeline.svg",    "Notification pipeline and the ownership constraint"),
    ("07_Assets/diagrams/configuration-precedence.svg", "Configuration precedence"),
    ("03_Performance/charts/cpu-by-state.png",          "CPU by shell state (clean build)"),
    ("03_Performance/charts/wallpaper-session-rss.png", "Memory across a wallpaper browsing session"),
    ("03_Performance/charts/decodes-vs-traversal.png",  "Decode count against traversal length"),
    ("03_Performance/charts/optimizations.png",         "Measured optimizations, before and after"),
    ("03_Performance/charts/desktop-stack-pss.png",     "Desktop stack memory (PSS)"),
]

TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*]+\*)")

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
            out.append(("li", ln.strip()[2:])); i += 1; continue
        m_ol = re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if m_ol:
            out.append(("oli", m_ol.group(1), m_ol.group(2))); i += 1; continue
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
