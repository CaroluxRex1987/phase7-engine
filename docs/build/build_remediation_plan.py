#!/usr/bin/env python3
"""
Builds the Step 5 remediation plan — GLM 5.3's sequence, verbatim, preceded by
Claude's verification record.

The plan itself is unedited. What is added in front of it is the list of which
of its claims were checked against real source and what happened, because the
Constitution's Evidence discipline says a finding is only as good as what can be
checked without re-running the reasoning that produced it.
"""

import re, html
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    HRFlowable, KeepTogether
)

OUT = "/tmp/outputs/Phase7_Remediation_Plan.pdf"
SRC = "/tmp/outputs/audit_raw/Step5_GLM53_remediation_sequence.md"

styles = getSampleStyleSheet()
NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
GREY = colors.HexColor("#5a5a5a")
GREEN = colors.HexColor("#1e7d32")
MAROON = colors.HexColor("#8a2f2f")
LIGHT_BG = colors.HexColor("#f3f6fa")

styles.add(ParagraphStyle(name="RTitle", fontName="Helvetica-Bold", fontSize=22,
    leading=27, textColor=NAVY, spaceAfter=6))
styles.add(ParagraphStyle(name="RSub", fontName="Helvetica", fontSize=12.5,
    leading=17, textColor=STEEL, spaceAfter=4))
styles.add(ParagraphStyle(name="Meta", fontName="Helvetica", fontSize=10,
    leading=14, textColor=GREY, spaceAfter=2))
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
styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.2,
    leading=11.4, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="CellHeader", fontName="Helvetica-Bold", fontSize=8.3,
    leading=10.5, textColor=colors.white))


def cell(text, header=False):
    return Paragraph(text, styles["CellHeader" if header else "Cell"])


def box(paragraphs, border_color=STEEL, bg=LIGHT_BG):
    t = Table([[paragraphs]], colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.1, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return [t, Spacer(1, 10)]


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r'<font face="Courier" size="8.6">\1</font>', s)
    # Bold must tolerate italics nested inside it. Eight of the sixteen item
    # headings are of the form **Title *(qualifier)*** — three trailing
    # asterisks, where the closing pair is the LAST two. A [^*]+ body cannot
    # match those, and a plain .+? closes on the first two, orphaning an
    # asterisk. The negative lookahead forces the close to the final pair.
    s = re.sub(r"\*\*(.+?)\*\*(?!\*)", r"<b>\1</b>", s)
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
                        html.escape(b, quote=False).replace(" ", "&nbsp;") for b in buf),
                        styles["Codex"]))
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
            flow.append(HRFlowable(width="100%", thickness=0.6,
                                   color=colors.HexColor("#d5dbe3")))
            flow.append(Spacer(1, 4))
        elif re.match(r"^\s*[-*]\s+", line):
            depth = (len(line) - len(line.lstrip())) // 2
            txt = re.sub(r"^\s*[-*]\s+", "", line)
            st = ParagraphStyle(name=f"b{depth}", parent=styles["Bul"],
                                leftIndent=14 + depth * 12, bulletIndent=4 + depth * 12)
            flow.append(Paragraph(inline(txt), st, bulletText="•"))
        elif re.match(r"^\s*\d+\.\s+", line):
            flow.append(Paragraph(inline(line.strip()), styles["Bul"]))
        else:
            flow.append(Paragraph(inline(line), styles["Bodyx"]))
    return flow


def on_page(c, doc):
    c.saveState()
    w, _ = LETTER
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Remediation Plan — Step 5")
    c.drawRightString(w - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    c.setStrokeColor(colors.HexColor("#d5dbe3"))
    c.line(0.75 * inch, 0.72 * inch, w - 0.75 * inch, 0.72 * inch)
    c.restoreState()


story = [
    Paragraph("Phase-7 Structural Quant Engine", styles["RSub"]),
    Paragraph("Remediation Plan", styles["RTitle"]),
    Paragraph("Step 5 of the audit sequence — “prioritise findings by severity and effort.”",
              styles["Meta"]),
    Paragraph("Produced by GLM 5.3 (z-ai/glm-5.3) on August 29, 2026. Verified by Claude the "
              "same day.", styles["Meta"]),
    Spacer(1, 12),
    HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")),
    Spacer(1, 12),
]

story.extend(box([
    Paragraph("<b>What this document is.</b>", styles["H2x"]),
    Paragraph("The unedited output of Step 5, preceded by the record of which of its claims "
              "were checked against real engine source and what those checks found. The plan "
              "is not summarised or reordered.", styles["Bodyx"]),
    Paragraph("It is a <b>plan</b>, not a finding. It changes no rule and grades no item. The "
              "adjudications it opens with are Viktor's, per Roles &amp; Authority, and two of "
              "them change the ordering — which is why they sit at position zero rather than "
              "being settled along the way.", styles["Bodyx"]),
    Paragraph("<b>There are five, not four.</b> Step 5's own Step 0 names four — Item 6's "
              "severity, Item 2's Compliant strength, Items 4/12, and the position-sizing "
              "question — and raises a fifth at item 9, the choice between halting and "
              "degrading on indicator failure. An earlier summary of this document by Claude "
              "listed four and dropped the position-sizing one, which propagated into Roadmap "
              "Revision 2. Corrected here and in Roadmap Revision 3. <i>The verbatim plan below "
              "was always right; the summary of it was not.</i>", styles["Bodyx"]),
]))

story.extend(box([
    Paragraph("<b>The reviewer, and what it had.</b>", styles["H2x"]),
    Paragraph("GLM 5.3 on OpenRouter — the pinned slug, deliberately not the "
              "<font face=\"Courier\">glm-latest</font> floating alias, which silently repoints "
              "when a successor ships and would make this document's record of which model "
              "produced what quietly false. Four attachments: the complete engine source, the "
              "frozen audit copy of the Constitution, all four audit runs, and the Engineering "
              "Notes.", styles["Bodyx"]),
    Paragraph("<b>Independence status:</b> GLM was clean on both the Constitution and source "
              "lists before this run. It no longer is. Luna Pro was considered and rejected for "
              "this step because it had already seen the Constitution during the hostile "
              "review. Still clean on both lists for the Step 8 re-audit: Meta, Mistral, Qwen, "
              "Cohere, Amazon, MiniMax.", styles["Bodyx"]),
], border_color=STEEL))

story.append(PageBreak())

# ============================================================
# VERIFICATION RECORD
# ============================================================
story.append(Paragraph("Verification record", styles["H1x"]))
story.append(Paragraph(
    "Every claim in the plan that could be checked against the real source was checked. Nine "
    "of nine held. This section exists because the Constitution's Evidence discipline requires "
    "a finding to be checkable without re-running the reasoning that produced it — and because "
    "this project has twice recorded Claude asserting something false about the source.",
    styles["Bodyx"]))

ver_rows = [
    ["The plan's claim", "Checked against source", "Result"],
    ["<font face='Courier'>requirements.txt</font> omits <font face='Courier'>requests</font> "
     "and <font face='Courier'>colorama</font>; declares <font face='Courier'>ccxt</font>, "
     "which nothing imports",
     "Manifest lists pandas, numpy, matplotlib, ccxt, pandas_ta. "
     "<font face='Courier'>requests</font> imported at line 1295, "
     "<font face='Courier'>colorama</font> at 1004. "
     "<font face='Courier'>ccxt</font> appears exactly once in the whole codebase — in the "
     "manifest itself.", "<b>Holds</b>"],
    ["The validator must sit before <font face='Courier'>close_time</font> is discarded",
     "Line 1369 defines the column in the raw response; line 1373 drops it. Staleness and "
     "last-candle-completeness checks need it, and nothing downstream ever sees it.",
     "<b>Holds</b> — and is the sharpest single observation in the plan"],
    ["<font face='Courier'>engine_version</font> exists in config and is written nowhere",
     "Defined at config line 260. Total occurrences in the source: one.", "<b>Holds</b>"],
    ["The indicator cache can never hit across runs",
     "Key at line 521 is symbol, timeframe, row count and last close, in a per-instance dict. "
     "Empty on every fresh process; a new bar produces a new key within one.",
     "<b>Holds</b> — deletion is therefore free"],
    ["mypy does not exist in the repository", "Zero occurrences.", "<b>Holds</b>"],
    ["Config declares chart height 10 and dpi 150; plotting hardcodes 8 and 200",
     "<font face='Courier'>CHART_HEIGHT = 10</font>, <font face='Courier'>CHART_DPI = 150</font> "
     "at config 356–357; <font face='Courier'>figsize=(14, 8)</font> at 4561 and "
     "<font face='Courier'>dpi=200</font> at 4743.", "<b>Holds</b>"],
    ["VWMA must stay — <font face='Courier'>entry_model</font> consumes it",
     "VWMA distance scoring at line 3094. Correctly excluded from the deletion list.",
     "<b>Holds</b>"],
    ["The <font face='Courier'>trend_failure</font> gate is dead",
     "<font face='Courier'>recent_struct == \"LH\"</font> is exact equality against a column "
     "whose values are full phrases such as “BEARISH SWING SEQUENCE (LH-LL)”. Never matches. "
     "Attributed by the plan to Run 1, which found it and described the mechanism correctly.",
     "<b>Holds</b>"],
    ["“23 commits and zero tags (checked)”",
     "Traced to the Engineering Notes, which record exactly that. A legitimate citation of "
     "supplied material, not a fabricated verification.", "<b>Holds</b>"],
]
data = [[cell(c, header=(i == 0)) for c in r] for i, r in enumerate(ver_rows)]
t = Table(data, colWidths=[1.95 * inch, 3.35 * inch, 1.2 * inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

story.append(Paragraph("Two things the verification found that the plan did not",
                       styles["H2x"]))
story.append(Paragraph(
    "<b>The dead-gate defect is a class, not an instance.</b> The codebase contains two comments "
    "acknowledging previous occurrences of the same shape — a gate comparing against a string "
    "literal no producer ever emits. One notes a check for "
    "<font face=\"Courier\">STRUCTURE_REGIME</font>, “which never existed”; the other notes that "
    "“BULLISH STRUCTURE” and “BEARISH STRUCTURE” “were never produced by anything.” Both were "
    "found and commented rather than turned into a check. That makes "
    "<font face=\"Courier\">trend_failure</font> the third instance, and argues for a "
    "class-level guard in the harness — assert that every string literal compared against a "
    "column belongs to that column's producible set — rather than a third individual repair.",
    styles["Bodyx"]))
story.append(Paragraph(
    "<b>A near-miss on Claude's side, recorded rather than tidied away.</b> Claude was one "
    "sentence from reporting that the plan understated the "
    "<font face=\"Courier\">trend_failure</font> fix, on the grounds that the "
    "<font face=\"Courier\">STRUCTURE</font> column is never assigned anywhere. It is — via a "
    "<font face=\"Courier\">.loc</font> form that the first search pattern did not match. That "
    "would have been the third false assertion of absence on this project, after the Layer 5 "
    "claim and the withdrawn accusation against Run A's auditor. An exhaustive re-search caught "
    "it before it reached Viktor. The plan's mechanism was right; the correction would have "
    "been wrong.", styles["Bodyx"]))

story.append(Spacer(1, 4))
story.extend(box([
    Paragraph("<b>One real discrepancy.</b>", styles["Bodyx"]),
    Paragraph("The plan says “the six logged runtime failure classes.” The runtime log holds "
              "seven distinct classes across nine occurrences. An undercount by one, immaterial "
              "to the sequence, recorded because unrecorded small errors are how large ones "
              "become invisible.", styles["Bodyx"]),
], border_color=MAROON))

story.append(Spacer(1, 4))
story.extend(box([
    Paragraph("<b>What verification cannot establish.</b>", styles["Bodyx"]),
    Paragraph("Every check above confirms that a claim about the source is true. None of them "
              "confirms that the <i>ordering</i> is right — that is a judgment, and it is "
              "reviewed by using the plan, not by grepping. The plan makes this point about "
              "itself: its own tests would prove a change matched its intention, never that the "
              "intention was correct. Only the independent re-audit at item 16 closes that gap.",
              styles["Bodyx"]),
], border_color=STEEL))

story.append(PageBreak())
story.append(Paragraph("The plan, verbatim", styles["H1x"]))
story.append(Paragraph(
    "Unedited from here to the end of the document, including its three self-flagged "
    "correlation warnings — the places where the reviewer notes that its own reasoning may "
    "share habits with the model family that built the engine.", styles["Meta"]))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")))
story.append(Spacer(1, 8))

md = open(SRC, encoding="utf-8").read()
story.extend(render(md))

doc = SimpleDocTemplate(OUT, pagesize=LETTER,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.85 * inch,
    title="Phase-7 Remediation Plan — Step 5",
    author="GLM 5.3, verified by Claude (Cowork)")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Built: {OUT}")
