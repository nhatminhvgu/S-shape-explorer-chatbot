"""
Text Cleaning and Preprocessing Module
Cleans review text and destination descriptions for NLP tasks.
Handles both English and Vietnamese text.
"""

import re
import string


# Common English stopwords (lightweight, no NLTK dependency needed here)
EN_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "have", "has", "had", "do", "did", "will", "would", "could", "should",
    "it", "its", "this", "that", "these", "those", "i", "you", "we", "they",
    "he", "she", "my", "your", "our", "their", "very", "just", "so", "not",
    "no", "if", "as", "all", "also", "more", "than", "there", "here",
}

# Common Vietnamese stopwords
VI_STOPWORDS = {
    "là", "và", "của", "trong", "có", "được", "cho", "với", "tôi", "bạn",
    "một", "những", "các", "này", "đó", "cũng", "như", "thì", "mà", "hay",
    "rất", "đã", "sẽ", "không", "nếu", "khi", "bởi", "vì", "về", "từ",
    "lên", "xuống", "ra", "vào", "đến", "đi", "làm", "nơi", "đây",
}


def remove_punctuation(text: str) -> str:
    """Remove punctuation from text."""
    return text.translate(str.maketrans("", "", string.punctuation))


def clean_english(text: str) -> str:
    """
    Clean English review text:
    - Lowercase
    - Remove URLs, special characters, extra whitespace
    - Remove stopwords
    """
    if not text or not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)          # remove URLs
    text = re.sub(r"[^a-z0-9\s]", " ", text)            # keep letters and digits
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    tokens = text.split()
    tokens = [t for t in tokens if t not in EN_STOPWORDS and len(t) > 1]

    return " ".join(tokens)


def clean_vietnamese(text: str) -> str:
    """
    Clean Vietnamese text:
    - Lowercase
    - Remove special characters while preserving Vietnamese diacritics
    - Remove stopwords
    """
    if not text or not isinstance(text, str):
        return ""

    text = text.lower().strip()
    # Keep Vietnamese Unicode range (0x00C0-0x024F covers many accented chars,
    # 0x1E00-0x1EFF covers Vietnamese-specific characters)
    text = re.sub(r"[^\w\s\u00C0-\u024F\u1E00-\u1EFF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    tokens = text.split()
    tokens = [t for t in tokens if t not in VI_STOPWORDS and len(t) > 1]

    return " ".join(tokens)


def clean_text(text: str, language: str = "en") -> str:
    """
    Main text cleaning function. Routes to language-specific cleaner.

    Args:
        text: input text string
        language: 'en' for English, 'vi' for Vietnamese

    Returns:
        Cleaned text string
    """
    if language == "vi":
        return clean_vietnamese(text)
    return clean_english(text)


def preprocess_reviews(reviews_df):
    """
    Add a 'cleaned_text' column to the reviews DataFrame.
    Cleans each review according to its language field.
    """
    import pandas as pd

    def _clean_row(row):
        lang = row.get("language", "en")
        return clean_text(str(row.get("review_text", "")), lang)

    reviews_df = reviews_df.copy()
    reviews_df["cleaned_text"] = reviews_df.apply(_clean_row, axis=1)
    return reviews_df


def build_destination_text_profile(row) -> str:
    """
    Build a single text string representing a destination.
    Used as input to TF-IDF in the content-based recommender.
    Tags are repeated to increase their weight in TF-IDF.
    """
    parts = []

    # Tags repeated for weighting
    if row.get("tags"):
        tag_text = row["tags"].replace(",", " ")
        parts.append(tag_text + " " + tag_text)

    # Primary category (repeated)
    if row.get("primary_category"):
        parts.append(row["primary_category"] + " " + row["primary_category"])

    # Region
    if row.get("region"):
        parts.append(row["region"] + " vietnam")

    # Best-for group types
    if row.get("best_for"):
        parts.append(row["best_for"].replace("|", " "))

    # Trip duration
    if row.get("trip_duration"):
        parts.append(row["trip_duration"].replace("|", " "))

    # English description (for additional context)
    if row.get("description"):
        # Clean it before adding
        parts.append(clean_english(str(row["description"])))

    return " ".join(parts).lower()
