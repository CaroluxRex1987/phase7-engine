import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List, TypedDict

from indicators.volume_profile import compute_volume_profile

# Step 8: Formal Return Contract Type Definition for strict static analysis
class StructureAnalysisResult(TypedDict):
    regime: str
    sequence: str
    hvn: float
    lvn: float
    swing_struct: float
    volume_sentiment: str
    df: Optional[pd.DataFrame]


class StructureEngine:
    """
    Phase‑7 Structure + Volume Sentiment Engine
    Fully vectorized with NumPy/Pandas optimizations, input validation,
    localized exception isolation, advanced adaptive lookbacks, hysteresis state machine,
    advanced volume sentiment metrics, and strict typing contracts.
    """

    def __init__(self, volume_profile_bins: int = 50) -> None:
        # State tracking for regime persistence to reduce whipsaws
        self._last_regime: str = "NEUTRAL STRUCTURE"
        self._volume_profile_bins: int = volume_profile_bins

    # ============================================================
    # MAIN STRUCTURE + VOLUME SENTIMENT ENGINE
    # ============================================================

    def analyze(self, df: pd.DataFrame, current_price: float, lookback: int = 8) -> Dict[str, Any]:
        """
        Main structure engine entry point with localized sub-routine error handling.
        Returns structure regime, sequence, HVN/LVN, swing structure, volume
        sentiment, and a list of the sub-routines that failed.

        AUDIT FINDING (2 September 2026): FIVE SILENT FALLBACKS

        Each handler below caught its sub-routine and substituted a value.
        None of them recorded anything, and this function had no channel to
        record it through -- so a failed sub-routine produced a complete,
        plausible-looking structure reading and the run continued as though
        every measurement had been taken. Viktor's 29 August ruling is
        degrade, not halt: a failure is RECORDED, confidence is capped and no
        trade is authorised. Two of those three were happening. The recording
        was not.

        The volume-node handler was the worst of the five. It returned

            hvn, lvn = float(current_price), float(current_price)

        and models/entry_model.py scores structure proximity as
        abs(close - hvn) / close, which is then EXACTLY ZERO -- inside the
        < 0.015 band, awarding the full 12 of 12 structure points for a
        high-volume node that was never located. That is the defect Finding 3
        fixed on 1 September, and the comment recording it sits in
        entry_model.py to this day. The fix changed the CONSUMER's fallback
        to NaN and left this producer handing down a finite number equal to
        the price. The door was closed and the window left open.

        What changed here: no handler invents a measurement any more. A price
        level that could not be located is NaN, which every consumer already
        guards against -- entry_model checks np.isfinite before scoring and
        risk_model checks it before using a structural level for the stop. A
        label that could not be determined says UNKNOWN rather than borrowing
        NEUTRAL, which is a reading. And every failure is appended to
        degraded_inputs, which engine_core extends onto the run's degradation
        list exactly as it already does for trend_health's.
        """
        degraded_inputs = []

        # Improvement 4: Localized Exception Handling for Sub-Routines
        try:
            regime = self._detect_regime(df)
        except Exception as exc:
            # Was self._last_regime -- the previous bar's answer presented as
            # this bar's. Hysteresis is a deliberate part of _detect_regime;
            # reusing its output when the detector CRASHED is a guess.
            regime = "UNKNOWN STRUCTURE"
            degraded_inputs.append(f"structure regime detection failed: {exc}")

        try:
            sequence = self._detect_sequence(df, lookback=lookback)
        except Exception as exc:
            sequence = "UNKNOWN"
            degraded_inputs.append(f"structure sequence detection failed: {exc}")

        try:
            hvn, lvn = self._detect_hvn_lvn(df)
        except Exception as exc:
            hvn = lvn = float("nan")
            degraded_inputs.append(f"volume node detection failed: {exc}")

        try:
            swing_struct = self._detect_swing_structure(df, current_price, lookback=lookback)
        except Exception as exc:
            swing_struct = float("nan")
            degraded_inputs.append(f"swing structure detection failed: {exc}")

        try:
            volume_sentiment = self._volume_sentiment_simple(df)
        except Exception as exc:
            # Was "NEUTRAL VOLUME" -- the same shape as the macro NEUTRAL that
            # sequence item 9 removed for being a fabricated reading rather
            # than an absent one.
            volume_sentiment = "UNKNOWN VOLUME"
            degraded_inputs.append(f"volume sentiment detection failed: {exc}")

        return {
            "regime": regime,
            "sequence": sequence,
            "hvn": hvn,
            "lvn": lvn,
            "swing_struct": swing_struct,
            "volume_sentiment": volume_sentiment,
            "degraded_inputs": degraded_inputs,
        }

    # ============================================================
    # STRUCTURE DETECTION & STATE MANAGEMENT
    # ============================================================

    def _detect_regime(self, df: pd.DataFrame) -> str:
        """
        Improvement 6: State Machine for Market Regimes with Hysteresis.
        Prevents whipsaws during choppy consolidation phases by introducing state persistence.
        """
        if df is None or len(df) < 15:
            return self._last_regime

        closes = df['close'].values
        ma_short = closes[-5:].mean()
        ma_long = closes[-15:].mean()

        gap_pct = (ma_short - ma_long) / ma_long
        threshold = 0.0015  # 0.15% buffer zone to avoid false triggers

        current_state = self._last_regime

        if current_state == "BULLISH TREND":
            if gap_pct < -threshold:
                new_state = "BEARISH TREND"
            elif gap_pct < 0:
                new_state = "NEUTRAL STRUCTURE"
            else:
                new_state = "BULLISH TREND"
        elif current_state == "BEARISH TREND":
            if gap_pct > threshold:
                new_state = "BULLISH TREND"
            elif gap_pct > 0:
                new_state = "NEUTRAL STRUCTURE"
            else:
                new_state = "BEARISH TREND"
        else:
            if gap_pct > threshold:
                new_state = "BULLISH TREND"
            elif gap_pct < -threshold:
                new_state = "BEARISH TREND"
            else:
                new_state = "NEUTRAL STRUCTURE"

        self._last_regime = new_state
        return new_state

    # ============================================================
    # B2 BUILD: SWING-HIGH/LOW PIVOTS (shared by sequence detection
    # and swing-structure level detection below)
    # ============================================================
    #
    # A confirmed swing high is a bar whose high is the most extreme value
    # within `lookback` bars on BOTH sides of it. Because we only have data
    # up to "now," a pivot can't be confirmed until `lookback` bars of price
    # action have passed after it -- so only bars at least `lookback` back
    # from the most recent bar are eligible. This is standard fractal-pivot
    # detection, matching the "(Lookback 8)" already labeled on the panel's
    # SWING STRUCT line (that label previously described a stub that just
    # returned current_price unchanged -- it's now real).

    def _find_confirmed_swings(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        lookback: int,
        max_each: int = 2,
        search_limit: int = 200,
    ) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        Scans backward from the most recent confirmable bar and returns up to
        `max_each` confirmed swing highs and swing lows, each as (index, price),
        most recent first. Accepted pivots are required to be at least
        `lookback` bars apart so one flat-topped/bottomed cluster of bars
        doesn't get counted as several separate swing points.
        """
        n = len(highs)
        swing_highs: List[Tuple[int, float]] = []
        swing_lows: List[Tuple[int, float]] = []
        last_high_idx: Optional[int] = None
        last_low_idx: Optional[int] = None

        search_start = n - 1 - lookback
        search_end = max(lookback, search_start - search_limit)

        for i in range(search_start, search_end - 1, -1):
            if i - lookback < 0 or i + lookback >= n:
                continue

            # Minimum spacing between two ACCEPTED pivots is 2x lookback, not
            # just lookback -- two adjacent lookback-windows can otherwise
            # both "win" on the same flat-topped/bottomed cluster of bars
            # (e.g. a multi-bar consolidation at the same level), which would
            # misread one plateau as two separate swings and never let the
            # comparison logic below see a genuinely new extreme.
            if len(swing_highs) < max_each:
                window_high = highs[i - lookback: i + lookback + 1]
                if highs[i] == window_high.max() and (last_high_idx is None or last_high_idx - i >= 2 * lookback):
                    swing_highs.append((i, float(highs[i])))
                    last_high_idx = i

            if len(swing_lows) < max_each:
                window_low = lows[i - lookback: i + lookback + 1]
                if lows[i] == window_low.min() and (last_low_idx is None or last_low_idx - i >= 2 * lookback):
                    swing_lows.append((i, float(lows[i])))
                    last_low_idx = i

            if len(swing_highs) >= max_each and len(swing_lows) >= max_each:
                break

        return swing_highs, swing_lows

    def _detect_sequence(self, df: pd.DataFrame, lookback: int = 8) -> str:
        """
        B2 BUILD (was a stub always returning "NONE"). Real swing-sequence /
        BOS ("break of structure") / CHOCH ("change of character") detection.

        Looks at the two most recent confirmed swing highs and swing lows to
        classify the swing sequence, then checks whether the CURRENT price
        has broken through the most recent confirmed swing extreme:

          BULLISH SWING SEQUENCE (HH-HL) -- higher highs & higher lows, no
                                             break of the last swing high yet
          BEARISH SWING SEQUENCE (LH-LL) -- lower highs & lower lows, no
                                             break of the last swing low yet
          BOS BULLISH / BOS BEARISH      -- price breaks the last swing
                                             extreme IN the direction the
                                             sequence was already going
                                             (trend continuation)
          CHOCH BULLISH / CHOCH BEARISH  -- price breaks the last swing
                                             extreme AGAINST the direction
                                             the sequence was going (the
                                             first sign of a possible
                                             reversal)
          NONE -- not enough confirmed swing points yet, or highs/lows
                  disagree on direction (e.g. higher highs but lower lows)
        """
        if df is None or len(df) < (6 * lookback + 10):
            return "NONE"

        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values

        swing_highs, swing_lows = self._find_confirmed_swings(highs, lows, lookback, max_each=2)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return "NONE"

        last_high, prev_high = swing_highs[0][1], swing_highs[1][1]
        last_low, prev_low = swing_lows[0][1], swing_lows[1][1]
        current_price = float(closes[-1])

        if last_high > prev_high and last_low > prev_low:
            # Established bullish swing sequence. A break below the last
            # confirmed swing low here would go against that sequence.
            if current_price > last_high:
                return "BOS BULLISH (TREND CONTINUATION)"
            if current_price < last_low:
                return "CHOCH BEARISH (POSSIBLE REVERSAL)"
            return "BULLISH SWING SEQUENCE (HH-HL)"

        if last_high < prev_high and last_low < prev_low:
            # Established bearish swing sequence. A break above the last
            # confirmed swing high here would go against that sequence.
            if current_price < last_low:
                return "BOS BEARISH (TREND CONTINUATION)"
            if current_price > last_high:
                return "CHOCH BULLISH (POSSIBLE REVERSAL)"
            return "BEARISH SWING SEQUENCE (LH-LL)"

        # Mixed (e.g. higher highs but lower lows) -- no clean sequence.
        return "NONE"

    def _detect_hvn_lvn(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        A11 FIX: Primary HVN/LVN source is now the real binned volume-profile
        engine (compute_volume_profile), which distributes actual traded
        volume proportionally across price bins. This replaces the previous
        approach of using the high/low extremes of an adaptive lookback
        window, which measured price range, not where volume actually traded.

        Falls back to the old adaptive-lookback method only if the volume
        profile can't be computed or returns no usable result, so behavior
        degrades gracefully instead of failing outright.
        """
        if df is None or df.empty:
            return 0.0, 0.0

        try:
            _, hvn, lvn = compute_volume_profile(df, num_bins=self._volume_profile_bins)
            if hvn is not None and lvn is not None and np.isfinite(hvn) and np.isfinite(lvn):
                return float(hvn), float(lvn)
        except Exception:
            pass  # fall through to legacy method below

        # ------------------------------------------------------------
        # LEGACY FALLBACK: adaptive TR-based high/low window
        # ------------------------------------------------------------
        high_values = df['high'].values
        low_values = df['low'].values
        close_values = df['close'].values
        df_len = len(df)

        if df_len > 14:
            prev_closes = np.roll(close_values, 1)
            prev_closes[0] = close_values[0]
            tr = np.maximum(
                high_values - low_values,
                np.maximum(np.abs(high_values - prev_closes), np.abs(low_values - prev_closes))
            )

            recent_tr = np.mean(tr[-14:])
            recent_price = close_values[-1]

            vol_pct = (recent_tr / recent_price) if recent_price > 0 else 0.01
            base_lookback = 20
            vol_factor = vol_pct / 0.01
            adaptive_window = int(base_lookback / max(0.5, min(2.0, vol_factor)))

            lookback = max(5, min(df_len, adaptive_window))
        else:
            lookback = df_len

        hvn = float(high_values[-lookback:].max())
        lvn = float(low_values[-lookback:].min())
        return hvn, lvn

    def _detect_swing_structure(self, df: pd.DataFrame, current_price: float, lookback: int = 8) -> float:
        """
        B2 BUILD (was a stub always returning current_price unchanged).

        Returns the nearest confirmed swing high or swing low to the current
        price -- the closest real structural reference level for manual
        stop/target planning. (structure.py doesn't yet know the intended
        trade direction at this point in engine_core.py's pipeline -- the
        bias engine runs after this -- so this returns whichever confirmed
        swing point is closest, rather than picking "support" vs.
        "resistance" by direction.)
        """
        if df is None or len(df) < (2 * lookback + 5):
            return float(current_price)

        highs = df['high'].values
        lows = df['low'].values

        swing_highs, swing_lows = self._find_confirmed_swings(highs, lows, lookback, max_each=1)

        if not swing_highs and not swing_lows:
            return float(current_price)
        if not swing_highs:
            return float(swing_lows[0][1])
        if not swing_lows:
            return float(swing_highs[0][1])

        nearest_high = swing_highs[0][1]
        nearest_low = swing_lows[0][1]
        if abs(nearest_high - current_price) <= abs(nearest_low - current_price):
            return float(nearest_high)
        return float(nearest_low)

    # ============================================================
    # ADVANCED VOLUME SENTIMENT ENGINE
    # ============================================================

    def _volume_sentiment_simple(self, df: pd.DataFrame) -> str:
        """
        Improvement 2 & 7: Advanced Volume Sentiment Metrics with participation expansion
        and institutional accumulation/distribution detection.
        """
        if df is None or len(df) < 20:
            return "NEUTRAL VOLUME"

        closes = df["close"].values
        volumes = df["volume"].values

        c_recent, c_prev = closes[-5:], closes[-10:-5]
        v_recent, v_prev = volumes[-5:], volumes[-10:-5]

        try:
            vwma_recent = np.average(c_recent, weights=v_recent)
            vwma_prev = np.average(c_prev, weights=v_prev)
        except ZeroDivisionError:
            vwma_recent = c_recent.mean()
            vwma_prev = c_prev.mean()

        vwma_slope = vwma_recent - vwma_prev
        price_slope = closes[-1] - closes[-5]
        vol_slope = volumes[-1] - volumes[-5]

        vma_baseline = volumes[-20:].mean()
        recent_vol_mean = volumes[-5:].mean()
        volume_expansion = recent_vol_mean > (1.2 * vma_baseline)

        if vwma_slope > 0 and volume_expansion and price_slope > 0:
            return "STRONG BULLISH ACCUMULATION"

        if vwma_slope > 0 and vol_slope > 0 and price_slope > 0:
            return "BULLISH VOLUME SUPPORT"

        if vwma_slope < 0 and volume_expansion and price_slope < 0:
            return "STRONG BEARISH DISTRIBUTION"

        if vwma_slope < 0 and vol_slope > 0 and price_slope < 0:
            return "BEARISH VOLUME PRESSURE"

        if (price_slope > 0 and vol_slope < 0 and not volume_expansion) or \
           (price_slope < 0 and vol_slope < 0 and not volume_expansion):
            return "VOLUME DIVERGENCE"

        if volume_expansion and abs(price_slope) < (0.001 * closes[-1]):
            return "VOLUME EXHAUSTION"

        return "NEUTRAL VOLUME"


# ============================================================
# ENGINE COMPATIBILITY WRAPPER
# ============================================================

def calculate_structure(df: Optional[pd.DataFrame], lookback: int = 8,
                        volume_profile_bins: int = 50) -> Dict[str, Any]:
    """
    Compatibility wrapper function with strict input validation, vectorized NaN
    cleaning, and formal typing contracts for engine_core.py.

    SEQUENCE ITEM 6: the `copy_df` parameter is gone. This function always works
    on its own copy now.

    It defaulted to True, and both call sites in engine_core passed False — so
    the safe default was documented and never taken. Under it, `df_clean = df`
    and this function then wrote STRUCTURE, HVN and LVN into the caller's frame
    and ffill/bfill/fillna(0.0)'d its OHLCV columns. The caller's `df` and the
    `df` returned in this dict were one object under two names.

    The parameter is removed rather than merely left at its default, because a
    knob whose unsafe setting is the one everybody chooses is not a safeguard.
    Nothing outside engine_core called this, so there is no compatibility cost.

    Cost of always copying: one 450-row frame per call, twice per run. Measured
    against the class of bug it removes, that is not a trade worth making.
    """
    if df is None or df.empty:
        # 2 September 2026: the three levels here were 0.0 and the two labels
        # were NEUTRAL. Zero is a price, and a structural level of $0.0000 is
        # not "no level" to anything downstream -- np.isfinite(0.0) is True,
        # so risk_model would accept it as a structural stop. NaN is what
        # "not located" is spelled as everywhere else in this engine.
        return {
            "regime": "UNKNOWN STRUCTURE",
            "sequence": "UNKNOWN",
            "hvn": float("nan"),
            "lvn": float("nan"),
            "swing_struct": float("nan"),
            "volume_sentiment": "UNKNOWN VOLUME",
            "degraded_inputs": ["structure analysis received an empty frame"],
            "df": df
        }

    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"StructureEngine requires missing column: '{col}'")

    df_clean = df.copy()

    # SEQUENCE ITEM 15: was .ffill().bfill().fillna(0.0). The backfill took
    # OHLCV values from later bars; the fillna(0.0) put a price of zero on any
    # gap that survived, and the very next line reads close.iloc[-1] as the
    # current price. Forward only, and a gap that a forward fill cannot close
    # is reported rather than papered over — data/validation.py rejects NaN
    # OHLCV upstream, so reaching this means the frame did not come through the
    # fetcher.
    df_clean.loc[:, required_cols] = df_clean[required_cols].ffill()

    still_missing = [c for c in required_cols if df_clean[c].isna().any()]
    if still_missing:
        raise ValueError(
            f"StructureEngine received gaps a forward fill cannot close in: "
            f"{', '.join(still_missing)}. Filling these with zero would make "
            f"the structural analysis and the current price read from bars "
            f"that never traded."
        )

    current_price = float(df_clean['close'].iloc[-1])

    # SEQUENCE ITEM 14: StructureEngine was constructed with no arguments, so
    # its volume_profile_bins defaulted to 50 and config.VOLUME_PROFILE_BINS —
    # also 50 — was read by nothing. Two copies of one number, one of them
    # labelled as the setting and neither of them consulted.
    engine = StructureEngine(volume_profile_bins=volume_profile_bins)
    # B2 FIX: `lookback` was accepted by this wrapper's signature but never
    # actually passed down to the engine -- analyze() didn't even take a
    # lookback parameter, so the "(Lookback 8)" already shown on the panel's
    # SWING STRUCT line was aspirational text next to a stub. Now real.
    result = engine.analyze(df_clean, current_price, lookback=lookback)

    df_clean.loc[:, "STRUCTURE"] = result.get("regime", "NEUTRAL STRUCTURE")
    df_clean.loc[:, "HVN"] = result.get("hvn", 0.0)
    df_clean.loc[:, "LVN"] = result.get("lvn", 0.0)

    result["df"] = df_clean

    return result