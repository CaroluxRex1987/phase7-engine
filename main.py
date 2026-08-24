import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.signal_router import SignalRouter
from core import config


def main():
    router = SignalRouter()

    # Run engine using default config values
    decision = router.route(
        symbol=config.SYMBOL,
        timeframe=config.TIMEFRAME
    )

    # The engine already prints the full Phase‑7 dashboard panel
    # through panel_render.py, so we do NOT print the raw object here.
    # If you ever want to inspect the raw dictionary, uncomment:
    #
    # print(decision)


if __name__ == "__main__":
    main()
