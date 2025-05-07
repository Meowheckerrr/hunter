import logging
import os
from typing import Optional

def setup_logger(log_file: Optional[str] = "logs/app.log", log_level: int = logging.INFO) -> logging.Logger:
    """
    Configure a centralized logger with console and file handlers.

    Args:
        log_file: Path to the log file (None for console-only logging).
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("project")
    logger.setLevel(log_level)

    # Avoid duplicate handlers if logger is reconfigured
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:  # Only create directory if it's non-empty
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Initialize the logger
logger = setup_logger()