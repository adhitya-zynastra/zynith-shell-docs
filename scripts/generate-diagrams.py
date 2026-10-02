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

def group(x, y, w, h, title, accent=False):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" '
         f'stroke="{ACCENT if accent else LINE}" stroke-width="1.4" stroke-dasharray="{"" if accent else "5 4"}"/>')
    s += f'<text x="{x+14}" y="{y+20}" font-size="12" font-weight="700" fill="{INK}">{title}</text>'
    return s

def note(x, y, text):
    return f'<text x="{x}" y="{y}" font-size="10" fill="{MUTE}">{text}</text>'

# 6 — current architecture (2026-10-02 audit)
b  = box(30, 16, 840, 48, "niri 26.04", "windows · workspaces · overview · blur · enforces ext-session-lock")
b += arrow(450, 64, 450, 90, "layer-shell surfaces · niri IPC socket · generated .kdl")
b += group(30, 90, 840, 250, "noctalia — Noctalia 5.1.0 + Zynith patches · one C++23 process · one poll loop · 34 threads", accent=True)
row = [("Bars ×3", "start / center / end widgets"), ("Panel host", "one surface · one panel at a time"),
       ("Lock · OSD · toasts", "ext-session-lock surfaces"), ("Wallpaper · backdrop", "Settings window (xdg)")]
for i, (t, s) in enumerate(row):
    b += box(46 + i*206, 118, 196, 52, t, s, small=True)
b += note(46, 186, "Application owns ≈ 100 members; services push single callbacks, surfaces pull in doUpdate()")
row = [("Config · theme · templates", "TOML merge · MCU palette"), ("PipeWire · spectrum · MPRIS", "WirePlumber mixer"),
       ("Network · Bluetooth · Power", "NM · BlueZ · UPower · logind · agents"), ("Notifications · tray · polkit", "D-Bus names owned")]
for i, (t, s) in enumerate(row):
    b += box(46 + i*206, 196, 196, 52, t, s, small=True)
row = [("Scene graph → GLES", "per surface · Cairo/Pango text"), ("Luau plugins", "in-process · runAsync"),
       ("IPC socket", "noctalia msg · dmenu"), ("Live wallpaper controller", "branch feature/live-wallpaper")]
for i, (t, s) in enumerate(row):
    b += box(46 + i*206, 268, 196, 52, t, s, small=True)
b += arrow(450, 340, 450, 366, "fork / exec")
row = [("PAM helper", "re-exec · non-dumpable"), ("linux-wallpaperengine", "exactly one · supervised"),
       ("hook and template commands", "post-hooks · user hooks"), ("plugin git · niri validate", "short-lived")]
for i, (t, s) in enumerate(row):
    b += box(46 + i*206, 366, 196, 50, t, s, small=True)
b += arrow(450, 416, 450, 442, "D-Bus · PipeWire · sysfs · files")
b += box(30, 442, 840, 50, "Linux · Wayland · D-Bus services",
         "PipeWire/WirePlumber · NetworkManager · BlueZ · UPower · logind · polkitd · gnome-keyring · Steam library")
svg("zynith-current-architecture.svg", 900, 510, b)

# 7 — proposed Zynith Architecture 2.0
b  = box(30, 16, 900, 48, "niri", "windows · workspaces · layout presets (generated) · blur · overview · lock enforcement")
b += arrow(350, 90, 350, 64, "layer-shell · xdg")
b += arrow(810, 90, 810, 64)
b += group(30, 90, 640, 262, "zynith-ui — Quickshell (QML) · draws, never fetches", accent=True)
row = [("Bars", "N · edge + anchor"), ("Panels", "focused surfaces"), ("Transient", "toasts · OSD · menus"),
       ("Launcher", "providers"), ("Desktop", "wallpaper · widgets")]
for i, (t, s) in enumerate(row):
    b += box(44 + i*124, 118, 116, 50, t, s, small=True)
b += arrow(350, 168, 350, 194, "bind state · call intents")
b += box(44, 194, 612, 44, "State — one QML singleton per domain", "state · intents · demand (retain / release)", accent=True)
b += box(44, 254, 300, 84, "Quickshell built-ins", "MPRIS · Notifications · Tray · UPower", small=True)
b += f'<text x="194" y="324" text-anchor="middle" font-size="10" fill="{MUTE}">PipeWire · Bluetooth · Networking (D-Bus direct)</text>'
b += box(356, 254, 300, 84, "Zynith.Native (C++ QML module)", "niri model · spectrum · sampler · images", accent=True, small=True)
b += box(690, 90, 240, 120, "zynith-settings", "Quickshell app · started on demand")
b += box(690, 228, 240, 124, "zynith-secure (native)", "lock + PAM · polkit · Wi-Fi · pairing", accent=True)
b += note(702, 336, "secrets never leave this process")
b += arrow(350, 352, 350, 380, "JSON lines · subscribe / call")
b += box(30, 380, 640, 56, "zynithd (native helper daemon)",
         "config · theme / templates / hooks · wallpaper · niri fragments · clipboard · night light · weather · plugins")
b += arrow(200, 436, 200, 462, "supervises")
b += box(30, 462, 340, 44, "linux-wallpaperengine (one)", "")
b += arrow(520, 436, 520, 530)
b += arrow(810, 352, 810, 530)
b += box(30, 530, 900, 50, "Linux · Wayland · D-Bus services",
         "PipeWire · NetworkManager · BlueZ · UPower · logind · polkitd · gnome-keyring · Steam library")
svg("zynith-architecture-2.0.svg", 960, 600, b)
print("diagrams written to", OUT)
