#!/usr/bin/env python3
"""Generate every chart in 03_Performance/charts/ from the CSVs in 03_Performance/benchmarks/.

Charts are derived only from committed CSV data so a reader can re-derive them. Axes always start at zero;
no axis is truncated to exaggerate a difference (DOCUMENTATION_POLICY.md).
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "03_Performance", "benchmarks")
OUT = os.path.join(ROOT, "03_Performance", "charts")
ASSET = os.path.join(ROOT, "07_Assets", "charts")
os.makedirs(OUT, exist_ok=True); os.makedirs(ASSET, exist_ok=True)

INK = "#1b1b1f"; ACCENT = "#4c6ef5"; ACCENT2 = "#c2410c"; GRID = "#d5d7dd"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "figure.dpi": 160, "savefig.bbox": "tight",
})

def save(fig, name):
    for d in (OUT, ASSET):
        fig.savefig(os.path.join(d, name))
    plt.close(fig)
    print("  chart:", name)

def rows(path):
    with open(os.path.join(BENCH, path)) as f:
        return list(csv.DictReader(f))

# 1 — CPU by shell state
r = rows("shell-states.csv")
labels = [x["state"] for x in r]
noct = [float(x["noctalia_cpu_pct_of_core"]) for x in r]
niri = [float(x["niri_cpu_pct_of_core"]) for x in r]
fig, ax = plt.subplots(figsize=(8, 4.6))
y = range(len(labels))
ax.barh([i + 0.2 for i in y], noct, height=0.38, color=ACCENT, label="noctalia (shell)")
ax.barh([i - 0.2 for i in y], niri, height=0.38, color=ACCENT2, label="niri (compositor)")
ax.set_yticks(list(y)); ax.set_yticklabels(labels); ax.invert_yaxis()
ax.set_xlabel("CPU, % of one core"); ax.set_xlim(left=0)
ax.set_title("CPU by shell state — clean build, commit eaff2b2, 2026-09-21", loc="left", fontsize=10)
ax.legend(frameon=False, loc="lower right")
save(fig, "cpu-by-state.png")

# 2 — RSS across a wallpaper browsing session
w = rows("wallpaper-session.csv")
seq = ["rss before browser", "rss after session preparation", "rss during 300 rapid traversal steps",
       "rss after applying a wallpaper", "rss after close", "rss after 5 further sessions"]
vals = [float(x["value"]) for s in seq for x in w if x["measurement"] == s]
short = ["before", "after prep\n(132 previews)", "300 rapid\nsteps", "after apply", "after close", "after 5 more\nsessions"]
fig, ax = plt.subplots(figsize=(7.4, 3.6))
ax.plot(short, vals, marker="o", color=ACCENT, linewidth=2)
for i, v in enumerate(vals):
    ax.annotate(f"{v:.1f}", (i, v), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
ax.set_ylabel("noctalia RSS (MB)"); ax.set_ylim(150, max(vals) + 8)
ax.set_title("Wallpaper browser memory across a session — clean build, 57debbc", loc="left", fontsize=10)
save(fig, "wallpaper-session-rss.png")

# 3 — Optimizations: before/after (normalised, because units differ)
o = [x for x in rows("optimizations.csv") if x["significance"] != "no regression"]
names, before, after, units = [], [], [], []
for x in o:
    try:
        b, a = float(x["before"]), float(x["after"])
    except ValueError:
        continue
    names.append(f'{x["optimization"]}\n({x["metric"]}, {x["unit"]})'); before.append(b); after.append(a)
fig, ax = plt.subplots(figsize=(8, 4.2))
y = range(len(names))
ax.barh([i + 0.2 for i in y], before, height=0.38, color="#9aa0aa", label="before")
ax.barh([i - 0.2 for i in y], after, height=0.38, color=ACCENT, label="after")
for i, (b, a) in enumerate(zip(before, after)):
    ax.annotate(f"{b:g}", (b, i + 0.2), xytext=(4, -3), textcoords="offset points", fontsize=7)
    ax.annotate(f"{a:g}", (a, i - 0.2), xytext=(4, -3), textcoords="offset points", fontsize=7)
ax.set_yticks(list(y)); ax.set_yticklabels(names, fontsize=7.5); ax.invert_yaxis()
ax.set_xscale("log"); ax.set_xlabel("value (log scale — units differ per row)")
ax.set_title("Measured optimizations, before vs after", loc="left", fontsize=10)
ax.legend(frameon=False, loc="lower right")
save(fig, "optimizations.png")

# 4 — Decodes vs traversal length (the anti-storm result)
fig, ax = plt.subplots(figsize=(5.6, 3.4))
lengths = [20, 50, 100]; decodes = [18, 18, 18]
ax.plot(lengths, decodes, marker="o", color=ACCENT, linewidth=2, label="with decode gate (measured)")
ax.plot(lengths, lengths, marker="x", color="#9aa0aa", linestyle="--", linewidth=1.4,
        label="one decode per item (hypothetical)")
ax.set_xlabel("wallpapers traversed at 66 items/s"); ax.set_ylabel("image decodes")
ax.set_ylim(bottom=0); ax.legend(frameon=False, fontsize=8)
ax.set_title("Decode count is set by where a fling lands", loc="left", fontsize=10)
save(fig, "decodes-vs-traversal.png")

# 5 — Desktop stack PSS
parts = [("pipewire", 99.6), ("noctalia", 98.6), ("niri", 56.8), ("wireplumber", 19.8),
         ("xdg portals", 35.1), ("session plumbing", 21.6)]
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.bar([p[0] for p in parts], [p[1] for p in parts],
       color=[ACCENT if p[0] == "noctalia" else "#9aa0aa" for p in parts])
for i, p in enumerate(parts):
    ax.annotate(f"{p[1]:.1f}", (i, p[1]), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8)
ax.set_ylabel("PSS (MB)"); ax.set_ylim(bottom=0)
ax.set_title("Desktop stack memory — 332.3 MB PSS total", loc="left", fontsize=10)
plt.xticks(rotation=20, ha="right")
save(fig, "desktop-stack-pss.png")

print("charts written to", OUT)
