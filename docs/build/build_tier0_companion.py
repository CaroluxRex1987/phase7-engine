#!/usr/bin/env python3
"""
Builds the Phase-7 Tier 0 Companion PDF.
A standalone philosophical document sitting above the Engineering
Constitution rather than inside its frozen scope. Organizes a
ten-question philosophical input Viktor brought into the project,
applies the input's own stated relevance test to each question, and
cross-references the ones that feed the Constitution back to their
specific Tier/Item or Future Amendment Candidate (added in Rev 4).
Not part of the Constitution's frozen scope, not ratified, not audited
the same way — a living reference document that can grow if more
philosophical material comes up later.
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

OUTPUT_PATH = "/tmp/outputs/Phase7_Tier0_Companion.pdf"

# ============================================================
# STYLES (shared house style, consistent with the rest of the family)
# ============================================================

styles = getSampleStyleSheet()

NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
STEEL_HEX = "#3d5a80"
LIGHT_BG = colors.HexColor("#f3f6fa")
GREEN = colors.HexColor("#1e7d32")
AMBER = colors.HexColor("#b06f00")
GREY = colors.HexColor("#5a5a5a")
MAROON = colors.HexColor("#8a2f2f")
PURPLE = colors.HexColor("#5b3d80")

styles.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=24,
    leading=29, textColor=NAVY, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="ReportSubtitle", fontName="Helvetica", fontSize=13,
    leading=17.5, textColor=STEEL, spaceAfter=4))
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
styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.5,
    leading=12, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="CellBold", parent=styles["Cell"], fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CellHeader", fontName="Helvetica-Bold", fontSize=8.8,
    leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Oblique", fontSize=9.3,
    leading=13.5, textColor=STEEL, spaceBefore=4, spaceAfter=8, leftIndent=14))
styles.add(ParagraphStyle(name="TOCItem", fontName="Helvetica", fontSize=10.3,
    leading=18, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="ItemLabel", fontName="Helvetica-Bold", fontSize=8.3,
    leading=11, textColor=colors.white))
styles.add(ParagraphStyle(name="TagText", fontName="Helvetica-Bold", fontSize=7.6,
    leading=10, textColor=colors.white, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="Directive", fontName="Helvetica-Bold", fontSize=12.5,
    leading=18, textColor=colors.white, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="DirectiveLabel", fontName="Helvetica-Bold", fontSize=8.5,
    leading=11, textColor=colors.HexColor("#b7c4da"), alignment=TA_LEFT))
styles.add(ParagraphStyle(name="QuestionText", fontName="Helvetica-Oblique", fontSize=10.5,
    leading=15, textColor=NAVY, spaceAfter=6))
styles.add(ParagraphStyle(name="FeedsInto", fontName="Helvetica-Bold", fontSize=8.3,
    leading=12, textColor=STEEL, spaceBefore=2))

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
    ("FONTSIZE", (0, 0), (-1, -1), 8.2),
])

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = LETTER
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Tier 0 Companion")
    canvas_obj.drawRightString(width - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas_obj.setStrokeColor(colors.HexColor("#d5dbe3"))
    canvas_obj.line(0.75 * inch, 0.72 * inch, width - 0.75 * inch, 0.72 * inch)
    canvas_obj.restoreState()

def section_header(title, intro_text):
    return [KeepTogether([P(title, "H1"), P(intro_text, "Body")])]

def question_box(number, title, question_text, body_text, feeds_into_text, tag_text, accent_color):
    data = [[
        Paragraph(f"{number}", styles["ItemLabel"]),
        Paragraph(f"<b>{title}</b>", ParagraphStyle(
            name=f"QTitle{number}", fontName="Helvetica-Bold",
            fontSize=10, textColor=colors.white, leading=13)),
        Paragraph(tag_text, styles["TagText"]),
    ]]
    t = Table(data, colWidths=[0.42 * inch, 4.08 * inch, 2.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, -1), NAVY),
        ("BACKGROUND", (2, 0), (2, -1), accent_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 0), (2, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, 0), 10), ("LEFTPADDING", (1, 0), (1, 0), 4),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
    ]))
    question = P(f"“{question_text}”", "QuestionText")
    body = P(body_text, "Body")
    feeds = P("Feeds into: " + feeds_into_text, "FeedsInto")
    return [KeepTogether([t, Spacer(1, 4), question, body, feeds, Spacer(1, 10)])]

# ============================================================
# ASSEMBLY
# ============================================================

story = []

# ---------- TITLE PAGE ----------
story.append(Spacer(1, 1.2 * inch))
story.append(P("The Phase-7 Tier 0 Companion", "ReportTitle"))
story.append(P("The Philosophical Questions the Governing Purpose Is Answering", "ReportSubtitle"))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=1.2, color=STEEL))
story.append(Spacer(1, 14))
story.append(P("Status: <b>Living reference document — not part of the Constitution's frozen "
    "scope, not ratified, not audited</b>", "MetaLine"))
story.append(P("Date: <b>August 26, 2026</b>", "MetaLine"))
story.append(P("Origin: <b>A ten-question philosophical input Viktor brought to the project "
    "(source not yet attributed), organized here and cross-referenced against the Engineering "
    "Constitution by Claude (Cowork)</b>", "MetaLine"))
story.append(P("Companion to: <b>Phase7_Engineering_Constitution_v1.0_Rev6.pdf</b> — this "
    "document sits above it, the way Tier 0's governing purpose sits above Tiers 1 through 4.",
    "MetaLine"))
story.append(Spacer(1, 24))
story.append(P(
    "<i>The Constitution states a governing purpose and asks you to hold to it. This document "
    "is what the purpose is an answer to — the questions worth sitting with before, and while, "
    "the engine gets built. It isn't a rulebook. Nothing here is checked at audit time, and "
    "nothing here can be violated the way an invariant can. It's closer to a foundation you "
    "can return to when a design decision feels arbitrary and you want to check whether it "
    "actually is.</i>", "Callout"
))
story.append(PageBreak())

# ---------- CONTENTS ----------
story.append(P("Contents", "H1"))
toc_items = [
    "How This Document Works",
    "What the Engine Can Know",
    "What Kind of Object a Market Is",
    "What You Are For",
    "What This Project Is Optimizing",
    "Where This Feeds Back Into the Constitution",
    "Source Notes",
    "Document History",
]
for item in toc_items:
    story.append(P(item, "TOCItem"))
story.append(PageBreak())

# ---------- HOW THIS DOCUMENT WORKS ----------
story.extend(section_header("How This Document Works",
    "Viktor asked what philosophical questions he should be asking himself about the engine's "
    "design, and got back a genuinely rigorous answer — rigorous enough that it applied its own "
    "filter to itself rather than treating every question that sounds deep as equally worth "
    "asking."
))
story.append(P("The relevance test", "H2"))
story.append(P(
    "Stated once, applied to all ten questions consistently: <b>a question earns its place "
    "here only if answering it differently would produce a different engine.</b> Questions like "
    "“what is value” or “can machines think” fail this test — they're genuinely interesting, "
    "but this project's engine comes out identical no matter how you answer them. That's why "
    "they don't appear below. This document only keeps the questions where a different answer "
    "changes a design decision, a rule, or a line of code.", "Body"
))
story.append(P("Two kinds of question", "H2"))
story.append(P(
    "Applying the test honestly split the original ten into two groups, and both are kept here "
    "rather than only the convenient one. <b>Engine-level questions</b> (tagged accordingly "
    "below) pass the test cleanly — a different answer changes the engine, and five of them "
    "already have — they're now Future Amendment Candidates in Constitution Revision 4, and two "
    "more sharpened rationale text already in the document. <b>Project-level questions</b> are "
    "just as real, but they change <i>you</i>, deciding how to build and grade the engine, "
    "rather than the engine's architecture. They don't belong in the Constitution — they belong "
    "here, sitting above it the way Tier 0 sits above Tier 1.", "Body"
))
story.append(P("Relationship to the Constitution", "H2"))
story.append(P(
    "This document is never audited, never ratified, and isn't subject to the scope freeze — "
    "it's reference material, not a rulebook. Where a question below fed a real change into the "
    "Constitution, that's named explicitly in its “Feeds into” line and summarized in the table "
    "near the end of this document. Nothing here changes automatically just because it's "
    "written down here; the Constitution's own frozen-scope process is still what actually "
    "governs the engine.", "Body"
))
story.append(P(
    "<i>Like Phase7_Engineering_Notes.pdf, this is a living document. If more philosophical "
    "material comes up later, it gets added here rather than starting a third companion "
    "document — see Document History at the end.</i>", "Callout"
))

# ---------- WHAT THE ENGINE CAN KNOW ----------
story.extend(section_header("What the Engine Can Know",
    "Four questions about the limits of what a decision-support engine can actually claim to "
    "know, and what it would take to check those claims honestly."
))

story.extend(question_box(1, "The Kill Condition",
    "What result would make me abandon this?",
    "This is Popper's demarcation test for whether a belief is scientific — a claim only counts "
    "as knowledge if there's some possible result that would prove it wrong. Markets make this "
    "far harder than a lab: a losing quarter is equally consistent with “the edge never existed” "
    "and “the edge is real and this is variance,” and there usually isn't time to collect enough "
    "independent trials to tell those apart before the market regime shifts underneath you. The "
    "practical version of the question isn't whether the engine is falsifiable in principle — "
    "it's whether you can actually collect the falsifying evidence in the time you have. If "
    "there's no result that would make you stop, the engine isn't an instrument of knowledge. "
    "It's a comfort object with good typography. The kill condition has to be written before "
    "the backtest runs, not chosen after looking at the equity curve.",
    "Constitution Rev 4, Future Amendment Candidate — “A Written Kill Condition” (Tier 3)",
    "ENGINE-LEVEL", STEEL))

story.extend(question_box(2, "Which Component Failed?",
    "When the engine is wrong, what exactly was wrong?",
    "This is the Duhem-Quine problem: a failed prediction never says on its own which component "
    "failed — the indicator, the risk model, the data, the regime assumption, the sizing. You "
    "can always rescue a losing system by adjusting some other belief slightly, and each "
    "individual adjustment will look reasonable at the time. That's exactly how systems rot — "
    "every loss absorbed by a small local tweak, none of them wrong on their own, the whole "
    "thing drifting into unfalsifiability one sensible fix at a time. This problem never fully "
    "goes away; it only gets disciplined, by deciding before a test runs which single component "
    "it's actually testing.",
    "Constitution Rev 4, Tier 3 “Controlled Changes” rationale (sharpened)",
    "ENGINE-LEVEL", STEEL))

story.extend(question_box(3, "Lens or Property?",
    "Do my numbers describe the market, or my choice of lens?",
    "“Trend strength: 0.72” isn't like “temperature: 21°C.” Temperature is a property of the "
    "gas. Trend is a property of the window you chose to look through it — swap a 20-period "
    "moving average for a 30-period one and the trend reading changes, even though nothing in "
    "the market did. Plenty of technical quantities are properties of the observer's chosen "
    "configuration, wearing the costume of properties of the world. The practical test for any "
    "given quantity: would two competent analysts, making different reasonable parameter "
    "choices, get materially different answers? If yes, it's a lens, not a fact, and the panel "
    "shouldn't display it with the same visual weight as something like price.",
    "Constitution Rev 4, Future Amendment Candidate — “Two-Analyst Lens-vs-Property Test” "
    "(Tier 3, audit methodology for Item 9)",
    "ENGINE-LEVEL", STEEL))

story.extend(question_box(4, "Calibration",
    "What would make “70% confident” true?",
    "For any single, non-repeatable event, nothing does — except calibration across many such "
    "claims over time. A real 70% probability means “when I say this, it happens about 70% of "
    "the time,” and that's a checkable fact, not an assumption you get to make because a number "
    "looks precise. The engine already keeps “confidence” conceptually separate from "
    "“probability” in its own terminology. What turns that separation from a definition into a "
    "fact is a log: every confidence value the engine emits, paired with what actually "
    "happened, plotted as a reliability curve. Until that log exists and gets checked, a "
    "confidence number is decoration, however carefully it was computed.",
    "Constitution Rev 4, Future Amendment Candidate — “Confidence Calibration Log” (Tier 2)",
    "ENGINE-LEVEL", STEEL))

# ---------- WHAT KIND OF OBJECT A MARKET IS ----------
story.extend(section_header("What Kind of Object a Market Is",
    "Two questions about what makes a market a fundamentally different kind of thing to study "
    "than the physical systems most engineering intuition comes from."
))

story.extend(question_box(5, "Reflexivity",
    "Does my engine assume it's observing a system that doesn't know it exists?",
    "This is reflexivity, in the precise sense rather than the loose popular one: the market "
    "being studied is made of other agents who are themselves modeling it — some of whom are "
    "modeling people doing exactly what this project is doing. Physics doesn't push back "
    "against being measured. Markets do. Edges decay because they get found, and the very "
    "process that's generating the data changes as a result of being modeled. The enforceable "
    "consequence: any claimed edge should come with a hypothesis for why it persists — who is "
    "reliably on the other side of that trade, and what keeps them taking it. Liquidity "
    "provision, forced flows, structural constraints, a behavioral bias with an actual "
    "mechanism behind it. An edge with no story about its own survival is usually a fit to "
    "noise that hasn't been embarrassed yet.",
    "Constitution Rev 4, Future Amendment Candidate — “Edge-Persistence Hypothesis "
    "Requirement” (Tier 1, companion to Item 7)",
    "ENGINE-LEVEL", NAVY))

story.extend(question_box(6, "Ergodicity",
    "Am I reasoning about the average across possible worlds, or my one actual path?",
    "This is ergodicity. A strategy with positive expected value, averaged across many parallel "
    "hypothetical attempts, can still ruin you with near certainty in the one world you actually "
    "live in — because you compound along a single trajectory and never get to average over the "
    "other versions where it went better. The ensemble average and the time average come apart, "
    "and the time average is the one that's real. Tier 1, Item 14 already refuses to let "
    "conviction substitute for risk; ergodicity is the mathematical reason that instinct is "
    "correct. It also means where entry, stop, and target prices sit relative to each other "
    "deserves as much engineering care as the directional read itself — not that the engine "
    "should have any hand in how much money a trader puts on a trade. That decision, in money "
    "terms, stays the trader's alone; the engine's job stops at price.",
    "Constitution Rev 5, Tier 1 Item 14 rationale (sharpened, then corrected); directly relevant "
    "to the configurable-risk-tolerance feature in Phase7_Engineering_Notes.pdf, Entry #5 — that "
    "feature shapes entry and target prices, never a money amount",
    "ENGINE-LEVEL", NAVY))

# ---------- WHAT YOU ARE FOR ----------
story.extend(section_header("What You Are For",
    "Two questions about the human role this engine is actually designed to support — and how "
    "easily that role can be quietly hollowed out without a single rule being broken."
))

story.extend(question_box(7, "The Moral Crumple Zone",
    "What judgment am I reserving for myself, and does the panel actually make it possible?",
    "Tier 1, Item 1 says tool, not autonomous actor — architecturally clean, but philosophically "
    "incomplete on its own. If the panel displays “BUY, confidence 78” and Viktor clicks, he "
    "isn't really the decision-maker at that point — he's a relay that adds latency and absorbs "
    "the liability. The term for that role is a moral crumple zone: a human kept in the loop "
    "mainly so there's somewhere for responsibility to land. Automation bias is well documented, "
    "and writing the code yourself doesn't grant immunity to it — if anything, authorship makes "
    "it worse, not better. This is the question with the most immediate design consequence: an "
    "interface that supports judgment shows what was observed, what was inferred from it, what "
    "remains unknown, and what would change the read. An interface that replaces judgment shows "
    "a verdict and a number. Item 1 can be fully satisfied in code and still be violated in the "
    "panel.",
    "Constitution Rev 4, Future Amendment Candidate — “UI-Level Enforcement of Item 1” (Tier 2)",
    "ENGINE-LEVEL", MAROON))

story.extend(question_box(8, "Returns vs. Understanding",
    "Do I want returns, or understanding?",
    "These genuinely trade off. The most predictive models tend to be the least interpretable, "
    "and Tier 4's existing preference for explainability over unnecessary opacity is, in effect, "
    "buying comprehension at some cost to a performance ceiling. That may be exactly the right "
    "purchase — the point isn't to reverse it, it's to make it a decision with a visible price "
    "rather than an inherited taste nobody chose on purpose. Worth revisiting deliberately "
    "whenever a specific design choice forces the trade-off into the open, rather than assuming "
    "the answer once and forgetting it was a choice at all.",
    "No Constitution change — Tier 4's existing preference already covers this; this question "
    "is what makes the trade-off a conscious decision instead of an inherited one",
    "PROJECT-LEVEL", PURPLE))

# ---------- WHAT THIS PROJECT IS OPTIMIZING ----------
story.extend(section_header("What This Project Is Optimizing",
    "Two questions that determine how to judge whether any of this is actually working — not "
    "about the engine's architecture, but about what building it is for."
))

story.extend(question_box(9, "What the Project Optimizes",
    "What is this project actually optimizing?",
    "Money, understanding, or the specific pleasure of building something rigorous — all three "
    "are respectable, and they are three different projects, with different success conditions "
    "and different stopping points. Worth being straight about which one this actually is: if "
    "the honest answer is strictly returns, a solo engine has to clear a genuinely hard bar "
    "against simply holding the asset. If the honest answer is the engineering and epistemics "
    "education, the project is already succeeding, and returns are a secondary measurement, not "
    "the scoreboard. The failure mode isn't picking one — it's optimizing for one while grading "
    "yourself by the other, without noticing the mismatch.",
    "Nothing in the Constitution — this is about Viktor's own motivation for the project, not "
    "the engine's behavior",
    "PROJECT-LEVEL", PURPLE))

story.extend(question_box(10, "The Project's Kill Condition",
    "What would make it safe to kill the engine?",
    "Tier 1, Item 15 already makes it safe to kill a single feature without it being personal — "
    "measured behavior wins over theoretical elegance, full stop. This question extends that up "
    "a level, to the whole project. If there's no state of the world that would make Viktor stop "
    "— no result, no elapsed time, no accumulated evidence — then sunk cost is already steering, "
    "quietly, and forty test runs of investment so far is exactly enough for that to become "
    "invisible without a deliberate check. This is the one question the input itself singled "
    "out as the place to start: everything else is downstream of having an honest answer to it.",
    "Nothing in the Constitution — this extends Item 15's spirit to the whole project, which is "
    "a personal commitment Viktor makes, not an engine rule",
    "PROJECT-LEVEL", PURPLE))

# ---------- FEEDS BACK TABLE ----------
story.append(PageBreak())
feeds_title = P("Where This Feeds Back Into the Constitution", "H1")
feeds_intro = P(
    "One table, all ten questions, so the disposition of each is visible at a glance without "
    "paging back through the sections above.", "Body"
)
feeds_rows = [
    ["#", "Question", "Where it landed"],
    ["1", "What result would make me abandon this?",
     "Future Amendment Candidate — Kill Condition (Tier 3)"],
    ["2", "When the engine is wrong, what exactly was wrong?",
     "Tier 3, Controlled Changes rationale (sharpened)"],
    ["3", "Do my numbers describe the market, or my choice of lens?",
     "Future Amendment Candidate — Lens-vs-Property Test (Tier 3)"],
    ["4", "What would make “70% confident” true?",
     "Future Amendment Candidate — Calibration Log (Tier 2)"],
    ["5", "Does my engine assume it's observing a system that doesn't know it exists?",
     "Future Amendment Candidate — Edge-Persistence Requirement (Tier 1)"],
    ["6", "Am I reasoning about the average across possible worlds, or my one actual path?",
     "Tier 1, Item 14 rationale (sharpened, then corrected in Rev 5); Notes Entry #5"],
    ["7", "What judgment am I reserving for myself, and does the panel make it possible?",
     "Future Amendment Candidate — UI-Level Enforcement of Item 1 (Tier 2)"],
    ["8", "Do I want returns, or understanding?",
     "Above the engine — sharpens Tier 4's existing preference, no rule change"],
    ["9", "What is this project actually optimizing?",
     "Above the engine — about Viktor, not the engine"],
    ["10", "What would make it safe to kill the engine?",
     "Above the engine — extends Item 15's spirit project-wide"],
]
tf = Table(wrap_table(feeds_rows), colWidths=[0.35 * inch, 3.75 * inch, 2.4 * inch])
tf.setStyle(row_style)
tf.repeatRows = 1
story.append(KeepTogether([feeds_title, feeds_intro]))
story.append(tf)
story.append(Spacer(1, 8))
story.append(P(
    "Five of ten fed real, checkable additions to Constitution Revision 4. Two sharpened "
    "rationale text already there. Three stayed here, correctly — they change Viktor's relationship "
    "to the project, not the engine's architecture, and forcing them into the Constitution would "
    "have been exactly the kind of padding the Tier 0 test exists to catch.", "BodySmall"
))

# ---------- SOURCE NOTES ----------
story.append(PageBreak())
story.append(P("Source Notes", "H1"))
story.append(P(
    "The ten questions above originated from a philosophical input Viktor brought into the "
    "project on August 26, 2026 — source not yet attributed in this document. Viktor, let me "
    "know who produced it and I'll credit it here by name, the same way Copilot, Gemini, "
    "ChatGPT, and the Constitution's fourth reviewer are credited in the rest of this document "
    "family. The input itself proposed writing this companion piece; that offer is the reason "
    "this document exists in this form rather than as a handful of scattered notes.", "Body"
))
story.append(Spacer(1, 6))
story.append(P(
    "<i>This document didn't audit the Constitution's rules. It audited whether the "
    "Constitution's foundations — the questions its governing purpose is quietly answering — "
    "were as solid as its process. Five gaps turned out to be real and are now logged as "
    "concrete work; the rest turned out to be questions about the builder, not the build, and "
    "are recorded here rather than forced somewhere they don't belong.</i>", "Callout"
))

# ---------- DOCUMENT HISTORY ----------
story.append(PageBreak())
hist_title = P("Document History", "H1")
hist_rows = [
    ["Version", "Date", "Notes"],
    ["v1.0", "August 26, 2026", "First version. Ten questions from the philosophical input "
     "organized into four themes, run through the input's own relevance test, and "
     "cross-referenced against Constitution Revision 4."],
    ["v1.1", "August 26, 2026", "Corrected Question 6 (Ergodicity): the body text and its "
     "“Feeds into” line had drifted toward implying the engine should size positions or "
     "recommend money amounts. Viktor caught this directly. Reworded to state plainly that "
     "ergodicity is a reason entry/stop/target price geometry deserves engineering care, not a "
     "reason for the engine to touch money amounts — that decision stays the trader's alone. "
     "Cross-referenced to Constitution Rev 5 and Engineering Notes, Entry #9."],
    ["v1.2", "August 26, 2026", "Pointer update only — the companion reference on the title "
     "page now points at Constitution Rev 6. Question 6's “Feeds into” line still cites Rev 5, "
     "correctly: that is where the correction actually happened, and it is a historical "
     "reference rather than a live pointer. No question text changed."],
]
th = Table(wrap_table(hist_rows), colWidths=[0.9 * inch, 1.4 * inch, 4.2 * inch])
th.setStyle(row_style)
hist_callout = P(
    "<i>Like the Engineering Notes, this document is meant to be appended to rather than "
    "rebuilt — if more philosophical material comes up later, it gets a new numbered version "
    "and a new section here, not a third companion document.</i>", "Callout"
)
story.append(KeepTogether([hist_title, th, Spacer(1, 10), hist_callout]))

# ============================================================
# BUILD
# ============================================================

doc = SimpleDocTemplate(
    OUTPUT_PATH, pagesize=LETTER,
    topMargin=0.85 * inch, bottomMargin=0.9 * inch,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    title="Phase-7 Tier 0 Companion",
    author="Claude (Cowork), with Viktor",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Wrote {OUTPUT_PATH}")
