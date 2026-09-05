import datetime
import os
import json

from models.signal_router import SignalRouter
from core import config


class LiveTradingSimulator:
    """
    SAFE live-trading wrapper for Phase-7.
    This module:
        - Runs the engine (via SignalRouter, the same entry point main.py uses)
        - Generates a simulated order object
        - Logs the intended trade
        - NEVER executes real trades

    FIX (previously broken): this used to `from engine_core import
    phase7_engine` and call that singleton directly -- but no such singleton
    ever existed (only the `Phase7Engine` class does), so this crashed on
    import. Even setting that aside, calling the engine directly like that
    would have bypassed SignalRouter entirely, meaning it would've gotten
    the raw, pre-DecisionModel engine output -- no real confidence score,
    no final_action, no BTC context, none of what the panel actually shows
    you. This is now rewired to go through SignalRouter.route_and_execute(),
    exactly like main.py does, so a simulated order always reflects the
    exact same decision the panel would render for that run.

    Also fixed: a few field names this read no longer matched the current
    decision object's actual shape (entry_zone_lower/upper -> zone_lower/
    upper, exit.final_action -> exit.action) -- these would have raised
    KeyErrors the moment the import itself was fixed.
    """

    # SEQUENCE ITEM 14: the default was the literal "Logs/LiveSim/". It is
    # derived from config.LOG_DIR now, so the simulator writes beside the rest
    # of the engine's output instead of into a directory that differs from it
    # by case on Linux.
    #
    # AUDIT FINDING (d), 5 September 2026: the os.makedirs call was here, and
    # the module ended with `live_trading_simulator = LiveTradingSimulator()`.
    # Between them, IMPORTING this module created a directory on disk. The
    # test suite imports every engine module to check that they import, so
    # `pytest` created logs/LiveSim/ on any machine that ran it, whether or
    # not the simulator was ever used.
    #
    # config.py already states the rule this broke: "the directories are
    # created on demand by the code that writes into them (engine_core's state
    # file, decision_log, plotting)". This was the one exception. The makedirs
    # has moved to _log_simulated_trade, which is the code that writes into
    # it, matching decision_log.log_decision.
    def __init__(self, log_dir=None):
        self.log_dir = log_dir if log_dir is not None else os.path.join(
            config.LOG_DIR, "LiveSim")
        self.router = SignalRouter()

    # ============================================================
    # RUN ENGINE + GENERATE SIMULATED ORDER
    # ============================================================

    def run_once(self, symbol=None, timeframe=None):
        """
        Run the engine once (through SignalRouter, same path main.py uses)
        and generate a simulated trade object -- never a real one.

        Falls back to config.py's SYMBOL/TIMEFRAME if not given, matching
        main.py's behavior. SignalRouter.route_and_execute() itself requires
        both to be given explicitly and does NOT apply config defaults on
        its own, so that fallback has to happen here.
        """
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAME

        result = self.router.route_and_execute(symbol, timeframe)

        # SignalRouter already renders the panel itself -- this just needs
        # to know whether the run succeeded before trying to build an order
        # from it. An error result has no entry/risk/exit sections to read.
        if not isinstance(result, dict) or "error" in result:
            error_message = (
                result.get("error", "Unknown engine error")
                if isinstance(result, dict) else "Engine returned invalid output"
            )
            return {
                "engine_result": result,
                "simulated_order": None,
                "log_path": None,
                "error": error_message,
            }

        # Build simulated order
        order = self._build_simulated_order(result)

        # Log simulated trade
        filepath = self._log_simulated_trade(order)

        return {
            "engine_result": result,
            "simulated_order": order,
            "log_path": filepath
        }

    # ============================================================
    # BUILD SIMULATED ORDER OBJECT
    # ============================================================

    def _build_simulated_order(self, result):
        """
        Convert engine output into a safe simulated order object.
        """

        entry = result.get("entry", {}) if isinstance(result.get("entry"), dict) else {}
        risk = result.get("risk", {}) if isinstance(result.get("risk"), dict) else {}
        exit_data = result.get("exit", {}) if isinstance(result.get("exit"), dict) else {}

        order = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "symbol": result.get("symbol", "UNKNOWN"),
            "timeframe": result.get("timeframe", "UNKNOWN"),
            "decision": exit_data.get("action", "UNKNOWN"),
            "entry_zone": {
                "lower": entry.get("zone_lower", 0.0),
                "upper": entry.get("zone_upper", 0.0)
            },
            "risk": {
                "atr_stop": risk.get("atr_stop", 0.0),
                "targets": risk.get("targets", (0.0, 0.0, 0.0)),
                "risk_valid": risk.get("risk_valid", True),
                "risk_reason": risk.get("risk_reason", "OK")
            },
            "signals": {
                "long_signal": entry.get("long_signal", False),
                "short_signal": entry.get("short_signal", False)
            },
            "current_price": exit_data.get("current_price", 0.0),
            "note": "This is a simulated order. No real trading occurs."
        }

        return order

    # ============================================================
    # LOGGING
    # ============================================================

    def _log_simulated_trade(self, order):
        """
        Save simulated trade to JSON file.
        """

        # AUDIT FINDING (d): created here, by the code that writes into it,
        # rather than in __init__ where importing the module was enough to
        # make a directory appear. Same shape as decision_log.log_decision.
        os.makedirs(self.log_dir, exist_ok=True)

        # 5 September 2026: was datetime.datetime.utcnow(), which is
        # deprecated and scheduled for removal. The repo fixed the same call
        # in data_fetcher.py on 2 September and missed this one. Both forms
        # produce the same UTC wall clock, so the filename is unchanged --
        # utcnow() returns it naive, this returns it aware, and strftime with
        # this format reads neither the tzinfo nor the offset.
        timestamp = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(self.log_dir, f"sim_trade_{timestamp}.json")

        with open(filepath, "w") as f:
            json.dump(order, f, indent=4)

        return filepath


# ============================================================
# SAFE LIVE-TRADING SIMULATOR — BUILT ON DEMAND
# ============================================================
#
# AUDIT FINDING (d), 5 September 2026. This was:
#
#     live_trading_simulator = LiveTradingSimulator()
#
# a module-level instance, so importing this module ran __init__, which ran
# os.makedirs and constructed a SignalRouter. Two side effects of an import,
# neither of them asked for, and nothing in the repository read the name.
#
# Deleted rather than made lazy-and-global, because the singleton was not
# serving anything. data_fetcher's module-level singleton is a different case
# and stays: it is shared state that engine_core and the tests deliberately
# patch as one object, and tests/test_imports.py asserts exactly that. This
# one had no second reader to agree with.
#
# An accessor is provided so a caller that wants one instance can have one,
# and pays for it when it asks rather than when it imports.

_simulator = None


def get_live_trading_simulator():
    """The process-wide simulator, constructed on first use."""
    global _simulator
    if _simulator is None:
        _simulator = LiveTradingSimulator()
    return _simulator
