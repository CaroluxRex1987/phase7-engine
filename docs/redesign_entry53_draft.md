# The redesign (entry 53) — design draft

*Draft v3, 7 November 2026, in the session that opened at 05:14 at `94b7e96`. Version 3
states §2's direction as Viktor ruled it on 7 November — EMA50's slope and the EMAs'
order, not EMA20's slope (DECISIONS, "Ruling, 7 November 2026 — the redesign's
direction is EMA50's slope and the EMAs' order …") — which reconciles §2, §3.1 and §4
(§16.4, §12's point 7) and leaves §3.1's and §4's rules as they were; it brings §0,
§3.1, §4, §13.1, §14 and §16 to it. No engine `.py` file changed between `4ab59d7` and
`94b7e96`, so version 2's reads of the code hold at `94b7e96`, where version 3's were
made. Version 2, 7 November 2026, was written in the session that opened at 04:30 at
`4ab59d7`. Version 2 adds §16, what the design weakens and the case against, written before any of the
reading of 14 November's data was read for it; writing it found that §2's direction
and the band of §3.1 and §4 cannot meet (§16.1), which adds point 7 to §12 and a
pointer each to §3.1 and §4. No engine `.py` file changed between `e69d5bb` and
`4ab59d7` (`git diff --stat`, files outside `docs/` and `tests/`), so version 1's
reads of the code hold at `4ab59d7`, where version 2's were made. Version 1, 1 November
2026, was written in the session that opened at 21:02. Version 0 was started
in the session that opened at 17:49, read at `e748b0b`, and filed at `e69d5bb`.
Version 1 adds §13, every golden field one by one, and §14, every test the design
moves one by one; reads entries 14 and 19 against §3.2 and rewrites that paragraph;
adds what those reads found to §0, §2, §3.1, §4 and §5; and records three statements
of version 0 that were wrong (§15). No `.py` file changed between `e748b0b` and
`e69d5bb`, so version 0's reads of the code hold at `e69d5bb`, where version 1's were
made. Claude's draft. It will be put to Viktor after the forward measurement's reading
of 14 November (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators …",
point 7). Nothing here is ruled but §2's direction (7 November), and no code is written
from it until the whole design is. Each
statement says where it comes from: **read** means read in the code at `e748b0b`
(version 0), `e69d5bb` (version 1), `4ab59d7` (version 2) or `94b7e96` (version 3);
**ruled** names the
ruling; **proposed** is Claude's suggestion; **to measure** is a number this draft
does not have yet. Where
something was not checked, the sentence says so.*

## 0. Who decides what

- **Viktor's, as the design's ruling** (25 October, "What follows"): the whole design
  before it is built. Inside it, these are new trading rules or change one of his
  rulings, so they are his even under the delegation of 29 October: the strength floor
  (§2; ruled on 7 November), the trigger candle (§5), the liquidity floor's value (§5), the tier lines
  (§4), whether the structure multiplier stays (§3.3), any ruled value named as
  tunable (§9), and, added in version 1, the exit watch's exhaustion and reversal
  flags, which go with trend health if nothing keeps them (§2).
- **Claude's, proposed here for him to reverse:** entry quality's formula and weights
  (§3), the order of the gates (§4), the sentence rule (§6), the code's shape, the
  tests, and the replacements for H1, H2 and H5 (§8), which Viktor accepts or rejects
  (DECISIONS, "Decision, 25 October 2026 — the held-back defects …", point 6).

## 1. Scope, from the rulings

From "Ruling, 25 October 2026 — the engine's indicators …" (points 1–8),
"Decision, 25 October 2026 — the held-back defects …", "Ruling, 31 October 2026 —
volume enters the redesign as two gates …", "Decision, 30 October 2026 — what may be
tuned …", and entry 58 (PHASE7_NEXT.md, "Found after 22 September"):

1. Direction from the EMA slope alone; ADX, structure regime and divergence stay as
   gates; continuation removed; volume sentiment out of the decision; SuperTrend in
   Exit Watch only.
2. Macro: a gate on LONG only; out of the bias, the entry score and the validation
   score.
3. Trend health and its 75 / 50 tiers removed; the tier from entry quality.
4. Entry quality: distance from the EMA band's middle in ATRs, and HVN nearness. RSI
   only in the divergence gate. The trend multiplier removed (Critical, by F4's
   precedent). F4's macro multiplier removed.
5. Confidence and the EV line dropped.
6. `bias_score`'s weighting and the HVN uses in the same change.
7. The strength floor that "a lean is not a case" (5 September) needs once the
   weighted sum is gone.
8. Two volume gates: a liquidity floor on `quote_volume`, and volume confirming the
   trigger above its recent median. Volume stays out of T1–T3.
9. No reasoning sentence rounds a compared value across its threshold (entry 58).
10. Entries 14 and 19 in scope (Claude's reading of 25 October, his to change).
11. The tunable list (at most three thresholds) named once the design is fixed.

Not in scope, and unchanged by this design: the stop (ATR × 1.2 × the volatility
factor, ruled 5 October), the 8% and 15% limits, the targets at 1×, 2× and 3× the stop
distance, the risk verdict, the plan-coherence refusal, the degradation rule of
29 August, the BTC section as reference only, and H3 (`live_trading.py`).

## 2. Direction and the strength floor

**Read.** `trend_direction_sign` is the sign of `trend_slope`, the mean of
`EMA20_Slope` and `EMA50_Slope` (`indicators/trend_health.py`), each the percent
change of that EMA over one 4h candle (`indicators/indicators.py`, the slope loop).
Today it signs trend health's 30% of `bias_score`; `raw_bias` comes from the whole
sum against `RAW_BIAS_THRESHOLD` (20), and the floor is `|bias_score|` against
`MIN_ACTION_BIAS` (30). The risk plan's side comes from the sign of `bias_score`
(`models/risk_model.py`, `calculate_stop_targets`).

**Ruled on 7 November** (Viktor's, by agreeing to Claude's suggestion; DECISIONS,
"Ruling, 7 November 2026 — the redesign's direction is EMA50's slope and the EMAs'
order …"): **direction is EMA50's slope and the EMAs' order, and that agreement is the
floor.**

- BULLISH when `EMA50_Slope > 0` and `EMA_20 > EMA_50`.
- BEARISH when both point down.
- Anything else is NEUTRAL: a lean, and WAIT. `EMA20_Slope` is not read.

Why: the 5 September ruling separates a lean from a case. Once the sum is gone, the
plainest version of that line on the slope itself is the averages' order and the slow
average's slope disagreeing: they have crossed and the slow one has not turned. The
fast average turning against the slow one is the pullback the hypothesis enters on
(ruling 1); versions 0 to 2 called it a lean as well, so that a pullback candle never
had a side and a candle with a side never closed inside the band (§16.1). That
introduces **no new number**, so it takes none of the three tunable places. ADX ≥ 20
stays the gate on how strong the trend is (5 October, point 4), so "how strong" is not
counted twice.

**The alternative, not proposed:** a minimum slope measured in ATRs (how far `EMA_20`
moved over the last *k* candles, divided by ATR). That adds a cutoff and a length, and
it measures with a second number the same thing ADX already gates.

**Consequences, all mechanical ones included:**

- `bias.raw` keeps its three values. `bias.score` no longer exists as a weighted sum.
  **Proposed:** remove it, rather than keep a number that no longer measures
  conviction (ruling 2: "No weighted sum is shown as conviction"). `bias.detailed`
  (BULLISH CONFIRMED / EARLY …) is built from the score (`bias_label`, read). Proposed:
  `detailed` takes the raw label, and the CONFIRMED / EARLY vocabulary goes.
- `calculate_stop_targets` takes the side, not `bias_score`. The plan-coherence
  refusal stays: it reads the plan's targets, not the bias, which is why it still
  catches the two disagreeing.
- `calculate_dynamic_bias` is replaced by a function of `EMA50_Slope` and the two
  EMAs. `trend_exhaustion`, `reversal_*`, `continuation_strength`,
  `volume_sentiment`, `supertrend_direction` and `macro_bias` are no longer its
  inputs, so H2 cannot stay (§8).
- The CHOCH-against-trend ×0.5 discount on `bias_score` disappears with the sum.
  Today it can push a bias under the floor and into WAIT. The structure-regime gate
  (§4) and the structure multiplier (§3.3) still read structure; whether CHOCH should
  also be its own gate is not proposed here. **Flagged for Viktor:** this is a path
  that can reach WAIT and goes away.
- The BTC section calls the same bias function (`core/engine_core.py`, the BTC
  block, read). It takes the new function and stays reference only;
  `btc_context.trend_health` and its score go.
- **Trend health is a score; `indicators/trend_health.py` is more than that** (read at
  `e69d5bb`). `compute_trend_health` also returns the `adx` gate 3 reads, the
  `momentum_divergence` and `divergence_direction` gate 5 reads (`core/engine_core.py`,
  the signal call, :1039–1041), the `degraded_inputs` the run's degradation list takes
  (:790) and the BTC section's takes (:936), and the `trend_exhaustion` and
  `reversal_*` the exit watch reads (`models/exit_model.py`, :110 and :143–144).
  **Proposed:** the module keeps ADX, the divergence and its degraded inputs, and loses
  the score, exhaustion, continuation, reversal, `momentum_mode` and `trend_direction`;
  the exit watch loses its exhaustion and reversal flags with them, and keeps the
  divergence and SuperTrend flags. **Flagged for Viktor (§0):** two exit-watch flags
  go, and neither has a ruling of its own.
- **The bias-flip flag would fire once on every pair.** The engine saves
  `detailed_bias` as its state (`core/engine_core.py`, `_save_state`, read), and the
  exit watch reports a flip when the saved label differs from this run's
  (`models/exit_model.py`, :192–195). Once `detailed` takes the raw label, the first
  live run after the change would print "Bias state changed from BULLISH CONFIRMED to
  BULLISH" on a pair whose direction did not change. **Proposed:** the state saves the
  raw label under a new key, `raw_bias`; an old state file has no such key, so the
  first run has nothing to compare and reports no flip.
- **BTC's reference line flips on the pinned run.** Today `btc_context.raw` is
  BEARISH (golden). On the pinned BTC candles both EMAs rise on the decision bar (EMA20
  +0.1412% a candle, EMA50 +0.1100%) and EMA20, 57,437.69, is above EMA50, 56,681.36,
  so the rule gives BULLISH, under versions 0 to 2 and under the ruled one, which reads
  only EMA50's slope. Computed in the sandbox from
  `tests/fixtures/pinned/BTCUSDT_4h.csv` with pandas' `ewm(span, adjust=False)`, not
  read from a record: BTC's EMAs are not recorded. The same computation on the pinned
  AERO candles gives the golden record's `EMA_20`, `EMA_50` and both slopes to the
  eighth decimal. BTC stays reference only, so no action moves with it; why today's
  weighted sum calls it BEARISH was not traced.
- **`EMA20_Slope` is read by nothing in the direction** (version 3). Today trend
  health reads it twice (`indicators/trend_health.py`, the mean slope and the
  acceleration, read at `94b7e96`), and the score both feed goes. Whether anything the
  design keeps still reads it is answered when built by
  `tests/test_no_dead_columns.py` (§14); not checked here. The record keeps it in
  `indicators_at_decision_bar` while the column is produced.
- `RAW_BIAS_THRESHOLD`, the six `WEIGHT_*` constants and `MIN_ACTION_BIAS` leave the
  fingerprinted constants. That moves `run_hash` (predicted).

**To measure before it is put to him:** on the ten pairs' archived candles, how often
the ruled direction agrees with today's `raw_bias`, and how often it is NEUTRAL
where today's would act.

## 3. Entry quality

**Read.** Five parts summing to 102 (EMA zone 30, ATR distance 25, VWMA 20, RSI 15,
HVN "structure" 12), times three multipliers (macro, trend and structure, each 0.90,
1.00 or 1.05), clipped to 100 (`models/entry_model.py`, `calculate_entry_quality`).
The HVN part uses percent distance (under 1.5% full, under 3% 8 points, else 4).

### 3.1 The two parts (proposed)

- **Distance:** `d = |close − band_mid| / ATR`, where `band_mid` is the midpoint of
  `EMA_20` and `EMA_50`, the band the engine already uses (`zone_lower` / `zone_upper`
  in the record, read). **D = 80 × max(0, 1 − d / 3).** Full points at the band's
  middle, nothing beyond three ATRs. Under §2 as ruled on 7 November the middle can be
  reached on a candle with a side (§16.4); under versions 0 to 2's direction it could
  not (§16.1).
- **HVN nearness:** `h = |close − HVN| / ATR`. **H = 20 × max(0, 1 − h / 2).** Measured
  in ATRs like distance, so the two parts read in one unit. Today's HVN part uses
  percent distance.
- **Entry quality = D + H**, from 0 to 100. There is no multiplier and no clip
  (except §3.3).

**Why 80 / 20.** The hypothesis is a pullback to the average (ruling 1), so distance
is the question; HVN is supporting evidence that a level is there. Keeping HVN at 20
also limits what H5 can move (§8). **Why straight lines rather than today's
`exp(−0.5·ratio)`.** Each point on the panel can be checked by hand, and the line
reaches zero at a stated distance instead of never.

**When an input is missing.** If ATR, the band or the HVN is missing, that part is
**not measured**. It is not given a neutral value. Entry quality is then not computed,
and the run is degraded. That is the 29 August rule: today's neutral defaults (VWMA
15, RSI 10, structure 6) are the fabrication shape the project has spent weeks
removing. **Consequence:** `ZONE_POINTS_NOT_MEASURED` and `ATR_POINTS_NOT_MEASURED`
go, and so do the VWMA and RSI defaults.

**Two distances in one record** (found in version 1). `entry.distance_from_zone`, the
percent distance from the band's midpoint since F5, sets STATUS and stays; `d` is the
same distance in ATRs. Which one STATUS reads is not proposed yet; noted so the record
does not carry one measurement under two names without saying so (F8, one name for
one meaning). Claude's, for version 2.

### 3.2 What leaves

`ema_pos_pts`, `atr_dist_pts`, `vwma_pts`, `rsi_pts`, `struct_pts`, `base_score`,
`component_max_points`, `macro_multiplier`, `trend_multiplier`, `combined_multiplier`,
`scaled_score`, `score_ceiling` and `score_clipped` leave the entry record. Whether the
VWMA column stays in the frame is answered when built by
`tests/test_no_dead_columns.py::test_consumed_columns_are_still_produced` (§14); not
checked here.

**Entries 14 and 19, read against this section** in version 1 (their text in
PHASE7_NEXT.md, "Found after 22 September", and the code, both at `e69d5bb`).
Version 0 said both were settled here; two of its reasons were wrong (§15).

- **Entry 14** is the test `macro_bias not in ["NEUTRAL", ""] and macro_bias !=
  trade_direction` (`models/entry_model.py:392` at `e69d5bb`; :384 when it was filed,
  at `01f2892`). It compares macro's BULLISH / BEARISH / NEUTRAL with the trade's
  LONG / SHORT, so it is always true, and it sits in the macro multiplier's branch.
  It is **settled because the macro multiplier leaves** (ruling 4, F4), not by a
  choice of vocabulary. **What carries forward:** gate 6 brings the same two
  vocabularies together again, a daily trend against a side. **Proposed:** gate 6 is
  written in one vocabulary, `side == "LONG" and macro_bias == "BEARISH"`, and a macro
  value outside BULLISH, BEARISH and NEUTRAL is refused as not measured, which
  degrades the run; it is neither passed nor penalised. Entry 14's defect was that
  such a value fell silently into one branch. **Test:** every macro value — the three,
  `""`, `"LONG"` and `None` — against both sides.
- **Entry 19** is `_VOLUME_SENTIMENT_SCORES.get(…, 0.0)` (`models/bias_engine.py:335`
  at `e69d5bb`): a failed volume read scores as NEUTRAL VOLUME does. It is in the
  bias, so it belongs to §2, not to this section. It is **settled because volume
  sentiment leaves the decision** (ruling 1): no table scores a volume label, and
  `volume_agreement` leaves with validation (§4). It was Viktor's as a weighting
  question; with the weighting gone, nothing of it is left to rule. **What carries
  forward:** gate 8 reads volume again. **Proposed:** an absent or non-finite volume
  on the decision candle, or fewer than twenty readable candles before it, fails gate
  8 as not measured, which degrades the run; it is never compared as though it were
  the median. `structure.volume_sentiment` stays in the record and on the panel as
  information nothing decides on.

### 3.3 The structure multiplier — Viktor's

BOS ×1.05 and CHOCH ×0.90 (read) are not covered by the eight rulings, and they stay
"unless Viktor rules otherwise" (25 October). **Claude's suggestion, his to rule:**
remove it. It is the last multiplier on a score whose other two were removed for
moving a tier on a factor measured elsewhere, and the structure regime is already a
gate. If it stays, it multiplies D + H, and the score is clipped at 100.

## 4. The ladder and the gates

A trade is taken only if every gate passes. Gates run in a fixed order, and each one
that fails records its own sentence.

| # | Gate | Source | Fails to |
|---|------|--------|----------|
| 0 | inputs well-formed | today, unchanged | WAIT |
| 1 | risk verdict present / passed | today, unchanged | NO-TRADE (RISK NOT ASSESSED / TOO HIGH) |
| 2 | direction not NEUTRAL (the floor, §2) | proposed | WAIT |
| 3 | ADX ≥ 20 | ruled 5 Oct; today in the confirmation gate | NO-TRADE (SIGNAL UNCONFIRMED) |
| 4 | structure regime agrees | today, in the confirmation gate | NO-TRADE (SIGNAL UNCONFIRMED) |
| 5 | no price/RSI divergence against | today, in the confirmation gate | NO-TRADE (SIGNAL UNCONFIRMED) |
| 6 | LONG only: daily trend not BEARISH | ruled 25 Oct, point 3 | NO-TRADE (MACRO AGAINST) — new label, proposed |
| 7 | liquidity floor (§5) | ruled 31 Oct | NO-TRADE (THIN MARKET) — new label, proposed |
| 8 | trigger, and its volume (§5) | ruled 31 Oct; the trigger proposed | WAIT — no resumption candle yet |
| 9 | entry quality ≥ the CONSERVATIVE line | ruled 25 Oct, point 4 | WAIT — not a pullback |

Gates 3–5 stay where they are, in `_apply_signal_gate`, with their sentences
unchanged. That keeps work order F's ruled order: a risk refusal stays the label. The
new gates 6–8 sit next to them, so that one place still lists every blocker for both
sides (`long_signal_blockers` / `short_signal_blockers`, read). **Proposed: 6 and 7
become blockers on that list, not new branches in the ladder.** Then a refused trade
shows every reason it failed, which is how the confirmation gate already works.

Macro NEUTRAL passes gate 6. That follows the ruling's wording, "no LONG while the
daily trend is bearish". A failed macro read is already a degraded run (read,
`core/engine_core.py`, the macro block), so a default NEUTRAL cannot open a LONG.
SHORT is not gated by macro. Gate 6's comparison is entry 14's, written in one
vocabulary (§3.2).

**Tiers, from entry quality only (ruling 4). Proposed lines, set by reasoning, to be
checked against the measured distribution so that no tier is empty and none takes
nearly every run:**

- **LONG / SHORT:** quality ≥ 70.
- **AGGRESSIVE:** quality ≥ 70, close inside the band, and the risk regime NORMAL or
  LOW. Today's rule minus trend health; Item 14's gate on intensity is kept as it is.
  Under §2 as ruled on 7 November a close with a side can be inside the band
  (§16.4); under versions 0 to 2's direction it never was (§16.1). Today's rule is not
  "inside the band" but ACTIVE ENTRY ZONE, a whole band width either side of the
  middle (§16.1, point 2); which one this line means is open, and the tier lines are
  Viktor's (§0). Computation 2 counts both.
- **CONSERVATIVE:** 50 ≤ quality < 70.
- **WAIT:** under 50 — not a pullback.

With no HVN points, LONG then needs `d` ≤ 0.375 ATR and CONSERVATIVE needs
`d` ≤ 1.125 ATR. With full HVN points, the limits are 1.125 and 1.875 ATR.
**Flagged for Viktor:** since 28 September every trade is one of ten equal capital
slices, so the tier changes no position size; it is a label. Keeping three labels
moves the fewest tests and panel lines. Collapsing them is a separate question, not
proposed here.

**H1 goes.** H1 is the WAIT on WEAK validation with trend health under 40. Its
inputs go: trend health is removed, and the validation score loses both of its parts
(macro agreement and volume agreement, read in `core/engine_core.py`). **Proposed:**
`validation_score`, `validation_state` and `validation_note` leave the decision. The
macro note stays on the panel as information beside gate 6.

## 5. The trigger and the two volume gates

**The trigger is proposed here; nothing in the code has one today** (searched at
`e748b0b`: no "trigger" or "resume" in `models/`, `core/engine_core.py`,
`indicators/` or `structure/`). The ruling of 31 October assumes "the candle that
resumes the trend after the pullback", so the design has to say which candle that is.

- **Proposed trigger, LONG:** the decision candle (the last closed one, since finding
  16) closes above its open and above the previous candle's close. SHORT is the
  mirror. Entry quality is read on that candle's close, so the pullback and its end
  are the same candle. A pullback that has not turned yet means WAIT.
- **Trigger volume:** that candle's `volume` > the median of the previous 20 candles'
  `volume`. The margin starts at zero: strictly above the median. Twenty is a length,
  not a cutoff (31 October, point 4). Base-asset volume is used because it is
  compared with itself on one pair.
- **Liquidity floor:** the decision candle's `quote_volume` ≥ **F** USDT. **F is to
  be measured:** from the ten pairs' candles, using `volume × close` as the stand-in
  the ruling allows for counting, F is set so the floor blocks the thinnest candles
  and not ordinary ones. Until it is measured, no value is proposed.
- **`quote_volume` has to reach the frame.** `data/data_fetcher.py` reads it as the
  eighth kline column and drops it (read: `_OHLCV_COLUMNS` keeps five). Keeping it
  changes the fetched frame. That moves the candle archive's `canonical_text`, and so
  every `input_hashes` value on a live run. **Traced in version 1:** `canonical_text`
  writes every column of the frame, sorted (`core/lineage.py:158`), and the input hash
  is the SHA-256 of that text (:244), so the new column moves every live input hash
  and the archive's text; `_decision_bar_row` records every column at the decision
  bar (`core/engine_core.py:338`), so the record gains
  `lineage.indicators_at_decision_bar.quote_volume`; and
  `tests/test_fetch_and_import_hygiene.py:193` asserts the frame's five columns.
  **Proposed:** `CANONICAL_FORMAT` stays 1, since a column is data in that format;
  and `data/validation.py` checks `quote_volume` as it checks `volume`.
- **Pinned data has no `quote_volume`** (golden `lineage.inputs`: five columns,
  read). **Proposed, changed in version 1:** an absent `quote_volume` is a missing
  input, so the run is degraded (29 August) and gate 7 records "not measured"; it is
  not computed from `volume × close`. Version 0 had it fail gate 7 as a NO-TRADE,
  which gives a market nobody measured the label of a thin one (§15). The pinned
  fixture gains a `quote_volume` column, written by `docs/build/make_pinned.py` with
  `MANIFEST.json`, so the golden run passes gate 7; §13 assumes it does. The pinned
  candles are synthetic, so the column is too: its rule is proposed once F is known,
  and F and the fixture are checked together. Its predicted moves are in §13.

**The case against, given with it:** the trigger and both volume gates each cut
trades, and the finish line needs about 100 closed trades of one version. The count
of how often each would have blocked comes from the 14 November data (31 October,
"Claude's error, recorded").

## 6. Entry 58's rule — no sentence rounds across its line

**Proposed:** one helper prints any value that a sentence sets against a threshold.
It adds decimals, up to two, until the printed value is on the same side of the line
as the real one. If two decimals are not enough, it floors a value below the line and
ceils one above it. `_adx_text` already does the floor for ADX; this generalises it.
Every sentence that names a threshold goes through the helper. **Test:** for every
threshold, the values `t − 10⁻⁹`, `t − 0.005`, `t − 0.5`, `t`, `t + 0.5` and
`t + 0.005` are printed in each sentence that quotes `t`, and each printed value is
on the same side of `t` as its true value. The lines at `models/decision_model.py`
:512, :519, :634, :680, :687–688 and :774 (read at `248037d`, entry 58) go away with
trend health or are rewritten through the helper.

## 7. Confidence, EV, and the degradation rule

`_compute_confidence`, `_compute_ev`, `AVG_REWARD_R`, `EV_BREAKEVEN_BAND_R`,
`risk.confidence_score`, `risk.assumed_win_rate`, `risk.ev_r` and `risk.avg_reward_r`
go (ruling 6). **The ruling of 29 August** says "confidence and trade quality must be
reduced". With confidence gone, **Claude's reading, his to correct:** the clause
applies to what is left. Trade quality, that is entry quality, is still capped at
`DEGRADED_CONFIDENCE_CEILING`, which is renamed to say what it caps. A degraded run
still authorizes no trade.

## 8. The held-back defects (Decision, 25 October)

- **H1:** replaced. Its branch is gone (§4). A replacement is searched for once this
  design is fixed.
- **H2:** replaced. The new direction function does not take `trend_exhaustion` (§2).
- **H5:** judged again. One HVN bin shifts `h` by the bin's width ÷ ATR, which moves
  H by at most 20 × width ÷ (2 × ATR). **To measure:** the bin width against ATR on
  the ten pairs. If that can move a run across 50 or 70, H5 is not minor, and it is
  fixed here and replaced.
- **H3:** stays.

## 9. Candidates for the tunable list (at most three; named when the design is fixed)

The ADX floor (20, a ruled value: his yes or no), the stop's 1.2 (ruled: his yes or
no), the liquidity floor F, and the trigger volume's margin. That is four candidates
for three places. **Proposed:** ADX floor, stop multiple, F. The margin stays at zero
and is not tuned.

## 10. What moves — tests, golden fields, constants

**Golden snapshot:** every field, one by one, in §13, with the pinned run's path
through the gates in §13.1. Version 0's grouped prediction is replaced by it. The
golden run stops exercising a trade (it becomes a WAIT at gate 8). **Proposed:** keep
this fixture as the WAIT case and add a second pinned decision that passes every gate,
so the golden snapshot still covers a trade's plan; its candle is not chosen yet.

**Tests:** every test, one by one, in §14. Version 0's per-file grep counts (at
`e748b0b`) are replaced by it. Still owed with the code: `core/decision_contract.py`
declaring the new fields and dropping the old, `core/decision_log.py` listing the new
constants (`tests/test_fingerprint_names_every_constant.py`), and every `startswith`
over the panel (the skill's decision-path scope).

**`code_hash`** moves. The change is decision-path work, so there is a live run
before its commit.

## 11. Read in passing

`trend_health.py` scores the slope as `tanh(|trend_slope| × 100) × 45`, while
`trend_slope` is already a percent. So the slope part reaches its 45 at about 0.01% a
candle, which may be part of why trend health passes 75 on 89% of bars (25 October,
reason 4). This was read, not checked against the record. It does not matter once
trend health goes, and it is noted so it is not lost.

## 12. Still to do before this goes to Viktor

1. The measurements marked **to measure**, from the 14 November data: direction
   agreement, the tier distribution, F, the trigger and its volume pass rates, and
   H5's bin width against ATR. Their computations, with point 4's, and the result that
   would count against this draft were fixed on 2 November, before the data was read
   (DECISIONS, "Decision, 2 November 2026 — how the reading of 14 November measures
   the redesign draft's gaps …"); version 1 is otherwise unchanged.
2. Done in version 1: every golden field (§13) and every test (§14). Left with the
   code: the three tests in §14 marked "to read", and each test's body read when it is
   rewritten.
3. Done in version 1: entries 14 and 19 read against §3.2.
4. A count of how often the whole ladder trades on the ten pairs, compared with
   today's version on the same candles.
5. Done in version 2: "what it weakens" and "the case against", written for the
   design as a whole (§16).
6. Added in version 1: which distance STATUS reads (§3.1), and the second pinned
   decision's candle (§10).
7. Added in version 2, done in version 3: §2, §3.1 and §4 reconciled (§16.1, §16.4),
   by Viktor's ruling of 7 November on the floor; entry quality's formula is
   unchanged. The decision of 2 November's computation 1 was amended in place the same
   day, before the reading's data was read. Left with the tier lines, Viktor's: which
   reading of AGGRESSIVE §4 means.

## 13. The golden snapshot, field by field (version 1)

Read from `tests/fixtures/golden_decision.json` at `e69d5bb`; predicted under this
draft, with the pinned fixture carrying `quote_volume` at or above F (§5). The values
marked computed were computed in the sandbox from the golden record and the pinned
CSV, not by the engine; every other "unchanged" is predicted from what produces the
field, and the re-baselined snapshot's diff is the check.

### 13.1 The pinned run through the gates

- **0–1:** inputs well-formed; `risk.risk_valid` true. Pass.
- **2, direction:** EMA50 slope +0.2236% a candle, EMA20 0.77559759 above EMA50
  0.76017364 (golden `indicators_at_decision_bar`): BULLISH, as today's `bias.raw`.
  Pass. (EMA20's slope, +0.3560%, is no longer read; version 2's rule gave BULLISH
  too.)
- **3–5:** ADX 31.96, at least 20; structure BULLISH TREND; divergence NONE. Pass.
- **6, macro:** BULLISH. Pass.
- **7, liquidity:** passes once the fixture carries `quote_volume` at or above F.
- **8, trigger:** fails twice over. The decision candle (16 March 2025, 20:00)
  closed at 0.80173175, under its open 0.80634644 and under the previous candle's
  close, 0.80634644; and its volume, 84,693.73, is under the median of the twenty
  candles before it, 179,247.89 (computed from `tests/fixtures/pinned/AEROUSDT_4h.csv`).
  **WAIT.**
- **9** would fail too: `d` = 3.2070 ATR and `h` = 15.1202 ATR, so D = 0, H = 0 and
  entry quality 0 (computed).

So the action moves from CONSERVATIVE LONG to WAIT, at gate 8.

### 13.2 Every leaf

227 leaves (a list counts as one). 125 unchanged, 81 removed, 15 move, 2 renamed, and
4 that are Viktor's.

**Removed — 81.** Each leaves the record with what produces it.
- `bias` (1): `score`
- `btc_context` (1): `trend_health`
- `entry` (13): `atr_dist_pts`, `base_score`, `combined_multiplier`, `component_max_points`, `ema_pos_pts`, `macro_multiplier`, `rsi_pts`, `scaled_score`, `score_ceiling`, `score_clipped`, `struct_pts`, `trend_multiplier`, `vwma_pts`
- `lineage.bias_components` (34): `after_discount`, `bias_score`, `choch_against_trend`, `clipped`, `factors.macro_bias.contribution`, `factors.macro_bias.input`, `factors.macro_bias.signed`, `factors.macro_bias.weight`, `factors.reversal_continuation.contribution`, `factors.reversal_continuation.input`, `factors.reversal_continuation.signed`, `factors.reversal_continuation.weight`, `factors.structure_regime.contribution`, `factors.structure_regime.input`, `factors.structure_regime.signed`, `factors.structure_regime.weight`, `factors.supertrend_direction.contribution`, `factors.supertrend_direction.input`, `factors.supertrend_direction.signed`, `factors.supertrend_direction.weight`, `factors.trend_health.contribution`, `factors.trend_health.input`, `factors.trend_health.signed`, `factors.trend_health.weight`, `factors.volume_sentiment.contribution`, `factors.volume_sentiment.input`, `factors.volume_sentiment.signed`, `factors.volume_sentiment.weight`, `raw_bias_threshold`, `reversal_direction`, `reversal_strength`, `trend_direction`, `trend_sequence`, `weighted_sum`
- `lineage.risk_inputs` (1): `bias_score`
- `provenance.module_constants` (20): `models.bias_engine.RAW_BIAS_THRESHOLD`, `models.bias_engine.WEIGHT_MACRO_BIAS`, `models.bias_engine.WEIGHT_REVERSAL_CONTINUATION`, `models.bias_engine.WEIGHT_STRUCTURE_REGIME`, `models.bias_engine.WEIGHT_SUPERTREND_DIRECTION`, `models.bias_engine.WEIGHT_TREND_HEALTH`, `models.bias_engine.WEIGHT_VOLUME_SENTIMENT`, `models.decision_model.DecisionModel.AGGRESSIVE_TREND_HEALTH_MIN`, `models.decision_model.DecisionModel.AVG_REWARD_R`, `models.decision_model.DecisionModel.CONSERVATIVE_TREND_HEALTH_MIN`, `models.decision_model.DecisionModel.EV_BREAKEVEN_BAND_R`, `models.decision_model.MIN_ACTION_BIAS`, `models.entry_model.ATR_DISTANCE_MAX_POINTS`, `models.entry_model.ATR_POINTS_NOT_MEASURED`, `models.entry_model.COMPONENT_MAX_POINTS`, `models.entry_model.EMA_ZONE_MAX_POINTS`, `models.entry_model.RSI_MAX_POINTS`, `models.entry_model.STRUCTURE_MAX_POINTS`, `models.entry_model.VWMA_MAX_POINTS`, `models.entry_model.ZONE_POINTS_NOT_MEASURED`
- `risk` (7): `assumed_win_rate`, `avg_reward_r`, `confidence_score`, `ev_r`, `validation_note`, `validation_score`, `validation_state`
- `trend` (4): `exhaustion`, `momentum_mode`, `trend_direction`, `trend_health`

**Move — 15**, each with its value on the pinned run where it can be computed now:
- `bias.detailed` — `BULLISH CONFIRMED` → `BULLISH` (takes the raw label, §2)
- `btc_context.detailed` — `BEARISH CONFIRMED` → `BULLISH`
- `btc_context.raw` — `BEARISH` → `BULLISH` (§2, computed, not read)
- `entry.score` — 45.18175716 → 0.0 (D = 0 at d = 3.2070 ATR, H = 0 at h = 15.1202 ATR)
- `exit.action` — `CONSERVATIVE LONG` → `WAIT` (gate 8, §13.1)
- `explanation.reasons` — rewritten whole: no trend strength, confidence or EV sentence; the gates' sentences
- `explanation.summary` — rewritten: names gate 8's WAIT
- `lineage.archive.path` — moves: it carries `run_hash`'s first sixteen digits
- `lineage.inputs.struct.columns` — gains `quote_volume` (six columns)
- `lineage.inputs.struct.sha256` — moves with the column
- `lineage.run_hash` — moves: the struct input hash and the fingerprinted constants
- `provenance.archive_path` — moves, as `lineage.archive.path`
- `provenance.input_hashes.struct` — moves with the column (the same digest)
- `provenance.run_hash` — moves, as `lineage.run_hash`
- `risk.trade_quality_proposed` — 45.18175716 → 0.0 (it is `entry.score` on an undegraded run)

**Renamed — 2:**
- `provenance.module_constants.models.decision_model.DecisionModel.AGGRESSIVE_ENTRY_SCORE_MIN` — becomes the one 70 line for LONG / SHORT and AGGRESSIVE (§4); value 70.0 unchanged
- `provenance.module_constants.models.decision_model.DecisionModel.DEGRADED_CONFIDENCE_CEILING` — renamed to say it caps trade quality (§7); value 50.0 unchanged

**Viktor's — 4**: removed if the structure multiplier goes (§3.3), unchanged if it stays:
- `entry` (1): `structure_multiplier`
- `provenance.module_constants` (3): `models.entry_model.CONFLUENCE_BOOST_MULT`, `models.entry_model.CONFLUENCE_PENALTY_MULT`, `models.entry_model.SCORE_CEILING`

**Unchanged — 125:**
- `bias` (3): `raw`, `regime`, `volatility`
- `btc_context` (9): `available`, `beta`, `broad_market_stress`, `correlation`, `correlation_label`, `degraded_inputs`, `n_observations`, `regime`, `volatility`
- `decision_log_path`
- `degradation` (3): `degraded`, `missing_inputs`, `trading_authorized`
- `entry` (8): `distance_from_zone`, `entry_status`, `long_signal`, `long_signal_blockers`, `short_signal`, `short_signal_blockers`, `zone_lower`, `zone_upper`
- `exit` (1): `current_price`
- `exit_watch`
- `lineage.archive` (2): `pruned_this_run`, `retention_days`
- `lineage.format`
- `lineage.indicators_at_decision_bar` (18): `ADX`, `ATR`, `EMA20_Slope`, `EMA50_Slope`, `EMA_20`, `EMA_50`, `HVN`, `LVN`, `RSI`, `STRUCTURE`, `ST_Direction`, `SuperTrend`, `VWMA`, `close`, `high`, `low`, `open`, `volume`
- `lineage.inputs` (13): `btc.columns`, `btc.first_candle`, `btc.last_candle`, `btc.rows`, `btc.sha256`, `macro.columns`, `macro.first_candle`, `macro.last_candle`, `macro.rows`, `macro.sha256`, `struct.first_candle`, `struct.last_candle`, `struct.rows`
- `lineage.risk_inputs` (4): `atr`, `current_price`, `risk_regime`, `volatility_state`
- `macro_bias`
- `provenance.canonical_format`
- `provenance.decision_candles` (18): `btc.basis`, `btc.close_time`, `btc.exchange_close_time`, `btc.forming_candles_dropped`, `btc.live_price`, `btc.open_time`, `macro.basis`, `macro.close_time`, `macro.exchange_close_time`, `macro.forming_candles_dropped`, `macro.live_price`, `macro.open_time`, `struct.basis`, `struct.close_time`, `struct.exchange_close_time`, `struct.forming_candles_dropped`, `struct.live_price`, `struct.open_time`
- `provenance.engine_version`
- `provenance.fetch` (6): `effective_rows.btc`, `effective_rows.macro`, `effective_rows.struct`, `macro_requested_limit`, `pinned`, `requested_limit`
- `provenance.input_hashes` (2): `btc`, `macro`
- `provenance.last_candle`
- `provenance.module_constants` (14): `indicators.indicators.SPIKE_RATIO`, `models.btc_context.CORRELATION_WINDOW`, `models.entry_model.MIN_TREND_ADX`, `models.risk_model.ATR_STOP_MULT`, `models.risk_model.MAX_STOP_DISTANCE_PCT`, `models.risk_model.MIN_STOP_DISTANCE_PCT`, `models.risk_model.REGIME_EXTREME_STOP_PCT`, `models.risk_model.TARGET1_MULT`, `models.risk_model.TARGET2_MULT`, `models.risk_model.TARGET3_MULT`, `models.risk_model.VOL_MULT_EXTREME`, `models.risk_model.VOL_MULT_HIGH`, `models.risk_model.VOL_MULT_LOW`, `structure.structure.StructureEngine.REGIME_HYSTERESIS_THRESHOLD`
- `provenance.row_count`
- `provenance.source`
- `risk` (5): `atr_stop`, `risk_reason`, `risk_regime`, `risk_valid`, `targets`
- `structure` (6): `hvn`, `lvn`, `regime`, `sequence`, `swing_struct`, `volume_sentiment`
- `symbol`
- `timeframe`
- `trend` (2): `divergence_direction`, `momentum_divergence`

### 13.3 New fields (proposed names)

- `entry`: `distance_atr` (3.20703059 on the pinned run, computed), `distance_pts`
  (0.0), `hvn_distance_atr` (15.12021342), `hvn_pts` (0.0), `trigger` (false),
  `trigger_volume` (84693.7281), `trigger_volume_median` (179247.8923),
  `quote_volume` (the fixture's value) and `liquidity_floor` (F).
- `lineage.direction`: `ema20_rising`, `ema50_rising`, `ema20_above_ema50` (each
  true) and `result` (BULLISH), in place of `lineage.bias_components`. The four
  numbers they compare are already in `lineage.indicators_at_decision_bar`, so they
  are not copied.
- `lineage.risk_inputs.side` (LONG), in place of `bias_score`.
- `lineage.indicators_at_decision_bar.quote_volume` (read: every column is recorded,
  §5).
- Module constants: entry quality's 80, 3.0, 20 and 2.0; the CONSERVATIVE line, 50;
  the liquidity floor, F; and the trigger's lookback, 20. Each listed in
  `core/decision_log.py`, where its module is fingerprinted. Whether
  `models.bias_engine` keeps an empty entry in `module_constants` once its last
  constant goes was not read.
- Each new field declared in `core/decision_contract.py`.

## 14. The tests, one by one (version 1)

**Method.** At `e69d5bb` the suite has 874 test functions in 92 files (pytest counts
911 with parameters). A script listed, for each test function, the names its body
uses that this design removes or changes — trend health, the bias sum and its
constants, the bias label, confidence and EV, validation, the entry parts and
multipliers, the trend outputs, volume sentiment, the tier constants, entry quality,
the action ladder, the golden record, the frame's columns, the contract and the
fingerprint — and the same for each file's shared helpers. Each test it found was
then classified from its name, its docstring's first line and those names. **Test
bodies were not read line by line;** where a verdict rests on something more, it says
so. The list is the prediction the built change is checked against: a test that
moves and is not here stops the work, as an unpredicted line in a diff does.

**Verdicts.** **G** goes: what it tests leaves with the design. **R** rewritten: what
it tests stays, and its inputs, its call or its expected values move. **X** rewritten,
and its expectation reverses. **H** names something that moves and is expected to hold
unchanged. **h** names nothing that moves, but its file's helper or fixture builds
inputs that do; its assertion is expected to hold.

**Totals:** 467 tests in 68 files — 95 G, 124 R, 2 X, 118 H, 128 h. The other 407
name nothing that moves, in their bodies or their helpers, and are expected to hold;
they were not examined further. Files that go whole: `test_engine_core_confidence_score_not_duplicated.py`,
`test_entry_score_reconciles.py`, `test_trend_direction_source.py`,
`test_trend_score_has_a_denominator.py`, `test_validation_score_has_a_denominator.py`
and `test_volume_agreement.py`; `test_bias_label.py` keeps two tests, and
`test_no_circular_reasoning.py` one.

**The two X**, flagged because a test written to hold a ruling would be turned
round: `test_macro_counts_once.py::test_a_conservative_long_does_not_depend_on_macro`
and `test_signal_confirms.py::test_an_opposing_macro_does_not_block_a_confirmed_trade`.
Both hold work order G's removal of macro from the signal; the ruling of 25 October,
point 3, makes macro a gate on LONG, so both now expect a LONG refused under a
bearish daily trend. That is the ruling's consequence, not a new rule.

**New tests (proposed):** the direction rule's truth table and its floor; D and H at
their ends and in between; a part not measured degrading the run; each gate's order
and sentence; gate 6 over every macro value (§3.2); the liquidity floor, and
`quote_volume` carried by the fetcher and validated; the trigger candle, its volume
strictly above the median, and volume not measured (§3.2); the tier lines; entry 58's
helper over every threshold (§6); the state's `raw_bias` key (§2); and the second
pinned decision. Fixture-free, so `run_tests.py`'s error count does not move.

**`test_an_absent_value_is_not_a_reading.py`** — 16 of 16
- `test_every_default_in_the_panel_is_listed_with_its_reason` — R: the panel's defaults list changes
- `test_every_default_in_the_router_is_listed_with_its_reason` — R: the router's defaults list changes
- `test_negative_control_present_readings_still_print` — R: its decision carries `detailed` and the validation fields
- `test_negative_control_a_complete_input_builds_a_decision` — R: its input carries `trend_exhaustion`
- `test_an_absent_exhaustion_flag_is_refused_not_recorded_as_false` — G: the exhaustion flag leaves
- `test_an_absent_entry_number_is_recorded_as_nan_not_zero` — R: the entry numbers are D, H and their distances
- `test_negative_control_a_present_entry_number_survives` — R: same
- `test_engine_core_reads_the_computed_values_directly` — R: the six values that feed bias and entry become the direction's four and entry's three
- h, its helper or fixture moves: `test_the_inventory_sees_a_reading_when_one_is_added`, `test_a_panel_with_every_reading_absent_prints_unknown_not_a_reading`, `test_a_measured_stress_flag_still_prints_yes`, `test_an_absent_signal_is_refused_not_recorded_as_false`, `test_an_incomplete_btc_block_is_unavailable_not_an_error_for_the_asset`, `test_negative_control_a_complete_btc_block_passes_through`, `test_an_absent_correlation_label_reads_not_measured`, `test_the_router_reads_the_engine_output_by_subscript`

**`test_b10_outputs_agree_with_finding_4_and_the_action.py`** — 3 of 10
- `test_every_action_the_decision_model_writes_is_a_side_wait_or_a_no_trade` — H: the new refusals are NO-TRADE or WAIT
- `test_on_the_golden_decision_the_note_prints_on_its_trade_and_not_on_a_wait` — R: the golden decision is a WAIT; the trade half moves to the second pinned decision
- `test_built_from_the_golden_decision_the_order_carries_its_band_and_close` — H: band and close are unchanged

**`test_b4_labels_say_what_is_measured.py`** — 8 of 8
- `test_the_divergence_compares_four_candles_back_not_highs` — H: the divergence stays (§2)
- `test_fading_volume_is_a_move_on_lower_volume_in_either_direction` — H: the structure label stays
- `test_every_label_the_detector_returns_is_one_the_engine_scores` — G: no volume label is scored
- `test_no_warning_label_reaches_the_neutral_note` — G: the note is validation's
- h, its helper or fixture moves: `test_the_exit_flag_says_what_is_compared_and_which_way`, `test_an_unrecorded_direction_is_named_not_guessed`, `test_no_divergence_no_flag`, `test_the_blockers_say_what_is_compared`

**`test_band_distance_is_from_the_midpoint.py`** — 3 of 3
- `test_inside_the_band_the_line_names_the_midpoint` — R: it calls `calculate_entry_quality`, whose signature moves; the distance it checks stays
- `test_outside_the_band_the_number_is_the_midpoint_distance` — R
- `test_the_recorded_number_is_unchanged` — R

**`test_bias_label.py`** — 7 of 7
- `test_the_label_at_every_boundary` — G
- `test_a_score_not_computed_is_neutral` — G
- `test_inputs_the_engine_never_produces_are_labelled_as_before` — G
- `test_the_label_has_no_memory` — G
- `test_engine_core_labels_both_series_through_bias_label` — G
- `test_bias_engine_has_no_state_machine_class` — H: still true
- h, its helper or fixture moves: `test_engine_core_holds_no_state_machine`

**`test_btc_correlation_alignment.py`** — 11 of 11
- `test_perfectly_aligned_series_are_unchanged_by_the_fix` — H
- `test_the_pinned_fixtures_are_fully_paired` — H
- `test_an_unusable_correlation_is_labelled_not_measured` — H
- `test_the_panel_still_prints_a_correlation_it_does_have` — H
- h, its helper or fixture moves: `test_a_missing_bar_no_longer_shifts_every_pairing`, `test_the_positional_answer_and_the_aligned_answer_actually_differ_here`, `test_two_series_that_share_no_timestamps_measure_nothing`, `test_series_without_a_time_index_are_refused_not_approximated`, `test_a_real_coefficient_is_still_labelled_normally`, `test_the_panel_does_not_print_a_correlation_it_does_not_have`, `test_the_btc_block_is_strict_json`

**`test_btc_degradation_stays_informational.py`** — 3 of 3
- `test_a_btc_only_indicator_failure_does_not_move_aeros_confidence_or_gate` — R: confidence leaves; the gate half stays
- `test_the_btc_only_failure_is_still_visible_in_the_record` — R: BTC's degraded inputs come from its trend readings, not its trend health
- h, its helper or fixture moves: `test_the_negative_control_has_no_degraded_inputs`

**`test_btc_is_reference_only.py`** — 9 of 9
- `test_the_decision_model_no_longer_computes_a_btc_figure` — H
- `test_evaluate_returns_no_btc_figure` — H
- `test_a_caller_still_passing_the_old_keywords_fails_loudly` — H
- `test_the_btc_block_carries_only_what_engine_core_measured` — R: the block loses `trend_health`
- `test_the_contract_declares_neither_field` — H
- `test_the_record_names_neither_constant` — H
- `test_the_panel_keeps_the_btc_section_and_prints_no_adjusted_line` — H
- `test_a_pinned_run_records_and_prints_no_btc_figure` — H
- h, its helper or fixture moves: `test_the_block_is_available_exactly_when_engine_core_says_so`

**`test_closed_candles.py`** — 2 of 16
- `test_the_decision_candle_is_read_from_the_frame_the_fetcher_returned` — H
- `test_the_golden_record_carries_a_decision_candle_for_every_series` — H

**`test_code_fingerprint.py`** — 28 of 28
- `test_the_record_says_which_code_the_run_was_made_on` — H
- `test_the_contract_declares_the_field` — H
- `test_module_snapshot_reaches_a_constant_held_on_a_class` — R: its constant is renamed (§7)
- `test_module_snapshot_reaches_the_aggressive_trend_health_min` — G: the constant leaves
- `test_module_snapshot_reaches_the_aggressive_entry_score_min` — R: the constant is renamed (§4)
- `test_module_snapshot_reaches_the_conservative_trend_health_min` — G: the constant leaves; the new 50 line needs its own
- `test_module_snapshot_reaches_the_structure_hysteresis_threshold` — H
- `test_the_entry_scoring_constants_are_fingerprinted` — R: the entry constants are the new four
- `test_regression_guard_no_fingerprinted_name_resolves_to_missing` — H
- `test_the_code_hash_is_deliberately_not_folded_into_the_run_hash` — H
- `test_negative_control_a_comment_does_not_move_the_hash` — H
- `test_a_bare_literal_moves_the_hash` — H
- `test_a_class_attribute_moves_the_hash` — R: its constant is renamed
- `test_a_call_site_literal_moves_the_hash` — H
- `test_a_changed_comparison_moves_the_hash` — R: the comparison it edits reads trend health
- `test_a_file_that_does_not_parse_is_recorded_rather_than_skipped` — H
- `test_the_hash_is_stable_across_two_calls_on_unchanged_source` — H
- `test_the_walk_covers_the_engine_and_excludes_the_tests` — H
- `test_the_fingerprint_carries_the_interpreter_version` — H
- h, its helper or fixture moves: `test_the_code_hash_survives_into_the_permanent_log_not_just_the_return`, `test_the_archive_meta_says_which_file_changed_not_only_that_one_did`, `test_module_snapshot_reaches_spike_ratio`, `test_module_snapshot_reaches_the_correlation_window`, `test_negative_control_a_docstring_does_not_move_the_hash`, `test_negative_control_line_endings_do_not_move_the_hash`, `test_a_function_local_moves_the_hash`, `test_adding_a_source_file_moves_the_hash`, `test_removing_a_source_file_moves_the_hash`

**`test_decision_bar_integrity.py`** — 6 of 20
- `test_a_missing_rsi_no_longer_scores_full_marks` — G: RSI leaves entry quality
- `test_a_missing_hvn_no_longer_scores_full_marks` — R: a missing HVN is not measured, and entry quality is not computed
- `test_a_missing_atr_is_not_scored_against_a_fabricated_two_percent` — R: same, for ATR
- `test_calculate_stop_targets_rejects_a_non_finite_atr` — R: the call takes the side, not `bias_score`
- `test_valid_inputs_still_produce_levels` — R: same call
- `test_the_panel_never_prints_a_non_finite_number` — R: its decision's fields move

**`test_decision_contract.py`** — 6 of 6
- `test_the_decision_object_matches_the_contract` — H: the contract file changes; the test does not
- `test_the_btc_block_is_legal_in_both_of_its_shapes` — H
- `test_every_field_a_consumer_reads_is_declared` — H
- `test_every_declared_field_is_actually_produced` — H
- `test_the_scheduled_removals_are_still_present_and_still_scheduled` — H
- `test_the_aliases_the_contract_names_really_are_duplicates` — H

**`test_decision_log_record_format.py`** — 1 of 8
- `test_finite_values_are_written_exactly_as_before` — H: its sample record is its own

**`test_degraded_state.py`** — 3 of 12
- `test_confidence_and_trade_quality_are_capped_when_degraded` — R: confidence leaves; the cap on trade quality stays
- `test_a_failed_risk_calculation_does_not_invent_levels` — R: the call takes the side
- `test_the_dead_trend_failure_gate_stays_removed` — H

**`test_direction_source.py`** — 13 of 13
- `test_the_live_run_of_2_september_no_longer_returns_a_long` — R: its inputs are built for the old ladder
- `test_a_bullish_macro_cannot_open_a_direction_against_a_bearish_bias` — R
- `test_a_bearish_macro_cannot_open_a_direction_against_a_bullish_bias` — R
- `test_an_entry_zone_signal_cannot_open_a_direction_on_its_own` — R
- `test_a_long_label_on_a_short_plan_is_refused` — H: the plan-coherence guard stays
- `test_a_short_label_on_a_long_plan_is_refused` — H
- `test_the_guard_reads_the_plan_and_not_the_bias` — H
- `test_the_guard_does_not_fire_on_coherent_plans` — H
- `test_the_guard_is_silent_when_there_is_no_plan_to_read` — H
- `test_a_no_trade_action_is_left_alone` — H
- `test_the_stated_reason_never_calls_a_bearish_bias_bullish` — R: the sentences are rewritten
- `test_a_genuine_bullish_run_still_reaches_a_long` — R: a long now needs the trigger, its volume and the floor
- `test_a_genuine_bearish_run_still_reaches_a_short` — R: same

**`test_each_reading_is_printed_once.py`** — 5 of 5
- h, its helper or fixture moves: `test_no_line_is_headed_regime`, `test_structure_prints_the_regime_at_its_source`, `test_volatility_is_printed_once_on_its_own_line`, `test_no_asset_reading_carries_a_vol_field`, `test_negative_control_bitcoin_keeps_its_vol_field`

**`test_engine_core_confidence_score_not_duplicated.py`** — 3 of 3
- `test_the_raw_engine_risk_block_no_longer_states_a_second_confidence` — G
- `test_negative_control_trend_health_is_still_recorded_in_full` — G
- `test_negative_control_the_routed_decisions_confidence_is_unchanged` — G

**`test_entry_score_reconciles.py`** — 12 of 12
- `test_the_component_maximum_is_the_sum_of_the_components` — G
- `test_the_panel_does_not_keep_its_own_copy_of_the_denominators` — G: the five parts and the multipliers leave; D + H = score replaces it
- `test_each_component_can_actually_reach_its_stated_maximum` — G
- `test_the_sub_scores_sum_to_the_subtotal_exactly` — G
- `test_the_subtotal_times_the_multiplier_is_the_score` — G
- `test_the_multipliers_reported_are_the_multipliers_applied` — G
- `test_the_clip_is_declared_when_it_fires` — G
- `test_a_score_under_the_ceiling_is_not_reported_as_clipped` — G
- `test_the_panel_shows_the_reconciliation` — G
- `test_the_displayed_components_add_up_to_the_displayed_subtotal` — G
- `test_the_panel_does_not_invent_a_sub_score_it_was_not_given` — G
- `test_the_decision_object_carries_the_reconciliation` — G

**`test_entry_zone_is_measured.py`** — 8 of 13
- `test_an_absent_zone_is_not_invented_from_the_price` — R: an absent band is not measured and degrades the run
- `test_an_absent_zone_also_stops_the_atr_distance_being_scored` — G: the ATR part leaves (D covers it)
- `test_only_one_bound_is_still_no_zone` — R
- `test_a_price_that_could_not_be_read_is_not_one_dollar` — R
- `test_a_zone_with_no_width_is_not_given_one` — G: D does not use the band's width
- `test_the_not_measured_policy_is_named` — G: the two constants leave
- `test_a_real_zone_still_scores_exactly_as_before` — R: new expected values
- `test_bounds_given_the_wrong_way_round_are_still_swapped` — R

**`test_exit_model_removal.py`** — 1 of 6
- `test_the_dead_hit_literals_are_gone_from_the_panel` — H

**`test_explicit_configuration.py`** — 2 of 9
- `test_every_fingerprinted_name_exists_and_is_read` — H
- `test_a_missing_fingerprinted_name_is_recorded_not_dropped` — H

**`test_fetch_and_import_hygiene.py`** — 1 of 8
- `test_a_well_formed_response_still_becomes_a_frame` — R: asserts the five columns; the frame gains `quote_volume`

**`test_fingerprint_names_every_constant.py`** — 3 of 3
- `test_every_numeric_constant_in_a_fingerprinted_module_is_listed` — H: the list in `core/decision_log.py` changes; the test does not
- `test_the_two_found_on_21_september_that_remain_are_recorded_with_their_values` — R: to read: whether its two are among the removed
- `test_the_scan_sees_class_constants_and_skips_sentinels` — R: its examples name removed constants

**`test_frame_ownership.py`** — 1 of 8
- `test_calculate_dynamic_bias_takes_no_frame` — R: the same property, of the new direction function

**`test_golden_path.py`** — 7 of 7
- `test_decision_object_matches_snapshot` — R: re-baselined (§13)
- `test_the_snapshot_covers_every_top_level_field` — H: no top-level key is added or removed
- `test_the_macro_series_is_actually_read` — R: macro is read by gate 6, not by the bias
- `test_a_bias_flip_against_prior_state_is_reported` — R: the state compares raw labels (§2)
- `test_explanation_does_not_name_a_hardcoded_symbol` — H
- h, its helper or fixture moves: `test_engine_is_deterministic_on_identical_input`, `test_a_supertrend_flip_against_prior_state_is_reported`

**`test_imports.py`** — 2 of 6
- `test_engine_modules_is_every_module_in_the_tree` — H
- `test_the_suite_walks_the_files_code_hash_reads` — H

**`test_indicator_overlap_tool.py`** — 6 of 13
- `test_each_variant_names_weights_the_bias_engine_has` — G: no weights to name
- `test_the_weights_are_restored_after_a_variant_and_after_a_failure` — G: no weights to vary
- `test_impact_counts_changes_trades_and_flips` — H
- `test_a_no_trade_label_naming_a_side_is_not_a_trade` — H
- `test_the_baseline_reproduces_the_golden_decision` — R: the golden decision moves
- `test_no_candle_after_the_bar_is_read` — H

**`test_lineage.py`** — 10 of 17
- `test_a_run_can_be_rebuilt_from_its_own_archive_and_gives_the_same_decision` — H
- `test_the_lineage_chain_has_every_link_the_constitution_names` — R: `bias_components` becomes `lineage.direction`
- `test_the_recorded_contributions_add_up_to_the_score_they_explain` — G: no weighted sum
- `test_the_hash_does_not_change_on_column_order_or_a_rebuild` — H
- `test_nan_survives_the_round_trip_as_nan` — H
- `test_the_run_hash_moves_when_a_bias_weight_moves` — R: moves a different fingerprinted constant
- `test_the_lineage_reaches_the_written_decision_log` — H
- `test_an_archive_that_cannot_be_written_does_not_stop_the_analysis` — H
- `test_the_recorded_archive_path_is_spelled_the_same_on_every_platform` — H
- `test_a_real_run_s_archive_matches_its_decision_log_record` — H

**`test_lineage_against_record.py`** — 4 of 11
- `test_an_archive_matches_the_record_of_the_run_that_wrote_it` — H
- `test_an_edit_that_rewrites_the_frame_and_its_digest_is_caught_by_the_record` — H
- `test_a_different_run_hash_is_reported` — H
- `test_nothing_to_compare_returns_empty` — H

**`test_macro_agreement.py`** — 5 of 5
- `test_agreement_scores_and_says_so` — R
- `test_disagreement_scores_and_says_so` — R
- `test_a_neutral_macro_is_reported_as_a_neutral_macro` — R
- `test_a_directional_macro_is_never_called_neutral` — R
- `test_the_note_never_claims_more_than_it_knows` — R

**`test_macro_counts_once.py`** — 11 of 11
- `test_a_conservative_long_does_not_depend_on_macro` — X: gate 6 refuses a LONG under a bearish daily trend
- `test_a_conservative_short_does_not_depend_on_macro` — R: still true for SHORT; inputs move
- `test_negative_control_below_the_conservative_line_still_waits` — R: the line is entry quality's 50
- `test_the_decision_model_takes_no_macro_parameter` — H: gate 6 is a blocker, computed with the signal
- `test_a_fifth_positional_argument_is_refused` — R: the signature moves
- `test_trend_short_is_named_and_entry_is_not_blamed` — G: no trend tier
- `test_entry_short_is_named_and_trend_is_not_blamed` — R
- `test_both_short_are_named` — G
- `test_the_sentence_makes_no_claim_about_macro` — R: gate 6 has its own sentence
- `test_the_sentence_names_the_bias_side_and_the_trend_direction` — G: no trend-strength sentence
- h, its helper or fixture moves: `test_the_record_still_carries_the_macro_reading`

**`test_main_takes_pairs.py`** — 1 of 9
- `test_a_pair_reads_the_same_alone_as_after_other_pairs` — H

**`test_minimum_bias_strength.py`** — 10 of 10
- `test_a_weak_lean_does_not_authorise_a_direction` — R: the floor is the EMAs' order and EMA50's slope disagreeing
- `test_the_same_floor_applies_to_the_short_side` — R
- `test_a_lean_at_the_threshold_still_waits` — G: no threshold
- `test_a_conviction_past_the_threshold_still_acts` — R
- `test_both_thresholds_are_live_and_distinct` — G
- `test_the_constant_is_fingerprinted` — G
- `test_the_reason_names_the_trend_direction_not_just_its_size` — G
- `test_a_bearish_trend_under_a_bullish_bias_is_visible_in_the_sentence` — G: cannot happen: both come from the slopes
- `test_a_flat_trend_says_flat` — R
- `test_every_directional_reason_carries_the_direction` — R: the sweep stays, over the new sentences

**`test_neutral_bias_prints_no_plan.py`** — 14 of 14
- `test_a_neutral_bias_prints_one_line_saying_why` — R: its input carries a score
- `test_the_plan_line_prints_a_negative_score_with_its_sign` — G: no `bias.score` to print
- `test_a_score_of_exactly_zero_prints_no_long` — G
- `test_a_neutral_score_not_computed_says_so` — G
- `test_on_a_real_decision_object_the_real_target_1_note_is_withheld` — H
- `test_a_neutral_bias_never_reaches_long_or_short` — R
- h, its helper or fixture moves: `test_a_neutral_bias_prints_no_stop_no_targets_and_no_rr`, `test_the_decision_close_is_printed_but_not_called_the_plans_entry`, `test_the_target_1_note_is_not_printed_but_other_flags_are`, `test_with_only_the_target_1_note_exit_watch_says_nothing_is_active`, `test_bullish_and_bearish_still_print_the_whole_plan`, `test_a_raw_bias_the_engine_never_emits_prints_the_plan_as_before`, `test_rendering_leaves_the_plan_in_the_decision_object`, `test_negative_control_the_same_grid_reaches_a_side_under_a_direction`

**`test_no_circular_reasoning.py`** — 14 of 14
- `test_confidence_is_a_pure_function_of_bias_score` — G
- `test_confidence_still_moves_with_bias_strength` — G
- `test_confidence_can_still_reach_the_top_of_its_range` — G
- `test_structure_regime_does_not_move_confidence_a_second_time` — G
- `test_macro_and_volume_agreement_do_not_move_confidence_a_second_time` — G
- `test_compute_confidence_signature_has_no_room_for_the_duplicated_inputs` — G
- `test_continuation_strength_no_longer_contains_a_health_derived_term` — G
- `test_continuation_strength_ignores_adx` — G
- `test_validation_is_not_seeded_with_trend_health` — G
- `test_the_panel_prints_trend_health_once` — G
- `test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input` — G
- `test_the_reasoning_no_longer_claims_structure_or_validation_as_a_bonus` — G
- `test_structure_regime_is_a_function_of_close_alone` — H: structure stays
- `test_rsi_exemption_holds_in_downtrends_and_not_in_uptrends` — G: trend health's RSI exemption

**`test_no_dead_columns.py`** — 3 of 3
- `test_consumed_columns_are_still_produced` — R: the consumers change; it will say whether VWMA is still read
- h, its helper or fixture moves: `test_deleted_columns_stay_deleted`, `test_slope_columns_are_not_all_zero`

**`test_no_fabricated_fallbacks.py`** — 3 of 7
- `test_engine_core_does_not_substitute_a_midpoint_trend_health` — G
- `test_compute_trend_health_is_total_which_is_why_the_handler_could_go` — R: the property, of the reduced function
- `test_a_broken_trend_contract_is_reported_not_papered_over` — R

**`test_no_position_sizing.py`** — 3 of 9
- `test_the_decision_log_does_not_fingerprint_a_balance` — H
- `test_the_survivors_are_still_there` — R: `trend_health` and `momentum_mode` are no longer survivors
- `test_the_decision_model_reads_the_canonical_trend_field` — G

**`test_no_risk_free_conviction.py`** — 10 of 10
- `test_high_conviction_in_a_normal_risk_regime_is_still_aggressive` — R: AGGRESSIVE comes from quality, band and regime
- `test_high_conviction_in_a_low_risk_regime_is_still_aggressive` — R
- `test_the_audits_concrete_scenario_no_longer_returns_aggressive` — R
- `test_high_conviction_in_an_extreme_risk_regime_is_not_aggressive` — R
- `test_the_short_side_is_gated_the_same_way` — R
- `test_the_capped_reasoning_names_the_risk_regime_not_a_position_size` — R
- `test_conviction_alone_cannot_select_aggressive_across_every_regime` — R
- `test_validate_risk_parameters_returns_the_risk_regime` — H
- h, its helper or fixture moves: `test_validate_risk_parameters_regime_across_volatility_tiers`, `test_validate_risk_parameters_regime_across_stop_widths`

**`test_no_trend_no_trade.py`** — 13 of 13
- `test_the_threshold_is_20_and_in_the_run_hash` — H
- `test_a_call_in_the_shape_before_fix_2_is_refused` — H
- `test_engine_core_hands_the_gate_adx_and_not_the_flag` — H: ADX stays in the trend readings
- `test_a_low_adx_refuses_a_trade_the_ladder_chose_and_says_why` — R: its inputs carry `detailed`
- `test_a_confirmed_trade_says_adx_is_20_or_more` — H
- `test_an_unreadable_adx_on_a_degraded_run_takes_the_signal_label` — R
- `test_on_the_engine_path_a_low_adx_refuses_the_pinned_long` — R: the pinned run is no longer a long
- h, its helper or fixture moves: `test_20_confirms_and_anything_under_it_blocks_both_sides`, `test_low_adx_blocks_the_side_whose_structure_agrees_and_adds_to_the_other`, `test_the_printed_adx_never_reads_as_the_threshold`, `test_an_adx_with_no_valid_reading_blocks_both_sides`, `test_numpy_numbers_are_valid_readings`, `test_on_the_engine_path_an_unreadable_adx_blocks_both_sides`

**`test_one_name_one_meaning.py`** — 5 of 5
- `test_a_name_that_says_vwma_reads_the_engines_vwma` — R: to read: VWMA leaves entry quality
- `test_the_check_sees_the_vwma_that_is_there` — R: same
- `test_the_check_catches_the_name_round_8_found` — H
- `test_the_momentum_label_is_printed_once_on_the_trend_line` — G: `momentum_mode` leaves
- h, its helper or fixture moves: `test_no_line_is_headed_momentum`

**`test_panel_no_fabricated_price_defaults.py`** — 8 of 8
- h, its helper or fixture moves: `test_an_absent_current_price_is_not_a_price_of_zero`, `test_an_absent_stop_is_not_a_price_of_zero`, `test_absent_targets_are_not_three_zeros`, `test_a_malformed_targets_value_is_not_three_zeros`, `test_a_target_present_without_a_known_stop_shows_rr_not_computed`, `test_negative_control_a_real_current_price_and_stop_survive`, `test_negative_control_a_real_zero_stop_is_still_a_real_zero`, `test_negative_control_lines_still_terminate_properly`

**`test_panel_prints_only_what_was_computed.py`** — 10 of 10
- `test_absent_scores_print_as_absent_not_as_zero` — R
- `test_a_computed_score_still_prints_with_its_scale` — R
- `test_a_real_zero_is_still_printed_as_zero` — R
- `test_decision_reasoning_says_trend_strength_was_not_computed` — G
- `test_the_panel_and_the_reasoning_use_one_function` — H
- h, its helper or fixture moves: `test_no_number_on_the_panel_prints_as_nan`, `test_the_btc_section_names_the_asset_the_run_was_made_on`, `test_a_btcusdt_run_does_not_mention_aero`, `test_an_aero_run_still_says_aero`, `test_asset_name_strips_the_quote_currency_longest_first`

**`test_pinned_runs_keep_their_own_records.py`** — 2 of 10
- `test_every_other_run_goes_to_pinned_spelled_the_same_on_every_platform` — H
- `test_exit_watch_compares_a_run_only_with_the_last_run_from_its_own_source` — R: the state key moves (§2)

**`test_pinned_source.py`** — 1 of 11
- `test_manifest_hashes_match_the_files` — H: `MANIFEST.json` is regenerated with the fixture

**`test_plan_direction_and_side.py`** — 6 of 6
- `test_detailed_bias_is_no_longer_accepted` — H
- `test_the_plan_direction_is_the_sign_of_bias_score` — R: the plan's direction is the side
- `test_a_nan_bias_score_is_refused_rather_than_read_as_short` — R: a side that is not LONG or SHORT is refused
- `test_every_plan_the_engine_can_ask_for_has_its_stop_on_the_correct_side` — R
- `test_a_stop_that_would_land_on_the_wrong_side_raises` — R: its trigger was |bias_score| ≥ 300; to read whether the guard still has a reachable case
- `test_the_lineage_no_longer_lists_detailed_bias_as_a_risk_input` — R: `bias_score` leaves the risk inputs too

**`test_regime_from_volatility_alone.py`** — 3 of 11
- `test_a_keyword_the_risk_check_does_not_take_is_refused` — H
- `test_the_regime_names_the_volatility_the_panel_prints` — H
- `test_the_two_adx_constants_are_gone` — H

**`test_risk_fingerprint.py`** — 11 of 11
- `test_the_risk_model_is_fingerprinted_at_all` — H
- `test_every_fingerprinted_name_exists_and_is_a_number` — H
- `test_no_fingerprinted_constant_is_dead` — H
- `test_the_multipliers_have_not_returned_to_the_instance` — H
- `test_the_stop_is_computed_from_the_fingerprinted_multiplier` — H
- `test_each_target_is_computed_from_its_own_fingerprinted_multiplier` — H
- `test_the_volatility_multipliers_are_read` — H
- `test_the_regime_boundaries_are_read` — H
- `test_the_stop_distance_limits_are_read` — H
- h, its helper or fixture moves: `test_module_snapshot_actually_carries_the_risk_constants`, `test_the_rejection_message_quotes_the_constant_it_enforces`

**`test_risk_regime_independence.py`** — 4 of 4
- `test_trend_health_is_not_a_parameter_of_classify_risk_regime` — H
- `test_validate_risk_parameters_rejects_trend_health_rather_than_ignoring_it` — H
- `test_control_extreme_gates_are_untouched` — H
- h, its helper or fixture moves: `test_control_extreme_risk_still_fails_risk_valid_outright`

**`test_risk_verdict_is_read_not_assumed.py`** — 18 of 18
- `test_negative_control_an_assessed_pass_still_authorizes` — R: its ladder inputs carry trend health
- `test_an_empty_risk_block_is_refused_rather_than_read_as_a_pass` — R
- `test_a_partial_risk_block_without_the_verdict_is_refused` — R
- `test_a_verdict_present_as_none_is_refused` — R
- `test_a_truthy_non_boolean_verdict_is_refused_not_believed` — R
- `test_negative_control_a_real_failed_check_still_says_so` — R
- `test_the_two_no_trade_states_are_not_the_same_string` — R
- h, its helper or fixture moves: `test_a_verdict_is_returned_only_when_there_is_one`, `test_negative_control_a_well_formed_engine_output_is_accepted`, `test_negative_control_an_error_payload_is_still_a_valid_payload`, `test_an_engine_output_whose_risk_block_has_no_verdict_is_rejected`, `test_a_run_with_no_risk_verdict_produces_an_error_not_a_decision`, `test_negative_control_a_stubbed_well_formed_run_still_reaches_a_decision`, `test_the_recorded_verdict_is_the_one_that_was_read_not_an_invented_pass`, `test_the_simulated_order_records_no_verdict_rather_than_a_pass`, `test_negative_control_the_simulated_order_still_carries_a_real_verdict`, `test_no_module_defaults_a_missing_risk_verdict_to_a_pass`, `test_negative_control_the_default_scan_can_report_a_violation`

**`test_round8_f9_claims_match_the_code.py`** — 11 of 11
- `test_trend_health_with_no_frame_reports_unavailable` — G
- `test_trend_health_without_its_slopes_reports_unavailable` — G
- `test_unavailable_trend_direction_moves_no_entry_score` — G: no trend multiplier
- `test_a_failed_volume_read_is_not_reported_as_neutral` — G: validation's note leaves; the lesson moves to gate 8 (§3.2)
- `test_a_neutral_volume_read_is_still_reported_as_neutral` — G
- `test_the_adx_failure_note_states_what_is_lost` — R: what is lost changes
- `test_the_trend_line_prints_unknown_for_a_missing_label` — R: the TREND line loses its health and momentum
- h, its helper or fixture moves: `test_the_gap_helper_builds_the_gap_it_is_asked_for`, `test_a_reused_engine_answers_as_a_fresh_one_does`, `test_the_regime_reads_the_side_the_gap_points_to_outside_the_band`, `test_a_frame_too_short_to_read_is_unknown_not_neutral`

**`test_router_btc_seam.py`** — 8 of 8
- `test_an_unmeasured_correlation_does_not_arrive_as_a_measurement` — H
- `test_a_failed_assembly_still_carries_the_runs_lineage` — H
- `test_the_lineage_survives_into_the_written_record` — H
- h, its helper or fixture moves: `test_the_merge_accepts_the_producers_not_measured_shape`, `test_a_measured_relationship_passes_through_unchanged`, `test_a_value_that_is_not_a_finite_number_is_not_measured`, `test_the_router_completes_when_the_correlation_cannot_be_measured`, `test_the_control_case_still_works`

**`test_router_no_fabricated_zero_defaults.py`** — 9 of 9
- h, its helper or fixture moves: `test_an_absent_entry_zone_is_not_located_at_zero`, `test_an_absent_stop_is_not_a_price_of_zero`, `test_an_absent_targets_tuple_is_not_three_zeros`, `test_a_malformed_targets_value_is_not_three_zeros`, `test_an_absent_current_price_is_not_a_price_of_zero`, `test_negative_control_a_real_entry_zone_survives`, `test_negative_control_a_real_stop_and_targets_survive`, `test_negative_control_a_real_current_price_survives`, `test_negative_control_a_real_zero_price_is_still_a_real_zero`

**`test_send_audit_round.py`** — 1 of 46
- `test_the_package_reads_the_engine_code_hash_reads` — H

**`test_send_round8_fix_verification.py`** — 1 of 25
- `test_the_package_carries_what_the_decision_names_in_order` — H

**`test_signal_confirms.py`** — 21 of 21
- `test_the_signal_no_longer_takes_the_inputs_that_were_ruled_out` — R: macro returns to the signal, as a LONG gate
- `test_a_clean_bullish_setup_confirms_the_long_and_not_the_short` — R: the signal function takes two more inputs (gates 6 and 7, §4)
- `test_each_side_signal_is_exactly_an_empty_blocker_list` — R
- `test_structure_against_the_side_blocks_it` — R
- `test_adx_under_20_blocks_both_sides` — R
- `test_a_divergence_against_the_trade_blocks_it` — R
- `test_a_divergence_pointing_with_the_trade_does_not_block_it` — R
- `test_a_divergence_of_unrecorded_direction_is_not_a_confirmation` — R
- `test_a_confirmed_long_is_still_taken` — R
- `test_a_confirmed_short_is_still_taken` — R
- `test_an_unconfirmed_long_becomes_no_trade_and_says_why` — R
- `test_a_counter_divergence_now_blocks_a_conservative_trade` — R
- `test_a_counter_divergence_refuses_an_upper_tier_trade_instead_of_demoting_it` — R
- `test_a_divergence_pointing_with_the_trade_no_longer_demotes_it` — R
- `test_the_ladder_no_longer_reads_divergence_at_all` — H
- `test_an_opposing_macro_does_not_block_a_confirmed_trade` — X: gate 6 blocks a LONG under a bearish daily trend
- `test_a_missing_signal_record_fails_safe` — H
- `test_a_signal_contradicting_its_own_blockers_is_not_a_confirmation` — H
- `test_risk_refusal_keeps_the_label_and_records_the_signal_failure_too` — H
- `test_risk_refusal_with_a_confirmed_signal_adds_nothing` — R: the signal function takes two more inputs (gates 6 and 7, §4)
- `test_a_degraded_run_keeps_the_signal_refusal_as_its_label` — H

**`test_smoke.py`** — 1 of 3
- `test_the_smoke_run_is_reproducible` — H

**`test_stop_ignores_conviction.py`** — 6 of 6
- `test_trend_health_is_no_longer_accepted` — H
- `test_a_positional_call_is_refused` — R: the old order names `bias_score`
- `test_the_stop_is_the_same_at_every_conviction` — G: no conviction is passed
- `test_the_risk_verdict_is_the_same_at_every_conviction` — G
- `test_engine_core_passes_no_trend_health_to_the_stop` — H
- `test_the_record_holds_every_input_the_stop_reads` — R: `side` replaces `bias_score`

**`test_stop_is_atr_only.py`** — 6 of 6
- `test_a_structural_level_is_no_longer_accepted` — R: call shape
- `test_the_stop_is_exactly_the_atr_stop` — R
- `test_on_the_engine_path_the_stop_is_the_atr_stop_not_the_hvn` — H
- h, its helper or fixture moves: `test_engine_core_passes_no_structural_level_to_the_stop`, `test_the_lineage_no_longer_lists_a_structural_level_as_a_risk_input`, `test_the_eight_and_fifteen_percent_limits_are_unchanged`

**`test_structure_fallbacks.py`** — 9 of 9
- `test_failed_labels_say_unknown_rather_than_neutral` — H
- `test_a_missing_volume_node_scores_no_structure_points` — R: a missing HVN is not measured and degrades the run
- `test_the_panel_does_not_draw_a_level_it_does_not_have` — H
- `test_the_swing_line_occupies_a_line_of_its_own` — H
- h, its helper or fixture moves: `test_every_failed_sub_routine_is_recorded`, `test_a_failed_volume_node_is_not_the_current_price`, `test_a_failed_swing_detector_is_not_the_current_price`, `test_a_clean_run_records_no_degradation`, `test_an_empty_frame_reports_levels_as_absent_not_as_zero`

**`test_summary_names_the_action_reason.py`** — 10 of 10
- `test_a_refused_trade_is_not_summarised_as_worth_taking` — R: no EV sentence to head it
- `test_the_ev_sentence_is_still_present_in_the_reasons` — G
- `test_a_degraded_run_that_changes_the_action_is_summarised_by_that_change` — R
- `test_an_incoherent_plan_refusal_is_summarised_by_the_refusal` — R
- `test_a_normal_long_is_summarised_by_the_reason_it_is_a_long` — R
- `test_the_ev_sentence_says_it_is_confidence_restated` — G
- `test_the_quoted_confidence_levels_follow_the_constants` — G
- `test_the_breakeven_band_constant_is_live` — G
- `test_ev_is_a_straight_line_in_confidence` — G
- h, its helper or fixture moves: `test_the_summary_reason_is_one_of_the_reasons`

**`test_swing_structure_is_not_invented.py`** — 15 of 15
- `test_the_absent_level_does_not_mark_the_run_degraded` — H
- `test_negative_control_analyze_still_locates_a_level_on_a_normal_frame` — H
- `test_the_panel_says_not_located_for_a_frame_that_located_nothing` — H
- h, its helper or fixture moves: `test_the_reachable_window_between_the_two_minimums_still_exists`, `test_a_twenty_row_frame_does_not_get_its_own_price_back`, `test_a_much_shorter_frame_does_not_get_its_own_price_back`, `test_a_missing_frame_does_not_get_a_price_back`, `test_a_frame_with_no_confirmable_swings_does_not_get_its_own_price_back`, `test_negative_control_a_locatable_swing_is_still_returned`, `test_analyze_reports_the_absent_level_rather_than_a_price`, `test_a_structure_block_with_no_swing_level_does_not_become_the_price`, `test_negative_control_a_located_level_still_reaches_the_record`, `test_the_producer_returns_no_expression_built_from_the_current_price`, `test_negative_control_the_return_scan_can_report_a_violation`, `test_the_router_assembles_the_field_with_no_price_shaped_default`

**`test_timeframe_disagreement.py`** — 2 of 7
- `test_a_bullish_macro_alone_cannot_produce_a_long` — H: direction no longer reads macro at all
- `test_the_engine_still_reaches_a_side_when_the_timeframes_agree` — R: on generated data, a side now also needs the trigger and its volume

**`test_traceability.py`** — 5 of 5
- `test_the_log_records_what_the_run_saw_not_just_what_it_decided` — H
- h, its helper or fixture moves: `test_the_decision_log_the_panel_claims_actually_exists`, `test_engine_version_is_written_somewhere_at_last`, `test_a_failed_write_is_reported_as_a_failure`, `test_the_panel_makes_no_unconditional_claims_about_files`

**`test_trend_direction_source.py`** — 7 of 7
- `test_a_decelerating_trend_keeps_its_direction` — G
- `test_the_same_holds_for_a_decelerating_downtrend` — G
- `test_continuation_still_floors_and_still_counts_for_nothing` — G
- `test_the_direction_is_not_inferred_from_continuation_any_more` — G
- `test_a_flat_trend_still_contributes_nothing` — G
- `test_the_parameter_is_required_and_validated` — G
- `test_trend_health_reports_a_sign_that_matches_its_own_label` — G

**`test_trend_score_has_a_denominator.py`** — 4 of 4
- `test_the_trend_score_carries_its_denominator` — G: the trend score leaves
- `test_the_floor_and_the_ceiling_both_print_it` — G
- `test_the_labels_are_still_printed_beside_the_score` — G
- `test_the_scale_the_panel_claims_is_the_one_the_indicator_produces` — G

**`test_validation_score_has_a_denominator.py`** — 4 of 4
- `test_the_validation_score_carries_its_denominator` — G: the validation score leaves
- `test_the_floor_and_the_ceiling_both_print_it` — G
- `test_the_state_is_still_printed_beside_the_score` — G
- `test_the_score_bounds_the_engine_can_produce_are_the_ones_claimed` — G

**`test_volume_agreement.py`** — 8 of 8
- `test_the_defect_itself` — G: volume agreement leaves with validation
- `test_agreement_scores_and_says_so` — G
- `test_disagreement_is_penalised_both_ways` — G
- `test_fading_volume_still_penalised_regardless_of_bias` — G
- `test_neutral_volume_scores_nothing` — G
- `test_a_neutral_bias_has_nothing_to_agree_with` — G
- `test_no_label_is_ever_called_supportive_while_opposing` — G
- `test_it_agrees_with_the_bias_engine_about_direction` — G

## 15. Corrections to version 0

Recorded, not quietly changed:

1. **§10 named the wrong gate.** Version 0 said the pinned run fails at gate 9
   "before the trigger and volume gates are even reached". By §4's own order gate 8
   comes before gate 9, and the pinned decision candle fails gate 8 on both of its
   counts (§13.1). The predicted action, WAIT, stood; the reason given did not. The
   sentence was written from `d` and `h` alone, without reading the candle.
2. **§3.2 settled entry 14 for the wrong reason and placed entry 19 in the wrong
   section.** Entry 14 is settled because the macro multiplier leaves, and its two
   vocabularies meet again at gate 6; entry 19 is in the bias (§2). Both had been
   marked as Claude's reading, to be confirmed, and reading them is what found this.
3. **§5 gave an unmeasured market the label of a thin one.** An absent
   `quote_volume` now degrades the run instead of failing gate 7 as NO-TRADE (THIN
   MARKET).

## 16. What it weakens, and the case against (version 2)

*Written on 7 November 2026, in the session that opened at 04:30 at `4ab59d7`, before
any of the reading of 14 November's data was read for it, so that the case against
cannot be fitted to that reading (§12, point 5). It is for the design as a whole, as
drafted; what the rulings themselves weaken is in their own entries ("Ruling,
25 October 2026 — the engine's indicators …", "Ruling, 31 October 2026 — volume enters
the redesign as two gates …"), and what the reading's method weakens in "Decision,
2 November 2026 — how the reading of 14 November measures the redesign draft's gaps …".
Neither is repeated here.*

### 16.1 Found writing it: §2's direction and the band of §3.1 and §4 cannot meet

*Version 3: resolved by Viktor's ruling of 7 November on §2's direction (§16.4). What
follows is version 2's finding, about versions 0 to 2's direction, kept as written.*

**Read** at `4ab59d7`, in `indicators/indicators.py`: `EMA_20` and `EMA_50` come from
`ta.ema`, or from `ewm(span, adjust=False)` when it fails, and each slope is the
one-candle change of its EMA, `(EMA_t − EMA_{t−1}) / EMA_{t−1} × 100` (the slope loop).
Both EMAs are recursive after their warm-up: `EMA_t = EMA_{t−1} + α × (close_t −
EMA_{t−1})`, with α = 2 / (length + 1) between 0 and 1. So, on every candle after the
warm-up:

- `EMA20_Slope` is above zero exactly when the close is above the previous candle's
  `EMA_20`; the same holds for `EMA50_Slope` and `EMA_50`.
- When it is, `EMA_20` moves part of the way toward the close and stops short of it,
  so **the close is above this candle's `EMA_20` as well.**

**Checked** in the sandbox (Linux), on the pinned candles: through the engine's
`add_technical_indicators` with `pandas_ta`, and through `ewm(span, adjust=False)`
alone without it, the sign of each slope equalled the sign of the close minus the
previous EMA on all 400 rows of `AEROUSDT_4h.csv` and of `BTCUSDT_4h.csv`, and on
every row §2's rule calls BULLISH the close was above `EMA_20` (236 rows on AERO, 110
on BTC), on every BEARISH row below it (42, 145). The identity is algebra and holds on
any candles and either platform; the check is that the code computes what the algebra
assumes. Whether `ta.ema`'s warm-up seed differs from `ewm`'s was not read; it does not
reach a candle after the warm-up.

What follows for the draft as written:

1. **§2's rule, stated plainly:** BULLISH is "the close is above both EMAs' previous
   values, and `EMA_20` is above `EMA_50`" — one candle's close against two levels.
   That is what "EMA slope up" in ruling 1's hypothesis means on a one-candle slope.
   Whether it is what Viktor meant is his to say (§0).
2. **No candle with a side closes inside the band.** When `EMA_20` is above `EMA_50`
   the band's upper edge is `EMA_20`, and a BULLISH close is above it; BEARISH is the
   mirror. **§4's AGGRESSIVE, read as "close inside the band", is never reached, on
   either side.** Version 1 called that condition "today's rule minus trend health";
   today's rule is ACTIVE ENTRY ZONE, a close within one band width of the midpoint
   (`models/entry_model.py`, `dist_to_mid <= zone_width`, read), which is not the same.
   Read that way, AGGRESSIVE is reached only by a close between the band's edge and
   half a band width beyond it. `docs/build/measure_draft_gaps.py` counts both (its
   reading 3); which one §4 means is open.
3. **§3.1's full distance points are never reached on a candle with a side.** There
   `d` is more than half the EMAs' gap in ATRs, `(EMA_20 − EMA_50) / (2 × ATR)`, so the
   gap caps D: at a gap of 2 ATR, D stays under 160 / 3, about 53.3, and LONG (70)
   needs the HVN within a third of an ATR. The tier therefore partly reads the EMAs'
   spread, and a wider spread scores worse. Whether a wider spread goes with a
   stronger trend on these pairs was not checked.
4. **What the design does, then:** it enters on the candle that closes back above the
   previous `EMA_20` (and above its own open and the previous close, §5's trigger), and
   scores how little that close is beyond the band. That is a defensible pullback
   entry, the reclaim of the fast average, but it is not the pullback to the band's
   middle that §3.1 says it scores.

**Predicted for the reading of 14 November, from the identity and not from data:**
computation 2's AGGRESSIVE count with the close inside the band is zero on every pair,
whatever the candles; its count as today reads AGGRESSIVE can hold only closes in the
strip of point 2. Every record whose close is at or under the previous `EMA_20` and
whose action today is a LONG is NEUTRAL under the draft, which bears on computation
1(b); no number is predicted for it.

**Not decided here.** §2, §3.1 and §4 are reconciled before the draft goes to Viktor
(§12, point 7). Ways it could go, none proposed yet: measure entry quality's distance
from `EMA_20`, or from the band's near edge, instead of the middle; take the floor
from `EMA_50`'s slope and the cross, which lets a close sit inside the band; or drop
AGGRESSIVE's band condition. The floor and the tier lines are Viktor's (§0); entry
quality's formula is Claude's.

### 16.2 What it weakens

- **Direction rests on one candle's close against one level, and the EMAs' order**
  (§16.4, point 1), where today's sum takes six inputs. A close a tick either side of
  the previous `EMA_50` turns BULLISH into NEUTRAL, with no hysteresis; under versions
  0 to 2 it was the previous `EMA_20` as well (16.1, point 1). Entry 6, a side held for N closed
  candles, is a separate trading rule of Viktor's and not in this design.
- **Three paths to WAIT go and nothing replaces them:** the CHOCH ×0.5 discount (§2),
  H1's branch (§4, §8) and trend health's tiers; and the exit watch loses its
  exhaustion and reversal flags (§2). Each is flagged where it is. Together, the design
  drops refusals of today's kind and adds gates of a new kind, and the reading counts
  only how often it would trade (computation 6), not whether the refusals it drops were
  right.
- **The record loses its continuous measures.** `bias.score`, confidence and the
  validation score leave (§2, §4, §7). A reader of the paper-trading year's records sees
  which gates passed and a tier, and no number for how strong a case was; entry
  quality is the only score left.
- **The golden snapshot stops covering a trade's plan** until the second pinned
  decision (§10) is chosen. Until then, a defect in a passing run's stop, targets or
  sizing would not move the golden test.
- **More runs degrade.** A missing ATR, band or HVN no longer scores a neutral part
  (§3.1), and an absent `quote_volume` degrades the run (§5). That keeps the rule of
  29 August, and it means more runs that authorize no trade.
- **Its new numbers are set by reasoning only:** entry quality's 80, 3, 20 and 2, the
  CONSERVATIVE line 50 and the trigger's lookback of 20 (§13.3) — six constants, none
  on the tunable list (§9) and none measured against an outcome. F is measured by the
  reading and is Viktor's.

### 16.3 The case against

1. **16.1.** As drafted in version 2, §2 and §3.1 and §4 described two different
   entries, and the draft was not ready to put to Viktor whatever the reading showed.
   Reconciled in version 3 by the ruling of 7 November (§16.4); what that ruling
   weakens is in its own entry.
2. **The trigger is proposed, not ruled** (§5): the ruling of 31 October assumes a
   resumption candle and does not define one, and the trigger decides when the engine
   enters. It is one candle's shape, chosen without data; backtesting is closed, so
   nothing will show whether it picks better entries than no trigger, and the reading
   counts only how often it blocks.
3. **Gates in series.** Ten gates, each a refusal. Today's sum lets a strong part
   outweigh a weak one; the gates do not. The reading counts what that costs in trades
   (computation 6), not what it saves.
4. **The size of one change.** 467 of the suite's 874 test functions move and 81 of
   227 golden leaves go (§13, §14), on the decision path, in one change (ruling 7 of
   25 October). The defect this project names most often, the `confidence_score` →
   `confidence` rename that broke fourteen modules, came from one renamed field. §14's
   list is the guard — a test that moves and is not on it stops the work — and its
   verdicts were classified from names and docstrings, not read line by line (§14,
   "Method").
5. **The design and this section have one author.** Every proposal here is the code's
   author's, and so is the case against it. Amazon's audit, after the design is built,
   is the first reading by anyone else (ruling 8 of 25 October).

### 16.4 Version 3: §2, §3.1 and §4 reconciled

*Written on 7 November 2026, in the session that opened at 05:14 at `94b7e96`, before
any of the reading of 14 November's data was read. §12's point 7.*

**Ruled.** Viktor ruled the floor on 7 November, by agreeing to Claude's suggestion
(DECISIONS, "Ruling, 7 November 2026 — the redesign's direction is EMA50's slope and the
EMAs' order …"): BULLISH when `EMA50_Slope > 0` and `EMA_20 > EMA_50`, BEARISH when both
point down, else NEUTRAL (§2). The other route put to him kept versions 0 to 2's
direction and measured entry quality's distance from `EMA_20` with a new AGGRESSIVE
line; the entry gives Claude's reasons for this one and what it weakens, not repeated
here.

**What follows, by the algebra of §16.1** (read at `94b7e96`,
`indicators/indicators.py`, unchanged since version 2's read):

1. **§2's rule, stated plainly:** BULLISH is "the close is above the previous candle's
   `EMA_50`, and `EMA_20` is above `EMA_50`". `EMA20_Slope` decides nothing.
2. **A BULLISH close is above this candle's `EMA_50` too**, so above the band's lower
   edge; BEARISH is the mirror. It can be inside the band: a close below the previous
   `EMA_20` and above the previous `EMA_50` turns the fast average down and keeps the
   side. §4's AGGRESSIVE, read as "close inside the band", is reachable; so is the
   reading as today's ACTIVE ENTRY ZONE. Which one §4 means is still open (§4).
3. **§3.1's full distance points are reachable on a candle with a side:** the band's
   middle is above `EMA_50`. On a candle whose close is above the band, `d` is still
   more than half the EMAs' gap in ATRs, as in §16.1's point 3; a close inside the band
   is not bound by it.
4. **What the design does, then:** within a trend whose slow average rises and whose
   averages are in order, it enters on the trigger candle (§5) and scores how near that
   close is to the band's middle. That is the pullback to the average §3.1 says it
   scores.

**Checked** in the sandbox (Linux, Python 3.12.3, pinned requirements, at `94b7e96`),
through `add_technical_indicators` with `pandas_ta`, on the pinned candles, all 400 rows
after the warm-up: the sign of `EMA50_Slope` equalled the sign of the close minus the
previous `EMA_50` on every row of `AEROUSDT_4h.csv` and of `BTCUSDT_4h.csv`, and no
close with a side under §2 was on the wrong side of `EMA_50`. Rows with a side: AERO
342, 64 of them inside the band; BTC 307, 52 inside (versions 0 to 2's direction: 278
and 255, none inside). Changes of side: AERO 41, BTC 45 (65 and 57). Without `pandas_ta`
the engine's indicators do not import; `ewm(span, adjust=False)` alone, over rows 50 to
449, gave AERO 343 and BTC 305 sides, 64 and 50 inside, 41 and 41 changes, and no close
on the wrong side; the warm-up seeds differ, not read. Synthetic candles: none of these
counts says anything about the live pairs.

**Predicted for the reading of 14 November, from the identity and not from data:** under
computation 1 as amended, no record with a side closes on the wrong side of its
`EMA_50`; every record whose close is at or under the previous `EMA_50` and whose action
today is a LONG is NEUTRAL under the draft, which bears on computation 1(b), and no
number is predicted for it. Version 2's prediction that computation 2's count of
AGGRESSIVE with the close inside the band is zero on every pair no longer holds, and
nothing is predicted for it.

**What this section changes elsewhere:** §0 marks the floor ruled; §2 states the rule;
§3.1's and §4's pointers; §12's point 7 done; §13.1's gate 2 reads EMA50's slope (the
pinned run is BULLISH under both rules); one verdict's reason in §14
(`test_a_weak_lean_does_not_authorise_a_direction`); §16.1 kept as version 2's finding;
§16.2's first bullet; §16.3's point 1. §13's leaves do not change: the pinned run is
BULLISH and passes gate 2 under both rules. §14's counts are not changed and no test was
re-classified for the rule, only one reason reworded; its verdicts were classified from
names and docstrings, as its method says, and were not re-read for version 3.
