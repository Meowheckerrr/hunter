import subprocess
import json
from typing import List
from .logging_config import logger

def count_lines_with_wc(file_name: str) -> int:
    """
    Count the number of lines in a file using `wc -l`.
    Args:
        file_name: Path to the file.
    Returns:
        Number of lines, or 0 if an error occurs.
    """
    try:
        result = subprocess.run(
            ['wc', '-l', file_name],
            capture_output=True,
            text=True,
            check=True
        )
        count = int(result.stdout.strip().split()[0])
        logger.debug(f"Counted {count} lines in {file_name}")
        return count
    except (subprocess.SubprocessError, ValueError) as e:
        logger.error(f"❗ Unable to count lines in {file_name}: {e}")
        return 0

def display_and_save_no_waf_domains(json_file: str, output_file: str = "no_waf_domains.txt") -> None:
    """
    Read a JSON file, extract domains without WAF, log them, and save to a file.

    Args:
        json_file: Path to the JSON file.
        output_file: Path to save the domains (default: no_waf_domains.txt).
    """
    try:
        with open(json_file, "r") as file:
            data = json.load(file)

        no_waf_domains: List[str] = [
            entry['url'] for entry in data
            if not entry.get("detected", False)
        ]

        if not no_waf_domains:
            logger.warning("❌ No domains without WAF found.")
            return

        logger.info("🎯 === Domains without WAF ===")
        for url in no_waf_domains:
            logger.info(f"🌟 {url} (No WAF detected)")

        with open(output_file, "w") as f:
            f.write("\n".join(no_waf_domains) + "\n")
        logger.info(f"✅ Saved {len(no_waf_domains)} domains to {output_file}")

    except FileNotFoundError:
        logger.error(f"💥 Error: {json_file} not found")
    except json.JSONDecodeError:
        logger.error(f"💥 Error: Invalid JSON format in {json_file}")
    except Exception as e:
        logger.error(f"💥 Error processing {json_file}: {e}")