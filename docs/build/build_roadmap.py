#!/usr/bin/env python3
"""
Builds the Phase-7 Roadmap — where the project stands after the audit and what
happens next, in order. A working document: it changes no rule and records no
finding. It exists so the sequence survives being put down and picked up again.
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

OUTPUT_PATH = "/tmp/outputs/Phase7_Roadmap.pdf"

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
styles.add(ParagraphStyle(name="PhaseNum", fontName="Helvetica-Bold", fontSize=13,
    leading=16, textColor=colors.white, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="PhaseTitle", fontName="Helvetica-Bold", fontSize=12,
    leading=15, textColor=colors.white))
styles.add(ParagraphStyle(name="PhaseTag", fontName="Helvetica-Bold", fontSize=8.2,
    leading=11, textColor=colors.white, alignment=2))


def P(text, style="Body"):
    return Paragraph(text, styles[style])


def cell(text, header=False):
    return Paragraph(text, styles["CellHeader" if header else "Cell"])


def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    width, _ = LETTER
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(0.75 * inch, 0.55 * inch, "Phase-7 Roadmap")
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


def phase_header(letter, title, tag, accent):
    data = [[
        Paragraph(letter, styles["PhaseNum"]),
        Paragraph(title, styles["PhaseTitle"]),
        Paragraph(tag, styles["PhaseTag"]),
    ]]
    t = Table(data, colWidths=[0.42 * inch, 4.28 * inch, 1.8 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, -1), STEEL),
        ("BACKGROUND", (2, 0), (2, -1), accent),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    return [t, Spacer(1, 8)]


story = []


story = []

# ============================================================
# COVER
# ============================================================
story.append(P("Phase-7 Structural Quant Engine", "ReportSubtitle"))
story.append(P("Roadmap", "ReportTitle"))
story.append(P("Revision 2 — August 29, 2026. Supersedes the August 28 edition.", "MetaLine"))
story.append(P("Status: <b>working document.</b> Changes no rule, records no finding.", "MetaLine"))
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#c7cfda")))
story.append(Spacer(1, 10))

story.extend(box([
    P("<b>The one-line version.</b>", "H2"),
    P("Make the audited state recoverable and the engine startable, build the measurement "
      "apparatus the findings themselves presuppose, strip dead complexity, fix the three "
      "Criticals, then reshape contracts and output truthfulness — and only then the backtest "
      "on-ramp and an independent re-audit. Severity decides which items belong to the gate "
      "sets. It does not decide their position.", "Body"),
]))

story.extend(box([
    P("<b>What changed since Revision 1.</b>", "Body"),
    P("Phase A is <b>done</b> — the harness exists, runs, and is published. Running it found "
      "three defects four audit passes had missed. Step 5 has since run on GLM 5.3 and returned "
      "a sixteen-item sequence, which replaces this document's earlier four-phase sketch. "
      "Machine learning has been put <b>on ice</b> by decision, with written conditions for "
      "revisiting. The earlier edition's dateline was wrong and is corrected here.", "Body"),
], border_color=GREEN))

# ============================================================
# WHERE WE ARE
# ============================================================
story.append(P("Where the project stands today", "H1"))

story.append(P(
    "The Constitution was ratified on August 26 and audited on August 27 — four runs through "
    "OpenRouter, using models with no prior involvement in the project, at roughly one dollar "
    "each. All 44 rules carry a recorded finding. The scope freeze lifted when the last Tier 1 "
    "item was graded, and three amendments were adopted the same day.", "Body"))

state_rows = [
    ["", "Compliant", "Non-compliant", "Unknown", "Total"],
    ["Tier 1 — invariants", "10", "10", "1", "21"],
    ["Tier 2 — architecture", "3", "4", "0", "7"],
    ["Tier 3 — process", "3", "3", "4", "10"],
    ["Tier 4 — preferences", "5", "0", "1", "6"],
    ["<b>Total</b>", "<b>21</b>", "<b>17</b>", "<b>6</b>", "<b>44</b>"],
]
data = [[cell(c, header=(i == 0)) for c in r] for i, r in enumerate(state_rows)]
t = Table(data, colWidths=[2.3 * inch, 1.05 * inch, 1.25 * inch, 0.95 * inch, 0.95 * inch],
          repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, LIGHT_BG]),
    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e6ebf2")),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

story.append(P("The three Critical findings", "H2"))
crit = [
    ("Item 3 — Data Integrity",
     "Nothing detects missing candles, duplicates, impossible prices, bad timestamp ordering, "
     "stale data or abnormal volume. Defects are silently filled in by ffill/bfill rather than "
     "caught, so the engine cannot tell “no defect found” from “defect fabricated away.”"),
    ("Item 11 — No Circular Reasoning",
     "trend_health is counted at least four times: 30% of bias_score, again directly in "
     "confidence, again as the whole base of validation_score, and again as Current Market. "
     "The panel presents one number as four agreeing signals."),
    ("Item 13 — Fail Safely",
     "When an indicator fails, the engine substitutes confident-looking constants — RSI 50, "
     "ADX 25, SuperTrend direction 1.0 — with no marker anywhere. A failed SuperTrend silently "
     "adds a permanent +15 bullish vote to the bias score."),
]
for title, body in crit:
    story.append(KeepTogether([P(f"<b>{title}</b>", "H2"), P(body, "Body")]))

story.append(Spacer(1, 6))
story.extend(box([
    P("<b>The release gate now in force.</b>", "Body"),
    P("No output of this engine may be relied on for a real trading decision while any Critical "
      "Tier 1 finding stands unresolved, and backtesting does not begin until Items 2, 3, 6 and "
      "18 are all Compliant. Running the engine to look at is fine. Acting on it is not.", "Body"),
], border_color=MAROON))

story.append(PageBreak())

# ============================================================
# WHAT PHASE A FOUND
# ============================================================
story.append(P("What Phase A found, and why it changed the ordering", "H1"))
story.append(P(
    "The harness was built to make the fixes safe. Its first real run found defects instead — "
    "three that four audit passes across three models had all missed, because every one of "
    "those passes read the code and none of them ran it.", "Body"))

found_rows = [
    ["Finding", "Status", "Where it lands"],
    ["<b>The repository does not start from a fresh clone.</b> main.py builds its log handler at "
     "module scope (line 16) and creates Logs/ inside main() (line 41). FileHandler opens "
     "eagerly, so import fails before the try/except that would catch it.",
     "Severity correction — Run 1 found the ordering and called it soft. It is not soft.",
     "Item 2 of the sequence, merged into T2-6"],
    ["<b>AERO is hardcoded into user-facing reasoning text</b> at decision_model.py 411, 413 and "
     "419, and panel_render.py:83. Run the engine on SOLUSDT and the explanation talks about "
     "AERO; run it on BTCUSDT and it compares BTC to itself.",
     "Unrated — no register run examined explanation-text provenance. Contradicts Run C's "
     "Compliant on T4-2: true of the arithmetic, false of the prose.",
     "Item 12, under Item 6 (traceability)"],
    ["<b>“relationship relationship”</b> — decision_model.py:419 appends the word to a label "
     "that already ends in it.",
     "Unrated. Minor, cosmetic, one line.",
     "Item 12, rides the same strings"],
]
data = [[cell(c, header=(i == 0)) for c in r] for i, r in enumerate(found_rows)]
t = Table(data, colWidths=[3.1 * inch, 2.05 * inch, 1.35 * inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 8))
story.append(P(
    "<i>The lesson is not that three models read badly. It is that reading and running are "
    "different instruments, and the project had been buying more of the first while owning none "
    "of the second.</i>", "Callout"))

story.append(PageBreak())

# ============================================================
# THE SEQUENCE
# ============================================================
story.append(P("The sequence", "H1"))
story.append(P(
    "Sixteen items, produced by Step 5 and verified against source. The organising principle is "
    "not severity: <b>position is set by what has to exist before a fix can be proven correct, "
    "and by which edits share a seam.</b> Severity decides membership in the gate sets.", "Body"))
story.append(Spacer(1, 6))
story.extend(box([
    P("<b>The sentence the whole ordering rests on.</b>", "Body"),
    P("A fix made before its apparatus exists can be <i>made</i>, never <i>resolved</i> — "
      "because “resolved” under the finding schema requires a Verification field, and the "
      "release gate requires resolution. That is why the apparatus phase is not process hygiene "
      "sitting in front of the real work. It is the gate-opener.", "Body"),
], border_color=STEEL))

seq = [
    ("0", "Adjudications and registrations", "PROCESS — VIKTOR", MAROON, [
        "Four rulings, two of which change the ordering. The two unrated harness findings enter "
        "the formal record here or get lost the way soft-rated defects already were.",
        "<b>Depends on</b> nothing. <b>Unblocks</b> stable positions for items 12 and 13, and "
        "the minimum gate-opening set. <b>Effort</b> small.",
    ]),
    ("1", "T3-7 — a known-good checkpoint", "FLOOR", GREEN, [
        "One git tag on the audited commit. The repository has 23 commits and zero tags, so "
        "there is currently no return point, and re-audit diffs have nothing to compare against.",
        "<b>Risk of not doing it:</b> the first bad change becomes archaeology. <b>Effort</b> "
        "small — a tag is metadata.",
    ]),
    ("2", "T2-6 — controlled dependencies, and the clone failure", "FLOOR", GREEN, [
        "Two mechanisms, one outcome. requirements.txt omits <font face=\"Courier\">requests</font> "
        "(which data_fetcher imports, so the first import fails) and "
        "<font face=\"Courier\">colorama</font>; it declares <font face=\"Courier\">ccxt</font>, "
        "which appears nowhere else in the codebase and is execution-capable. Separately, the "
        "log handler is built before the directory exists.",
        "<b>Position:</b> second, because nothing downstream is verifiable from a clean "
        "environment until the engine runs. <b>Effort</b> small. The harness's clone test becomes "
        "the regression guard.",
    ]),
    ("3", "Pinned-data path and archived datasets", "APPARATUS", STEEL, [
        "<font face=\"Courier\">load_csv</font> exists but nothing wires it in — "
        "<font face=\"Courier\">get_tf</font> always fetches live, so the engine cannot currently "
        "produce two comparable runs, and even T2-4's own prescribed verification is impossible.",
        "Inject a source at get_tf covering all three series the engine fetches — base, macro 1d, "
        "and BTC context — or runs stay network-dependent. <b>Effort</b> small-medium. Closes "
        "T3-5's Unknown as a side effect.",
    ]),
    ("4", "T3-3 / T3-4 stage 1 — bring the harness in", "APPARATUS", STEEL, [
        "The harness currently lives outside the nineteen-file source. Bring it in as the suite "
        "skeleton, add a smoke run on pinned data and grep guards for ccxt and credential "
        "patterns, and begin commit-per-change with dated notes — the remediation then generates "
        "the evidence that later closes T3-1, T3-2 and T3-8.",
        "No CI exists in the repository. Do not assume it; a locally green suite is the standard. "
        "<b>Effort</b> medium.",
    ]),
    ("5", "Item 16 — delete unconsumed complexity", "APPARATUS", STEEL, [
        "Before the golden pin, so the baseline does not enshrine dead code. Delete the Bollinger "
        "trio, KAMA and its slope, DIP/DIM, Typical_Price, the unreachable VWAP plot branch, "
        "compute_exit, the dead TARGET-HIT colour branches, the unreachable hysteresis branches "
        "in _detect_regime, and the stale roadmap comments describing code that no longer exists.",
        "<b>VWMA stays</b> — entry_model consumes it for distance scoring. <b>Verification:</b> "
        "deleting unconsumed code is provable by output-invariance on pinned data. <b>Effort</b> "
        "small-medium.",
    ]),
    ("6", "T2-1 and cache removal — shared-frame aliasing", "APPARATUS", STEEL, [
        "calculate_dynamic_bias rewrites its caller's columns in place. The indicator cache "
        "mutates cached frames, and its key embeds the last close in a per-process dict — so it "
        "can never hit across runs at all.",
        "<b>Deleting the cache is cheaper than repairing the key</b>, and it dissolves the open "
        "Items 4 / 12 dispute by repair rather than adjudication. <b>Effort</b> small.",
    ]),
    ("7", "T3-4 stage 2 — the golden baseline", "APPARATUS", STEEL, [
        "Captured after cleanup and before any semantic change, so every later delta is "
        "attributable to exactly one controlled change. Exclude chart PNGs (unstable hashes); "
        "make any uninjected fetch fail deterministically — the data_fetcher singleton binds "
        "base_url at import, so patch the instance, not just config.",
        "<b>Effort</b> small. Without this, the Item 11 and 13 fixes are unprovable as “changed "
        "exactly as intended.”",
    ]),
    ("8", "Item 3 — Data Integrity", "CRITICAL", MAROON, [
        "First Critical because it is upstream: no downstream number is trustworthy while "
        "garbage enters silently. The validation gate must sit in fetch_ohlc <b>before</b> the "
        "close_time column is discarded — the raw response carries it and throws it away one "
        "line later, and staleness checks need it.",
        "Reject, do not fabricate. A failed macro timeframe renders UNAVAILABLE, never NEUTRAL — "
        "a fabricated neutral is a directional vote at 10% weight. <b>Effort</b> medium. The "
        "eight corrupted fixtures are already written.",
    ]),
    ("9", "Items 13 + 8 — fail safely, merged", "CRITICAL", MAROON, [
        "One defect family reported under two invariants. Delete the fabrication constants — "
        "RSI 50, ADX 25, ATR at 2% of price, SuperTrend = close, ST_Direction 1.0, the "
        "trend_health 50.0 defaults, risk_model's direction-blind except-return — and let "
        "failures reach the existing error path.",
        "<b>A decision for Viktor sits here:</b> halt on failure, or degrade with a flag and cut "
        "confidence. Step 5 declined to choose, on the stated grounds that its preference for "
        "the simpler branch is a habit it shares with the model family that built this engine. "
        "<b>Effort</b> medium.",
    ]),
    ("10", "T2-3 — the decision-object contract", "SHAPE", AMBER, [
        "Between the shape-neutral Criticals and the reshaping items, because 11 through 13 add, "
        "remove and rename fields — and renaming without a net is this codebase's demonstrated "
        "failure mode: a rename once broke fourteen modules at once.",
        "mypy does not exist in the repository. Adding it is apparatus belonging to this item. "
        "<b>Effort</b> medium.",
    ]),
    ("11", "Item 11 — no circular reasoning", "CRITICAL", MAROON, [
        "Third Critical, sequenced after 8 and 9 so the score being de-circularised is computed "
        "on validated, non-fabricated data — otherwise the golden deltas conflate two causes. "
        "Remove trend_health from _compute_confidence (it is already inside bias_strength at "
        "0.30), rebase validation_score, and delete the redundant renderings rather than "
        "inventing distinct metrics.",
        "<b>Coupling rule:</b> the reason strings change in the same commit. Prose describing the "
        "old formula is an Item 8 regression the moment the number changes. <b>Effort</b> medium.",
    ]),
    ("12", "Items 5 + 6 — reproducibility and traceability", "SHAPE", AMBER, [
        "Implement the decision log the panel already claims exists. Make “Trade logged” name a "
        "file that provably exists; fix the chart path printing None; stamp engine_version, which "
        "exists in config and is written nowhere; add Item 7's epistemic label; replace the "
        "hardcoded AERO with the run's symbol; fix the doubled word.",
        "<b>Position is conditional on the Item 6 ruling</b> — sequenced here under the stricter "
        "reading. A Major ruling swaps this with item 13. <b>Effort</b> medium.",
    ]),
    ("13", "Item 14 — risk is not conviction", "SHAPE", AMBER, [
        "Remove the risk_score / signal_strength aliases; remove bias_factor from stop_mult — "
        "conviction currently tightens stops arithmetically, which is Item 14's prohibition "
        "written as code; wire volatility_state into calculate_stop_targets, which engine_core "
        "omits, leaving the HIGH and EXTREME widening tiers permanently inert; normalise the "
        "inverted entry zone at source.",
        "<b>Effort</b> small-medium. Stop distances will change — intended, but review it as a "
        "scan diff rather than merging silently.",
    ]),
    ("14", "T2-4 — explicit configuration", "SHAPE", AMBER, [
        "After the deletions, so knobs are not wired to indicators just removed. Config declares "
        "CHART_HEIGHT 10 and CHART_DPI 150 while plotting hardcodes 8 and 200 — wiring it changes "
        "chart artifacts, visibly and intentionally.",
        "<b>Effort</b> small; near-zero risk on the decision path, since config values equal the "
        "current hardcodes. Assert via golden invariance.",
    ]),
    ("15", "Item 2's standing caveat — bfill quarantine", "BACKTEST ON-RAMP", STEEL, [
        "Last code item, because nothing in the live path reads it — the decision row is always "
        "the last bar — and because its verification apparatus, re-computing historical decisions "
        "on truncated data, exists in no form and is itself half a backtester.",
        "<b>The backtest gate's letter does not require Items 11 and 13 fixed.</b> This plan "
        "fixes them earlier anyway: backtesting an engine with double-counted confidence "
        "manufactures precisely the false validation Item 7 exists to prevent. <b>Effort</b> "
        "medium.",
    ]),
    ("16", "Step 8 — independent re-audit, scoped to what changed", "RE-AUDIT", GREEN, [
        "Terminal, and it belongs to an independent auditor rather than the party that made the "
        "fixes. Scope it to changed items with artifact evidence — panel screenshots, test "
        "output, log files — per the Evidence discipline.",
        "<b>This is where the release gate formally opens.</b> Item 15 stays Unknown until "
        "backtesting exists; that is the honest status, not a lapse. <b>Effort</b> small.",
    ]),
]

for num, title, tag, accent, paras in seq:
    block = phase_header(num, title, tag, accent)
    for pr in paras:
        block.append(P(pr, "Body"))
    block.append(Spacer(1, 4))
    story.append(KeepTogether(block))

story.append(PageBreak())

# ============================================================
# THE MERGES AND THE DELETIONS
# ============================================================
story.append(P("Four findings that are one defect reported twice", "H1"))
story.append(P(
    "The invariants stay distinct for re-audit purposes. The <i>edits</i> merge — which is why "
    "seventeen Non-compliances do not mean seventeen pieces of work.", "Body"))

merge_rows = [
    ["Reported under", "The single underlying defect", "Fixed at"],
    ["Items 5, 6 and 8(b)", "The phantom trade log — the panel announces a CSV that no code "
     "writes, every run.", "item 12"],
    ["Item 3, Item 8(a), Item 13, blind-run finding 2",
     "The fabricated fallback constants.", "item 9"],
    ["Item 10(c) and Item 14(a)", "The risk_score / signal_strength aliasing.", "item 13"],
    ["Item 11, Item 10(a), Item 14(b)",
     "trend_health overloading — one quantity doing four jobs, rendered three times, and the "
     "validation gate rebasing that follows from fixing it.", "item 11"],
]
data = [[cell(c, header=(i == 0)) for c in r] for i, r in enumerate(merge_rows)]
t = Table(data, colWidths=[1.85 * inch, 3.6 * inch, 1.05 * inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 6))
story.append(P(
    "Item 8 — Epistemic Honesty — has no unique remediation work of its own. It is the parent "
    "principle whose every concrete instance is co-reported elsewhere, and its re-audit rides "
    "items 9 and 12.", "Body"))

story.append(P("Five things cheaper to delete than to repair", "H1"))
story.append(P(
    "Deletion is a legitimate remedy, not a shortcut — and all five are git-reversible and "
    "provable by output-invariance.", "Body"))
for a, b in [
    ("Item 16's dead indicators", "wiring them would be new-feature work"),
    ("compute_exit", "wiring it presupposes a held-position concept the engine deliberately "
     "lacks, and exit_watch already performs the advisory role"),
    ("The indicator and structure caches", "they never hit across runs; deletion removes the "
     "stale-serving hazard and the mutation hazard at zero functional cost"),
    ("The fabricated fallbacks", "cheaper than building a degraded-mode subsystem — though this "
     "is the decision Step 5 handed to Viktor rather than making"),
    ("The redundant MOMENTUM and Current-Market lines", "deleting is honest; inventing distinct "
     "underlying metrics to justify them is new-feature work"),
]:
    story.append(P(f"<b>{a}</b> — {b}.", "Body"))

story.append(PageBreak())

# ============================================================
# OPEN DECISIONS
# ============================================================
story.append(P("Open decisions — all Viktor's", "H1"))
story.append(P(
    "Two of these change the ordering, which is why Step 5 puts them at position zero rather "
    "than leaving them to be settled along the way.", "Body"))

dec_rows = [
    ["Decision", "The disagreement", "What it changes"],
    ["<b>Item 6 severity</b>",
     "Claude says Critical, the auditor says Major. The panel tells the operator a trade was "
     "logged to a file that no code writes, on every run.",
     "<b>Ordering.</b> Swaps items 12 and 13, and changes the minimum set that opens the "
     "release gate."],
    ["<b>Item 13 — halt or degrade</b>",
     "When an indicator fails: stop and emit an error, or keep computing while marked degraded "
     "with confidence cut? Step 5 declined to choose and flagged its own preference as "
     "correlated with the model family that built the engine.",
     "<b>Scope of item 9.</b> Halting adds no machinery; degrading is the richer repair and the "
     "auditor's stated Required action."],
    ["<b>Item 2 reasoning</b>",
     "Compliant stands either way. But “backward fill cannot affect the decision” is too strong "
     "— input-side bfill reaches the final bar through recursive indicators.",
     "Force, not order. Upholding it makes item 15 mandatory for the backtest gate rather than "
     "advisory."],
    ["<b>Items 4 and 12</b>",
     "Auditor says Compliant, Claude says Non-compliant, over a cache key that includes the last "
     "close but not the bar's high, low or volume.",
     "<b>Possibly nothing.</b> Deleting the cache at item 6 makes both readings true. The "
     "dispute dissolves by repair and spends none of the adjudication budget."],
    ["<b>Item 20 amendment</b>",
     "Item 20 does not name crash-reporter capture of the process environment.",
     "Blocked on a reviewer who is not Claude — the amendment-control rule adopted on August 27 "
     "applies to the party that wrote it."],
]
data = [[cell(c, header=(i == 0)) for c in r] for i, r in enumerate(dec_rows)]
t = Table(data, colWidths=[1.3 * inch, 2.8 * inch, 2.4 * inch], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7cfda")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

story.extend(box([
    P("<b>The smallest set that opens the release gate.</b>", "Body"),
    P("The clone fix (item 2); the thin apparatus slice — pinned dataset, corrupted fixtures, "
      "fault injection, one golden baseline; Item 3; Item 13; Item 11; Item 6 under the "
      "conservative reading — <i>or</i> a Major ruling, which removes it at zero code cost, "
      "making the adjudication itself part of the minimal path. Then a scoped independent "
      "re-audit, because “resolved” is not self-declared.", "Body"),
    P("<b>One honesty caveat:</b> the phantom “Trade logged” line is a one-line deletion whose "
      "exclusion would leave the panel lying on the very first run anyone relies on. Include it "
      "regardless of what the minimal set technically requires.", "Body"),
], border_color=GREEN))

story.append(PageBreak())

# ============================================================
# PHASE D — ON ICE
# ============================================================
story.extend(phase_header("D", "AI and machine learning", "ON ICE", GREY))

story.extend(box([
    P("<b>Parked by decision on August 29, 2026 — not cancelled.</b>", "Body"),
    P("The conditions for revisiting are written down below so that the decision can be "
      "revisited on evidence rather than on enthusiasm. This section is kept in full because "
      "the reasoning is the useful part.", "Body"),
], border_color=GREY))

story.append(P("Can you add an LLM?", "H2"))
story.append(P(
    "<b>Yes, easily.</b> It would read the panel and explain it. But the panel currently shows "
    "one number three times and calls it three signals — so the LLM would confidently describe "
    "agreement that isn't there. It would hide the bugs, not find them.", "Body"))
story.append(P(
    "Architecturally it is straightforward: an LLM layer sits outside the decision path and "
    "touches no invariant about execution or authority. The problem is epistemic rather than "
    "technical. Fluent commentary over defective numbers is worse than no commentary, because it "
    "makes the defect harder to notice. This becomes reasonable after item 11, not before it.",
    "Body"))

story.append(P("Can you add machine learning?", "H2"))
story.append(P(
    "<b>Yes, eventually.</b> The obvious use is fitting your six bias weights "
    "(0.30 / 0.20 / 0.15 / 0.15 / 0.10 / 0.10) against real outcomes instead of choosing them by "
    "hand.", "Body"))
story.append(P(
    "Those weights are currently judgment calls. Fitting them is a legitimate, modest, testable "
    "application — and it needs labelled outcomes, which need a backtester. There is no shortcut "
    "around that ordering.", "Body"))

story.append(Spacer(1, 4))
story.extend(box([
    P("<b>The trap that kills these projects.</b>", "Body"),
    P("Training a model means evaluating at historical decision points, which is precisely what "
      "converts the dormant backward-fill leak into a live one. The model would learn from "
      "information that did not exist at the time. It would look excellent in testing and be "
      "worthless in use — and the failure is silent, because a leaking model produces beautiful "
      "results rather than obvious errors. The leak is already installed and already documented. "
      "Removing it is cheap now and expensive to diagnose later.", "Body"),
], border_color=MAROON))

story.append(P("Three further reasons, found by checking the source", "H2"))
story.append(P(
    "<b>The training data does not exist.</b> live_trading.py:210 does persist a decision as a "
    "JSON file, but nothing anywhere records what price did afterward, and engine_core.py:466 "
    "overwrites its state file each run rather than accumulating. Decisions without outcomes are "
    "unlabelled examples.", "Body"))
story.append(P(
    "<b>Item 11 makes fitted weights worse, not better.</b> Fitting over features that are "
    "secretly the same feature produces large offsetting coefficients that swing on tiny data "
    "changes. Hand-picked weights on collinear inputs are crude; fitted weights on collinear "
    "inputs are crude and wearing a lab coat.", "Body"))
story.append(P(
    "<b>Item 13's sentinels would become learned signal.</b> RSI = 50 means the indicator broke. "
    "A model trained on that learns to predict from failure markers.", "Body"))

story.append(P("Conditions for taking it off ice — all five", "H2"))
for n, txt in [
    ("1", "Items 2, 3, 11 and 13 fixed <b>and verified by the harness</b>."),
    ("2", "A working decision <i>and</i> outcome log, with real accumulated history."),
    ("3", "A backtester validated against known-answer cases."),
    ("4", "A kill condition written down <b>before</b> the first fit — already a Constitution "
     "amendment candidate."),
    ("5", "An out-of-sample test that beats the current hand weights. If it does not, that is a "
     "real result: it means the hand weights were fine."),
]:
    story.append(P(f"<b>{n}.</b> {txt}", "Body"))

story.append(Spacer(1, 4))
story.extend(box([
    P("<b>What to stay suspicious of.</b>", "Body"),
    P("Machine learning feels like the milestone that makes a project serious. That instinct is "
      "precisely what the Constitution was written to catch. It is also worth noting that "
      "fitting six coefficients is a small regression, grid-searchable by hand once outcome data "
      "exists — calling it machine learning oversells what it is. ML earns its place only for "
      "interactions the hand weights cannot express, and that needs far more data than six "
      "weights do.", "Body"),
], border_color=GREY))

story.append(P("What has to happen to the Constitution before any of this", "H2"))
story.append(P(
    "Nineteen proposed invariants were declined on August 27 — multiple-testing correction, "
    "out-of-sample validation, calibration monitoring, regime and distribution-shift handling, "
    "statistical uncertainty on point estimates — on the correct grounds that they constrain a "
    "system with backtesting and execution that this engine does not have.", "Body"))
story.append(P(
    "Every one of them becomes load-bearing the day machine learning enters. Feature selection "
    "and parameter search across a few hundred four-hour candles is a machine for manufacturing "
    "false discoveries, and those rules are the defence against it. They are recorded in Future "
    "Amendment Candidates. Pull them back in <i>before</i> the first line of model code, not "
    "after the first promising result — the point at which a fitted model looks good is the "
    "worst possible moment to start negotiating with the rules that would invalidate it.", "Body"))

story.append(PageBreak())

# ============================================================
# CLOSING
# ============================================================
story.append(P("What this roadmap deliberately does not include", "H1"))
story.append(P(
    "No new features. Nothing is added to the engine anywhere in items 1 through 15 — every one "
    "is a repair, a test, or a piece of measurement apparatus. The engine gets smaller and more "
    "honest before it gets larger.", "Body"))
story.append(P(
    "No date estimates. The engine was built fast and audited once. Guessing how long sixteen "
    "items take, in a codebase whose test suite is four days old, would be the same kind of "
    "confident number the audit spent all day objecting to. Effort is stated as small, medium or "
    "large and nothing finer.", "Body"))
story.append(P(
    "No claim that this ordering is the only defensible one. Step 5 named two places where a "
    "second ordering is arguable and gave the trade-off rather than picking silently: doing "
    "Item 11 before the decision-object contract would open the release gate one item sooner, at "
    "the cost of renaming fields without a net in the codebase where exactly that once broke "
    "fourteen modules.", "Body"))
story.append(Spacer(1, 6))
story.append(P(
    "<i>The sequence is the point. Each item exists to make the next one measurable — the "
    "apparatus makes the fixes provable, the fixes make the backtester meaningful, and the "
    "backtester is what would make machine learning something other than a guess with better "
    "presentation.</i>", "Callout"))

doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=LETTER,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.85 * inch,
    title="Phase-7 Roadmap")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Built: {OUTPUT_PATH}")
