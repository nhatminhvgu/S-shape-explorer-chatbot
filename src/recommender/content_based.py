"""
Content-Based Filtering Module

How it works:
1. Each destination is represented as a TF-IDF vector built from its
   tags, category, region, best_for, and description text.
2. User preferences (categories, region, budget, group type, travel style)
   are converted into a query string and also vectorized.
3. Cosine similarity is computed between the user query vector and all
   destination vectors.
4. Hard filters (region, budget) are applied first, then similarity scoring
   ranks the remaining destinations.
5. A small rating bonus (10% weight) ensures highly-rated places
   are preferred when similarity scores are close.

Academic note: TF-IDF + cosine similarity is the standard baseline for
content-based recommendation systems and is well-documented in the literature.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from ..data_processing.cleaner import build_destination_text_profile


def build_user_query(preferences: dict) -> str:
    """
    Convert a preferences dict into a plain text query for TF-IDF matching.

    Expected keys in preferences:
        categories   : list[str]  e.g. ['beach', 'nature']
        region       : str        e.g. 'north', 'central', 'south', or ''
        budget       : str        e.g. 'budget', 'mid', 'premium', or ''
        group_type   : str        e.g. 'solo', 'couple', 'family', 'friends'
        travel_style : list[str]  e.g. ['relaxation', 'adventure']
        trip_duration: str        e.g. 'short', 'long', or ''
    """
    parts = []

    # Repeat categories twice to increase their TF-IDF weight
    for cat in preferences.get("categories", []):
        parts.append(f"{cat} {cat}")

    region = preferences.get("region", "")
    if region:
        parts.append(f"{region} vietnam")

    for style in preferences.get("travel_style", []):
        parts.append(style)

    group = preferences.get("group_type", "")
    if group:
        parts.append(group)

    duration = preferences.get("trip_duration", "")
    if duration:
        parts.append(duration)

    return " ".join(parts).lower().strip()


class ContentBasedRecommender:
    """
    Content-Based Recommender using TF-IDF and Cosine Similarity.
    Must call fit() before recommend().
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=500,
            sublinear_tf=True,       # dampen high-frequency terms
        )
        self.tfidf_matrix = None
        self.destinations_df = None
        self.fitted = False

    def fit(self, destinations_df: pd.DataFrame) -> "ContentBasedRecommender":
        """Build the TF-IDF matrix from destination text profiles."""
        self.destinations_df = destinations_df.reset_index(drop=True)

        profiles = self.destinations_df.apply(
            build_destination_text_profile, axis=1
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(profiles)
        self.fitted = True
        return self

    def recommend(self, preferences: dict, top_n: int = 5) -> pd.DataFrame:
        """
        Return top-N destinations ranked by content similarity.

        Returns a DataFrame with a 'cb_score' column added.
        """
        if not self.fitted:
            raise RuntimeError("Call fit() before recommend().")

        user_query = build_user_query(preferences)

        if not user_query:
            # No query: fall back to top-rated
            result = self.destinations_df.copy()
            result["cb_score"] = result["avg_rating"] / 5.0
            return result.nlargest(top_n, "cb_score").reset_index(drop=True)

        # Compute cosine similarities
        user_vec = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(user_vec, self.tfidf_matrix).flatten()

        result = self.destinations_df.copy()
        result["cb_score"] = similarities

        # Apply hard filters (region, budget)
        result = self._apply_hard_filters(result, preferences)

        # Blend with normalized rating (10% weight)
        scaler = MinMaxScaler()
        if len(result) > 1:
            rating_norm = scaler.fit_transform(result[["avg_rating"]]).flatten()
        else:
            rating_norm = np.array([1.0] * len(result))

        result["cb_score"] = 0.90 * result["cb_score"] + 0.10 * rating_norm

        return result.nlargest(top_n, "cb_score").reset_index(drop=True)

    def _apply_hard_filters(self, df: pd.DataFrame, preferences: dict) -> pd.DataFrame:
        """
        Filter destinations by region and budget.
        If filters produce fewer than 3 results, they are relaxed to avoid
        an empty recommendation list.
        """
        filtered = df.copy()

        region = preferences.get("region", "")
        if region in ("north", "central", "south"):
            filtered = filtered[filtered["region"] == region]

        budget = preferences.get("budget", "")
        if budget == "budget":
            filtered = filtered[filtered["price_level"] == 1]
        elif budget == "premium":
            filtered = filtered[filtered["price_level"] == 3]

        # Relax filters if too restrictive
        if len(filtered) < 3:
            return df
        return filtered
