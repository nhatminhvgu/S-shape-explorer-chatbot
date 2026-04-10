"""
General helper utilities used across modules.
"""

import os
import re


# Absolute path to the project root (two levels up from this file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


def get_data_path(filename: str) -> str:
    """Return the absolute path to a file inside the data/ directory."""
    return os.path.join(DATA_DIR, filename)


def stars(rating: float) -> str:
    """Convert a numeric rating to a star string for display."""
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


def format_tags(tags_str: str) -> list:
    """
    Parse a comma-separated tags string into a cleaned list.
    Example: 'beach,nature,relaxation' -> ['beach', 'nature', 'relaxation']
    """
    if not tags_str or not isinstance(tags_str, str):
        return []
    return [t.strip() for t in tags_str.split(",") if t.strip()]


def format_best_for(best_for_str: str) -> list:
    """
    Parse a pipe-separated best_for string.
    Example: 'couple|family' -> ['couple', 'family']
    """
    if not best_for_str or not isinstance(best_for_str, str):
        return []
    return [b.strip() for b in best_for_str.split("|") if b.strip()]


def format_trip_duration(duration_str: str) -> str:
    """
    Convert trip_duration field to a readable string.
    Example: 'short|long' -> 'Short or long trip'
    """
    if not duration_str:
        return "Flexible"
    parts = [d.strip().capitalize() for d in duration_str.split("|")]
    return " or ".join(parts) + " trip"


def price_level_label(level: int, lang: str = "en") -> str:
    """Return a human-readable price level label."""
    labels = {
        "en": {1: "Budget-friendly ($)", 2: "Mid-range ($$)", 3: "Premium ($$$)"},
        "vi": {1: "Tiết kiệm ($)", 2: "Tầm trung ($$)", 3: "Cao cấp ($$$)"},
    }
    return labels.get(lang, labels["en"]).get(level, str(level))


def region_label(region: str, lang: str = "en") -> str:
    """Return a human-readable region label."""
    labels = {
        "en": {"north": "North Vietnam", "central": "Central Vietnam", "south": "South Vietnam"},
        "vi": {"north": "Miền Bắc", "central": "Miền Trung", "south": "Miền Nam"},
    }
    return labels.get(lang, labels["en"]).get(region, region.capitalize())


def clean_text(text: str) -> str:
    """Basic text cleaning: lowercase, remove special characters."""
    if not text or not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\u00C0-\u024F\u1E00-\u1EFF]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len characters with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."
