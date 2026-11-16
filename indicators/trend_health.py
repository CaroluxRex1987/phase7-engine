import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

# ============================================================
# TREND HEALTH -- THE SCORE AND ITS SIBLINGS REMOVED at the redesign's
# stage 5, 15 November 2026
# ============================================================
#
# What this module computed until this stage, and what became of each part:
#
#   trend_health          the 0-100 score: slope_strength (tanh of the mean
#                         EMA slope, up to 45) + adx_strength (ADX x 1.2, up
#                         to 40) + rsi_strength (an RSI band, up to 15).
#                         REMOVED. It was 0.30 of the weighted sum, the
#                         panel's TREND score, and the yardstick the trade
#                         quality sentence compared the entry against. The
#                         redesign gives it no reader: the direction is
#                         EMA50's slope and the EMAs' order
#                         (models/bias_engine.py, direction_from_emas), the
#                         tiers are entry quality's (models/decision_model.py,
#                         gate 9), and the sum is gone (ruling 3, 25 October
#                         2026: "Trend health and its 75 / 50 tiers removed;
#                         the tier from entry quality").
#   trend_slope           inputs to the score, to continuation_strength and
#   trend_acceleration    to trend_regime. REMOVED with all three. Neither
#                         was ever in the decision object: nothing outside
#                         this module read either.
#   trend_regime          a label (STRONG TREND / ACCELERATING / ...) built
#                         from the score, ADX, the acceleration, the
#                         divergence and the exhaustion flag. REMOVED.
#                         Nothing outside this module read it either.
#   trend_exhaustion      REMOVED. Its readers were the weighted sum, the
#                         reversal magnitude below, trend_regime, and the
#                         exit watch's exhaustion flag -- which Viktor ruled
#                         out on 9 November 2026 (DECISIONS, "Ruling,
#                         9 November 2026 -- the redesign's exit watch drops
#                         its exhaustion and reversal flags"), with nothing
#                         replacing it. Round 8's held-back defect H2 is
#                         replaced by its removal: the direction function
#                         does not take it.
#   continuation_strength REMOVED. One consumer, the sum's sixth factor.
#   reversal_direction    REMOVED. The sum's discount and the exit watch's
#   reversal_strength     reversal flag, both gone by the same ruling.
#   momentum_mode         REMOVED. The panel's TREND line printed it after
#                         the slash, and it scaled the reversal magnitude.
#   trend_direction       REMOVED. An informational BULLISH/BEARISH/NEUTRAL
#   trend_direction_sign  label from the slope's sign, and the same as a
#                         number, which signed the sum's trend-health
#                         factor. The direction the engine acts on comes
#                         from the EMAs now, and recording a second
#                         direction from a different rule beside it is the
#                         two-places-computing-one-thing shape this project
#                         keeps finding defects in.
#
# WHAT IS LEFT, AND WHO READS IT. Three keys and the degradation list:
#
#   adx                   models/entry_model.py's confirmation gate, against
#                         MIN_TREND_ADX (gate 3; fix 2, 5-6 October 2026).
#   momentum_divergence   the same gate (gate 5, a divergence that points
#   divergence_direction  against the trade) and the exit watch's flag.
#   degraded_inputs       the run's degradation list (core/engine_core.py).
#
# THE INPUTS THIS MODULE NOW READS ARE ADX AND RSI, AND ONLY THOSE. It read
# EMA20_Slope and EMA50_Slope as well, for the score and the acceleration,
# and named them in degraded_inputs when they were absent. It does not read
# them now, so it no longer names them -- the EMA columns are read by
# direction_from_emas, which degrades the run with the column named, and
# BTC's are read by subscript so a missing one raises and takes the BTC
# section (the redesign's stage 2). The early return for "both slopes
# absent" went with them.
#
# THE NAME IS NOT FIXED HERE, DELIBERATELY. A module called trend_health.py
# whose function is compute_trend_health and which computes no trend health
# is the "one name for one meaning" defect round 8 found as F8. Renaming it
# touches every caller, the tests that import it and the audit change list,
# and a rename is not a removal: it belongs in stage 6, the reconciliation
# against the draft, and is recorded there as owed rather than done quietly
# here.


def compute_trend_health(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """
    Read the ADX the confirmation gate compares, and the momentum
    divergence it and the exit watch read, naming any input that was
    missing.

    See the record above for the score, the exhaustion flag, the
    continuation and reversal readings, the momentum mode and the trend
    direction this returned until the redesign's stage 5.
    """
    # SEQUENCE ITEM 9a: every value here is an admission that the function
    # could not run, not a reading. ADX is None rather than a number --
    # models/entry_model.py's gate refuses both sides on None (fix 3,
    # 6 October 2026), so an unmeasured ADX infers nothing and takes no
    # trade. The divergence is False with its direction NONE, which is the
    # same pair a successful read gives when it finds no divergence; what
    # distinguishes the two is degraded_inputs, which is why that list is
    # the one field this branch fills with a reason.
    default_response = {
        # ITEM 14, 11 September 2026. ADX was read here as an input to the
        # trend health score and never left this function; it is exposed
        # because models/entry_model.py's confirmation gate compares it.
        "adx": None,
        "degraded_inputs": ["the trend readings could not be computed at all"],
        "momentum_divergence": False,
        # WORK ORDER F, 21 September 2026: which way a divergence points.
        # entry_model's gate blocks only a divergence that points against
        # the trade, so the direction has to leave this module.
        "divergence_direction": "NONE",
    }

    # Unchanged from before stage 5: twenty candles. The divergence itself
    # needs ten (below); the guard is left where it was rather than lowered
    # with the score that set it, because lowering it would admit frames
    # this module has always refused and that is a behaviour change, not a
    # removal.
    if df is None or not isinstance(df, pd.DataFrame) or df.empty or len(df) < 20:
        return default_response

    try:
        # SEQUENCE ITEM 9a: these extractions were the engine's second
        # fabrication layer -- ADX 25.0 (the trend/no-trend boundary) and
        # RSI 50.0 (dead centre) when the column was missing. Missing means
        # missing: the value is None and the input is named.
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

        adx_val = _read("ADX", "ADX")
        _read("RSI", "RSI")

        # ============================================================
        # MOMENTUM DIVERGENCE DETECTION
        # ============================================================
        momentum_divergence = False
        divergence_direction = "NONE"
        #
        # B4's LABELS, 14 October 2026 (the 5 October self-review, B4; point
        # 8 of round 8's triage). What this measures: this candle's close and
        # RSI against the close and RSI four candles back -- two points, not
        # swing highs or lows. The four locals below were named
        # price_higher_high, rsi_lower_high, price_lower_low and
        # rsi_higher_low, and the comments said "price making new highs" and
        # "new lows"; a close above the close four candles back can sit far
        # below the highs in between. Renamed; every value is the same. The
        # keys momentum_divergence and divergence_direction keep their names
        # (a rename would change the decision contract and the golden
        # snapshot for a word -- the same call as F9's
        # REGIME_HYSTERESIS_THRESHOLD), and the sentences that print them
        # say what is compared. Whether this should veto a side is a trading
        # rule, Viktor's, not ruled; nothing here changes it.
        #
        # The condition reads the COLUMN, not the value _read returned: an
        # RSI present but not finite at the last bar leaves both comparisons
        # False and so no divergence, which is what it did before stage 5.
        # Left exactly as it was.
        if len(df) >= 10 and "RSI" in df.columns:
            close_above_4_back = bool(df["close"].iat[-1] > df["close"].iat[-5])
            rsi_below_4_back = bool(df["RSI"].iat[-1] < df["RSI"].iat[-5])

            close_below_4_back = bool(df["close"].iat[-1] < df["close"].iat[-5])
            rsi_above_4_back = bool(df["RSI"].iat[-1] > df["RSI"].iat[-5])

            if close_above_4_back and rsi_below_4_back:
                # Close up on four candles back, RSI down -> recorded BEARISH
                momentum_divergence = True
                divergence_direction = "BEARISH"
            elif close_below_4_back and rsi_above_4_back:
                # Close down on four candles back, RSI up -> recorded BULLISH
                momentum_divergence = True
                divergence_direction = "BULLISH"

        return {
            # ITEM 14, 11 September 2026. The raw ADX, exposed rather than
            # only folded into a score. None when the column was absent or
            # unreadable -- the same value _read() returned -- so a reader
            # can tell an unmeasured ADX from a measured low one.
            "adx": (float(adx_val) if adx_val is not None else None),
            # SEQUENCE ITEM 9a: names every input the readings above were
            # taken WITHOUT. Empty means they used everything they claim to.
            "degraded_inputs": list(degraded_inputs),
            "momentum_divergence": bool(momentum_divergence),
            "divergence_direction": str(divergence_direction),
        }

    except Exception as e:
        # SEQUENCE ITEM 9a: this used to return default_response and swallow
        # `e` entirely -- the caller received trend_health 50.0 with no way
        # to know the computation had failed rather than found a middling
        # market. `e` was bound and never used, which is the tell. The
        # payload carries the reason, so a failure here reaches the panel as
        # a failure.
        out = dict(default_response)
        out["degraded_inputs"] = [f"the trend readings raised {type(e).__name__}: {e}"]
        return out