"""Utilities for handling filenames."""

import re


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Convert a string to a safe filename by removing special characters.

    Args:
        name: The original string to sanitize
        replacement: Character to replace spaces with (default: "_")

    Returns:
        A sanitized string safe for use as a filename

    Examples:
        >>> sanitize_filename("Sea Kayak Pro")
        'Sea_Kayak_Pro'
        >>> sanitize_filename("My/Kayak\\Design")
        'MyKayakDesign'
    """
    # Remove any characters that aren't alphanumeric, whitespace, hyphens, or underscores
    clean_name = re.sub(r"[^\w\s-]", "", name)
    # Strip leading/trailing whitespace
    clean_name = clean_name.strip()
    # Replace spaces with the replacement character
    clean_name = re.sub(r"\s+", replacement, clean_name)
    # Ensure the filename is not empty
    if not clean_name:
        clean_name = "unnamed"

    return clean_name.lower()
