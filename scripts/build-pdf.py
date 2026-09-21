#!/usr/bin/env python3
"""Compile the canonical Markdown into ZynithShell-Technical-Report.pdf (reportlab platypus)."""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docbuild_common as C

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# The base-14 fonts are WinAnsi-encoded, so characters the documentation genuinely uses --
# the non-breaking hyphen in dates, arrows in priority chains, the minus in "Phase -1",
# validation ticks, theta -- render as solid black boxes. DejaVu Sans covers all of them.
# Registered under the base-14 names so every existing style picks it up unchanged; if the
# font is not installed the report still builds with Helvetica and ascii_prose() below.
_DJV = "/usr/share/fonts/dejavu-sans-fonts"
UNICODE_SANS = False
try:
    pdfmetrics.registerFont(TTFont("Helvetica", _DJV + "/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("Helvetica-Bold", _DJV + "/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Helvetica-Oblique", _DJV + "/DejaVuSans-Oblique.ttf"))
    pdfmetrics.registerFont(TTFont("Helvetica-BoldOblique", _DJV + "/DejaVuSans-BoldOblique.ttf"))
    pdfmetrics.registerFontFamily("Helvetica", normal="Helvetica", bold="Helvetica-Bold",
                                  italic="Helvetica-Oblique", boldItalic="Helvetica-BoldOblique")
    UNICODE_SANS = True
except Exception as e:
    print("  note: DejaVu Sans unavailable (%s); prose glyphs will be transliterated" % e)

INK = colors.HexColor("#1b1b1f"); MUTE = colors.HexColor("#5b6070")
ACCENT = colors.HexColor("#304fd6"); GRID = colors.HexColor("#c8ccd6")
BG = colors.HexColor("#f5f7fb")

ss = getSampleStyleSheet()
def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.4, leading=13.2, textColor=INK, spaceAfter=5)
    base.update(kw); return ParagraphStyle(name, **base)

BODY   = S("body")
H1     = S("h1", fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=ACCENT, spaceBefore=12, spaceAfter=8)
H2     = S("h2", fontName="Helvetica-Bold", fontSize=13, leading=17, spaceBefore=10, spaceAfter=5)
H3     = S("h3", fontName="Helvetica-Bold", fontSize=11, leading=14.5, spaceBefore=8, spaceAfter=4)
H4     = S("h4", fontName="Helvetica-Bold", fontSize=9.8, leading=13, spaceBefore=6, spaceAfter=3)
CODE   = S("code", fontName="Courier", fontSize=7.4, leading=9.4, textColor=INK,
           backColor=BG, borderPadding=5, leftIndent=6, spaceBefore=3, spaceAfter=7)
BULLET = S("bullet", leftIndent=12, bulletIndent=3, spaceAfter=2.5)
QUOTE  = S("quote", leftIndent=12, textColor=MUTE, fontName="Helvetica-Oblique")
CAP    = S("cap", fontSize=7.8, textColor=MUTE, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
CELL   = S("cell", fontSize=7.4, leading=9.4, spaceAfter=0)
CELLH  = S("cellh", fontSize=7.4, leading=9.4, fontName="Helvetica-Bold", spaceAfter=0, textColor=colors.white)

def esc(t):
    """Markdown inline → reportlab markup. Code spans are extracted first so that
    characters like * inside `*.toml` are never treated as emphasis."""
    spans = []
    def stash(m):
        spans.append(m.group(1))
        return "\x00%d\x00" % (len(spans) - 1)
    t = re.sub(r"`([^`]+)`", stash, t)
    t = ascii_prose(t)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", t)
    def unstash(m):
        # Inline code stays Courier, which is base-14 and has none of these glyphs,
        # so transliterate unconditionally here.
        code = force_ascii(spans[int(m.group(1))])
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return '<font face="Courier" size="8">%s</font>' % code
    return re.sub(r"\x00(\d+)\x00", unstash, t)

# Courier (a base-14 font) has no box-drawing glyphs; they render as solid blocks.
BOX = {"\u2500": "-", "\u2502": "|", "\u250c": "+", "\u2510": "+", "\u2514": "+", "\u2518": "+",
       "\u251c": "+", "\u2524": "+", "\u252c": "+", "\u2534": "+", "\u253c": "+",
       "\u2550": "=", "\u2551": "|", "\u2554": "+", "\u2557": "+", "\u255a": "+", "\u255d": "+",
       "\u2192": "->", "\u2193": "v", "\u2190": "<-", "\u2191": "^", "\u25c0": "<", "\u25b6": ">",
       "\u2026": "...", "\u2014": "--", "\u2013": "-", "\u00b7": "*", "\u2713": "OK", "\u2715": "x"}

def ascii_art(t):
    for k, v in BOX.items():
        t = t.replace(k, v)
    return t

# Only used when DejaVu Sans is unavailable: keep prose readable rather than boxed.
PROSE = {"\u2011": "-", "\u2212": "-", "\u2192": " -> ", "\u2190": " <- ", "\u2193": "v",
         "\u2248": "~", "\u2260": "!=", "\u2264": "<=", "\u2265": ">=", "\u2713": "OK",
         "\u03b8": "theta", "\u2605": "*", "\u25c0": "<", "\u25b6": ">", "\u25b2": "^",
         "\u25bc": "v", "\u25ba": ">"}

def ascii_prose(t):
    if UNICODE_SANS:
        return t
    return force_ascii(t)

def force_ascii(t):
    for k, v in PROSE.items():
        t = t.replace(k, v)
    return t


class Doc(BaseDocTemplate):
    def __init__(self, path, meta):
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=20*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=16*mm,
                                 title="Zynith Shell — Technical Report", author="M.S.Adhitya")
        self.meta = meta
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="body", frames=[frame], onPage=self.decorate)])

    def decorate(self, canv, doc):
        canv.saveState()
        if doc.page > 1:
            canv.setFont("Helvetica", 7.2); canv.setFillColor(MUTE)
            canv.drawString(20*mm, A4[1]-12*mm, "Zynith Shell — Technical Report")
            canv.drawRightString(A4[0]-18*mm, A4[1]-12*mm,
                                 f"v{self.meta['documentation_version']} · commit {self.meta['source_commit']}")
            canv.setStrokeColor(GRID); canv.setLineWidth(0.4)
            canv.line(20*mm, A4[1]-14*mm, A4[0]-18*mm, A4[1]-14*mm)
            canv.drawCentredString(A4[0]/2, 10*mm, str(doc.page))
        canv.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            st = flowable.style.name
            if st in ("h1", "h2"):
                self.notify("TOCEntry", (0 if st == "h1" else 1, flowable.getPlainText(), self.page))

def table(rows, width):
    cols = max(len(r) for r in rows)
    data = []
    for ri, row in enumerate(rows):
        cells = []
        for ci in range(cols):
            txt = esc(row[ci]) if ci < len(row) else ""
            cells.append(Paragraph(txt, CELLH if ri == 0 else CELL))
        data.append(cells)
    cw = [width/cols]*cols
    t = Table(data, colWidths=cw, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, BG]),
        ("GRID", (0,0), (-1,-1), 0.35, GRID),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    return t

def main():
    meta = C.meta()
    out = os.path.join(C.ROOT, "99_Reports", "generated", "ZynithShell-Technical-Report.pdf")
    doc = Doc(out, meta)
    W = doc.width
    story = []

    # cover
    story += [Spacer(1, 55*mm),
              Paragraph('<font size="34" color="#304fd6"><b>ZYNITH SHELL</b></font>',
                        S("cover", alignment=TA_CENTER, fontSize=34, leading=40)),
              Spacer(1, 4*mm),
              Paragraph("An Engineering Record",
                        S("sub", alignment=TA_CENTER, fontSize=13, leading=17)),
              Paragraph("Fedora 44 · niri 26.04 · patched Noctalia 5.1.0",
                        S("sub2", alignment=TA_CENTER, fontSize=10, textColor=MUTE)),
              Spacer(1, 14*mm)]
    info = [["Documentation version", meta["documentation_version"]],
            ["Generated", meta["generated"]],
            ["Source commit", meta["source_commit"]],
            ["Last audited phase", str(meta["last_audited_phase"])],
            ["Machine", meta["machine"]["cpu"]],
            ["GPU / display", meta["machine"]["gpu"] + " · " + meta["machine"]["display"]],
            ["OS / kernel", meta["machine"]["os"] + " · " + meta["machine"]["kernel"]],
            ["Author", "M.S.Adhitya"],
            ["Engineering assistant", "Claude Code (Anthropic)"]]
    story += [table([["Field", "Value"]] + info, W*0.8),
              Spacer(1, 10*mm),
              Paragraph(C.FOREWORD, S("fw", alignment=TA_LEFT, fontSize=9, leading=13.5, textColor=MUTE)),
              PageBreak()]

    # toc
    toc = TableOfContents()
    toc.levelStyles = [S("toc1", fontName="Helvetica-Bold", fontSize=10, leading=15, spaceBefore=5),
                       S("toc2", fontSize=9, leading=12.5, leftIndent=12, textColor=MUTE)]
    story += [Paragraph("Contents", H1), toc, PageBreak()]

    fig_n = [0]; tab_n = [0]
    def figure(rel, cap):
        png = os.path.join(C.ROOT, rel.replace(".svg", ".png"))
        if not os.path.exists(png): return
        from PIL import Image as PILImage
        try:
            iw, ih = PILImage.open(png).size
        except Exception:
            iw, ih = 1200, 700
        w = min(W, 165*mm); h = w * ih / iw
        if h > 195*mm:
            h = 195*mm; w = h * iw / ih
        fig_n[0] += 1
        story.append(KeepTogether([Image(png, width=w, height=h),
                                   Paragraph(f"Figure {fig_n[0]}. {esc(cap)}", CAP)]))

    for section, files in C.REPORT:
        story.append(Paragraph(esc(section), H1))
        for path in files:
            if not os.path.exists(os.path.join(C.ROOT, path)): continue
            first = True
            for b in C.blocks(path):
                k = b[0]
                if k == "h":
                    lvl = b[1]
                    st = H2 if (first and lvl == 1) else {1: H2, 2: H3, 3: H4}.get(lvl, H4)
                    story.append(Paragraph(esc(b[2]), st)); first = False
                elif k == "p":
                    story.append(Paragraph(esc(b[1]), BODY))
                elif k == "li":
                    story.append(Paragraph(esc(b[1]), BULLET, bulletText="\u2022"))
                elif k == "oli":
                    story.append(Paragraph(esc(b[2]), BULLET, bulletText=b[1] + "."))
                elif k == "quote":
                    story.append(Paragraph(esc(b[1]), QUOTE))
                elif k == "code":
                    for chunk in b[1].split("\n\n"):
                        story.append(Paragraph(ascii_art(esc(chunk)).replace("\n", "<br/>"), CODE))
                elif k == "table":
                    tab_n[0] += 1
                    story.append(table(b[1], W))
                    story.append(Paragraph(f"Table {tab_n[0]}", CAP))
        if section == "Architecture":
            for rel, cap in C.FIGURES[:5]: figure(rel, cap)
        if section == "Performance Engineering":
            for rel, cap in C.FIGURES[5:]: figure(rel, cap)
        story.append(PageBreak())

    story.append(Paragraph("Appendix — Interface", H1))
    for fn, cap in C.SHOTS:
        figure(os.path.join("07_Assets", "screenshots", fn), cap)

    doc.multiBuild(story)
    print("PDF written:", out, f"({fig_n[0]} figures, {tab_n[0]} tables)")

if __name__ == "__main__":
    main()
