from typing import List
from .logging_config import logger

# Global configuration for static file extensions
STATIC_EXTENSIONS: List[str] = [
    "jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "ico", "tiff", "tif", "avif",
    "woff", "woff2", "ttf", "otf", "eot", "fon",
    "mp4", "avi", "mov", "mkv", "webm", "flv", "m4v",
    "mp3", "wav", "ogg", "flac", "aac",
    "css", "less", "sass", "scss"
]

def get_static_filter_grep() -> str:
    """
    Generate a grep pattern to filter out static file extensions.

    Returns:
        A grep command string for excluding static files.
    """
    pattern = '|'.join(map(str.lower, STATIC_EXTENSIONS))  # Ensure case-insensitive matching
    grep_command = f"grep -Eiv '\\.({pattern})(\\?.*)?$'"
    logger.debug(f"Generated grep pattern: {grep_command}")
    return grep_command