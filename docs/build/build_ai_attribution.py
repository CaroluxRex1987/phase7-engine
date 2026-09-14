#!/usr/bin/env python3
"""
Builds the Phase-7 AI-Attribution Statement -- item 5 of the six
portfolio-ready criteria in docs/PHASE7_NEXT.md ("Two goals, and the order
they finish in"): "What Viktor designed, decided, tested and ruled on,
versus what Claude produced... never assembled into one place."

This is deliberately a separate document from Phase7_Portfolio_Document.pdf
(item 4), per that document's own front matter and per Viktor's 14
September instruction to do the two in order. It does not narrate the
engine or the project's history -- Phase7_Portfolio_Document.pdf already
does that -- it accounts for who did what.

Sources: the Constitution's own "Roles & Authority" section, inline
"VIKTOR'S RULING" comments in the production code, docs/PHASE7_NEXT.md's
recorded rulings, commit messages, and the tag taxonomy already used by
docs/build/build_engineering_notes.py's ~118 numbered entries (counted
directly from that script, not estimated).
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)

import _output

OUTPUT_PATH = _output.output_path("Phase7_AI_Attribution.pdf")

styles = getSampleStyleSheet()

NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
LIGHT_BG = colors.HexColor("#f3f6fa")
GREEN = colors.HexColor("#1e7d32")
AMBER = colors.HexColor("#b06f00")
GREY = colors.HexColor("#5a5a5a")
MAROON = colors.HexColor("#8a2f2f")

styles.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=22,
    leading=27, textColor=NAVY, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="ReportSubtitle", fontName="Helvetica", fontSize=12.5,
    leading=17, textColor=STEEL, spaceAfter=4))
styles.add(ParagraphStyle(name="MetaLine", fontName="Helvetica", fontSize=10,
    leading=14, textColor=GREY, spaceAfter=2))
styles.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=16,
    leading=20, textColor=NAVY, spaceBefore=18, spaceAfter=9))
styles.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=11.8,
    leading=15, textColor=STEEL, spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=9.7,
    leading=14, textColor=colors.HexColor("#222222"), spaceAfter=7, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Cell", fontName="Helvetica", fontSize=8.2,
    leading=11.4, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="CellHeader", fontName="Helvetica-Bold", fontSize=8.3,
    leading=10.5, textColor=colors.white))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Oblique", fontSize=9.2,
    leading=13.3, textColor=STEEL, spaceBefore=4, spaceAfter=8, leftIndent=14))


def P(text, style="Body"):
    return Paragraph(text, styles[style])


def cell(text, header=False):
    return Paragraph(text, styles["CellHeader" if header else "Cell"])


def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    width, _ = LETTER
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(0.75 * inch, 0.55 * inch, "Phase-7 AI-Attribution Statement")
    canvas_obj.drawRightString(width - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas_obj.setStrokeColor(colors.HexColor("#d5dbe3"))
    canvas_obj.line(0.75 * inch, 0.72 * inch, width - 0.75 * inch, 0.72 * inch)
    canvas_obj.restoreState()


def box(paragraphs, border_color=STEEL, bg=LIGHT_BG):
    t = Table([[paragraphs]], colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.1, border_color),
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return [t, Spacer(1, 10)]


def table(rows, col_widths, header=True):
    data = [[cell(c, header=(header and i == 0)) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY) if header else ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, LIGHT_BG]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 10)]


story = []

# ============================================================
# COVER
# ============================================================
story.append(P("Phase-7 Structural Quant Engine", "ReportSubtitle"))
story.append(P("AI-Attribution Statement", "ReportTitle"))
story.append(P("Prepared 14 September 2026, covering the project from its 26 August 2026 "
               "ratification of the Engineering Constitution to date.", "MetaLine"))
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")))
story.append(Spacer(1, 10))

story.extend(box([
    P("<b>What this document is.</b>", "H2"),
    P("Item 5 of the six criteria docs/PHASE7_NEXT.md sets for calling this project "
      "“portfolio-ready.” Its own words for the job: “What Viktor designed, "
      "decided, tested and ruled on, versus what Claude produced... never assembled into one "
      "place.” This is that assembly. It is a separate document from "
      "Phase7_Portfolio_Document.pdf (item 4), which narrates the engine and its history; this "
      "document instead accounts for authorship -- who decided, who wrote, who was overruled, "
      "and by what evidence each of those claims can be checked.", "Body"),
]))

story.append(PageBreak())

# ============================================================
# 1. METHOD
# ============================================================
story.append(P("Method", "H1"))
story.append(P(
    "Every claim in this document is checkable against something outside it: an inline code "
    "comment (grep-able by the tag “VIKTOR'S RULING”), a dated entry in the "
    "engineering log (docs/Phase7_Engineering_Notes.pdf, itself append-only and never "
    "retroactively edited), a commit message, or docs/PHASE7_NEXT.md's own recorded rulings. "
    "Nothing here is asserted from memory alone. Where the underlying evidence is a memory of a "
    "conversation rather than a committed artifact, this document says so rather than presenting "
    "it with the same weight as a commit hash.", "Body"))
story.append(P(
    "The engineering log alone -- docs/build/build_engineering_notes.py, counted directly from "
    "its own source rather than estimated -- carries 118 numbered entries as of this writing, "
    "tagged by kind:", "Body"))
story.extend(table([
    ["Tag", "Count", "What it records"],
    ["DECISION — ADOPTED / ON ICE", "30", "A ruling Viktor made and acted on (or "
                                              "deliberately deferred)."],
    ["PROCESS — RECORDED", "20", "A change to how the work itself is done."],
    ["OBSERVATION — FILED FOR THE RECORD", "17", "Noted, not (yet) acted on."],
    ["FINDINGS — FIXED / FROM EXECUTION / FROM AN UNFINISHED AUDIT", "22",
     "A defect: found, and (in 11 of the 22) closed."],
    ["MILESTONE — RECORDED / PHASE A COMPLETE", "7", "A phase or step completed."],
    ["AUDIT RUN/STEP — RECORDED or VERIFIED", "7", "An independent model's audit pass, "
                                                        "logged."],
    ["EXTERNAL ASSESSMENT", "6", "An outside party's judgment on the project itself (Grok, "
                                 "Gemini, GPT-6 Astra, Meta Muse Spark)."],
    ["REFERENCE — FILED FOR THE RECORD", "5", "Background material kept for context."],
    ["CANDIDATE — NOT ADOPTED", "2", "Proposed, considered, and deliberately not taken."],
    ["IDEA / KEY INSIGHT", "2", "A single unevaluated idea, and one named structural insight."],
], col_widths=[2.6 * inch, 0.7 * inch, 3.2 * inch]))
story.append(P(
    "118 entries, verified by parsing docs/build/build_engineering_notes.py's own source "
    "(every entry_box()/highlighted_entry_box() call, numbered 1 through 118 with no gap and no "
    "duplicate) rather than counted by eye.", "Callout"))

# ============================================================
# 2. ROLES
# ============================================================
story.append(P("Roles, as the Constitution itself defines them", "H1"))
story.append(P(
    "The Phase-7 Engineering Constitution states the working relationship directly, in its own "
    "“Roles &amp; Authority” section: this document assigns Claude the technical and "
    "architectural judgment calls -- not blind authority. “The working relationship is: "
    "Claude proposes, reasons, challenges, implements, and tests; Viktor reviews, questions, "
    "performs QA, and ultimately accepts or rejects the change.” Audit independence is "
    "structured the same way: “Claude prepares the audit package... the independent auditor "
    "writes none of the findings” -- a third party, neither Viktor nor Claude, evaluates "
    "the engine against the register both of them helped write.", "Body"))
story.append(P(
    "In practice this produced three distinct roles rather than two: Viktor, who ratifies, "
    "rules, and accepts or rejects; Claude, who drafts, implements, tests, and researches, "
    "under review; and a rotating set of independent AI models, commissioned specifically "
    "because neither Viktor nor Claude can certify Claude's own work as compliant with rules "
    "Claude helped write.", "Body"))

# ============================================================
# 3. DECISIONS VIKTOR MADE HIMSELF
# ============================================================
story.append(P("Decisions Viktor made himself", "H1"))
story.append(P(
    "A representative set, not an exhaustive one -- the engineering log's 29 "
    "“DECISION — ADOPTED” entries carry the complete record. Each of these below "
    "is independently checkable: the inline comments cited exist verbatim in the current "
    "source.", "Body"))
story.extend(table([
    ["Date", "Ruling", "Where it is checkable"],
    ["27 Aug 2026", "Item 6 (Traceability) raised from Major to Critical, on the principle "
                    "that severity reflects consequence rather than repair effort.",
                    "docs/PHASE7_NEXT.md"],
    ["29 Aug 2026", "“Degrade, don't halt” — a failed input is recorded and "
                    "confidence capped, rather than the run stopping.",
                    "models/decision_model.py's _apply_degradation()"],
    ["29 Aug 2026", "The engine must not compute monetary position sizing; a portfolio layer's "
                    "job, not the engine's.", "core/config.py, SEQUENCE ITEM 13 comment"],
    ["31 Aug 2026", "Items 3, 11, and 14's re-audit rulings, decided personally rather than "
                    "delegated (“decide items 3, 11, 14 myself”).",
                    "docs/PHASE7_NEXT.md, commit c4dfcc7"],
    ["2 Sep 2026", "Bias is the sole source of trade direction; no other signal may open or "
                   "override it.", "models/decision_model.py, models/signal_router.py"],
    ["5 Sep 2026", "“A lean is not a case” — a directional bias below a fixed "
                   "strength floor (MIN_ACTION_BIAS) waits rather than acting.",
                   "models/decision_model.py"],
    ["5 Sep 2026", "trend_health is an unsigned magnitude and may not be read as a directional "
                   "signal on its own.", "models/decision_model.py"],
    ["14 Sep 2026", "The setup's direction (long/short) must be stated in words on the panel, "
                    "not only inferable from the targets — specified placement (under the "
                    "DECISION line) himself.", "core/panel_render.py, commit 66f1479"],
    ["14 Sep 2026", "A NEUTRAL bias prints no direction line at all, overruling Claude's own "
                    "unrequested “no directional lean” addition.",
                    "core/panel_render.py, commit 39e0e79"],
    ["14 Sep 2026", "Closing round 6's findings needs the same auditor confirming its own fixes, "
                    "not a fresh independent model — a genuinely independent pass is saved "
                    "for immediately before backtesting.", "docs/PHASE7_NEXT.md"],
], col_widths=[0.85 * inch, 4 * inch, 1.65 * inch]))

story.append(PageBreak())

# ============================================================
# 4. WHAT CLAUDE PRODUCED
# ============================================================
story.append(P("What Claude produced", "H1"))
story.append(P(
    "Most of the code and most of the prose in this repository, under the review relationship "
    "described above -- proposed, reasoned about, implemented, and tested, then accepted, "
    "corrected, or rejected by Viktor. Concretely, across this project: the majority of the "
    "engine's Python implementation across core/, data/, indicators/, models/, structure/, and "
    "utils/; the drafting of the Engineering Constitution's prose (from a joint principles "
    "discussion, then revised across eight revisions in response to outside review); the "
    "engineering log and its 118 entries; the test suite's design and the golden-path/pinned-data "
    "reproducibility mechanism; the git archaeology and cross-referencing used to keep documents "
    "honest against the actual commit history (including, twice, catching this project's own "
    "documentation going stale); and the mechanics of every patch delivered into this repository "
    "-- verification against a fresh clone, code_fingerprint and golden-snapshot checks, and the "
    "commit messages themselves.", "Body"))
story.append(P(
    "None of that authorship implies authority. Every one of those outputs reached the "
    "repository because Viktor reviewed and accepted it, and a meaningful fraction did not reach "
    "it unchanged -- Section 5 accounts for those.", "Body"))

# ============================================================
# 5. WHERE CLAUDE WAS WRONG
# ============================================================
story.append(P("Where Claude was wrong, and Viktor caught it", "H1"))
story.append(P(
    "An attribution statement that only credits Viktor's decisions and Claude's execution would "
    "misstate the actual working relationship, which included real errors, caught by review, not "
    "by construction. Recorded here rather than omitted, per this project's own standing "
    "practice of keeping mistakes in the log rather than quietly correcting them.", "Body"))
story.extend(table([
    ["What happened", "How it was corrected"],
    ["1 Sep 2026: Claude told Viktor “nine Major and Moderate findings still open,” a "
     "count taken from an audit report's verdicts rather than checked against the actual code.",
     "Checking each location the report quoted found three already closed by unrelated work; "
     "the true count was different. Recorded in docs/PHASE7_NEXT.md rather than silently "
     "revised."],
    ["3 Sep 2026: five separate errors in one session, all the same shape — a conclusion "
     "stated with the same confidence whether or not it had actually been checked (two "
     "incomplete change predictions, a shipped defect, three unread-first documentation alarms, "
     "one vacuous test assertion).",
     "Viktor named the pattern explicitly and asked for a standing practice: state a claim's "
     "verification status inside the sentence making the claim, not as a caveat after it. "
     "Adopted as a working rule, still in force."],
    ["Some point before 29 Aug 2026: the engine computed monetary position sizing "
     "(account balance and risk-percent constants, read only by a sizing block in "
     "engine_core.py).",
     "Viktor ruled the engine must not size positions — a portfolio layer's job, not an "
     "analytical tool's. The computation and its constants were removed entirely, not gated "
     "behind a flag."],
    ["Constitution drafting: a rationale text drifted toward implying the engine should size "
     "positions, introduced during an earlier revision.",
     "Viktor caught the drift on his own reading and it was corrected in Revision 5, before "
     "ratification — recorded in the Constitution's own revision history rather than "
     "silently rewritten."],
    ["14 Sep 2026: Claude added an unrequested “NEUTRAL — no directional lean this "
     "run” line to the panel, reasoning it matched the style of other “not "
     "located” messages elsewhere.",
     "Viktor ruled a NEUTRAL bias is a correct reading, not a failed measurement, and should "
     "print nothing — overruling the addition. Landed at commit 39e0e79."],
], col_widths=[3.5 * inch, 3 * inch]))

# ============================================================
# 6. INDEPENDENT THIRD PARTIES
# ============================================================
story.append(P("Independent third parties", "H1"))
story.append(P(
    "Neither Viktor nor Claude certifies the engine compliant with the Constitution -- that is "
    "the audit's entire reason to exist, and it is why this section is neither “Viktor” "
    "nor “Claude.” Multiple AI models across multiple labs (at various points: "
    "DeepSeek, Kimi K3, GLM 5.3, GPT-5.6 Luna Pro, GPT-6 Astra, and Meta's Muse Spark, among "
    "others, per README.md and the engineering log) have reviewed the Constitution, audited the "
    "engine's source, or verified a specific set of fixes. Which document each model has seen is "
    "tracked deliberately, because a model that has read the standard it is later asked to audit "
    "against is no longer independent of it -- a distinction this project treats as load-bearing "
    "rather than a formality, and checks explicitly before naming an auditor for a given round.",
    "Body"))
story.append(P(
    "One exposure is stated rather than glossed over: three models (Claude Sonnet 4, DeepSeek "
    "V3, and DeepSeek R1) touched this codebase during the build itself via an AI coding tool, "
    "which means a later, nominally blind audit run by a DeepSeek-lineage model carried weaker "
    "independence than it first appeared. Independence is tracked at the lab level for exactly "
    "this reason, not at the model-version level, since treating a version bump as a reset would "
    "make the safeguard ceremonial.", "Body"))

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=LETTER,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.85 * inch,
    title="Phase-7 AI-Attribution Statement")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Built: {OUTPUT_PATH}")
