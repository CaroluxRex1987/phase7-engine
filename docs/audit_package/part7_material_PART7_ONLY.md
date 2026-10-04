# Material for Part 7

*Written for the Part 7 pass of round 7, 30 September 2026, drafted by Claude and checked
by the project owner before that round's send. Round 7 never reached its Part 7 pass, so
no reviewer has been sent this document before you. Corrected for round 8 on 4 October
2026, by Claude under the project owner's delegation of this audit, only where it named
round 7 as its own round and where a later ruling made a sentence untrue (Section 2, the
threshold): the list, each entry's classification and what "found" means for each entry
are unchanged. Section 12 of your instruction said the second message would say what this
document is. This is that statement.*

**Every entry in Section 3 was known to the project before your package was sent, and
none has been fixed. Some are named in code comments you read (Section 3.2). Four of the
others are what your Parts 1–6 are measured against, and nothing in your first message
named them. That was deliberate.** Parts 1–6 were saved and committed before this
message was sent. Nothing below changes them, and nothing you write from here on counts
toward that measure.

Your instruction said nothing untrue about this. It left it out, because a reviewer who
knows it is being measured against a hidden list reads differently from one that does
not. The rest of this document says what the list is, how Parts 1–6 are measured
against it, and what else the project decided to show you only now.

Line numbers were read at commit `01f2892`, 30 September 2026. The engine code and the
tests have not changed between that commit and the tagged commit your package was built
from; this was checked before round 7's send, and again on 4 October 2026 for this one.

---

## 1. Why the list exists, and why it was held back

On 22 September 2026 the project closed its list of work to finish before this audit. It
ruled that anything found after that date would be written down and would wait until
after the audit, rather than growing the list. Most entries in Section 3 were found after
that, between 26 and 30 September. Three (N4, N5 and O1) come from questions asked on
15 September (Section 5), which the project set aside with its other open items on
20 September and moved onto the list on 29 September.

**None was left unfixed in order to test you.** Each was deferred for another reason
first: most under the 22 September ruling, three when the open items were set aside on
20 September. On 29 September the project decided to measure the audit against
the ones already on the list. That measure was committed before round 7 was sent, and
this round is measured by it unchanged. The project rejected the alternative, which was
to plant defects in a copy of the code, for three reasons. The package would no longer be
the repository tree that its SHA-256 manifest claims. Your instruction would have had to warn you that
planted defects might exist. And with about five seeds the result would be very rough:
three found out of five fits anything from about 15% to 95%.

Section 4a of your instruction describes an earlier round in which the project decided
*not* to leave known defects in place to measure an auditor. This round differs in the
order of events: the defects were deferred first, for the reasons above, and the decision
to measure you against them came afterwards. Whether that difference matters is for you
to judge.

---

## 2. How Parts 1–6 are measured

This rule, the list and each entry's classification were committed before round 7's
send, on 29 and 30 September, so that none of it can be adjusted after a report is read.
One thing has been ruled since: how many runs an auditor gets (the threshold, below),
decided after round 7's first run was scored. It changes no entry, no classification and
no "found" sentence. The rule and the first classification are in the project's
decision record (29 September). The entries added
since then, and what "found" means for each of S1–S4, are in this document, which was
committed before round 7's send; the correction for this round changed none of them.

- **What counts:** only the defects on the list for after the audit (Section 3). New
  trading rules on that list are design choices, not defects, and do not count.
- **Usable:** still in the code you were sent, *and* nothing in your package gives it
  away. A code comment, docstring or test name that names the problem gives it away. An
  entry ruled out on that ground is shown in Section 3.2 with the line that gives it away.
- **Four are usable:** S1–S4 in Section 3.1.
- **Found:** your saved Parts 1–6 name the same place (file and function) *and* the same
  fault. The right file with a different problem does not count. Each of S1–S4 states
  what "found" means for that entry.
- **The threshold:** fewer than half, meaning none or one of the four, and the round is
  run again, in a fresh session that has not seen this document. Two or more is a pass.
  Each run is scored on its own, and Compliant ratings count only from a run that passes.
  Two runs in all: if both stay under half, the next step is a different auditor, not a
  third run. (Ruled on 30 September 2026, after this document was first written; it
  read "if run after run stays under half".)
- **Who scores.** Claude, which wrote this engine and its fixes (Section 5 of your
  instruction), chose these entries and classified them. It scores from the committed
  text of Parts 1–6, and the project owner checks the scoring.

**What the measure is worth, as the project recorded it.** Three of the four change no
trade: one changes what the panel and the log say, and two decide nothing. A careful
auditor could reasonably leave them out as cosmetic, so a miss is weak evidence of a
blind spot. The fourth is a gap in the decision record, which bears on Item 6
(Traceability).

---

## 3. The list for after this audit

Every finding on the list as it stood at `01f2892`. Only one line of the list is left
out: a line naming who will work on the list after the audit, which is not a finding.

### 3.1 Scored — four

**S1. The risk gate runs before the bias checks.**
`models/decision_model.py`, `DecisionModel._determine_final_action`. The risk verdict
returns `NO-TRADE (RISK TOO HIGH)` at lines 551–553. That is before every check that
would have answered WAIT: the weak-validation check (656–660), the lean check (663–668),
and the closing WAIT that a NEUTRAL bias falls through to (750–754). So a run with no
case for a trade in any direction, for example under a NEUTRAL bias, is reported as
refused on risk. In the project owner's decision log, as counted on 26 September, 2 of
the 33 refused runs were of this kind. This changes what the panel and the log say, not
which trades are taken. Found by Claude reading the code, 26 September 2026, and
deferred by the project owner the same day.
Nothing shipped names it. `tests/test_neutral_bias_prints_no_plan.py:272` asserts that
under a NEUTRAL bias the ladder answers only WAIT or `NO-TRADE (RISK TOO HIGH)`, and does
not call the second answer a problem.
*Found means:* Parts 1–6 name `_determine_final_action` and say that the risk refusal is
returned ahead of the bias-based WAIT answers, so that a run with no directional case is
reported as a risk refusal.

**S2. `lineage.risk_inputs` leaves out an input that sets the stop.**
`core/engine_core.py`, `Phase7Engine.run`, the `risk_inputs` block of the decision
record (1443–1469). `RiskModel.calculate_stop_targets` (`models/risk_model.py:335–338`)
scales the ATR stop by `trend_factor`, which is computed from `trend_health`. Trend health
therefore sets the stop distance, and through it the 8% and 15% limits, but `risk_inputs`
does not record it. Its comment (the ITEM 14 note at 1458–1465) says trend_health
"no longer" feeds the risk decision. That is true of the risk-regime classification but
not of the stop. `LineageBlock`'s docstring (`core/decision_contract.py:328–330`) says
the stop and targets are computed "from price and ATR". The value is still in the record,
under `trend.trend_health`, so a stop can be rebuilt from the record. It cannot be rebuilt
from the lineage the record declares for it. Found by Claude reading the code while
building a fix on 27 September 2026, and deferred under the 22 September ruling.
*Found means:* Parts 1–6 name the `risk_inputs` lineage (in `Phase7Engine.run`, or as
`LineageBlock` describes it) and say that it omits trend health (or `trend_factor`)
although that value sets the stop.

**S3. Under a NEUTRAL bias, the entry score is measured for a side nothing chose.**
`core/engine_core.py`, `Phase7Engine.run`, 1004–1009. Entry quality is scored for
`eq_trade_direction`, and under a NEUTRAL bias that is the sign of `bias_score` (line
1009). This is the rule that finding 5 found in the plan. The panel still prints ENTRY
QUALITY and TRADE QUALITY for that side, while its PLAN line says there is no plan. It
decides nothing, because a NEUTRAL bias never reaches a side. The nearest shipped text is
the finding 5 comment at `core/panel_render.py:357–370`, which describes the same rule in
the plan but not in the entry score. Found by Claude reading a rendered NEUTRAL panel on
27 September 2026, and deferred under the 22 September ruling.
*Found means:* Parts 1–6 name the entry-quality direction in `Phase7Engine.run` (or
`calculate_entry_quality` as called from it) and say that under a NEUTRAL bias it is
scored for a direction the bias did not choose.

**S4. The weak-validation WAIT decides nothing.**
`models/decision_model.py`, `DecisionModel._determine_final_action`, 656–660. The ladder
returns WAIT when validation is WEAK and trend health is under 40. But trend health under
40 already fails the CONSERVATIVE tier (50, line 464) and the upper tiers (75, line 462),
so the answer would be WAIT anyway. The branch only chooses which sentence is printed.
This branch is the only place the ladder reads the validation score, so it is also why
that score changes no action today (Section 4, item 4). Found by Claude reading the code on
27 September 2026, and deferred under the 22 September ruling.
*Found means:* Parts 1–6 name this branch of `_determine_final_action` and say that it
cannot change the action: it is dead, redundant, or only selects the message.

### 3.2 Defects not scored — a shipped line names them

**N1. The candles are not checked for bad data.** On price, `data/validation.py`
(`validate_ohlcv`) rejects NaN, inf, non-positive values and impossible candles, and
nothing else. An extreme but internally consistent print therefore reaches the
indicators, and since finding 7 nothing downstream erases it. Deferred by the project
owner, 27 September. *Named at* `indicators/indicators.py:126`.

**N2. Nothing gates on HVN proximity.** The HVN (high-volume node) still carries weight,
through the entry score's structure points and trend health's reversal reading, but it
vetoes nothing. A long can therefore be authorised directly under a high-volume node.
Deferred by the project owner, 27 September. *Named at* `models/entry_model.py:507–513`
and `tests/test_stop_is_atr_only.py:16`.

**N3. At exactly 30.0 the ladder can take a side while the label is not CONFIRMED.**
`MIN_ACTION_BIAS` acts at ≥ 30, while the CONFIRMED label needs > 30. Recorded, not
ruled, 27 September. *Named at* `models/decision_model.py:69–74`.

**N4. The confidence score is read as a win rate** (question 1 of 15 September, Section
5). `DecisionModel._compute_ev` sets `win_rate = confidence / 100` (line 910), and the EV
figure in R that the explanation prints is computed from it. The confidence score is not
a measured win rate. The EV decides nothing. *Named at* the function's docstring,
`models/decision_model.py:898–902`.

**N5. The BTC adjustment has no baseline** (question 3). `DecisionModel._compute_btc_adjusted`
moves a second confidence figure by up to ±20 points (`BTC_ADJUSTMENT_CAP`, line 957),
and by −15 under broad market stress (`BTC_STRESS_PENALTY`, line 958). Nothing has tested
whether that predicts anything. It decides nothing: only the record and the panel read
it. *Named at* `core/panel_render.py:676`, which prints "empirically unvalidated — no
backtest supports this adjustment".

### 3.3 Not scored, for other reasons

**O1. Is ×0.90 enough against the macro trend?** (question 4). `calculate_entry_quality`
(`models/entry_model.py:380–385`) multiplies the entry score by
`CONFLUENCE_PENALTY_MULT` (0.90) when macro opposes the trade. This is not scored because
it asks how large a weight should be, not whether the code does what it says; it is one
of the weighting questions in Section 4. It is also named at
`models/decision_model.py:690–693`.

**O2. "ROUND 6" in seven test comments means round 5's requested run 6.** Six comments
read `ROUND 6 MUTANT ESCAPE (GPT-6 Astra), 12 September 2026`: `run_tests.py:150`,
`tests/test_frame_ownership.py:219` and `:300`, `tests/test_smoke.py:130`,
`tests/test_timeframe_disagreement.py:353`, and `tests/test_trend_direction_source.py:223`.
One docstring says "round 6 (GPT-6 Astra)": `tests/test_run_tests_filter_matching.py:2`.
GPT-6 Astra graded round 5, and these came from its requested run 6, a day before the
round the project calls round 6 was sent. This is not scored because the shipped line is
itself the defect. Found by Claude on 30 September and left as it was, because the code
sent to you was not edited for the audit.

**O3. A comparison between two vocabularies.** `calculate_entry_quality`,
`models/entry_model.py:384`, tests `macro_bias != trade_direction`. `macro_bias` is BULLISH,
BEARISH or NEUTRAL, and `trade_direction` is LONG or SHORT, so the test is always true.
The two branches above it catch agreement, and `core/engine_core.py` only ever passes
BULLISH, BEARISH or NEUTRAL (lines 519–551). The result is therefore right for every
value any caller passes. A caller passing any other macro value would be penalised as
opposing. This is not scored because it changes nothing observable. Found by Claude on
30 September 2026 while checking O1 for this document; it is on the list by the
22 September ruling.

### 3.4 New trading rules — not defects, not scored

- **Entering at the EMA band.** The plan would become a limit order at the band's edge,
  with an expiry. Today the decision candle's close is the entry.
- **A side must hold for N closed candles before a trade.** What the old "bias state
  machine" was once assumed to do. It never did.
- **Renaming CONFIRMED.** The label reads as a lean that has held for a while, but it
  means |`bias_score`| > 30.
- **A floor on T1 of at least 3% after fees.** Today T1 equals the stop distance, which
  can be anywhere from 0.2% to 8%.
- **A range-trading mode.** Buying at support and selling at resistance, as a second
  strategy with its own log and its own verdict.

Each was ruled for after the audit by the project owner, between 27 and 28 September.

---

## 4. The `bias_score` findings

The project ruled on 22 September that the weighting of `bias_score` waits until after
this audit, and that the auditor is shown these findings. They are not on the list in
Section 3 and are not scored. All four are also stated in comments in the code you read;
item 4 adds one point those comments do not make.

1. **The six weights have never been reviewed:** 0.30 / 0.20 / 0.15 / 0.15 / 0.10 / 0.10
   (`models/bias_engine.py:152–157`), chosen by hand, with no written reason for the
   split. Stated at `models/bias_engine.py:57–60`.
2. **The blend asks one question four times.** Trend health (0.30), structure regime
   (0.20), SuperTrend direction (0.15) and macro bias (0.10) are four transforms of the
   recent direction of `close`, together 0.75 of the blend. In a sustained trend they
   agree by construction, and `bias_score` presents that agreement as four confirmations.
   Stated at `models/bias_engine.py:108–130`.
3. **RSI reaches `bias_score` twice:** through trend health's `rsi_strength` and through
   continuation's `momentum_component`. The two curves correlate at r = 0.37 in
   downtrends and r = 0.83 in uptrends, and the duplicated path is worth at most 1.5
   points. Stated at `models/bias_engine.py:132–141`.
4. **One disagreement can bring three penalties.** Volume reaches three different
   outputs: `bias_score` (weight 0.15), the validation score (+15 / −25) and the entry
   score (VWMA distance, 20 of 102 points). Macro also reaches three: `bias_score` (0.10),
   the validation score (+10 / −20) and the entry score's confluence multiplier
   (×1.05 / ×0.90). The paths are traced at `models/bias_engine.py:62–89`. That comment
   leaves open whether three separate penalties for one disagreement is the right total
   weight. **Not in that comment:** the validation score's only effect on the ladder is
   the WAIT in S4, which changes no action. Of the three paths, only the other two can
   change the action.

---

## 5. The questions of 15 September

A short list of questions about one of the engine's printed panels, dated 15 September
2026 and kept outside the repository. Its questions are shown below, numbered as the
project numbers them rather than in the list's own order, with the list's mathematical
markup removed, and with where each now stands in the code you were sent.

| # | Question, in the list's words | Where it stands |
|---|---|---|
| 1 | "Mapping a composite heuristic 'confidence score' directly to a raw win probability (56%) without empirical calibration creates an artificial expected value." | Live. N4. |
| 2 | "Triple Volume Accounting … If all three penalize the score separately, it double- or triple-counts the same input." | Partly live. The panel's "Vol:" field is volatility (ATR / price, `calculate_dynamic_regime`), not volume. The other two are one reading, volume sentiment, which reaches `bias_score` and the validation score; volume also reaches the entry score through the VWMA distance. Whether that is too much weight is a weighting question: Section 4, item 4. |
| 3 | "Boosting confidence by +10.55 points purely based on BTC correlation adds a major layer of complexity that has no baseline justification." | Live. N5. |
| 4 | "The confluence multiplier applies a penalty (macro x0.90), but is a 10% reduction sufficient when trading directly against the macro trend?" | Live, as a weighting question. O1. |
| 5 | "VALIDATION : WEAK (Score: 5.00). What is this score out of?" | Not live. The panel prints "/100". The same question's second clause, a weak validation beside a high trend strength, is the design: validation starts at 50 and moves only on macro and volume, never on trend health (`core/engine_core.py`, the VALIDATION block). |
| 6 | "A max denominator of 102 rather than 100 suggests an unadjusted constant or a floating-point/weighting drift in the scoring module." | Not a defect. 102 is the sum of the entry score's five component maxima, documented as such at `models/entry_model.py:35–40`. |

---

## 6. What this document leaves out

The project's reasoning for its rulings, its session records and its decision record are
not part of this round, apart from the rule and classification restated in Sections 2
and 3. On 20 September the project also scrapped a list of open items. Of that list you
have now seen the weighting findings (Section 4) and the questions still live (Section
5). The rest is not shown: an unwritten statement of the engine's market thesis, the
scope of a planned engine review, when backtesting may start, and a stale to-do list kept
outside the repository. None of these is a defect in the code, as far as the project
knows.

---

## 7. What would help most in Part 7

Section 12 of your instruction describes Part 7. In addition, these would help most:

- **Any entry your own reading does not support**: one that is described wrongly, is not
  live, or is live in more places than stated.
- **Any classification you think is wrong.** For example, a line in Section 3.2 that in
  your reading does not actually give its entry away, a line somewhere in your package
  that gives away S1–S4, or an entry in 3.3 or 3.4 that you would call a defect.
- **Anything here that changes a view you formed in Parts 1–6**, stated as a change, not
  written back into the earlier parts.

You may say which of S1–S4 you think your Parts 1–6 found. The score is taken from the
saved text, not from that statement.
