#!/usr/bin/env python3
"""Emit the architecture diagrams as standalone SVG (no external renderer needed).

Each diagram is a column of labelled bands with arrows, or a flow of boxes. Kept deliberately plain so the
SVG stays diffable and embeds cleanly in DOCX/PDF.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "07_Assets", "diagrams")
os.makedirs(OUT, exist_ok=True)

INK="#1b1b1f"; MUTE="#5b6070"; LINE="#c8ccd6"; ACCENT="#4c6ef5"; FILL="#f5f7fb"; ACC_FILL="#e7edff"

def svg(name, width, height, body):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="Inter,Segoe UI,DejaVu Sans,sans-serif">'
           f'<rect width="{width}" height="{height}" fill="white"/>'
           f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{MUTE}"/></marker></defs>{body}</svg>')
    open(os.path.join(OUT, name), "w").write(doc)
    print("  diagram:", name)

def box(x, y, w, h, title, sub="", accent=False, small=False):
    f = ACC_FILL if accent else FILL
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{f}" stroke="{ACCENT if accent else LINE}"/>'
    ty = y + (h/2 + 4 if not sub else h/2 - 3)
    s += f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" font-size="{11 if small else 13}" font-weight="600" fill="{INK}">{title}</text>'
    if sub:
        s += f'<text x="{x+w/2}" y="{y+h/2+13}" text-anchor="middle" font-size="10" fill="{MUTE}">{sub}</text>'
    return s

def arrow(x1, y1, x2, y2, label=""):
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTE}" stroke-width="1.6" marker-end="url(#a)"/>'
    if label:
        s += f'<text x="{(x1+x2)/2+7}" y="{(y1+y2)/2+3}" font-size="10" fill="{MUTE}">{label}</text>'
    return s

# 1 — system layers
b=""; y=16
layers=[("Applications","kitty · Zen · VS Code · Spotify"),
        ("Zynith Shell (noctalia process)","bar · panels · notifications · OSD · lock screen · wallpaper"),
        ("niri 26.04","window management · layer-shell · blur · screencopy · session-lock"),
        ("Wayland protocols","layer-shell · screencopy · session-lock · data-control"),
        ("Mesa 26.2.2 → EGL / OpenGL ES 3.2",""),
        ("Linux 7.2.5 — DRM/KMS · i915 · zram",""),
        ("Intel Core Ultra 5 125H · Arc iGPU · eDP-1 1920×1200","")]
for i,(t,s) in enumerate(layers):
    b += box(30, y, 700, 52, t, s, accent=(i==1))
    if i < len(layers)-1: b += arrow(380, y+52, 380, y+68)
    y += 68
svg("system-layers.svg", 760, y+6, b)

# 2 — animation pipeline
b = (box(20,20,150,52,"input event","") + arrow(170,46,205,46) +
     box(205,20,190,52,"component","chooses a target") + arrow(395,46,430,46) +
     box(430,20,300,52,"AnimationManager::animate","from · to · duration ÷ speed · easing", accent=True) +
     arrow(580,72,580,96) +
     box(430,96,300,46,"MotionService","speed 0.05–4.0 · enabled → instant") +
     arrow(430,119,300,119) +
     box(150,96,150,46,"TimerManager::tick","") + arrow(225,142,225,166) +
     box(150,166,300,46,"AnimationManager::tick","index walk · pending · dead flags", accent=True) +
     arrow(450,189,500,189) + box(500,166,230,46,"Node property → render",""))
svg("animation-pipeline.svg", 760, 236, b)

# 3 — wallpaper pipeline
b=""; y=16
steps=[("WallpaperScanner","background walk · dir-mtime cache"),
       ("beginSession()","idle budget raised · entries tagged"),
       ("prefetch whole collection @384 px","preview tier — instant browsing"),
       ("promotion window  focus−1 … focus+3","display tier @768 px · leans with travel"),
       ("tile draws promoted if decoded, else preview","a card never blanks"),
       ("Enter / click focused → applyWallpaperFromEntry()","palette transition · desktop updates live"),
       ("endSession()","drops only this session's idle entries")]
for i,(t,s) in enumerate(steps):
    b += box(30, y, 660, 50, t, s, accent=(i in (2,3)))
    if i < len(steps)-1: b += arrow(360, y+50, 360, y+66)
    y += 66
svg("wallpaper-pipeline.svg", 720, y+6, b)

# 4 — notification pipeline
b = (box(20,20,180,50,"Application","notify-send · browser") + arrow(200,45,240,45,"D-Bus") +
     box(240,20,250,50,"org.freedesktop.Notifications","exactly ONE owner", accent=True) +
     arrow(365,70,365,96) +
     box(240,96,250,50,"Noctalia NotificationManager","history · grouping · DND") +
     arrow(240,121,180,121) + box(20,96,160,50,"SoundPlayer","in-process → PipeWire") +
     arrow(365,146,365,172) +
     box(240,172,250,50,"layer-shell toast","niri layer-rule: blur") +
     f'<text x="520" y="50" font-size="11" fill="{MUTE}">swaync claimed this name in the</text>'
     f'<text x="520" y="66" font-size="11" fill="{MUTE}">niri session → no toast, no sound.</text>'
     f'<text x="520" y="82" font-size="11" fill="{MUTE}">Fixed by a systemd ConditionEnvironment.</text>')
svg("notification-pipeline.svg", 780, 244, b)

# 5 — configuration precedence
b=""; y=16
cfg=[("Noctalia built-in defaults","src/config/config_types.h"),
     ("~/.config/noctalia/*.toml","merged ALPHABETICALLY: lockscreen · motion · rice"),
     ("~/.local/state/noctalia/settings.toml","written by the GUI — WINS OVER EVERYTHING"),
     ("schema validation","src/config/schema/config_schema.cpp"),
     ("runtime configuration → components","live reload via inotify")]
for i,(t,s) in enumerate(cfg):
    b += box(30, y, 640, 50, t, s, accent=(i==2))
    if i < len(cfg)-1: b += arrow(350, y+50, 350, y+66)
    y += 66
svg("configuration-precedence.svg", 700, y+6, b)
print("diagrams written to", OUT)
