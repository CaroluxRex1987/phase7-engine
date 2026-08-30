from typing import NamedTuple

import pandas as pd
import numpy as np
import pandas_ta as ta

from core import config


class IndicatorFailure(NamedTuple):
    """
    One indicator that could not be computed, and what the engine loses by it.

    SEQUENCE ITEM 9a. `consequence` is written for the person reading the
    panel, not for the person reading the traceback: "trend health is computed
    without ADX" tells an operator what to distrust, where
    "ta.adx returned None" does not.
    """
    indicator: str
    reason: str
    consequence: str

    def __str__(self):
        return f"{self.indicator}: {self.reason} — {self.consequence}"

def clean_series(series: pd.Series, method: str = "forward_fill", fallback_value: float = None) -> pd.Series:
    """
    Clean a series by handling inf and extreme values, and filling gaps FORWARD.

    SEQUENCE ITEM 15 — Item 2 (No Future Information / Look-Ahead Bias) and the
    remainder of item 9a.

    THIS FUNCTION DID TWO THINGS IT DID NOT SAY IT DID

    (1) `method="forward_fill"` ran `.ffill().bfill()`. Every caller asked for a
    forward fill and got a backward one too. `ffill` covers every gap after the
    first valid value, so `bfill` only ever fired on the leading edge — the
    warm-up rows of an indicator, filled with the first value that indicator
    ever produced, which lies in their future.

    In the engine as it stands that cannot reach a decision: the analysis is
    made at the last bar of a 450-row frame and the contaminated rows are four
    hundred bars behind every window. It is a latent leak, not a live one. But
    Item 2 says "information unavailable at the exact decision timestamp must
    never influence that decision", and the Constitution's own note on
    backtesting says Item 2 "deserves the most explicit, deliberate checking of
    any invariant in this document once that work starts, since a backtest with
    a hidden look-ahead leak is the single most common way a system convinces
    itself it works when it doesn't." A backtest walks the decision timestamp
    backwards. On the day that harness is written, every one of these fills
    becomes a live leak, silently, with no code change to blame.

    (2) The final sweep — `fillna(median or 0.0)` — was a fabrication of the
    exact kind item 9a was written to remove, one layer below where item 9a
    looked.

    It mattered more than the backfill. An indicator that came back entirely
    NaN left this function as a column of ZEROS, and the callers' guards read

        rsi = clean_series(ta.rsi(...))
        if rsi is None or rsi.isna().all():   # can never be true
            raise ValueError("pandas_ta returned no usable RSI")

    `isna().all()` was already false, because this function had replaced every
    NaN with 0.0 before the check ran. So a completely failed RSI became RSI=0
    on every bar — maximum oversold — with no failure reported. A completely
    failed ATR became ATR=0, which is a stop distance of zero and three targets
    on top of the entry price. Item 9a's tests injected failures by raising, so
    the returns-nothing path was never exercised and the guards were never
    watched to see whether they could fire.

    WHAT IT DOES NOW

    Forward only, and NaN is a legitimate return value. A series that is all
    NaN comes back all NaN, so the caller's guard means what it says. Leading
    NaNs stay NaN, because a 14-period RSI genuinely has no value at bar 3 and
    inventing one is the leak.

    Args:
        series: Input series to clean
        method: 'forward_fill', 'interpolate', 'drop', or 'fill_value'
        fallback_value: Value to use when method='fill_value' — the one
            explicit substitution left, and the caller has to ask for it by
            name and supply the number itself.

    Returns:
        Cleaned series. May contain NaN. That is the point.
    """
    if series is None or series.empty:
        return series

    # Replace inf values with NaN
    series = series.replace([np.inf, -np.inf], np.nan)

    # Handle extreme outliers (beyond 5 standard deviations)
    if len(series.dropna()) > 10:
        mean_val = series.mean()
        std_val = series.std()
        if np.isfinite(mean_val) and np.isfinite(std_val) and std_val > 0:
            outlier_mask = np.abs(series - mean_val) > (5 * std_val)
            series.loc[outlier_mask] = np.nan

    # Apply cleaning method. SEQUENCE ITEM 15: `.bfill()` removed from the
    # forward_fill branch and limit_direction changed from 'both' to 'forward'.
    # Both filled from later rows; see the docstring.
    if method == "forward_fill":
        series = series.ffill()
    elif method == "interpolate":
        series = series.interpolate(method='linear', limit_direction='forward')
    elif method == "fill_value" and fallback_value is not None:
        series = series.fillna(fallback_value)
    elif method == "drop":
        series = series.dropna()

    # SEQUENCE ITEM 15: the final sweep lived here.
    #
    #     if series.isna().any():
    #         median_val = series.median()
    #         series = series.fillna(median_val if isfinite(median_val) else 0.0)
    #
    # It is gone. A median is a plausible number and that is precisely what
    # makes it dangerous — the reader cannot distinguish it from a measurement.
    # An all-NaN input took the `else 0.0` branch and came back as a column of
    # zeros, which is what silenced three of item 9a's guards.
    return series

def pct_slope(series: pd.Series) -> pd.Series:
    """Return the normalized percentage slope of a series with NaN handling."""
    if series is None or len(series) < 2:
        return pd.Series(dtype=float, index=series.index if series is not None else [])

    # Clean input series first
    series = clean_series(series, method="forward_fill")

    # Calculate slope with zero division protection
    prev_values = series.shift(1)
    slope = (series.diff() / prev_values) * 100

    # Handle division by zero cases
    slope = slope.replace([np.inf, -np.inf], 0.0)

    return clean_series(slope, method="forward_fill")


def add_technical_indicators(df: pd.DataFrame, inplace: bool = False):
    """
    Add the core technical indicators, and report anything that could not be
    computed instead of inventing a value for it.

    Returns:
        (df, failures) — the frame, and a list of IndicatorFailure records.
        An empty list means every indicator was computed from real data.

    SEQUENCE ITEM 9a. Item 13 (Fail Safely) and Item 8 (Epistemic Honesty),
    which the audit reported separately and which are one defect.

    WHAT THIS USED TO DO

    Every indicator here had an `except` that substituted a constant:

        RSI          50.0     the exact centre of the scale — "no opinion",
                              which is a reading, not the absence of one
        ADX          25.0     the conventional trend/no-trend boundary
        ATR          close × 0.02
        SuperTrend   close
        ST_Direction 1.0      bullish
        EMA_20/50    an ewm() fallback, which is a real computation

    Every one of those is a number the engine then treated as a measurement.
    Nothing downstream could tell a fabricated 50.0 from a market that really
    is at RSI 50, and the panel printed both identically.

    ST_Direction = 1.0 is the sharpest case: a failed SuperTrend calculation
    reported *bullish*. Not neutral, not unknown — a direction, chosen by
    whoever wrote the fallback, presented as the market's.

    WHAT IT DOES NOW

    On failure the column is NOT WRITTEN and the failure is recorded. Two
    channels on purpose: the absent column means no fabricated value can be
    read by accident, and the record is the explicit signal the engine acts on.

    An absent column alone would have been quieter but not safer — Item 3's
    lesson is that a defect you cannot name is a defect you cannot report, and
    engine_core needs to tell the operator *which* indicator failed, not merely
    that something did.

    THE EMA FALLBACK IS KEPT, DELIBERATELY

    close.ewm(span=20).mean() is not a fabrication. It is the definition of an
    EMA, computed with pandas instead of pandas_ta, and it produces the same
    number. A fallback that recomputes the same quantity by another route is
    not the defect this item is about — substituting a constant for a
    measurement is. Recorded so the distinction is deliberate rather than an
    oversight.

    RUNS THAT DEGRADE DO NOT HALT

    Viktor ruled on 29 August that a failed indicator degrades rather than
    halts: the engine continues, records what failed, reduces confidence and
    trade quality accordingly, and a degraded result does not by itself
    authorize trading. That ruling went against both GLM's recommendation and
    Claude's instinct, which is why it was Viktor's to make.

    So this returns failures rather than raising. engine_core decides what a
    run missing ADX is still allowed to say.
    """

    if not inplace:
        df = df.copy()

    failures = []

    def failed(indicator, exc, consequence):
        failures.append(IndicatorFailure(
            indicator=indicator,
            reason=f"{type(exc).__name__}: {exc}",
            consequence=consequence,
        ))

    # Validate and clean input data (vectorized operations)
    required_cols = ["open", "high", "low", "close", "volume"]

    # Batch clean all columns at once to reduce overhead
    #
    # SEQUENCE ITEM 15: was `.ffill().bfill()`. Backfilling a price column
    # invents a bar out of the one after it. Forward only now.
    #
    # Worth knowing that this loop is close to unreachable for the NaN case:
    # data/validation.py rejects any NaN in an OHLCV column (validation.py:147)
    # and runs in data_fetcher before the frame gets here. It is kept as a
    # guard for callers that did not come through the fetcher, not deleted,
    # because the cost is one pass and the failure it guards against is a
    # fabricated price.
    for col in required_cols:
        if col in df.columns:
            # Use in-place operations where possible
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].ffill()

    # ============================================================
    # CORE INDICATORS WITH NaN PROTECTION (Optimized)
    # ============================================================

    # Pre-extract close prices to avoid repeated column access
    close_prices = df["close"]

    # Calculate EMAs with optimized fallback
    # The ewm() fallbacks below are NOT fabrications and are kept — see the
    # function docstring. They compute the same exponential moving average
    # pandas_ta would, using pandas directly.
    # SEQUENCE ITEM 14: the lengths were 20 and 50 literal, while
    # config.EMA_FAST and config.EMA_SLOW held 20 and 50 and were read by
    # nothing. The column NAMES stay literal on purpose — they are the
    # dataframe's contract with trend_health, entry_model and plotting, and a
    # column named from a config value cannot be looked up by anything that
    # does not also read that value.
    for length, name in ((config.EMA_FAST, "EMA_20"), (config.EMA_SLOW, "EMA_50")):
        try:
            ema = ta.ema(close_prices, length=length)
            # SEQUENCE ITEM 15: was ema.ffill().bfill(). An EMA's leading
            # NaNs are its warm-up and backfilling them stated a value the
            # average did not have yet.
            df[name] = ema.ffill() if ema.isna().any() else ema
        except Exception:
            try:
                df[name] = close_prices.ewm(span=length, adjust=False).mean()
            except Exception as e:
                failed(name, e,
                       "trend health loses its slope component and entry "
                       "quality cannot score EMA zone position")

    # SEQUENCE ITEM 9a: both paths used to end in fallback_value=50.0.
    #
    # The second path is a real RSI calculation, so it stays — like the EMA
    # fallback, it computes the same quantity by another route. What goes is
    # the constant underneath both: 50.0 is the exact centre of the scale, and
    # an oscillator pinned there reads as "perfectly balanced", which is a
    # measurement. A failed RSI is not balanced. It is absent.
    try:
        rsi = clean_series(ta.rsi(df["close"], length=config.RSI_LENGTH),
                           method="forward_fill")
        if rsi is None or rsi.isna().all():
            raise ValueError("pandas_ta returned no usable RSI")
        df["RSI"] = rsi
    except Exception as primary:
        try:
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=config.RSI_LENGTH).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=config.RSI_LENGTH).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = clean_series(100 - (100 / (1 + rs)), method="forward_fill")
            if rsi.isna().all():
                raise ValueError("manual RSI produced no usable values")
            df["RSI"] = rsi
        except Exception as fallback:
            failed("RSI", fallback,
                   "entry quality scores RSI extension at 0 of 15, and trend "
                   f"health loses its momentum component (primary: {primary})")

    # SEQUENCE ITEM 5a: Bollinger Bands removed. BB_lower, BB_middle and
    # BB_upper were written on both the success and fallback paths and read
    # nowhere in the engine — verified by scanning every module for a read.
    # Item 16 (no unconsumed complexity): computing three columns per run that
    # nothing consumes is cost without benefit, and every fallback that writes
    # a fabricated value is one more path Item 13 would otherwise have to give
    # honest semantics to.
    #
    # config.BB_LENGTH and config.BB_STD were left unused by 5a and are
    # removed from config.py at sequence item 14.

    # ADX / DI with error handling
    try:
        adx_df = ta.adx(df["high"], df["low"], df["close"], length=config.ADX_LENGTH)
        if adx_df is not None and not adx_df.empty:
            # SEQUENCE ITEM 5a: DIP and DIM (the directional indicators at
            # columns 1 and 2) were written here and read nowhere. ADX itself
            # is consumed — trend_health and bias both read it — so the call
            # stays and only the two unread columns go.
            #
            # Note for anyone deleting by name: `DIM` is also colorama's
            # dim-text style, used at panel_render.py:1181 as `dim =
            # Style.DIM`. That is unrelated to this dataframe column and
            # removing it breaks the panel's formatting.
            adx = clean_series(adx_df.iloc[:, 0], method="forward_fill")

            # SEQUENCE ITEM 15: ADX had no all-NaN guard, unlike RSI, ATR and
            # SuperTrend. It did not need one while clean_series was quietly
            # turning an all-NaN column into zeros — nothing looked NaN, ever.
            # With that removed, a frame that comes back present but empty of
            # values has to be caught here or it reaches trend_health as a
            # column of NaN with no failure recorded. ADX 0 would have read as
            # "no trend at all", the opposite end of the scale from the 25.0
            # item 9a removed.
            if adx.isna().all():
                raise ValueError("ta.adx returned a frame with no usable values")
            df["ADX"] = adx
        else:
            raise ValueError("ta.adx returned an empty frame")
    except Exception as e:
        # SEQUENCE ITEM 9a: was pd.Series(25.0, index=df.index).
        #
        # 25 is the conventional line between "trending" and "not trending",
        # so a failed ADX did not merely invent a number — it invented the
        # single most ambiguous one, sitting exactly on the boundary that
        # trend_health and bias both test against.
        failed("ADX", e,
               "trend health loses its ADX component (25 of its 100 points) "
               "and bias cannot test trend strength")

    # SuperTrend with error handling
    # A9 FIX: This is now the single, canonical SuperTrend implementation for the
    # engine (pandas_ta-based). The previous standalone custom loop-based
    # implementation in supertrend.py was never imported/called anywhere in the
    # pipeline (main.py, engine_core.py, structure.py, plotting.py, or any other
    # module) — it was dead code that only posed a future collision risk on the
    # same "SuperTrend" / "ST_Direction" column names. It has been deleted.
    # Length/multiplier are pulled from config.py instead of being hardcoded,
    # so config.SUPERTREND_LENGTH / config.SUPERTREND_MULT actually control the
    # calculation. Sequence item 14 did the same for every other length in this
    # file — until then SuperTrend was the only indicator config could reach.
    try:
        st_df = ta.supertrend(
            df["high"], df["low"], df["close"],
            length=config.SUPERTREND_LENGTH,
            multiplier=config.SUPERTREND_MULT,
        )
        if st_df is not None and not st_df.empty:
            df["SuperTrend"] = clean_series(st_df.iloc[:, 0], method="forward_fill")
            direction = clean_series(st_df.iloc[:, 1], method="forward_fill")
            if direction.isna().all():
                raise ValueError("SuperTrend produced no usable direction")
            df["ST_Direction"] = direction
        else:
            raise ValueError("ta.supertrend returned an empty frame")
    except Exception as e:
        # SEQUENCE ITEM 9a: was df["SuperTrend"] = df["close"] and
        # df["ST_Direction"] = pd.Series(1.0, index=df.index).
        #
        # This is the sharpest of the fabrications. ST_Direction = 1.0 is
        # BULLISH. A failed SuperTrend calculation did not report "unknown" or
        # even "neutral" — it reported a direction, chosen by whoever wrote the
        # fallback, and the engine presented it as the market's.
        #
        # bias_engine reads supertrend_direction as one of its factors and
        # build_exit_watch compares it against the previous run to raise a
        # "SuperTrend flipped" flag. Both were being fed a constant.
        failed("SuperTrend", e,
               "bias loses its SuperTrend factor and Exit Watch cannot detect "
               "a SuperTrend flip against the previous run")

    # SEQUENCE ITEM 5a: Typical_Price removed — written once, read nowhere.
    # It is the classic (H+L+C)/3 input to VWAP and CCI, neither of which this
    # engine calculates.

    # ============================================================
    # SECONDARY INDICATORS WITH NaN PROTECTION
    # ============================================================

    # SEQUENCE ITEM 9a: the primary path's fallback_value was
    # df["close"].iloc[-1] * 0.02 — a flat 2% of the last price, asserted as
    # this market's volatility.
    #
    # ATR sets the stop distance and all three targets. A fabricated ATR does
    # not produce a wrong indicator reading; it produces a wrong risk plan,
    # with stop and targets placed by a constant that has nothing to do with
    # how this instrument actually moves.
    #
    # The manual true-range calculation stays: like the EMA and RSI fallbacks
    # it is the same quantity by another route, not a substitute for it.
    try:
        atr = clean_series(
            ta.atr(df["high"], df["low"], df["close"], length=config.ATR_LENGTH),
            method="forward_fill")
        if atr is None or atr.isna().all():
            raise ValueError("pandas_ta returned no usable ATR")
        df["ATR"] = atr
    except Exception as primary:
        try:
            tr1 = df["high"] - df["low"]
            tr2 = (df["high"] - df["close"].shift(1)).abs()
            tr3 = (df["low"] - df["close"].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1, skipna=True)
            atr = clean_series(tr.rolling(window=config.ATR_LENGTH).mean(),
                               method="forward_fill")
            if atr.isna().all():
                raise ValueError("manual true range produced no usable values")
            df["ATR"] = atr
        except Exception as fallback:
            failed("ATR", fallback,
                   "no stop distance and no targets can be computed — the "
                   f"entire risk plan is unavailable (primary: {primary})")

    # SEQUENCE ITEM 5a: KAMA removed. The column itself was read by exactly
    # one thing — the slope loop below, which produced KAMA_Slope, which
    # nothing read. A dead chain two links long: the only consumer of KAMA
    # existed to feed a consumer that did not exist.
    #
    # config.KAMA_LENGTH was left unused by 5a and is removed from config.py at
    # sequence item 14.

    # VWMA with optimized calculation (avoid intermediate Series creation)
    try:
        volume_col = df["volume"]
        # Use rolling operations directly without creating intermediate cleaned series
        volume_sum = volume_col.rolling(window=config.VWMA_LENGTH).sum()
        price_volume_sum = (close_prices * volume_col).rolling(
            window=config.VWMA_LENGTH).sum()

        # Vectorized calculation with safe division
        valid_mask = (volume_sum > 0) & np.isfinite(volume_sum) & np.isfinite(price_volume_sum)
        df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, close_prices)

        # SEQUENCE ITEM 15: this line was
        #
        #     df["VWMA"] = df["VWMA"].ffill().bfill().fillna(close_prices)
        #
        # and the `.fillna(close_prices)` is the identical fabrication item 9a
        # removed from the except branch eight lines below — where the comment
        # already explains why substituting close for VWMA "invented the most
        # favourable number available", a zero VWMA distance and a perfect 20
        # of 20 entry-quality points. Item 9a fixed the branch that raises and
        # left the one that quietly succeeds.
        #
        # Forward fill only, and no substitution. A VWMA that has no value has
        # no value.
        if df["VWMA"].isna().any():
            df["VWMA"] = df["VWMA"].ffill()
    except Exception as e:
        # SEQUENCE ITEM 9a: was df["VWMA"] = close_prices.
        #
        # entry_model scores how far price sits from VWMA, worth 20 of the 100
        # entry-quality points. Substituting close for VWMA makes that distance
        # exactly zero — a perfect score, awarded because the calculation
        # failed. The fabrication did not merely invent a number, it invented
        # the most favourable one available.
        failed("VWMA", e,
               "entry quality loses its VWMA distance component (20 of 100 "
               "points)")

    # ============================================================
    # SLOPES WITH OPTIMIZED CALCULATION
    # ============================================================

    # Batch calculate slopes to reduce function call overhead
    #
    # SEQUENCE ITEM 5a: was four columns; VWMA_Slope and KAMA_Slope were
    # produced here and read nowhere, and KAMA itself is now gone. The two
    # that remain are genuinely consumed — trend_health.py reads EMA20_Slope
    # at three places and EMA50_Slope at one, so this loop stays.
    #
    # VWMA is NOT removed: entry_model consumes it for distance scoring. Only
    # its slope was dead.
    slope_columns = ["EMA_20", "EMA_50"]
    slope_names = ["EMA20_Slope", "EMA50_Slope"]

    for col, slope_name in zip(slope_columns, slope_names):
        if col in df.columns:
            # Optimized slope calculation without function call overhead
            series = df[col]
            prev_values = series.shift(1)
            slope = ((series - prev_values) / prev_values * 100).replace([np.inf, -np.inf], 0.0)
            # SEQUENCE ITEM 15: was slope.ffill().bfill().fillna(0.0). Zero
            # is not a neutral filler for a slope — it is the specific claim
            # that the moving average is flat, and trend_health reads these at
            # four places to decide whether a trend is strengthening.
            df[slope_name] = slope.ffill()

    # ============================================================
    # FINAL SWEEP
    # ============================================================
    #
    # SEQUENCE ITEM 9a: this block used to be a second fabrication layer.
    # Any critical indicator that came out all-NaN was overwritten with the
    # same constants the except branches used — 50.0, 25.0, close, close × 0.02
    # — so even an indicator that failed *quietly*, without raising, ended up
    # as an invented number.
    #
    # It now drops the column and reports, which is the same treatment a raised
    # exception gets. An indicator that produced nothing but NaN did not
    # compute; how it failed to compute is not the operator's problem.
    critical_indicators = ["EMA_20", "EMA_50", "RSI", "ATR", "ADX"]
    for indicator in critical_indicators:
        if indicator in df.columns and df[indicator].isna().all():
            df.drop(columns=[indicator], inplace=True)
            failed(indicator,
                   ValueError("computed without raising, but every value is NaN"),
                   "silent failure — the calculation returned, and returned nothing")

    return df, failures