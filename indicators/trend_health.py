import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def compute_trend_health(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """
    Compute advanced trend health, slope, acceleration, failure,
    exhaustion, momentum divergence, continuation/reversal scoring,
    and trend regime classification.
    """
    # SEQUENCE ITEM 9a: trend_health was 50.0 here — the exact middle of the
    # scale, returned whenever this function could not run at all. "Moderately
    # healthy trend" is a reading. The absence of one is not, and 50.0 is the
    # value most likely to be mistaken for a measurement because it is the one
    # a real market can genuinely produce.
    #
    # 0.0 instead, paired with degraded_inputs below. Zero is the floor of the
    # scale rather than a plausible point on it, and the engine now blocks
    # trading on any run carrying degraded inputs — so the number cannot be
    # read as conviction the way 50.0 could.
    default_response = {
        "trend_health": 0.0,
        "degraded_inputs": ["trend health could not be computed at all"],
        "trend_exhaustion": False,
        "momentum_mode": "NEUTRAL",
        "trend_slope": 0.0,
        "trend_acceleration": 0.0,
        "momentum_divergence": False,
        "trend_regime": "NEUTRAL",
        # B1 additions — see sections 2b and 7 below.
        "continuation_strength": 0.0,
        "reversal_direction": "NONE",
        "reversal_strength": 0.0,
        # New: explicit trend direction label — see section 1b below.
        "trend_direction": "NEUTRAL",
        # 4 SEPTEMBER 2026: the same direction as a NUMBER, for consumers that
        # need to sign a magnitude. See the return block below for why.
        "trend_direction_sign": 0,
    }

    if df is None or not isinstance(df, pd.DataFrame) or df.empty or len(df) < 20:
        return default_response

    try:
        # SEQUENCE ITEM 9a: these four extractions were the engine's second
        # fabrication layer. Where indicators.py substituted a constant when a
        # calculation failed, this substituted one when the column was missing
        # — ADX 25.0 (the trend/no-trend boundary), RSI 50.0 (dead centre),
        # both slopes 0.0 (a flat market).
        #
        # Since indicators.py now DROPS a column it could not compute rather
        # than inventing one, these `else` branches became the live path for
        # every indicator failure. Left alone they would have re-fabricated
        # exactly what item 9a removed, one module downstream.
        #
        # Missing now means missing: the value is None, the component it feeds
        # scores zero, and the input is named in degraded_inputs. Zero rather
        # than a midpoint because an unavailable component must lower
        # conviction, never hold it steady — that is what Viktor's ruling means
        # by "reduced accordingly".
        degraded_inputs = []

        def _read(column, label):
            if column not in df.columns:
                degraded_inputs.append(f"{label} (column absent)")
                return None
            try:
                value = float(df[column].iat[-1])
            except Exception:
                degraded_inputs.append(f"{label} (unreadable)")
                return None
            if not np.isfinite(value):
                degraded_inputs.append(f"{label} (not finite)")
                return None
            return value

        ema20_slope = _read("EMA20_Slope", "EMA20_Slope")
        ema50_slope = _read("EMA50_Slope", "EMA50_Slope")
        adx_val = _read("ADX", "ADX")
        rsi_val = _read("RSI", "RSI")

        # The slopes are the only inputs trend health itself is computed from,
        # so their absence is not a degraded score — it is no score. Reported
        # as such rather than as a flat market.
        if ema20_slope is None and ema50_slope is None:
            out = dict(default_response)
            out["degraded_inputs"] = degraded_inputs
            return out
        ema20_slope = 0.0 if ema20_slope is None else ema20_slope
        ema50_slope = 0.0 if ema50_slope is None else ema50_slope

        # ============================================================
        # 1. TREND SLOPE & ACCELERATION
        # ============================================================
        trend_slope = float((ema20_slope + ema50_slope) / 2.0)

        # Calculate acceleration (change in slope over the last 3 periods)
        trend_acceleration = 0.0
        if "EMA20_Slope" in df.columns and len(df) >= 4:
            prev_slope = float(df["EMA20_Slope"].iat[-4])
            if np.isfinite(prev_slope):
                trend_acceleration = float(ema20_slope - prev_slope)

        # ============================================================
        # 2. TREND HEALTH SCORE (0–100)
        # ============================================================
        normalized_slope = float(np.tanh(abs(trend_slope) * 100) * 45)
        slope_strength = min(normalized_slope, 45.0)

        # SEQUENCE ITEM 9a: the `else` branches here awarded 20.0 of 40 for a
        # missing ADX and 10.0 of 15 for a missing RSI — half marks for an
        # input that was never read. Trend health is the number the panel calls
        # TREND and that bias, confidence and trade quality all build on, so
        # half marks for absent data propagated into every score downstream.
        #
        # Zero now. An input that does not exist contributes nothing.
        adx_strength = 0.0 if adx_val is None else min(max(adx_val, 0.0) * 1.2, 40.0)

        if rsi_val is None:
            rsi_strength = 0.0
        elif 45.0 <= rsi_val <= 65.0:
            rsi_strength = 15.0
        elif 35.0 <= rsi_val < 45.0 or 65.0 < rsi_val <= 75.0:
            rsi_strength = 12.0
        elif 25.0 <= rsi_val < 35.0 or 75.0 < rsi_val <= 85.0:
            rsi_strength = 8.0
        else:
            rsi_strength = 5.0

        trend_health = float(slope_strength + adx_strength + rsi_strength)
        trend_health = max(0.0, min(100.0, trend_health))

        # ============================================================
        # 2b. CONTINUATION STRENGTH (B1)
        # Signed: positive = bullish continuation, negative = bearish
        # continuation, magnitude 0-100. This is what actually unblocks
        # A3 — bias_engine.calculate_dynamic_bias() gates BULLISH/BEARISH
        # on continuation_strength being non-None and > 0 / < 0, which was
        # permanently impossible while this field didn't exist.
        #
        # Direction comes from trend_slope's sign. Magnitude is built from:
        # trend health, ADX strength, whether RSI sits in a healthy
        # continuation zone for that direction (vs. overextended/weak),
        # and whether the trend is accelerating or decelerating in its own
        # direction (deceleration actively subtracts, not just "doesn't help").
        # ============================================================
        if trend_slope > 0:
            direction = 1
        elif trend_slope < 0:
            direction = -1
        else:
            direction = 0

        # ============================================================
        # 1b. TREND DIRECTION (new)
        # A plain BULLISH/BEARISH/NEUTRAL label, so the direction the EMAs
        # are actually sloping is available as its own field instead of
        # only being implied by trend_slope's sign or by momentum_mode
        # (which reflects RSI intensity, not direction -- a strong
        # downtrend and an early uptrend can both show a "BUILDING"
        # momentum_mode, for example). Uses the exact same sign-of-slope
        # test as continuation_strength above, so the two never disagree.
        # Informational only -- doesn't feed into or change trend_health,
        # bias, or any decision logic.
        # ============================================================
        if direction > 0:
            trend_direction = "BULLISH"
        elif direction < 0:
            trend_direction = "BEARISH"
        else:
            trend_direction = "NEUTRAL"

        if direction != 0:
            # ITEM 11 RE-AUDIT (Finding 4). This block used to open with:
            #
            #     health_component = (trend_health / 100.0) * 40.0
            #
            # and add it into raw_continuation below. continuation_strength
            # has exactly one consumer: bias_engine.calculate_dynamic_bias(),
            # which already weights trend_health directly at
            # WEIGHT_TREND_HEALTH = 0.30. Feeding 40% of this score from the
            # same trend_health reading meant one measurement reached
            # bias_score through two of its six "independent" factors at
            # once -- the auditor's own quoted example of Item 11's broken
            # clause, "a signal reinforcing itself through multiple derived
            # layers and then presented as independent confirmation."
            #
            # Removed rather than reweighted: there is no independent
            # fraction of health_component to keep, since it was wholly a
            # function of the same trend_health value bias_engine already
            # reads. What is left below -- ADX, RSI-relative-to-direction,
            # and acceleration -- has no other channel into bias_score, so it
            # remains genuinely independent evidence about whether this
            # trend is continuing.
            #
            # Ruled by Viktor, 31 August 2026 (delegated). No rescale: the
            # ceiling this score can reach without a health-derived term is
            # honestly lower (60, not 100) rather than stretched back to 100
            # by a multiplier invented to hide that the trend-health share is
            # gone.

            # SEQUENCE ITEM 9a: an unavailable input scores zero rather than
            # scoring from a substituted constant. continuation_strength is
            # now out of 60 (ADX 25 + RSI-momentum 15 + acceleration 20);
            # without ADX its ceiling is 35, without RSI 45, and
            # degraded_inputs says which. A lower score for a less complete
            # picture is the intended behaviour, not a side effect.
            if adx_val is None:
                adx_component = 0.0
            else:
                adx_component = (min(max(adx_val, 0.0), 50.0) / 50.0) * 25.0

            if rsi_val is None:
                momentum_component = 0.0
            elif direction > 0:
                if 50.0 <= rsi_val <= 75.0:
                    momentum_component = 15.0
                elif 40.0 <= rsi_val < 50.0 or 75.0 < rsi_val <= 85.0:
                    momentum_component = 8.0
                else:
                    momentum_component = 2.0
            else:
                if 25.0 <= rsi_val <= 50.0:
                    momentum_component = 15.0
                elif 15.0 <= rsi_val < 25.0 or 50.0 < rsi_val <= 60.0:
                    momentum_component = 8.0
                else:
                    momentum_component = 2.0

            accel_aligned = trend_acceleration * direction
            accel_magnitude = float(np.tanh(abs(accel_aligned) * 50.0) * 20.0)
            accel_component = accel_magnitude if accel_aligned >= 0 else -accel_magnitude

            raw_continuation = adx_component + momentum_component + accel_component
            continuation_strength = float(direction * max(0.0, min(100.0, raw_continuation)))
        else:
            continuation_strength = 0.0

        # ============================================================
        # 3. TREND FAILURE — REMOVED at sequence item 9c
        # ============================================================
        #
        # The block here read the last five values of the STRUCTURE column and
        # set trend_failure if any equalled "LH" or "LL".
        #
        # structure.py never writes those. It writes regime labels — "BULLISH
        # TREND", "BEARISH TREND", "NEUTRAL STRUCTURE" — so the comparison
        # could not match and trend_failure was False on every run this engine
        # has ever made.
        #
        # Four modules acted on it: entry_model blocked entries, bias_engine
        # halved the bias score, exit_model raised a watch flag, and the router
        # published it as trend.failure. All four have been removed with it.
        # In each case it sat beside a live signal (trend_exhaustion, a
        # reversal, a CHOCH against trend), so the deletion is output-invariant
        # — proven by the golden snapshot.
        #
        # WHY DELETED RATHER THAN WIRED. Viktor delegated the call; the
        # reasoning is recorded in claude/phase7-rulings.md and in the commit.
        # In short: the audit found a gate that never fires, not a
        # specification for one that should. Choosing when to block a trade is
        # a trading decision, and wiring it would produce a behaviour change
        # this project cannot yet evaluate — the golden baseline proves a
        # change is attributable, never that it is correct, and backtesting
        # sits behind the release gate.
        #
        # It remains available as a deliberate feature once there is something
        # to validate it against. This deletion does not foreclose it; it
        # declines to smuggle it in as a repair.

        # ============================================================
        # 4. TREND EXHAUSTION
        # ============================================================
        range_val = float(df["high"].iat[-1] - df["low"].iat[-1])
        range_prev = float(df["high"].iat[-2] - df["low"].iat[-2])
        range_expanding = bool(range_val > range_prev)

        # SEQUENCE ITEM 9a: both clauses tested adx_val against a threshold.
        # With ADX unavailable, neither can be evaluated — and asserting
        # "not exhausted" would be a claim, not an absence of one. The flag is
        # left False, which is its default, and ADX's absence is already named
        # in degraded_inputs so the panel can say the check did not run.
        if adx_val is None:
            trend_exhaustion = False
        else:
            weak_adx = bool(adx_val < 20.0)
            trend_exhaustion = bool(
                (range_expanding and weak_adx)
                or (trend_health < 35.0 and adx_val < 15.0)
            )

        # ============================================================
        # 5. MOMENTUM DIVERGENCE DETECTION
        # ============================================================
        momentum_divergence = False
        # B1: track which direction a detected divergence points, not just
        # a yes/no bool — needed by the reversal detection in section 7.
        divergence_direction = "NONE"
        if len(df) >= 10 and "RSI" in df.columns:
            price_higher_high = bool(df["close"].iat[-1] > df["close"].iat[-5])
            rsi_lower_high = bool(df["RSI"].iat[-1] < df["RSI"].iat[-5])

            price_lower_low = bool(df["close"].iat[-1] < df["close"].iat[-5])
            rsi_higher_low = bool(df["RSI"].iat[-1] > df["RSI"].iat[-5])

            if price_higher_high and rsi_lower_high:
                # Price making new highs while momentum weakens -> bearish divergence
                momentum_divergence = True
                divergence_direction = "BEARISH"
            elif price_lower_low and rsi_higher_low:
                # Price making new lows while momentum firms up -> bullish divergence
                momentum_divergence = True
                divergence_direction = "BULLISH"

        # ============================================================
        # 6. MOMENTUM MODE & REGIME CLASSIFICATION
        # ============================================================
        # SEQUENCE ITEM 9a: both classifications are labels the panel prints as
        # statements about the market — MOMENTUM: STRONG, REGIME: MODERATE
        # TREND. With their input missing there is nothing to classify, and any
        # label chosen would be an assertion the engine cannot support. So they
        # say so.
        if rsi_val is None:
            momentum_mode = "UNAVAILABLE"
        elif rsi_val < 40.0:
            momentum_mode = "BUILDING"
        elif rsi_val < 55.0:
            momentum_mode = "HEALTHY"
        elif rsi_val < 70.0:
            momentum_mode = "STRONG"
        elif rsi_val < 80.0:
            momentum_mode = "EXTENDED"
        else:
            momentum_mode = "EXTREME"

        if adx_val is None:
            # Without ADX only the divergence/exhaustion branch is decidable,
            # and "MODERATE TREND" as a default would be the old fabrication
            # wearing a label instead of a number.
            trend_regime = ("EXHAUSTING / DIVERGENT"
                            if (momentum_divergence or trend_exhaustion)
                            else "UNAVAILABLE")
        elif trend_health >= 75.0 and adx_val >= 25.0:
            trend_regime = "STRONG TREND"
        elif trend_acceleration > 0.0 and trend_health >= 50.0:
            trend_regime = "ACCELERATING"
        elif momentum_divergence or trend_exhaustion:
            trend_regime = "EXHAUSTING / DIVERGENT"
        elif adx_val < 20.0:
            trend_regime = "MEAN REVERTING / CHOP"
        else:
            trend_regime = "MODERATE TREND"

        # ============================================================
        # 7. REVERSAL DETECTION (B1)
        # reversal_direction is a label ("BULLISH" / "BEARISH" / "NONE");
        # reversal_strength is a 0-100 magnitude regardless of direction —
        # entry_model.py already treats reversal_strength > 0 as "block
        # entries", independent of which way the reversal points, so this
        # intentionally does NOT sign it.
        #
        # Built from momentum divergence (section 5) plus proximity to the
        # HVN structural level (real since A11 wired in compute_volume_profile
        # — previously this would've been measuring the wrong thing), gated
        # by whether the trend is actually extended/exhausting enough for a
        # reversal signal to mean anything.
        # ============================================================
        structural_direction = "NONE"
        structural_proximity_component = 0.0
        if "HVN" in df.columns:
            hvn_val = float(df["HVN"].iat[-1])
            current_close = float(df["close"].iat[-1])
            if np.isfinite(hvn_val) and current_close > 0:
                hvn_dist_pct = abs(current_close - hvn_val) / current_close * 100.0
                if hvn_dist_pct < 1.5:
                    structural_proximity_component = 20.0
                    structural_direction = "BEARISH" if current_close >= hvn_val else "BULLISH"
                elif hvn_dist_pct < 3.0:
                    structural_proximity_component = 10.0
                    structural_direction = "BEARISH" if current_close >= hvn_val else "BULLISH"

        reversal_direction = "NONE"
        reversal_strength = 0.0

        candidate_direction = divergence_direction if divergence_direction != "NONE" else structural_direction

        if candidate_direction != "NONE":
            divergence_bonus = 25.0 if momentum_divergence else 0.0
            exhaustion_bonus = 20.0 if trend_exhaustion else 0.0
            raw_reversal = divergence_bonus + structural_proximity_component + exhaustion_bonus

            # Reversal signals are only meaningful against an established,
            # extended trend -- scale down sharply if momentum isn't
            # actually extended/exhausted yet.
            if not (momentum_mode in ("EXTENDED", "EXTREME") or trend_exhaustion):
                raw_reversal *= 0.4

            reversal_strength = float(max(0.0, min(100.0, raw_reversal)))
            reversal_direction = candidate_direction if reversal_strength > 0 else "NONE"

        return {
            "trend_health": float(trend_health),
            # SEQUENCE ITEM 9a: names every input this score was computed
            # WITHOUT. Empty means the score used everything it claims to.
            "degraded_inputs": list(degraded_inputs),
            "trend_exhaustion": bool(trend_exhaustion),
            "momentum_mode": str(momentum_mode),
            "trend_slope": float(trend_slope),
            "trend_acceleration": float(trend_acceleration),
            "momentum_divergence": bool(momentum_divergence),
            "trend_regime": str(trend_regime),
            "continuation_strength": float(continuation_strength),
            "reversal_direction": str(reversal_direction),
            "reversal_strength": float(reversal_strength),
            "trend_direction": str(trend_direction),

            # 4 SEPTEMBER 2026. The direction, as a number, taken from the same
            # slope test that produced the label three lines up -- not
            # recomputed, just exposed.
            #
            # It exists because models/bias_engine.py had been INFERRING this
            # from the sign of continuation_strength, and continuation_strength
            # is a magnitude with a floor at zero. When a trend decelerates hard
            # enough that raw_continuation goes negative, the floor makes
            # continuation_strength exactly 0.0 -- correctly, because the trend
            # is not continuing -- and the inferred direction went to 0 with it.
            # bias_engine then multiplied trend_health by that zero, so a 30%
            # weight silently vanished while the panel still printed
            # TREND: BULLISH.
            #
            # Measured across 9,800 bars on fifteen pairs: it fired on 0.71% of
            # them, with a median effect of 21.3 points on a -100..100 score
            # where 20 decides direction. 52 of 70 firings exceeded that
            # threshold. Zero of them were sign disagreements -- the floor never
            # corrected a direction, it only deleted a factor.
            #
            # Direction and continuation answer different questions. Which way is
            # the trend pointing, and is it still going. Deriving the first from
            # the second is what coupled them.
            "trend_direction_sign": int(direction),
        }

    except Exception as e:
        # SEQUENCE ITEM 9a: this used to return default_response and swallow
        # `e` entirely — the caller received trend_health 50.0 with no way to
        # know the computation had failed rather than found a middling market.
        # `e` was bound and never used, which is the tell.
        #
        # The payload now carries the reason, and trend_health is 0.0 rather
        # than 50.0, so a failure here reaches the panel as a failure.
        out = dict(default_response)
        out["degraded_inputs"] = [f"trend health raised {type(e).__name__}: {e}"]
        return out