"""
Phase‑7 Structural Quant Engine — Configuration Module
Centralized settings for market, risk, indicators, logging, and charting.
"""


# ============================================================
# ENGINE METADATA
# ============================================================

engine_version = "Phase‑7 Structural Quant Engine v1.0"


# ============================================================
# MARKET SETTINGS
# ============================================================

# Default trading symbol and timeframe
SYMBOL = "AEROUSDT"          # Main trading pair
TIMEFRAME = "4h"            # Execution candle interval
MACRO_TIMEFRAME = "1d"      # Macro Higher Timeframe for MTF Confluence


# ============================================================
# API SETTINGS
# ============================================================

# SEQUENCE ITEM 14: API_KEY and API_SECRET were declared here as empty strings
# and read by nothing. The engine uses only public OHLC endpoints and is never
# permitted to execute a trade, so there is no code path that could need a
# credential. Two empty credential slots sitting in the config of an engine
# that must not trade are an invitation, not a setting.

# Base URL for MEXC REST API
API_BASE_URL = "https://api.mexc.com"

# AUDIT FINDING (c), 5 September 2026. data_fetcher.fetch_ohlc called
# requests.get with no timeout at all. requests' default is to wait FOREVER:
# a server that accepts the connection and then sends nothing hangs the run
# with no error, no log line and no way to tell it from a slow market.
#
# 15 seconds. A 450-candle klines response is well under a second on a normal
# link, so this is roughly twenty times the expected worst case -- long enough
# that a slow connection is not mistaken for a dead one, short enough that a
# hung socket ends the run instead of owning it.
#
# NOT fingerprinted, deliberately. FINGERPRINTED_CONFIG is the set of knobs
# that can change WHAT a run decided; this one can only change whether the
# fetch succeeded at all. A run that returns candles returns the same candles
# at any value of it.
#
# requests applies this separately to the connect and the read phase, so the
# real worst case is 30 seconds, not 15.
API_TIMEOUT_SECONDS = 15.0


# ============================================================
# LOGGING & STORAGE
# ============================================================

# SEQUENCE ITEM 14: lowercase. .gitignore ignores `logs/`, and these were
# `Logs/`. On Windows that is the same directory and the mismatch is
# invisible; on Linux it is a second directory that git does not ignore, so a
# clone that runs the engine gets its run artifacts staged for commit.
LOG_DIR = "logs/"
CHART_DIR = "logs/charts/"

# SEQUENCE ITEM 14: TRADE_LOG_DIR and REQUIRED_DIRS removed.
#
# TRADE_LOG_DIR was read by nothing but REQUIRED_DIRS, and REQUIRED_DIRS was
# read by nothing at all — the directories are created on demand by the code
# that writes into them (engine_core's state file, decision_log, plotting), so
# the list was a second declaration of a fact already enforced elsewhere.
#
# TRADE_LOG_DIR also named a directory for the trade log that sequence item 12
# established does not exist and never did. Keeping it would leave the last
# trace of that claim in the config.


# ============================================================
# RISK SETTINGS
# ============================================================

# SEQUENCE ITEM 13: DEFAULT_ACCOUNT_BALANCE (10,000) and DEFAULT_RISK_PERCENT
# (1.0) were defined here and read only by the position-sizing block in
# engine_core.py. Viktor ruled on 29 August 2026 that the engine must not
# compute monetary sizing, so both the computation and these constants are
# gone. Leaving them would leave a placeholder balance sitting in config for
# the next reader to wire back up.


# ============================================================
# STRUCTURE SETTINGS
# ============================================================

# Swing lookback for structural highs/lows
STRUCT_LOOKBACK = 8

# Volume profile resolution
VOLUME_PROFILE_BINS = 50


# ============================================================
# INDICATOR SETTINGS
# ============================================================

# EMA settings
EMA_FAST = 20
EMA_SLOW = 50

# Core indicators
RSI_LENGTH = 14
ADX_LENGTH = 14
ATR_LENGTH = 14

# SEQUENCE ITEM 14: BB_LENGTH, BB_STD and KAMA_LENGTH removed. Sequence item
# 5a deleted the Bollinger Bands and KAMA calculations as unconsumed output
# and left these three constants for this item, which is where config hygiene
# belongs. A length for an indicator the engine does not compute is a setting
# that cannot be set.

# Volume-weighted moving average
VWMA_LENGTH = 20

# Supertrend
SUPERTREND_LENGTH = 10
SUPERTREND_MULT = 3.0


# ============================================================
# CHART SETTINGS
# ============================================================

# SEQUENCE ITEM 14: these are now read by utils/plotting.py, which hardcoded
# figsize=(14, 8), dpi=200 and "dark_background" and ignored all four.
#
# Two of them DISAGREED with the code: config said height 10 and dpi 150, the
# renderer used 8 and 200. The declaration is corrected to what the engine has
# actually been drawing rather than the other way round — every chart Viktor
# has looked at came out at 14x8 and 200 dpi, and silently resizing them is a
# visible change nobody asked for. They are settings now, so changing these
# numbers changes the chart.
CHART_WIDTH = 14
CHART_HEIGHT = 8
CHART_DPI = 200
CHART_STYLE = "dark_background"