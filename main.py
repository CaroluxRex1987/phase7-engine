import sys
import os
import re
import logging

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 17 October 2026 -- THE FORWARD MEASUREMENT: a run started as a script works
# from the repository's own folder, whatever folder it was started from.
#
# Every path the engine writes is relative -- config.LOG_DIR is "logs/" -- so a
# run has always written its decision log, archive, state, chart and process
# log into whichever folder it was started from. Started by hand from
# E:\phase7_engine, that is the repository. Started by Windows Task Scheduler,
# it is the folder a scheduled task starts in when none is set, which as far as
# Claude knows is C:\Windows\System32 (not checked on Viktor's machine when this
# was written; the first scheduled run is the check). Changing folder here,
# before anything below opens a file, leaves every recorded path exactly as it
# was ("logs/..."). That is why it is done this way and not by making the paths
# absolute: an absolute path would be written into every decision record, and
# would differ from machine to machine.
#
# Only when run as a script. tests/test_imports.py imports this module from a
# scratch folder precisely so that the makedirs and FileHandler below cannot
# reach the real logs/ (6 September 2026); a change of folder on import would
# undo that. tests/test_main_takes_pairs.py holds both halves.
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Log directories must exist before anything opens a file inside them.
# logging.FileHandler opens its file at construction, not at first write, so
# the basicConfig call below raises FileNotFoundError during import on any
# machine where the log directory does not already exist — before main() runs,
# and so outside the reach of the try/except inside it. This never appeared on
# the development machine, where it has existed since the first run; it appears
# for anyone cloning the repository.
#
# Placed here rather than immediately above basicConfig because module-scope
# code in the import chain can also touch the filesystem.
#
# SEQUENCE ITEM 14: config is imported first so the directory and the log file
# both come from config.LOG_DIR. They were the literals 'Logs' and
# 'Logs/phase7_engine.log', naming a directory .gitignore does not ignore — so
# on Linux the engine's own log file was offered for commit on any clone.
from core import config

os.makedirs(config.LOG_DIR, exist_ok=True)

from models.signal_router import SignalRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOG_DIR, 'phase7_engine.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# 17 October 2026 -- the pairs a run analyses come from the command line:
#
#     python main.py                     config.SYMBOL (AEROUSDT), as before
#     python main.py ETHUSDT SOLUSDT     each pair in turn, in this process
#
# Viktor's ruling of 17 October (DECISIONS, "Ruling, 17 October 2026 — the
# forward measurement ...") runs ten pairs every four hours to measure how often
# the engine says LONG; until now main.py could run only config.SYMBOL.
#
# A pair is upper-case letters and digits ending in USDT. Spot against USDT is
# the only market the engine's actions describe ("Ruling, 28 September 2026 —
# what 'finished' means ...", point 3: on spot, SHORT means sell to USDT).
# Anything else -- a lower-case name, another quote currency, a pair named
# twice -- refuses the whole command before any pair runs, so a typo shows on
# the first run by hand instead of as a pair silently missing from a month of
# scheduled runs.
PAIR_PATTERN = re.compile(r"[A-Z0-9]{1,20}USDT")


def parse_pairs(args):
    """
    The pairs to run, in the order given, or ValueError naming what is wrong.

    No arguments means config.SYMBOL alone, which is what main.py ran before
    it took any.
    """
    if not args:
        return [config.SYMBOL]
    malformed = [a for a in args if not PAIR_PATTERN.fullmatch(a)]
    if malformed:
        raise ValueError(
            "not a spot pair against USDT in upper case (for example SOLUSDT): "
            + ", ".join(repr(a) for a in malformed))
    repeated = sorted({a for a in args if args.count(a) > 1})
    if repeated:
        raise ValueError("named more than once: " + ", ".join(repeated))
    return list(args)


def run_pair(symbol):
    """
    One engine run for one pair, with a router of its own. True on success.

    config.SYMBOL is the pair for the length of the run, and restored after it.
    The decision log records config.SYMBOL among the settings that change a
    decision (core/decision_log.py, FINGERPRINTED_CONFIG), so left at AEROUSDT
    every other pair's record would say it was configured for AEROUSDT.
    Restored, so that a caller running main() in-process -- the tests -- gets
    config back as it was.
    """
    original = config.SYMBOL
    config.SYMBOL = symbol
    try:
        logger.info(f"Starting Phase-7 engine for {symbol} on {config.TIMEFRAME}")
        router = SignalRouter()
        decision = router.route(
            symbol=symbol,
            timeframe=config.TIMEFRAME
        )
        # Check for errors in the decision object. A run that fails this way
        # writes no decision record (models/signal_router.py returns the error
        # before decision_log.write), so this line in the process log is the
        # only trace an unattended run leaves of it.
        if decision and "error" in decision:
            logger.error(f"Engine returned error for {symbol}: {decision['error']}")
            return False
        logger.info(f"Phase-7 engine completed successfully for {symbol}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error in the run for {symbol}: {e}")
        return False
    finally:
        config.SYMBOL = original


def main(argv=None):
    """
    Main entry point for Phase-7 Structural Quant Engine.

    `argv` is the pairs, sys.argv[1:] when not given. Returns 0 when every pair
    ran, 1 when any failed or the configuration is incomplete, and 2 when the
    command line names something that is not a pair -- in which case no pair is
    run at all.
    """
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        # Validate required configuration
        if not args and (not hasattr(config, 'SYMBOL') or not config.SYMBOL):
            logger.error("Missing or empty config.SYMBOL")
            return 1

        if not hasattr(config, 'TIMEFRAME') or not config.TIMEFRAME:
            logger.error("Missing or empty config.TIMEFRAME")
            return 1

        try:
            pairs = parse_pairs(args)
        except ValueError as e:
            logger.error(f"Refused, and no pair was run: {e}")
            return 2

        # Ensure log directory exists
        os.makedirs(config.LOG_DIR, exist_ok=True)

        # One pair after another, each with its own router; a pair that fails
        # does not stop the ones after it.
        failed = [symbol for symbol in pairs if not run_pair(symbol)]
        if failed:
            logger.error(f"{len(failed)} of {len(pairs)} pairs failed: {', '.join(failed)}")
            return 1
        return 0

    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return 1
    except AttributeError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
