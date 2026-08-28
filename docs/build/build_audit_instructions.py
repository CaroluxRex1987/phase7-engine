#!/usr/bin/env python3
"""
Builds the Phase-7 Audit Execution Instructions — the operational procedure
for running Step 3, including the two verbatim auditor instructions.

This is a working document, not a normative one. It changes no rule and
records no finding. It exists because the audit is run by hand, possibly
across several sessions, and the procedure needs to survive being put down
and picked up again. It is also part of the audit record under Item 6
(Traceability): how the auditor was asked bears on what the auditor found.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Preformatted
)

OUTPUT_PATH = "/tmp/outputs/Phase7_Audit_Execution_Instructions.pdf"

styles = getSampleStyleSheet()

NAVY = colors.HexColor("#1a2b4a")
STEEL = colors.HexColor("#3d5a80")
LIGHT_BG = colors.HexColor("#f3f6fa")
GREEN = colors.HexColor("#1e7d32")
AMBER = colors.HexColor("#b06f00")
GREY = colors.HexColor("#5a5a5a")
MAROON = colors.HexColor("#8a2f2f")
CODE_BG = colors.HexColor("#f7f8fa")

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
styles.add(ParagraphStyle(name="CellMono", fontName="Courier", fontSize=7.9,
    leading=11, textColor=colors.HexColor("#222222")))
styles.add(ParagraphStyle(name="CellHeader", fontName="Helvetica-Bold", fontSize=8.3,
    leading=10.5, textColor=colors.white))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Oblique", fontSize=9.2,
    leading=13.3, textColor=STEEL, spaceBefore=4, spaceAfter=8, leftIndent=14))
# Instruction 2 runs to ~60 lines and has to stay on one page so it can be copied in a
# single selection; a Preformatted inside a Table will not split. Leading is set to fit
# the longer of the two blocks, not chosen for looks.
styles.add(ParagraphStyle(name="Instr", fontName="Courier", fontSize=8.0,
    leading=10.3, textColor=colors.HexColor("#1a1a1a")))

def P(text, style="Body"):
    return Paragraph(text, styles[style])

def cell(text, header=False, mono=False):
    if header:
        return Paragraph(text, styles["CellHeader"])
    if mono:
        return Paragraph(text, styles["CellMono"])
    return Paragraph(text, styles["Cell"])

def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = LETTER
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Audit Execution Instructions")
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

def instruction_block(text):
    """The verbatim text to paste. Courier, preserved line breaks, boxed."""
    pre = Preformatted(text, styles["Instr"])
    t = Table([[pre]], colWidths=[6.5 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#b8c2d0")),
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [t, Spacer(1, 10)]

# ============================================================
# THE TWO INSTRUCTIONS — verbatim, as pasted to the auditors
# ============================================================

INSTRUCTION_1 = """You are reviewing a Python codebase. I want your honest technical
assessment of what is wrong with it.

Context, kept deliberately minimal: this is a market-analysis engine for
a single cryptocurrency pair. It reads market data and produces analysis
output. It was written by one person with heavy AI assistance. That is
all you need to know, and I am withholding further
context on purpose - I do not want you evaluating it against anyone
else's stated intentions, including mine.

Read the source and tell me what is actually wrong with it. Prioritise:

1. Anything that would produce silently incorrect output - wrong numbers
   that look plausible, rather than crashes.
2. Anything where the code could do something the reader of it would not
   expect. State plainly if you cannot determine from the code alone what
   the program is capable of doing.
3. Structural or architectural problems that will cause real trouble
   later, as opposed to style preferences.
4. Anything that looks like it was written to work in one specific case
   and would break in adjacent ones.

Rank findings by how much damage they could cause, not by how easy they
are to fix. Be specific: name the file and, where you can, the function.

Do not soften the assessment. Do not open with praise. If large parts of
it are fine, say so in one line and spend the response on what is not.

If you find nothing serious, say that plainly - do not manufacture
findings to seem thorough."""

INSTRUCTION_2 = """You are performing an independent compliance audit. You have been
commissioned specifically because you did not write this code and did not
write the standard it is being judged against.

MATERIALS
- The complete engine source.
- The Phase-7 Engineering Constitution: a ratified 44-rule register
  (21 Tier 1 invariants, 7 Tier 2, 10 Tier 3, 6 Tier 4).
- A Step 2a audit package: a file manifest, evidence pointers, and a
  self-documented failure history.
- Runtime logs and one simulated trade record.

DISCLOSURE YOU SHOULD ACT ON
The audit package was assembled by Claude, which also wrote most of the
engine and co-drafted the Constitution. It is therefore not a neutral
document. Treat every factual claim in it - including its stated search
results - as a claim to be verified against the source yourself, not as
an established fact. Where you cannot verify one, say so.

YOUR TASK
Evaluate the engine against the register. Begin with the Minimum Viable
Audit gate - Items 2, 3, 6 and 18 - then work through the remaining Tier
1 invariants, then Tiers 2 to 4.

Record every finding in this schema:

  Principle       - which item, by number and name
  Status          - Compliant / Non-compliant / Unknown
  Severity        - Critical / Major / Moderate / Minor
  Effort          - rough cost to remedy
  Evidence        - the specific file, function or log line. Evidence
                    must be independently checkable by someone who has
                    not read your reasoning.
  Impact          - what goes wrong in practice if this stands
  Required action - what would have to change
  Verification    - how one would confirm the fix worked
  Re-audit        - whether this needs rechecking later

RULES THAT ARE NOT NEGOTIABLE
- "Unknown" is a legitimate and expected result. If a claim cannot be
  evidenced from the artefacts in front of you, the status is Unknown.
  Do not argue an Unknown into a Compliant because the code looks like it
  probably does the right thing.
- Do not treat the Constitution's own confidence about the engine as
  evidence about the engine.
- Two items are handed to you as open questions in the package's Section
  5 rather than as findings. Test them; do not confirm them.
- The Constitution's Version History contains a row labelled DEFECT,
  recording an internal contradiction about the composition of the
  Minimum Viable Audit gate. You are required to record a formal finding
  resolving which passage stands.
- Where your own reasoning may be correlated with that of the model that
  built this - shared training data, shared habits - say so explicitly at
  that point in the audit. Do not present a possibly-shared blind spot as
  an independent confirmation.

Do not open with an assessment of the document's quality. Start with
findings."""

story = []

# ============================================================
# COVER
# ============================================================
story.append(P("Phase-7 Structural Quant Engine", "ReportSubtitle"))
story.append(P("Audit Execution Instructions", "ReportTitle"))
story.append(P("Written August 27, 2026 — the procedure for running Step 3", "MetaLine"))
story.append(P("Status: <b>working document.</b> Changes no rule, records no finding.", "MetaLine"))
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")))
story.append(Spacer(1, 10))

story.extend(box([
    P("<b>What this document is for.</b>", "H2"),
    P("The audit is run by hand, in a browser, possibly across several sessions days "
      "apart. This document exists so the procedure survives being put down and picked up "
      "again, without reconstructing it from a chat log. It also forms part of the audit "
      "record: under Item 6 (Traceability), how the auditor was asked bears directly on what "
      "the auditor found, so the exact wording used is preserved here rather than "
      "paraphrased.", "Body"),
]))

story.append(P("Two runs, in a fixed order", "H2"))
story.append(P(
    "<b>Run 1 is a blind review.</b> One model receives the source code and nothing else — "
    "no Constitution, no audit package. It is asked what is wrong with the code, with no "
    "knowledge of what the project claims about itself. Its value is narrow but real: it is "
    "the only run that can find a problem <i>the 44-rule register does not cover</i>, which "
    "is precisely the trigger that lifts the scope freeze.", "Body"))
story.append(P(
    "<b>Run 2 is the compliance audit — Step 3 proper.</b> The intended primary auditor is "
    "Kimi K3 (Moonshot AI), per the Constitution's AUDITOR row. It receives the full "
    "material and evaluates the engine against the register, item by item, recording "
    "Compliant / Non-compliant / Unknown for each.", "Body"))

story.extend(box([
    P("<b>The order is not negotiable, and the reason is mechanical.</b>", "H2"),
    P("A model that has seen the Constitution cannot un-see it. Once it knows what the "
      "engine is supposed to do, it can no longer tell you what it would have noticed "
      "without knowing. Run 1 is therefore available exactly once, and only before Run 2. "
      "Running them out of order does not produce a worse blind review — it produces none at "
      "all.", "Body"),
], border_color=MAROON, bg=colors.HexColor("#fbf3f3")))

story.append(PageBreak())

# ============================================================
# 1. MATERIALS
# ============================================================
story.append(P("1. Materials", "H1"))
story.append(P(
    "All five files live in one folder. Byte sizes are given so a stale or truncated copy is "
    "caught before it reaches an auditor rather than after — this has already happened once, "
    "with an outdated copy of the Constitution missing the two rows Run 2 requires a finding "
    "on.", "Body"))

mat_rows = [
    ["File", "Bytes", "Used in", "What it is"],
    ["Phase7_Source_For_Audit.txt", "207,625", "Runs 1 and 2",
     "All 19 source files concatenated, each preceded by a delimiter naming its path. "
     "Roughly 56,000 tokens."],
    ["Phase7_Engineering_Constitution_<br/>v1.0_RATIFIED_AUDITCOPY.pdf", "101,831",
     "Runs A, B and C",
     "The 44-rule register, 34 pages. The frozen audit copy — see the warning below. "
     "Deliberately not the same filename as the live document in docs/."],
    ["Phase7_Step2a_Audit_Package.pdf", "21,386", "Run 2 only",
     "File manifest, evidence pointers, self-documented failure history, and two open "
     "questions. Assembled by Claude and therefore not neutral — Instruction 2 says so "
     "explicitly."],
    ["Phase7_Step2a_Evidence.zip", "7,011", "Run 2 only",
     "Runtime log, scan summary, engine state file, one simulated trade record. None of "
     "these are in the public repository."],
    ["Phase7_Step2a_Source.zip", "62,987", "Neither",
     "The same source as the .txt above, in original directory structure. A backup for the "
     "case where a plain-text upload fails."],
]
data = [[cell(c, header=(i == 0), mono=(i > 0 and j == 0))
         for j, c in enumerate(r)] for i, r in enumerate(mat_rows)]
t = Table(data, colWidths=[1.85*inch, 0.62*inch, 0.72*inch, 3.31*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

story.extend(box([
    P("<b>Two Constitutions now exist, and they must not be swapped.</b>", "H2"),
    P("The copy in the audit folder is frozen at <b>101,831 bytes, 34 pages</b> — the exact "
      "document Runs A and B were graded against. The copy in <font face=\"Courier\">docs/</font> "
      "is the live one, and it grows: after Run B it gained an AUDITED row and became 104,090 "
      "bytes at 35 pages.", "Body"),
    P("Run C must receive the frozen 101,831-byte copy. The AUDITED row states how many items "
      "came back Compliant and names which findings were rated Critical — handing that to the "
      "next auditor tells it what its predecessors concluded before it has read a line, which "
      "is the contamination the rules in Section 4 exist to prevent. All three runs are graded "
      "against one unchanging register; the live document records what the grading found.", "Body"),
    P("The two files are therefore named differently on purpose. The audit folder holds "
      "<font face=\"Courier\">…_RATIFIED_AUDITCOPY.pdf</font> and nothing else called a "
      "Constitution; <font face=\"Courier\">docs/</font> holds "
      "<font face=\"Courier\">…_RATIFIED.pdf</font> and keeps growing. This is not tidiness. "
      "Both files briefly sat in the audit folder under the same name, and the wrong one was "
      "staged for upload within twenty minutes of this warning first being written — caught "
      "only because the byte count was read off a directory listing before sending. Check the "
      "size before every upload regardless; a distinct filename removes the way it went wrong "
      "the first time, not every way it could.", "Body"),
], border_color=MAROON))

story.append(P("Where the runs happen", "H2"))
story.append(P(
    "OpenRouter (openrouter.ai), which requires no subscription: credits are bought once, "
    "do not expire, and are drawn down per token. A full Run 2 costs roughly one US dollar "
    "even on the most expensive frontier models; Run 1 costs less. Cost is therefore not a "
    "constraint on how carefully this is done, and should not be treated as one.", "Body"))

story.append(PageBreak())

# ============================================================
# 2. RUN 1
# ============================================================
story.append(P("2. Run 1 — Blind Review", "H1"))

story.append(P("Setup", "H2"))
story.append(P(
    "Open a <b>new conversation</b>. Upload <b>only</b> "
    "<font face='Courier'>Phase7_Source_For_Audit.txt</font>. Nothing else from the folder "
    "may enter this conversation at any point — not the Constitution, not the audit package, "
    "not a summary of either, and not an explanation of what the engine is supposed to "
    "guarantee. Then paste the text below verbatim.", "Body"))

story.extend(instruction_block(INSTRUCTION_1))

story.extend(box([
    P("<b>Note on this text.</b>", "Body"),
    P("The build-time detail this instruction originally gave the auditor - \"over six "
      "days\" - was removed on 29 August, after Run 1 had already executed against the "
      "wording that included it. Recorded here rather than silently changed, per the "
      "project's practice of not editing history quietly.", "Body"),
], border_color=STEEL))

story.append(P("What a good result looks like", "H2"))
story.append(P(
    "Expect noise. A reviewer with no context will raise generic points — missing tests, "
    "absent type hints, broad exception handling — that may be true but are not what this "
    "run is for. The signal to watch for is narrower and worth reading carefully: a "
    "<b>serious problem that none of the 44 items would have caught</b>. That is the finding "
    "that matters, because it is evidence the register itself has a hole, and under the "
    "scope freeze that is the specific condition that permits the register to change.", "Body"))
story.append(P(
    "A second thing worth noting: if the reviewer says it cannot determine from the code "
    "alone whether the program can place trades, that is a real finding about the code's "
    "legibility, not a failure of the review. It was deliberately not told the answer.",
    "Callout"))

story.append(PageBreak())

# ============================================================
# 3. RUN 2
# ============================================================
story.append(P("3. Run 2 — Compliance Audit (Step 3)", "H1"))

story.append(P("Setup", "H2"))
story.append(P(
    "Open a <b>separate new conversation</b> — not a continuation of Run 1, and not a "
    "conversation that has previously discussed this project. Select Kimi K3 (Moonshot AI). "
    "Upload four files: the Constitution, the source, the audit package, and the evidence "
    "archive. Then paste the text on the next page verbatim.", "Body"))

# Notes precede the instruction here, unlike Run 1: Instruction 2 is nearly a full page on
# its own and cannot split, so anything placed after it would orphan onto a third page.
story.append(P("Notes on running it", "H2"))
story.append(P(
    "The full material is roughly 100,000 tokens of input. That fits comfortably in Kimi "
    "K3's context window, but if the model's replies begin referring vaguely to material it "
    "should be able to quote exactly, suspect truncation and check that all four files were "
    "actually received.", "Body"))
story.append(P(
    "If the audit stalls partway — a long register is a long task — asking it to continue "
    "from a named item is legitimate. Asking it to summarise, shorten, or skip ahead is not: "
    "an item without a recorded finding is an item the scope freeze still rests on.", "Body"))
story.append(P(
    "Expect this run to be long and to read as tedious. That is the correct shape for it: "
    "44 items, each needing a status and evidence. A short, fluent audit that reads well is "
    "the failure mode to watch for, not the success case.", "Callout"))

story.append(PageBreak())
story.extend(instruction_block(INSTRUCTION_2))

story.append(PageBreak())

# ============================================================
# 4. WHAT NOT TO DO
# ============================================================
story.append(P("4. Contamination Rules", "H1"))
story.append(P(
    "Each of these has a specific failure behind it, either in this project's own history or "
    "in the reasoning the Constitution was written to enforce.", "Body"))

rules = [
    ("Do not run Run 2 before Run 1.",
     "The blind review is available once. See the note on the first page."),
    ("Do not use a model that has already discussed this project.",
     "Grok reviewed the Constitution favourably on August 26 and was removed from the "
     "auditor plan partly for that reason — see Engineering Notes Entries #18 and #20. "
     "Gemini, ChatGPT and Copilot reviewed the document during drafting; Claude wrote it. "
     "All five are disqualified."),
    ("Do not tell the auditor what you are hoping it will find.",
     "This includes framing like “I think Item 17 is fine, but check it” and equally "
     "“I suspect the backtesting isolation is broken.” Both convert a test into a "
     "confirmation."),
    ("Do not let an Unknown be argued into a Compliant.",
     "Instruction 2 forbids it, but watch for it happening anyway — it usually appears as "
     "reasoning about what the code probably does rather than evidence of what it does. "
     "Under Item 8, Unknown is a legitimate result and does not need rescuing."),
    ("Do not treat agreement between auditors as validation.",
     "Revision 3 already corrected this document for making exactly that mistake about its "
     "own reviewers. If Run 1 and Run 2 agree, that is weak evidence. Where they "
     "<i>disagree</i> is the part worth reading twice."),
    ("Do not paste Claude's answers back to the auditor.",
     "Step 4a is Claude answering findings adversarially. Those answers go to Viktor, who "
     "adjudicates. Feeding them back to the auditor mid-audit turns an independent review "
     "into a negotiation."),
]
for title, body in rules:
    story.append(KeepTogether([P(f"<b>{title}</b>", "H2"), P(body, "Body")]))

story.append(PageBreak())

# ============================================================
# 5. AFTERWARDS
# ============================================================
story.append(P("5. After Both Runs", "H1"))

story.append(P(
    "Bring both results back to Claude in full — not summarised, and including anything that "
    "reflects badly on Claude's own work, which is the part most at risk of being trimmed on "
    "the way. What follows is defined by the Constitution, not by this document:", "Body"))

after = [
    ("Step 4a — Claude answers every finding adversarially.",
     "Including, and especially, findings against code Claude wrote. The standard is not "
     "whether a finding is convenient but whether it is correct."),
    ("Viktor adjudicates disagreements.",
     "Where Claude and an auditor disagree, neither resolves it internally. That decision "
     "is Viktor's, per Roles &amp; Authority."),
    ("The DEFECT row must receive a formal finding.",
     "The Minimum Viable Audit gate contradiction was recorded rather than repaired "
     "precisely so the auditor would resolve it. If Run 2 does not address it, ask again "
     "before closing the audit."),
    ("The scope freeze lifts only when every Tier 1 item has a recorded finding.",
     "Compliant, Non-compliant or Unknown — all three count. Fixes do not have to have "
     "landed. An item with no finding at all leaves the freeze in force."),
    ("Then, and only then, decide whether more runs are worth it.",
     "DeepSeek and GLM (Z.ai) remain available as further independent runs. Whether they "
     "add anything is a question the first two results answer. Adding auditors is easy and "
     "feels productive; answering findings honestly is the harder work and the part that "
     "improves the engine."),
]
for title, body in after:
    story.append(KeepTogether([P(f"<b>{title}</b>", "H2"), P(body, "Body")]))

story.append(Spacer(1, 8))
story.append(P(
    "Both instructions above, and the method behind them, get recorded in Engineering Notes "
    "once the audit has run — alongside the findings they produced, rather than in advance "
    "of them. An instruction written down before any result exists cannot say the one thing "
    "worth knowing about it: whether it worked.", "Callout"))

story.append(PageBreak())

# ============================================================
# 6. AMENDMENT — THE THREE-RUN SPLIT
# ============================================================
story.append(P("6. Amendment — Instruction 2 Split Into Three Runs", "H1"))
story.append(P("Added August 27, 2026, after the first attempt at Run 2", "MetaLine"))
story.append(Spacer(1, 6))

story.extend(box([
    P("<b>Why this section exists.</b>", "H2"),
    P("Section 2 above states that the exact wording given to the auditor is preserved here "
      "<i>rather than paraphrased</i>, because under Item 6 how the auditor was asked bears on "
      "what the auditor found. Instruction 2 was then changed before it was ever used. Recording "
      "the change is the whole point of having written the original down; leaving it unrecorded "
      "would have made Section 3 a description of an instruction nobody ran.", "Body"),
], border_color=MAROON)

)

story.append(P("What happened", "H2"))
story.append(P(
    "The first attempt at Run 2 was sent with Instruction 2 exactly as recorded in Section 3, to "
    "Kimi K3 with all five materials attached. It produced a 16,384-token reasoning trace and then "
    "stopped, having written no findings at all. The cause was not the model: OpenRouter's chat "
    "interface leaves Max Tokens unset by default and falls back to 16,384, and reasoning tokens "
    "are billed against that same ceiling. The auditor spent its entire output budget thinking and "
    "was cut off before the answer began.", "Body"))
story.append(P(
    "The trace was not wasted — it was read, and three of its claims were checked against the "
    "source and confirmed. But it contained no findings in the required schema, so it forms no "
    "part of the audit record. Settings were corrected (Max Tokens 64,000; reasoning enabled at "
    "maximum effort; OpenRouter's default system prompt cleared) and the audit was split.", "Body"))

story.append(P("The split", "H2"))
story.append(P(
    "Maximum reasoning effort across all 44 items risked the same truncation at a higher ceiling. "
    "Rather than lower the effort, the register was divided across three runs, each getting the "
    "full budget for a quarter of the work. The division follows the Constitution's own priority "
    "order rather than being invented for convenience: the Minimum Viable Audit gate first, the "
    "remaining Tier 1 invariants second, Tiers 2 to 4 third.", "Body"))
story.append(P(
    "Everything in Instruction 2 stays byte-identical across all three runs except the YOUR TASK "
    "paragraph, reproduced below in each of its three forms, plus one addition to the Evidence "
    "field noted after them. The DEFECT clause appears in Run A only, and is dropped from B and C "
    "once Run A has resolved it.", "Body"))

story.append(KeepTogether(
    [P("Run A — Minimum Viable Audit gate", "H2")] + instruction_block(
        "This run covers the Minimum Viable Audit gate ONLY: Item 2 (Look-Ahead\n"
        "Bias), Item 3 (Data Integrity), Item 6 (Traceability) and Item 18\n"
        "(Read-Only Market Access), plus the DEFECT row resolution described\n"
        "below. Do not proceed to the remaining Tier 1 invariants or to Tiers 2\n"
        "to 4 - those are separate runs. Spend the depth you would have spent\n"
        "across 44 items on these four instead.")))

story.append(KeepTogether(
    [P("Run B — remaining Tier 1 invariants", "H2")] + instruction_block(
        "This run covers the Tier 1 invariants OUTSIDE the Minimum Viable Audit\n"
        "gate: Items 1, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20 and\n"
        "21. Items 2, 3, 6 and 18 were audited in a separate run and are out of\n"
        "scope here - do not re-audit them. Do not proceed to Tiers 2 to 4; those\n"
        "are a separate run.")))

story.append(KeepTogether(
    [P("Run C — Tiers 2 to 4", "H2")] + instruction_block(
        "This run covers Tiers 2, 3 and 4 only - the 7 architectural principles,\n"
        "the 10 process disciplines and the 6 stated preferences. All 21 Tier 1\n"
        "invariants were audited in earlier runs and are out of scope here.")))

story.append(P("One addition to the Evidence field, from Run B onward", "H2"))
story.extend(box([
    P("<b>A withdrawn accusation, kept here rather than deleted.</b>", "Body"),
    P("This section originally justified the addition below with a claim that Run A's auditor had "
      "invented a citation — that it reported "
      "<font face=\"Courier\">[ERROR] Insufficient data</font> entries firing on the 1h and 1w scans "
      "which existed nowhere. That was wrong. The entries appear fourteen times in "
      "<font face=\"Courier\">scan_summary_report.txt</font>, one of the two evidence files supplied, "
      "each directly beneath an <font face=\"Courier\">ASSET / TIMEFRAME</font> header reading 1h or "
      "1w. The auditor's claim was correct in every particular, including the 1h/1w detail; it named "
      "the wrong file, and its own reasoning trace names the right one. Claude had searched "
      "<font face=\"Courier\">phase7_engine.log</font> alone and concluded from that one search that "
      "the string did not exist — the same error, made hours apart, that produced the Layer 5 "
      "falsehood in the Step 2a package. The accusation is withdrawn.", "Body"),
], border_color=MAROON))
story.append(P(
    "The addition originally drafted told the auditor not to infer log entries from format strings in "
    "the source. That was aimed at a fabrication that never happened, and it carried a cost: an "
    "auditor warned off citing logs cites fewer of them, and Run A's log work was among its most "
    "useful. The error that did occur was one of attribution — two evidence files were supplied and "
    "the wrong one was named — and the checker was misled because he searched only the file the "
    "auditor named. So the addition from Run B onward is narrower, and asks for the thing that would "
    "have prevented the whole episode:", "Body"))
story.extend(instruction_block(
    "When you cite a log line, name which of the supplied files it is in."))
story.append(P(
    "Run 1's unverified citation — a specific issue in a third-party library's tracker — is a separate "
    "matter and remains unverified rather than disproved. One unverified citation is not a pattern, "
    "and no instruction is added on its account.", "Body"))
story.append(P(
    "The DISCLOSURE paragraph also gains one sentence from Run B onward, since by then it is a fact "
    "rather than a caution: <i>At least one factual claim in that package has already been shown "
    "false by an earlier run; assume there may be others.</i> That refers to Section 5.2 of the Step "
    "2a package, which stated that Roadmap Layer 5 did not appear anywhere in the nineteen files "
    "under that name. It appears three times. Run A found it.", "Body"))

story.append(Spacer(1, 6))
story.extend(box([
    P("<b>What this amendment does not do.</b>", "Body"),
    P("It changes no rule, resolves no finding, and does not alter the register, which stays frozen "
      "at 21 / 7 / 10 / 6. Splitting an audit across three sessions is a scheduling decision forced "
      "by a token ceiling, not a judgement about scope. Every one of the 44 items still requires a "
      "recorded finding, and the freeze still lifts only when all 21 Tier 1 items have one.", "Body"),
]))

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=LETTER,
    leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.85*inch,
    title="Phase-7 Audit Execution Instructions")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Built: {OUTPUT_PATH}")
