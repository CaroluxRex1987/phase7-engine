#!/usr/bin/env python3
"""
Bundles all four raw audit outputs into one PDF, verbatim.

Exists because the four findings files are markdown, and markdown downloads
have been unreliable on Viktor's end while PDFs have worked throughout. One
attachment instead of four, in a format that reliably opens.

Content is unedited. Only the container changes.
"""

import re, html
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)

OUT = "/tmp/outputs/Phase7_Audit_Findings_Complete.pdf"
SRC = "/tmp/outputs/audit_raw"

FILES = [
    ("Run 1 — DeepSeek V4 Pro", "Blind review: source code only, no Constitution, no register",
     f"{SRC}/Run1_DeepSeek_blind_review.md"),
    ("Run A — Kimi K3", "Minimum Viable Audit gate: Items 2, 3, 6, 18, plus the DEFECT resolution",
     f"{SRC}/RunA_KimiK3_MVA_gate_findings.md"),
    ("Run B — Kimi K3", "Remaining Tier 1 invariants: Items 1, 4, 5, 7–17, 19–21",
     f"{SRC}/RunB_KimiK3_tier1_findings.md"),
    ("Run C — Kimi K3", "Tiers 2, 3 and 4: 7 architectural, 10 process, 6 preferences",
     f"{SRC}/RunC_KimiK3_tiers234_findings.md"),
]

styles = getSampleStyleSheet()
NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
GREY = colors.HexColor("#5a5a5a")
LIGHT_BG = colors.HexColor("#f3f6fa")

styles.add(ParagraphStyle(name="RTitle", fontName="Helvetica-Bold", fontSize=22,
    leading=27, textColor=NAVY, spaceAfter=6))
styles.add(ParagraphStyle(name="RSub", fontName="Helvetica", fontSize=12.5,
    leading=17, textColor=STEEL, spaceAfter=4))
styles.add(ParagraphStyle(name="Meta", fontName="Helvetica", fontSize=10,
    leading=14, textColor=GREY, spaceAfter=2))
styles.add(ParagraphStyle(name="RunTitle", fontName="Helvetica-Bold", fontSize=18,
    leading=23, textColor=NAVY, spaceBefore=4, spaceAfter=4))
styles.add(ParagraphStyle(name="H1x", fontName="Helvetica-Bold", fontSize=14,
    leading=18, textColor=NAVY, spaceBefore=14, spaceAfter=7))
styles.add(ParagraphStyle(name="H2x", fontName="Helvetica-Bold", fontSize=11.5,
    leading=15, textColor=STEEL, spaceBefore=11, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", fontName="Helvetica", fontSize=9.3,
    leading=13.2, textColor=colors.HexColor("#222222"), spaceAfter=5, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Bul", fontName="Helvetica", fontSize=9.3,
    leading=13.2, textColor=colors.HexColor("#222222"), spaceAfter=3,
    leftIndent=14, bulletIndent=4))
styles.add(ParagraphStyle(name="Codex", fontName="Courier", fontSize=8.2,
    leading=11, textColor=colors.HexColor("#1a1a1a"), leftIndent=10,
    backColor=colors.HexColor("#f7f8fa"), spaceBefore=3, spaceAfter=5))


def inline(s):
    """Minimal markdown inline -> reportlab markup, escaping everything else."""
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8.6">\1</font>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", s)
    return s


def render(md):
    flow, in_code, buf = [], False, []
    for raw in md.split("\n"):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            if in_code:
                if buf:
                    flow.append(Paragraph("<br/>".join(
                        html.escape(b, quote=False).replace(" ", "&nbsp;") for b in buf), styles["Codex"]))
                buf, in_code = [], False
            else:
                in_code = True
            continue
        if in_code:
            buf.append(line)
            continue
        if not line.strip():
            continue
        if line.startswith("### "):
            flow.append(Paragraph(inline(line[4:]), styles["H2x"]))
        elif line.startswith("## "):
            flow.append(Paragraph(inline(line[3:]), styles["H1x"]))
        elif line.startswith("# "):
            flow.append(Paragraph(inline(line[2:]), styles["H1x"]))
        elif line.strip() in ("---", "***", "___"):
            flow.append(Spacer(1, 4))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#d5dbe3")))
            flow.append(Spacer(1, 4))
        elif re.match(r"^\s*[-*]\s+", line):
            depth = (len(line) - len(line.lstrip())) // 2
            txt = re.sub(r"^\s*[-*]\s+", "", line)
            st = ParagraphStyle(name=f"b{depth}", parent=styles["Bul"],
                                leftIndent=14 + depth * 12, bulletIndent=4 + depth * 12)
            flow.append(Paragraph(inline(txt), st, bulletText="•"))
        elif re.match(r"^\s*\d+\.\s+", line):
            flow.append(Paragraph(inline(line.strip()), styles["Bul"]))
        elif line.startswith("|"):
            flow.append(Paragraph(inline(line.strip("|").replace("|", " · ")), styles["Bodyx"]))
        else:
            flow.append(Paragraph(inline(line), styles["Bodyx"]))
    return flow


def on_page(c, doc):
    c.saveState()
    w, _ = LETTER
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Audit Findings — complete record")
    c.drawRightString(w - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    c.setStrokeColor(colors.HexColor("#d5dbe3"))
    c.line(0.75 * inch, 0.72 * inch, w - 0.75 * inch, 0.72 * inch)
    c.restoreState()


story = [
    Paragraph("Phase-7 Structural Quant Engine", styles["RSub"]),
    Paragraph("Audit Findings — Complete Record", styles["RTitle"]),
    Paragraph("Four independent runs, August 27, 2026. Verbatim auditor output.", styles["Meta"]),
    Spacer(1, 12),
    HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")),
    Spacer(1, 12),
]

note = Table([[[
    Paragraph("<b>What this document is.</b>", styles["H2x"]),
    Paragraph("The unedited output of four audit runs, collected into one file. Nothing has "
              "been summarised, reordered or corrected — including the places where an auditor "
              "was later shown to be wrong, and the places where it caught Claude being wrong. "
              "Together these cover all 44 rules of the register: 21 Compliant, 17 "
              "Non-compliant, 6 Unknown, with three findings rated Critical.", styles["Bodyx"]),
    Paragraph("Claude's verification of these findings against the real source is recorded "
              "separately, in Engineering Notes entries #22 and #24 through #27. It is "
              "deliberately not included here.", styles["Bodyx"]),
]]], colWidths=[6.5 * inch])
note.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1.1, STEEL),
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
    ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
]))
story.append(note)

for title, sub, path in FILES:
    story.append(PageBreak())
    story.append(Paragraph(title, styles["RunTitle"]))
    story.append(Paragraph(sub, styles["Meta"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")))
    story.append(Spacer(1, 8))
    md = open(path, encoding="utf-8").read()
    md = re.sub(r"\A#[^\n]*\n", "", md)          # drop my added file header
    md = re.sub(r"\A(.*?\n)---\n", "", md, flags=re.S)
    story.extend(render(md))

doc = SimpleDocTemplate(OUT, pagesize=LETTER,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.85 * inch,
    title="Phase-7 Audit Findings — Complete Record")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Built: {OUT}")
