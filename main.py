import argparse
import logging
import signal
import sys
from utils.logging_config import *
from utils.config import *
from utils.subprocess_utils import *
from utils.file_utils import *
from utils.network_utils import *


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="ScanScript")
    parser.add_argument('--auto', action='store_true', help='Enable automation mode (default all interactive options to Y)')
    parser.add_argument('--tor', action='store_true', help='Use Tor as the proxy')
    parser.add_argument('--burp-path', help='Path to Burp Suite executable', default='/home/kali/BurpSuitePro')
    return parser.parse_args()

def confirm_burp_start(automate: bool) -> bool:
    """
    Prompt the user to confirm starting Burp Suite, defaulting to Yes.

    Args:
        automate: Whether automation mode is enabled (skips prompt).

    Returns:
        True if Burp Suite should start, False otherwise.
    """
    if automate:
        logger.info("Automation mode enabled, starting Burp Suite by default")
        return True

    response = input("Start Burp Suite? [Y/n]: ").strip().lower()
    # Accept 'Y', 'y', or empty input as Yes
    return response in ('', 'y', 'yes')

def main() -> None:

    # Parse CLI arguments
    args = parse_args()
    AUTOMATE = args.auto
    USE_TOR = args.tor

    # Configure logger
    setup_logger(log_file="logs/app.log", log_level=logging.DEBUG)
    logger.info(f"Starting application (Auto: {AUTOMATE}, Tor: {USE_TOR})")

     # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda _sig, _frame: kill_all_sub_process())

    # Check domain.txt
    if not os.path.exists("domain.txt"):
        logger.error("找不到 'domain.txt' 呀～你是不是又忘記放了啊！快自己去創一個啦～")
        sys.exit(1)
    logger.info("Found domain.txt")


    try:
        # Find Burp Suite path
        BURP_PATH = locate_executable(
            executable_name="BurpSuitePro",
            provided_path=args.burp_path
        )

        logger.info(f"Using Burp Suite path: {BURP_PATH}")
        # Example: Generate and log static filter pattern
        static_filter = get_static_filter_grep()
        logger.info(f"Static filter pattern: {static_filter}")


    
    except Exception as e:
        logger.error(f"💥 Application error: {e}")
        sys.exit(1)

main()