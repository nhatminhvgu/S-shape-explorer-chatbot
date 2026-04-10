"""
Sentiment Analysis Module

English: VADER (from nltk) - well-suited for short reviews and social text.
Vietnamese: Keyword-based lexicon approach - practical and dependency-free.

Academic justification:
- VADER is a validated, published sentiment analysis tool (Hutto & Gilbert, 2014)
- For Vietnamese, a lexicon approach is standard practice given limited free tooling
- Both approaches are transparent and reproducible
"""

import nltk


def _ensure_vader():
    """Download VADER lexicon if not already present."""
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)


# Vietnamese sentiment lexicon
# Source: curated common travel-domain adjectives
VI_POSITIVE_WORDS = [
    "đẹp", "tuyệt", "tuyệt vời", "hay", "thích", "yêu", "thú vị", "tốt",
    "xuất sắc", "hài lòng", "hoàn hảo", "lý tưởng", "ấn tượng", "dễ chịu",
    "sạch", "sạch sẽ", "thân thiện", "ngon", "rẻ", "phù hợp", "thoải mái",
    "vui", "đáng", "đáng tiền", "hấp dẫn", "kỳ diệu", "đặc sắc", "độc đáo",
    "nên đi", "tuyệt đỉnh", "phong phú", "yên bình", "trong lành", "tươi",
]

VI_NEGATIVE_WORDS = [
    "tệ", "xấu", "chán", "thất vọng", "tồi", "bẩn", "đắt", "ồn", "nguy hiểm",
    "không hài lòng", "kém", "khó chịu", "xấu xí", "đông đúc", "nhàm chán",
    "không ổn", "mệt", "cũ", "xuống cấp", "lộn xộn", "tắc nghẽn", "nhàm",
    "không đáng", "quá tải", "thiếu", "nghèo nàn",
]


def analyze_sentiment_english(text: str) -> dict:
    """
    Analyze English review sentiment using VADER.

    Returns:
        dict with 'score' (float, -1 to 1), 'label' (positive/neutral/negative),
        and 'details' (VADER component scores)
    """
    _ensure_vader()
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {"score": compound, "label": label, "details": scores}


def analyze_sentiment_vietnamese(text: str) -> dict:
    """
    Analyze Vietnamese text sentiment using keyword counting.

    Returns:
        dict with 'score' (float, -1 to 1) and 'label' (positive/neutral/negative)
    """
    text_lower = text.lower()

    pos_count = sum(1 for word in VI_POSITIVE_WORDS if word in text_lower)
    neg_count = sum(1 for word in VI_NEGATIVE_WORDS if word in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return {"score": 0.0, "label": "neutral"}

    score = (pos_count - neg_count) / total

    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {"score": score, "label": label}


def analyze_sentiment(text: str, language: str = "en") -> dict:
    """
    Main sentiment analysis entry point.

    Args:
        text: review text
        language: 'en' or 'vi'

    Returns:
        dict with 'score' and 'label'
    """
    if not text or not isinstance(text, str) or not text.strip():
        return {"score": 0.0, "label": "neutral"}

    if language == "vi":
        return analyze_sentiment_vietnamese(text)
    return analyze_sentiment_english(text)


def score_destination_sentiment(reviews_df, destination_id: int) -> dict:
    """
    Aggregate sentiment across all reviews for a single destination.

    Returns:
        dict with 'avg_score', 'label', 'positive_pct', 'negative_pct', 'neutral_pct'
    """
    dest_reviews = reviews_df[reviews_df["destination_id"] == destination_id]

    if dest_reviews.empty:
        return {"avg_score": 0.0, "label": "neutral",
                "positive_pct": 0, "negative_pct": 0, "neutral_pct": 100}

    scores = []
    for _, row in dest_reviews.iterrows():
        result = analyze_sentiment(str(row.get("review_text", "")),
                                   str(row.get("language", "en")))
        scores.append(result["score"])

    avg_score = sum(scores) / len(scores)

    # Count labels
    labels = [analyze_sentiment(str(r["review_text"]),
                                str(r.get("language", "en")))["label"]
              for _, r in dest_reviews.iterrows()]

    n = len(labels)
    pos_pct = round(100 * labels.count("positive") / n)
    neg_pct = round(100 * labels.count("negative") / n)
    neu_pct = 100 - pos_pct - neg_pct

    if avg_score >= 0.05:
        label = "positive"
    elif avg_score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "avg_score": round(avg_score, 3),
        "label": label,
        "positive_pct": pos_pct,
        "negative_pct": neg_pct,
        "neutral_pct": neu_pct,
    }


def add_sentiment_scores(destinations_df, reviews_df):
    """
    Enrich the destinations DataFrame with aggregated sentiment scores.
    Adds columns: sentiment_score, sentiment_label, positive_pct.
    """
    records = []
    for dest_id in destinations_df["id"]:
        result = score_destination_sentiment(reviews_df, dest_id)
        records.append({
            "id": dest_id,
            "sentiment_score": result["avg_score"],
            "sentiment_label": result["label"],
            "positive_pct": result["positive_pct"],
        })

    import pandas as pd
    sentiment_df = pd.DataFrame(records)
    enriched = destinations_df.merge(sentiment_df, on="id", how="left")
    enriched["sentiment_score"] = enriched["sentiment_score"].fillna(0.0)
    enriched["sentiment_label"] = enriched["sentiment_label"].fillna("neutral")
    enriched["positive_pct"] = enriched["positive_pct"].fillna(0)

    return enriched
