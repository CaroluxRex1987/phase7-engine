import sys
import os
import logging

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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


def main():
    """
    Main entry point for Phase-7 Structural Quant Engine.
    Returns 0 for success, 1 for failure.
    """
    try:
        # Validate required configuration
        if not hasattr(config, 'SYMBOL') or not config.SYMBOL:
            logger.error("Missing or empty config.SYMBOL")
            return 1
            
        if not hasattr(config, 'TIMEFRAME') or not config.TIMEFRAME:
            logger.error("Missing or empty config.TIMEFRAME")
            return 1
            
        logger.info(f"Starting Phase-7 engine for {config.SYMBOL} on {config.TIMEFRAME}")
        
        # Ensure log directory exists
        os.makedirs(config.LOG_DIR, exist_ok=True)
        
        router = SignalRouter()

        # Run engine using default config values with exception handling
        decision = router.route(
            symbol=config.SYMBOL,
            timeframe=config.TIMEFRAME
        )
        
        # Check for errors in the decision object
        if decision and "error" in decision:
            logger.error(f"Engine returned error: {decision['error']}")
            return 1
            
        logger.info("Phase-7 engine completed successfully")
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
