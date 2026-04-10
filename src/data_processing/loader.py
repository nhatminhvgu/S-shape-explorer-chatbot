"""
Data Loader Module
Loads and validates the CSV datasets for destinations, reviews, and ratings.
Uses caching so data is only read once per session.
"""

import os
import pandas as pd
from ..utils.helpers import get_data_path


def load_destinations() -> pd.DataFrame:
    """
    Load destination metadata from CSV.
    Returns a cleaned DataFrame with all destination fields.
    """
    path = get_data_path("destinations.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"destinations.csv not found at {path}")

    df = pd.read_csv(path)

    # Ensure required columns exist
    required = ["id", "name", "region", "primary_category", "tags", "avg_rating", "price_level"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"destinations.csv is missing columns: {missing}")

    # Fill missing text fields with empty string
    for col in ["description", "description_vi", "name_vi", "tags", "best_for", "trip_duration"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    # Ensure numeric types
    df["avg_rating"] = pd.to_numeric(df["avg_rating"], errors="coerce").fillna(0.0)
    df["price_level"] = pd.to_numeric(df["price_level"], errors="coerce").fillna(2).astype(int)
    df["num_reviews"] = pd.to_numeric(df.get("num_reviews", 0), errors="coerce").fillna(0).astype(int)

    return df.reset_index(drop=True)


def load_reviews() -> pd.DataFrame:
    """
    Load user reviews from CSV.
    Returns a DataFrame with review text and pre-labeled sentiment.
    """
    path = get_data_path("reviews.csv")
    if not os.path.exists(path):
        # Return empty DataFrame with correct schema if file missing
        return pd.DataFrame(columns=["review_id", "destination_id", "user_id",
                                      "rating", "review_text", "language", "sentiment"])

    df = pd.read_csv(path)
    df["review_text"] = df["review_text"].fillna("")
    df["language"] = df["language"].fillna("en")
    df["sentiment"] = df["sentiment"].fillna("neutral")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(3).astype(int)

    return df.reset_index(drop=True)


def load_ratings() -> pd.DataFrame:
    """
    Load user-item ratings from CSV.
    Returns a DataFrame suitable for collaborative filtering.
    """
    path = get_data_path("ratings.csv")
    if not os.path.exists(path):
        return pd.DataFrame(columns=["user_id", "destination_id", "rating"])

    df = pd.read_csv(path)

    # Keep only ratings for destination IDs that exist in our dataset
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.dropna(subset=["rating"])
    df["rating"] = df["rating"].clip(1, 5)

    return df.reset_index(drop=True)


def load_all():
    """
    Convenience function: load all three datasets at once.
    Returns (destinations_df, reviews_df, ratings_df).
    """
    destinations = load_destinations()
    reviews = load_reviews()
    ratings = load_ratings()

    # Filter ratings to valid destination IDs only
    valid_ids = set(destinations["id"].tolist())
    ratings = ratings[ratings["destination_id"].isin(valid_ids)].reset_index(drop=True)

    return destinations, reviews, ratings
