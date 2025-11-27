"""Utilities for the bot's business code."""
import re

INVALID_CHARS_REGEX = r"[^A-Za-z0-9\-!\. ]"

def slugify(original_string: str) -> str:
    """'Slugify' a string to make it safe to use as a filename."""
    return re.sub(INVALID_CHARS_REGEX, "-", original_string)
    
