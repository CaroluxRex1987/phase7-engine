import pandas as pd
import requests
import time
from core import config


class DataFetcher:
    """
    Phase‑7 Data Fetcher
    Supports:
        - Local CSV OHLC loading
        - MEXC API OHLC fetching
    """

    def __init__(self):
        self.base_url = config.API_BASE_URL

    # ============================================================
    # LOCAL CSV LOADING
    # ============================================================

    def load_csv(self, filepath):
        """
        Load OHLCV data from a CSV file.
        CSV must contain: timestamp, open, high, low, close, volume
        """

        df = pd.read_csv(filepath)

        # Convert timestamp → datetime index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

        return df

    # ============================================================
    # MEXC API OHLC FETCHER
    # ============================================================

    def fetch_ohlc(self, symbol, timeframe, limit=300):
        """
        Fetch OHLCV candles from MEXC API.
        MEXC returns **8 fields**, not 12.
        """

        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            return {"error": f"API request failed: {e}"}

        if not isinstance(data, list) or len(data) == 0:
            return {"error": "Empty or invalid API response."}

        # ============================================================
        # CORRECT MEXC FORMAT (8 fields)
        # ============================================================

        df = pd.DataFrame(data, columns=[
            "timestamp",        # open time (ms)
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",       # close time (ms)
            "quote_volume"
        ])

        # Keep only OHLCV
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        # Convert types
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        df.set_index("timestamp", inplace=True)

        return df

    # ============================================================
    # UNIFIED FETCH WRAPPER
    # ============================================================

    def get_tf(self, symbol, timeframe, limit=300):
        """
        Unified fetch wrapper used by the engine.

        A13 FIX: previously, any API failure silently returned an empty
        DataFrame with only a logger warning upstream — indistinguishable
        from a genuine "no signal" / insufficient-history condition once it
        reached engine_core.py. A real data outage would look identical to
        a normal HOLD in the panel, with no visibility into what actually
        happened.

        Now the failure reason is attached to the empty DataFrame via
        `.attrs["fetch_error"]` so engine_core.py can surface a distinct
        "data fetch failed" error state instead of the generic
        "insufficient market data" message. The return type is unchanged
        (still always a DataFrame) so nothing else calling get_tf() breaks.
        """

        df = self.fetch_ohlc(symbol, timeframe, limit)

        # If API returned an error dict, surface it as a distinct,
        # identifiable error state rather than falling through as an
        # ordinary empty-data path.
        if isinstance(df, dict) and "error" in df:
            empty_df = pd.DataFrame()
            empty_df.attrs["fetch_error"] = df["error"]
            return empty_df

        return df


# ============================================================
# GLOBAL FETCHER INSTANCE
# ============================================================

data_fetcher = DataFetcher()