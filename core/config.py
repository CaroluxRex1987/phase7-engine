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

# Optional API keys (not required for public OHLC endpoints)
API_KEY = ""
API_SECRET = ""

# Base URL for MEXC REST API
API_BASE_URL = "https://api.mexc.com"


# ============================================================
# LOGGING & STORAGE
# ============================================================

LOG_DIR = "Logs/"
CHART_DIR = "Logs/Charts/"
TRADE_LOG_DIR = "Logs/Trades/"

# Directories the engine ensures exist
REQUIRED_DIRS = [
    LOG_DIR,
    CHART_DIR,
    TRADE_LOG_DIR
]


# ============================================================
# RISK SETTINGS
# ============================================================

# Default account balance used for position sizing
DEFAULT_ACCOUNT_BALANCE = 10_000

# Default risk percentage per trade (1% of account)
DEFAULT_RISK_PERCENT = 1.0


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

# Bollinger Bands
BB_LENGTH = 20
BB_STD = 2.0

# Volume-weighted moving average
VWMA_LENGTH = 20

# Kaufman adaptive moving average
KAMA_LENGTH = 10

# Supertrend
SUPERTREND_LENGTH = 10
SUPERTREND_MULT = 3.0


# ============================================================
# CHART SETTINGS
# ============================================================

CHART_WIDTH = 14
CHART_HEIGHT = 10
CHART_DPI = 150
CHART_STYLE = "dark_background"