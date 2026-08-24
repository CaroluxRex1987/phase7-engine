import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_engine_chart(df, entry_data, risk_data, save_path="chart_output.png"):
    """
    Modular Phase‑7 chart renderer.
    Draws:
        - Candles
        - EMA20 / EMA50
        - VWAP
        - Entry zone shading
        - ATR stop
        - Targets T1 / T2 / T3
    """

    plt.style.use("dark_background")

    fig, ax = plt.subplots(figsize=(14, 8))

    # ============================================================
    # CANDLE PLOTTING
    # ============================================================

    up = df[df["close"] >= df["open"]]
    down = df[df["close"] < df["open"]]

    # Candle wicks
    ax.vlines(up.index, up["low"], up["high"], color="#22c55e", linewidth=1)
    ax.vlines(down.index, down["low"], down["high"], color="#ef4444", linewidth=1)

    # Candle bodies
    ax.bar(
        up.index,
        up["close"] - up["open"],
        bottom=up["open"],
        width=0.0008,
        color="#22c55e"
    )

    ax.bar(
        down.index,
        down["open"] - down["close"],
        bottom=down["close"],
        width=0.0008,
        color="#ef4444"
    )

    # ============================================================
    # EMA & VWAP
    # ============================================================

    ax.plot(df.index, df["EMA_20"], label="EMA20", color="#f59e0b", linewidth=1.4)
    ax.plot(df.index, df["EMA_50"], label="EMA50", color="#a855f7", linewidth=1.4)

    if "VWAP" in df.columns:
        ax.plot(df.index, df["VWAP"], label="VWAP", color="#00ffff", linewidth=1.2)

    # ============================================================
    # ENTRY ZONE SHADING
    # ============================================================

    entry_zone_lower = entry_data["entry_zone_lower"]
    entry_zone_upper = entry_data["entry_zone_upper"]

    ax.axhspan(
        entry_zone_lower,
        entry_zone_upper,
        color="yellow",
        alpha=0.12,
        label="Entry Zone"
    )

    # ============================================================
    # ATR STOP & TARGETS
    # ============================================================

    atr_stop = risk_data["atr_stop"]
    t1, t2, t3 = risk_data["targets"]

    ax.axhline(atr_stop, color="red", linestyle="--", linewidth=1.2, label="ATR Stop")
    ax.axhline(t1, color="green", linestyle="--", linewidth=1.2, label="T1")
    ax.axhline(t2, color="lime", linestyle="--", linewidth=1.2, label="T2")
    ax.axhline(t3, color="darkgreen", linestyle="--", linewidth=1.2, label="T3")

    # ============================================================
    # CHART FORMATTING
    # ============================================================

    ax.set_title("Phase‑7 Structural Quant Engine — Market Structure & Signals", fontsize=14)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")

    # Date formatting
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()

    return save_path
