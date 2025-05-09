import argparse
import logging
import signal
import sys

# Custom Moudles 
from utils.logging_config import *
from utils.config import *
from utils.subprocess_utils import *
from utils.file_utils import *
from utils.network_utils import *

## Tools Args t
def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="ScanScript")
    parser.add_argument('--auto', action='sore_true', help='Enable automation mode (default all interactive options to Y)')
    parser.add_argument('--tor', action='store_true', help='Use Tor as the proxy')
    parser.add_argument('--burp-path', help='Path to Burp Suite executable', default='/home/kali/BurpSuitePro/BurpSuitePro')
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

        # Confirm Burp Suite startup
        BurpSuit = None
        proxy_port = 9050 if USE_TOR else 8080

        proxy = 

        if confirm_burp_start(AUTOMATE):
            logger.info(f"Starting Burp Suite at {BURP_PATH}")
            BurpSuit = run_tool_as_thread(BURP_PATH, log_file="logs/burp.log")
            logger.info("Burp Suite started in thread")

            # Wait for Burp Suite proxy port (default 8080, or 9050 for Tor)
            if wait_for_port("localhost", proxy_port, timeout=9999):
                logger.info(f"Burp Suite proxy port {proxy_port} is ready")
            else:
                logger.error(f"Burp Suite proxy port {proxy_port} not ready")
                sys.exit(1)
        else:
            logger.info("Skipping Burp Suite startup")

        
        #------------------------------------------------------------------

        # Check assetFinder path
        ASSETFINDER_PATH = "/root/assetFinder.py"
        if not os.path.exists(ASSETFINDER_PATH):
            logger.error(f"assetFinder not found at {ASSETFINDER_PATH}. Please ensure it’s installed.")
            sys.exit(1)
        
        # Check subfinder and httpx-toolkit executables
        SUBFINDER_PATH = locate_executable("subfinder")
        HTTPX_PATH = locate_executable("httpx-toolkit")
        logger.info(f"Using subfinder path: {SUBFINDER_PATH}")
        logger.info(f"Using httpx-toolkit path: {HTTPX_PATH}")

        # Run assetFinder with alive check
        logger.info("Starting assetFinder with alive check")
        assetFinder_thread = run_tool_as_thread(
            f"python3 {ASSETFINDER_PATH}",
            f"{HTTPX_PATH} -l assets.txt -ports 443,80,8080,8000,888 -threads 200 | anew aliveAssets.txt",
            log_file="logs/assetFinder.log"
        )

        # Run subfinder with alive check
        logger.info("Starting subfinder with alive check")
        subfinder_thread = run_tool_as_thread(
            f"{SUBFINDER_PATH} -dL domain.txt | anew subdomains.txt",
            f"{HTTPX_PATH} -l subdomains.txt -ports 443,80,8080,8000,888 -threads 200 | anew aliveSubDomains.txt",
            log_file="logs/subfinder.log"
        )

        # Wait for assetFinder and subfinder to complete
        assetFinder_thread.join()
        subfinder_thread.join()
        logger.info("AssetFinder and subfinder tasks completed")

        #------------------------------------------------------------------

        # Check wafw00f executables & Use Proxy or not 
        WAFW00F_PATH = locate_executable("wafw00f")
        logger.info(f"Using wafw00f path: {WAFW00F_PATH}")
        use_proxy = USE_TOR or BurpSuit is not None


        if use_proxy:
            logger.info(f"[WAF] Using {'Tor' if USE_TOR else 'Burp'} proxy to scan WAF ({proxy_port})")
            # Run wafw00f scan
            logger.info(f"🚀 [Scanning] Using proxy {proxy_port} to scan domains and subdomains")
            logger.info(f"[WAF] Using {'Tor' if USE_TOR else 'Burp'} proxy to scan WAF ({proxy_port})")
            wafw00f_cmd = f"{WAFW00F_PATH} --input=subdomains.txt --format=json --verbose --output=waffSubDomains.json --proxy {proxy_port}"
        else:
            logger.info("[WAF] Scanning without proxy")
            wafw00f_cmd = f"{WAFW00F_PATH} --input=subdomains.txt --format=json --verbose --output=waffSubDomains.json"
        
        wafw00f_thread = run_tool_as_thread(
            wafw00f_cmd,
            log_file="logs/wafw00f.log"
        )
        wafw00f_thread.join()
        logger.info("WAF scan completed")

        # Process WAF results
        display_and_save_no_waf_domains("waffSubDomains.json", "no_waf_domains.txt")




    except Exception as e:
        logger.error(f"💥 Application error: {e}")
        sys.exit(1)

main()