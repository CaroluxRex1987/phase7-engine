#!/usr/bin/env python3
"""
Builds the Phase-7 Documentation & Change-Log Standard PDF.
A standalone practical companion to the Engineering Constitution — explains
Viktor's own record-keeping concern (documented, certified product, not
snake oil) and gives him a working Change Impact Record standard to start
using immediately. Deliberately NOT an edit to the Constitution itself.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

OUTPUT_PATH = "/tmp/outputs/Phase7_Documentation_and_Change_Log_Standard.pdf"

# ============================================================
# STYLES (shared house style, consistent with the Constitution family)
# ============================================================

styles = getSampleStyleSheet()

NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
LIGHT_BG = colors.HexColor("#f3f6fa")
GREEN = colors.HexColor("#1e7d32")
AMBER = colors.HexColor("#b06f00")
GREY = colors.HexColor("#5a5a5a")
MAROON = colors.HexColor("#8a2f2f")

styles.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=23,
    leading=28, textColor=NAVY, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="ReportSubtitle", fontName="Helvetica", fontSize=12.5,
    leading=17, textColor=STEEL, spaceAfter=4))
styles.add(ParagraphStyle(name="MetaLine", fontName="Helvetica", fontSize=10,
    leading=14, textColor=GREY, spaceAfter=2))
styles.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=16.5,
    leading=21, textColor=NAVY, spaceBefore=20, spaceAfter=10))
styles.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=12.3,
    leading=16, textColor=STEEL, spaceBefore=13, spaceAfter=6))
styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9.8,
    leading=14.3, textColor=colors.HexColor("#222222"), spaceAfter=7, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="BodySmall", fontName="Helvetica", fontSize=8.7,
    leading=12.5, textColor=colors.HexColor("#333333"), spaceAfter=5))
styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.3,
    leading=11.8, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="CellBold", parent=styles["Cell"], fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CellHeader", fontName="Helvetica-Bold", fontSize=8.6,
    leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Oblique", fontSize=9.3,
    leading=13.5, textColor=STEEL, spaceBefore=4, spaceAfter=8, leftIndent=14))
styles.add(ParagraphStyle(name="TOCItem", fontName="Helvetica", fontSize=10.3,
    leading=18, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="ItemLabel", fontName="Helvetica-Bold", fontSize=8.3,
    leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="TagText", fontName="Helvetica-Bold", fontSize=7.6,
    leading=10, textColor=colors.white, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="Directive", fontName="Helvetica-Bold", fontSize=12,
    leading=17, textColor=colors.white, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="DirectiveLabel", fontName="Helvetica-Bold", fontSize=8.5,
    leading=11, textColor=colors.HexColor("#b7c4da"), alignment=TA_LEFT))

def P(text, style="Body"):
    return Paragraph(text, styles[style])

def cell(text, header=False, bold=False):
    if header:
        return Paragraph(text, styles["CellHeader"])
    if bold:
        return Paragraph(text, styles["CellBold"])
    return Paragraph(text, styles["Cell"])

def wrap_table(rows):
    wrapped = []
    for r_idx, row in enumerate(rows):
        wrapped_row = []
        for c_idx, val in enumerate(row):
            if isinstance(val, Paragraph):
                wrapped_row.append(val)
            elif r_idx == 0:
                wrapped_row.append(cell(str(val), header=True))
            else:
                wrapped_row.append(cell(str(val), bold=(c_idx == 0)))
        wrapped.append(wrapped_row)
    return wrapped

row_style = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("FONTSIZE", (0, 0), (-1, -1), 8.1),
])

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = LETTER
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Documentation & Change-Log Standard — v1.0")
    canvas_obj.drawRightString(width - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas_obj.setStrokeColor(colors.HexColor("#d5dbe3"))
    canvas_obj.line(0.75 * inch, 0.72 * inch, width - 0.75 * inch, 0.72 * inch)
    canvas_obj.restoreState()

def section_header(title, intro_text):
    return [KeepTogether([P(title, "H1"), P(intro_text, "Body")])]

def verdict_box(number, title, body_text, tag_text, accent_color):
    data = [[
        Paragraph(f"{number}", styles["ItemLabel"]),
        Paragraph(f"<b>{title}</b>", ParagraphStyle(
            name=f"VTitle{number}", fontName="Helvetica-Bold",
            fontSize=10, textColor=colors.white, leading=13)),
        Paragraph(tag_text, styles["TagText"]),
    ]]
    t = Table(data, colWidths=[0.42 * inch, 4.28 * inch, 1.8 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, -1), NAVY),
        ("BACKGROUND", (2, 0), (2, -1), accent_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 0), (2, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, 0), 10), ("LEFTPADDING", (1, 0), (1, 0), 4),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
    ]))
    body = P(body_text, "Body")
    return [KeepTogether([t, Spacer(1, 4), body, Spacer(1, 8)])]

# ============================================================
# ASSEMBLY
# ============================================================

story = []

# ---------- TITLE PAGE ----------
story.append(Spacer(1, 1.2 * inch))
story.append(P("The Phase-7 Documentation &amp; Change-Log Standard", "ReportTitle"))
story.append(P("A Practical Companion to the Engineering Constitution — Recording What Changed, "
    "What It Did to the Engine, and Whether It Was Progress", "ReportSubtitle"))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1.2, color=STEEL))
story.append(Spacer(1, 14))
story.append(P("Status: <b>Working Standard, v1.0 — in effect immediately</b>", "MetaLine"))
story.append(P("Date: <b>August 25, 2026</b>", "MetaLine"))
story.append(P("Relationship to the Constitution: <b>a separate, practical companion document — "
    "not an edit to the Constitution's frozen 17 / 7 / 10 / 6 rules</b>. See the closing section "
    "for exactly why that distinction is being kept.", "MetaLine"))
story.append(Spacer(1, 24))
story.append(P(
    "<i>“I do not want to sell snake oil. I want to sell a documented and certified good "
    "product, as good as it can be for its specific purpose.”</i> — Viktor, on why this "
    "document exists.", "Callout"
))
story.append(PageBreak())

# ---------- CONTENTS ----------
story.append(P("Contents", "H1"))
toc_items = [
    "Why This Document Exists",
    "What the Constitution Already Requires — and Where It Stops",
    "The Change Impact Record",
    "The Record-Keeping Standard",
    "Worked Example: The Confidence-Score Rename",
    "Template — Start Using This Today",
    "How This Feeds a Future Customer-Facing Disclosure",
    "Relationship to the Constitution",
    "Version History",
]
for item in toc_items:
    story.append(P(item, "TOCItem"))
story.append(PageBreak())

# ---------- WHY THIS EXISTS ----------
story.extend(section_header("Why This Document Exists",
    "This document exists because of one message. Viktor pointed out that if Phase-7 is ever "
    "sold to real customers — even at a low, accessible price — it can't be sold on confidence "
    "alone. It has to be sold on evidence: a documented, certified product, as good as it can "
    "be for its specific purpose, not something dressed up to look more capable than it's been "
    "shown to be."
))
story.append(P(
    "That's a business concern and an engineering concern at the same time, and they turn out "
    "to require the same thing: a habit of recording, for every meaningful change to the "
    "engine, what changed, why, what effect it actually had once measured, and whether that "
    "effect was progress, regression, or still unclear. Not a memory of that — a written "
    "record. This document defines exactly what that record looks like and starts it today.", "Body"
))

# ---------- WHAT THE CONSTITUTION ALREADY COVERS ----------
story.extend(section_header("What the Constitution Already Requires — and Where It Stops",
    "The Engineering Constitution already asks for most of the raw ingredients here. It's worth "
    "being precise about what's already covered before describing what's missing — the gap is "
    "real, but it's narrower than it might first sound."
))
covered_rows = [
    ["Already required by the Constitution", "What it covers"],
    ["Traceability (Tier 1, Item 6)", "Any output must be explainable, step by step, back to "
     "the raw data that produced it."],
    ["Reproducibility (Tier 1, Item 5)", "Any past result should be reconstructable later — "
     "same data, same code version, same configuration."],
    ["Documentation of significant decisions (Tier 3)", "Why a change was made, not just what "
     "changed — usually as a short Architectural Decision Record."],
    ["Fixed evaluation datasets (Tier 3)", "A stable dataset changes get measured against, so "
     "“better” and “worse” mean the same thing from one change to the next."],
    ["Hypothesis-driven development (Tier 3)", "Every change already has a measurement and an "
     "evaluation step built into its process, before it's accepted or rejected."],
    ["Regression tests &amp; known-good checkpoints (Tier 3)", "A change isn't allowed to "
     "silently destroy something that used to work, and every major version stays recoverable."],
]
tc = Table(wrap_table(covered_rows), colWidths=[2.5 * inch, 4.0 * inch])
tc.setStyle(row_style)
story.append(tc)
story.append(Spacer(1, 8))
story.append(P(
    "Taken together, these already mean the engine is <i>supposed to</i> be measured and "
    "documented at every change. What's missing is narrower: none of these require that record "
    "to live anywhere as one running, referenceable log. Right now, the evidence that a given "
    "change helped, hurt, or did nothing measurable could exist only in a chat history, a "
    "memory, or nowhere at all. That's the specific gap this document closes — not by adding a "
    "new rule to the Constitution today, but by starting the practice now.", "Body"
))

# ---------- THE CHANGE IMPACT RECORD ----------
story.extend(section_header("The Change Impact Record",
    "A Change Impact Record is a short, dated entry created every time something meaningful "
    "changes about the engine — closing the loop between “we made a change” and “here's "
    "what actually happened, measured.”"
))
story.append(P(
    "It's a close cousin of an Architectural Decision Record, but answers a different "
    "question. An ADR records the decision — what was decided, and why, at the moment the "
    "change was made. A Change Impact Record records the outcome — what was actually observed "
    "once the change existed, checked against a fixed dataset, and given an honest verdict. A "
    "significant change deserves both: the reasoning going in, and the evidence coming out.", "Body"
))
story.append(P(
    "The four verdict categories below are deliberately built the same way the Constitution "
    "already treats audit findings: real categories, including one that means “we don't know "
    "yet,” because guessing at a verdict would violate the same epistemic honesty the "
    "Constitution already requires of the engine itself.", "Body"
))

story.extend(verdict_box(1, "Improvement",
    "The change was measured against the fixed evaluation dataset (or otherwise verified) and "
    "produced a better, more reliable, or more correct result than before — with the evidence "
    "attached, not just the impression that it went well.", "IMPROVEMENT", GREEN))
story.extend(verdict_box(2, "Regression",
    "The change made something measurably worse — even if it fixed the thing it was meant to "
    "fix. A regression isn't a failure to hide; it's exactly the kind of finding this log "
    "exists to catch before it reaches a customer.", "REGRESSION", MAROON))
story.extend(verdict_box(3, "Neutral / No Measurable Effect",
    "The change did what it was supposed to do without making anything measurably better or "
    "worse — a legitimate, common outcome, especially for refactors, cleanups, or safety "
    "changes that aren't meant to move a metric.", "NEUTRAL", STEEL))
story.extend(verdict_box(4, "Not Yet Measurable",
    "The honest answer when there isn't yet enough data, time, or a suitable test to know the "
    "effect. This is not a placeholder for laziness — it's the same “Unknown” principle the "
    "Constitution already uses for audit findings, applied here to change impact.", "NOT YET", AMBER))

# ---------- THE RECORD-KEEPING STANDARD ----------
story.extend(section_header("The Record-Keeping Standard",
    "Every Change Impact Record should carry the same fields, so entries stay comparable to "
    "each other over the life of the project — the same reasoning behind the audit-finding "
    "structure already used in the Constitution's Next Steps section."
))
schema_rows = [
    ["Field", "What goes here"],
    ["Date &amp; Change ID", "When the change happened, and a short reference id so it can be "
     "cited elsewhere (a bug report, a future audit finding, a customer-facing claim)."],
    ["What changed", "A plain description — one or two sentences, no jargon required."],
    ["Why", "The reasoning behind the change. Link to the ADR if one exists for this change."],
    ["Affected module(s)", "Which part of the engine this touched — helps a future reader (or "
     "audit) understand blast radius."],
    ["How it was measured", "Which fixed dataset, test, or comparison was used to check the "
     "effect. “I ran it and it looked fine” is not a measurement."],
    ["Before / after comparison", "The actual numbers, behavior, or output difference observed "
     "— the evidence itself, not a summary of it."],
    ["Verdict", "Improvement / Regression / Neutral / Not Yet Measurable — one of the four, "
     "chosen honestly, not the one that reads best."],
    ["Notes", "Anything else worth knowing later — surprises, caveats, follow-up needed."],
]
ts = Table(wrap_table(schema_rows), colWidths=[1.7 * inch, 4.8 * inch])
ts.setStyle(row_style)
story.append(ts)
story.append(Spacer(1, 8))
story.append(P(
    "<b>When an entry is required:</b> anything that could plausibly affect what the engine "
    "outputs — a new indicator, a model tweak, a bug fix, a changed default, a reworked "
    "calculation. Formatting, comments, and other changes with no behavioral effect don't need "
    "an entry — the standard is “could this change what a customer would see,” not “did a "
    "file change.”", "Body"
))

# ---------- WORKED EXAMPLE ----------
story.extend(section_header("Worked Example: The Confidence-Score Rename",
    "The Constitution already references a real incident from this project's history: a code "
    "path silently renamed confidence_score to confidence, and the mismatch broke fourteen "
    "downstream modules before it was caught. Here's what a Change Impact Record for that "
    "change would have looked like, had this standard existed at the time — reconstructed here "
    "for illustration, not as a claim about exactly how or when it was actually caught."
))
example_rows = [
    ["Field", "Entry"],
    ["Date / Change ID", "(illustrative) — CHG-EXAMPLE-01"],
    ["What changed", "A code path's output field was renamed from confidence_score to "
     "confidence."],
    ["Why", "Naming cleanup, intended to be purely cosmetic."],
    ["Affected module(s)", "The renaming module, plus every downstream module reading the old "
     "field name."],
    ["How it was measured", "Not measured before merging — this is precisely the gap that let "
     "the break happen silently."],
    ["Before / after comparison", "Fourteen downstream modules began silently reading a missing "
     "or mismatched field."],
    ["Verdict", "Regression — severe. Would have been caught immediately had a Change Impact "
     "Record been required before the change was considered complete."],
]
te = Table(wrap_table(example_rows), colWidths=[1.7 * inch, 4.8 * inch])
te.setStyle(row_style)
story.append(te)
story.append(Spacer(1, 8))
story.append(P(
    "This is exactly the kind of finding the standard exists to surface early rather than "
    "after the fact — and it's also why Tier 2 of the Constitution already contains a rule "
    "(“explicit, evaluated changes to interfaces or behavior”) written in direct response "
    "to this same incident. The two documents are reinforcing the same lesson from two "
    "different angles.", "Body"
))

# ---------- TEMPLATE ----------
story.extend(section_header("Template — Start Using This Today",
    "A blank Change Impact Record, ready to copy for the next meaningful change made to the "
    "engine. No tooling required to start — a plain text file or spreadsheet row is enough; "
    "what matters is that it exists and gets filled in honestly."
))
template_rows = [
    ["Field", "Entry"],
    ["Date / Change ID", "—"],
    ["What changed", "—"],
    ["Why", "—"],
    ["Affected module(s)", "—"],
    ["How it was measured", "—"],
    ["Before / after comparison", "—"],
    ["Verdict", "Improvement / Regression / Neutral / Not Yet Measurable"],
    ["Notes", "—"],
]
tt = Table(wrap_table(template_rows), colWidths=[1.7 * inch, 4.8 * inch])
tt.setStyle(row_style)
story.append(tt)

# ---------- FUTURE DISCLOSURE ----------
story.extend(section_header("How This Feeds a Future Customer-Facing Disclosure",
    "This is the point that connects the practice directly back to the reason Viktor raised it "
    "in the first place."
))
story.append(P(
    "When it's time to write the document a future customer would actually read — something "
    "explaining what the engine does, how it does it, and how it was validated — every claim "
    "in that document should be able to point to something. Not “it works well,” but “here's "
    "the dated record showing what changed, how it was tested, and what the measured effect "
    "was.” A product described this way isn't snake oil, because the description isn't the "
    "only evidence for itself — there's a trail behind it. That trail is exactly what a running "
    "set of Change Impact Records becomes, almost as a side effect of just keeping honest "
    "records along the way.", "Body"
))
story.append(P(
    "This also means the customer-facing disclosure document, whenever it gets built, doesn't "
    "have to be written from memory or reconstructed after the fact. It gets pulled from this "
    "log — which is a much stronger position to sell from than trying to recall, months later, "
    "what was actually tested and what wasn't.", "Body"
))

# ---------- RELATIONSHIP TO THE CONSTITUTION ----------
story.extend(section_header("Relationship to the Constitution",
    "Worth stating plainly, since the Constitution and this document sit right next to each "
    "other in purpose."
))
story.append(P(
    "This standard is deliberately <b>not</b> an edit to the Engineering Constitution. The "
    "Constitution's scope — 17 Tier 1 invariants, 7 Tier 2 principles, 10 Tier 3 process items, "
    "6 Tier 4 preferences — is frozen, on purpose, until the audit described in its Next Steps "
    "section actually runs. Adding a new rule to that document right now, even a good one, "
    "would break the exact discipline the Constitution's own “Scope Freeze” section exists to "
    "protect. Viktor's own instruction when this came up was explicit: this doesn't need to go "
    "into the Constitution right now.", "Body"
))
story.append(P(
    "What this document does instead is operationalize principles the Constitution already "
    "contains — Traceability, Reproducibility, Documentation of Significant Decisions, Fixed "
    "Evaluation Datasets — into one concrete, usable habit, starting immediately, without "
    "touching the frozen document at all. If it proves useful in practice, formalizing "
    "“Change Impact Logging” as an actual Tier 3 item is a natural, well-evidenced candidate "
    "for consideration once the audit runs and the freeze is revisited — but that's a decision "
    "for later, made with real experience behind it rather than as a guess made today.", "Body"
))

# ---------- VERSION HISTORY ----------
story.append(P("Version History", "H1"))
version_rows = [
    ["Version", "Date", "Status", "Notes"],
    ["v1.0", "August 25, 2026", "Working standard — in effect immediately",
     "Initial version, written directly from Viktor's stated concern about selling a "
     "documented, certified product rather than an undocumented one. Not part of the "
     "Constitution's frozen scope; usable starting today."],
]
tv = Table(wrap_table(version_rows), colWidths=[0.8 * inch, 1.3 * inch, 2.0 * inch, 2.4 * inch])
tv.setStyle(row_style)
story.append(tv)
story.append(Spacer(1, 10))
story.append(P(
    "<i>This document is a working tool, not a governing one — it can be revised freely as the "
    "practice of using it reveals what works and what doesn't. The one thing worth keeping "
    "constant is the reason it exists: an engine sold honestly needs a paper trail, not just a "
    "pitch.</i>", "Callout"
))

# ============================================================
# BUILD
# ============================================================

doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=LETTER,
    topMargin=0.85 * inch, bottomMargin=0.9 * inch,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    title="Phase-7 Documentation & Change-Log Standard",
    author="Claude (Cowork), with Viktor",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Wrote {OUTPUT_PATH}")
