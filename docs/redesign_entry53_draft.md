# The redesign (entry 53) — design draft

*Draft v0, started 1 November 2026 in the session that opened at 17:49, read at
`e748b0b`, and filed in the repository by the commit that records `f6aa126`'s landing.
Claude's draft. It will be put to Viktor after the forward measurement's
reading of 14 November (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators
…", point 7). Nothing here is ruled, and no code is written from it until it is.
Each statement says where it comes from: **read** means read in the code at
`e748b0b`; **ruled** names the ruling; **proposed** is Claude's suggestion; **to
measure** is a number this draft does not have yet. Where something was not checked,
the sentence says so.*

## 0. Who decides what

- **Viktor's, as the design's ruling** (25 October, "What follows"): the whole design
  before it is built. Inside it, these are new trading rules or change one of his
  rulings, so they are his even under the delegation of 29 October: the strength floor
  (§2), the trigger candle (§5), the liquidity floor's value (§5), the tier lines
  (§4), whether the structure multiplier stays (§3.3), and any ruled value named as
  tunable (§9).
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

**Proposed: direction needs both EMAs to agree, and that agreement is the floor.**

- BULLISH when `EMA20_Slope > 0`, `EMA50_Slope > 0` and `EMA_20 > EMA_50`.
- BEARISH when all three point down.
- Anything else is NEUTRAL: a lean, and WAIT.

Why: the 5 September ruling separates a lean from a case. Once the sum is gone, the
plainest version of that line on the slope itself is the two averages disagreeing:
the fast one has turned and the slow one has not, or they have crossed back. That
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
- `calculate_dynamic_bias` is replaced by a function of the two slopes and the two
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
- `RAW_BIAS_THRESHOLD`, the six `WEIGHT_*` constants and `MIN_ACTION_BIAS` leave the
  fingerprinted constants. That moves `run_hash` (predicted).

**To measure before it is put to him:** on the ten pairs' archived candles, how often
the proposed direction agrees with today's `raw_bias`, and how often it is NEUTRAL
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
  middle, nothing beyond three ATRs.
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

### 3.2 What leaves

`ema_pos_pts`, `atr_dist_pts`, `vwma_pts`, `rsi_pts`, `struct_pts`, `base_score`,
`component_max_points`, `macro_multiplier`, `trend_multiplier`, `combined_multiplier`,
`scaled_score`, `score_ceiling` and `score_clipped` leave the entry record. **Entry
14**, the two vocabularies inside `calculate_entry_quality`, is settled by the
rewrite: one vocabulary, the new one. **Entry 19**, an unknown volume label scored
as neutral, is settled because volume sentiment leaves the score. Both are Claude's
reading, to be confirmed against the entries' text before building. The VWMA column
stays in the frame only if something else reads it. **Not checked.**

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
SHORT is not gated by macro.

**Tiers, from entry quality only (ruling 4). Proposed lines, set by reasoning, to be
checked against the measured distribution so that no tier is empty and none takes
nearly every run:**

- **LONG / SHORT:** quality ≥ 70.
- **AGGRESSIVE:** quality ≥ 70, close inside the band, and the risk regime NORMAL or
  LOW. Today's rule minus trend health; Item 14's gate on intensity is kept as it is.
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
  every `input_hashes` value on a live run. **Not traced end to end: whether the
  archive's hash covers every column of the frame.**
- **Pinned data has no `quote_volume`** (golden `lineage.inputs`: five columns,
  read). **Proposed:** an absent `quote_volume` fails the liquidity gate as not
  measured, and it is not computed from `volume × close`. The pinned fixture then
  gains a `quote_volume` column, so the golden run still exercises a passing gate.
  That is a fixture change with its own predicted moves: `input_hashes.struct` and
  `run_hash`.

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

**Golden snapshot (predicted, whole groups):** `bias.score` and `bias.detailed`;
every entry field in §3.2, plus `entry.score`'s value; `risk.confidence_score`,
`assumed_win_rate`, `ev_r`, `avg_reward_r`, `validation_*` and
`trade_quality_proposed`'s value; `trend.trend_health`, `exhaustion`,
`momentum_mode` and anything else trend health only feeds (**not yet listed field by
field**); `lineage.bias_components` whole; `lineage.module_constants` for
`models.bias_engine`, `models.decision_model` and `models.entry_model`; `run_hash`;
`btc_context.trend_health`; `structure.volume_sentiment`, if it leaves the record;
`explanation`; and, if the fixture gains `quote_volume`, `lineage.inputs` and
`provenance.input_hashes.struct`. The pinned run's action, from the golden record's own close, band, ATR and HVN
(computed in the sandbox, not by the engine): `d` = 3.21 ATR and `h` = 15.1 ATR, so
entry quality is 0 under §3.1 and the action moves from CONSERVATIVE LONG to WAIT
(gate 9) — before the trigger and volume gates are even reached. The golden test
would then stop exercising a trade. **Proposed:** keep this fixture as the WAIT case
and add a second pinned decision that passes every gate, so the golden snapshot still
covers a trade's plan.

**Tests (grep at `e748b0b`, files that name each thing; each still to be read before
building):** `trend_health` 39 files, `confidence` 19, `validation_state` 15,
`volume_sentiment` 10, `calculate_entry_quality` 6, `calculate_dynamic_bias` 4,
`continuation` 4, `WEIGHT_` 5, `MIN_ACTION_BIAS` 3, the five entry sub-scores 2–3
each, `ev_r` 2. Also `tests/test_decision_contract.py` (the declared fields),
`tests/test_fingerprint_names_every_constant.py` (new constants listed in
`core/decision_log.py`), and every `startswith` over the panel (the skill's
decision-path scope).

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
   H5's bin width against ATR.
2. Each golden field listed field by field, and the tests file by file.
3. Entries 14 and 19's text read against §3.2.
4. A count of how often the whole ladder trades on the ten pairs, compared with
   today's version on the same candles.
5. "What it weakens" and "the case against", written for the design as a whole.
