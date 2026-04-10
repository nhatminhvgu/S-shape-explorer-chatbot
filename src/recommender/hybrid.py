"""
Hybrid Recommender Module

Combines content-based filtering (CBF) and collaborative filtering (CF)
using a weighted linear combination:

    hybrid_score = α × cb_score + (1 − α) × cf_score

Design choices:
- α = 0.65 (CBF weight): CBF is more reliable when user history is sparse.
  CF provides diversity and serendipitous discoveries.
- When CF has no data for the user, α = 1.0 (pure CBF fallback).
- Sentiment score adds a small bonus for destinations with positive reviews.

This is a "cascade hybrid" variant: CBF filters candidates, CF re-ranks them.
Reference: Burke (2002) "Hybrid Recommender Systems: Survey and Experiments".
"""

import pandas as pd
import numpy as np

from .content_based import ContentBasedRecommender
from .collaborative import CollaborativeRecommender


CB_WEIGHT = 0.75   # content-based weight (higher = less CF noise on cold start)
CF_WEIGHT = 0.25   # collaborative filtering weight
SENTIMENT_BONUS = 0.05  # small bonus for destinations with positive reviews


class HybridRecommender:
    """
    Hybrid recommendation engine combining CBF + CF.
    Call fit() once at startup, then recommend() for each user request.
    """

    def __init__(self):
        self.cb = ContentBasedRecommender()
        self.cf = CollaborativeRecommender(n_components=8)
        self.destinations_df = None
        self.cf_available = False
        self.fitted = False

    def fit(
        self,
        destinations_df: pd.DataFrame,
        ratings_df: pd.DataFrame,
    ) -> "HybridRecommender":
        """Fit both sub-recommenders on the provided data."""
        self.destinations_df = destinations_df.reset_index(drop=True)

        # Always fit content-based
        self.cb.fit(destinations_df)

        # Attempt to fit CF; degrade gracefully if data is insufficient
        try:
            if len(ratings_df) >= 10:
                self.cf.fit(ratings_df)
                self.cf_available = True
            else:
                self.cf_available = False
        except Exception as exc:
            print(f"[HybridRecommender] CF fitting skipped: {exc}")
            self.cf_available = False

        self.fitted = True
        return self

    def recommend(
        self,
        preferences: dict,
        liked_destination_ids: list = None,
        top_n: int = 5,
    ) -> pd.DataFrame:
        """
        Generate hybrid recommendations.

        Args:
            preferences: user preference dict (see ContentBasedRecommender)
            liked_destination_ids: list of destination IDs user has liked
                                   (used for CF component)
            top_n: number of recommendations to return

        Returns:
            DataFrame with columns including 'hybrid_score', sorted desc.
        """
        if not self.fitted:
            raise RuntimeError("Call fit() before recommend().")

        liked = liked_destination_ids or []

        # Step 1: Get CB scores for ALL destinations (for complete ranking)
        cb_results = self.cb.recommend(preferences, top_n=len(self.destinations_df))

        # Step 2: Get CF scores if available
        cf_score_map = {}
        if self.cf_available:
            cf_list = self.cf.recommend_for_new_user(liked, top_n=len(self.destinations_df))
            cf_score_map = {dest_id: score for dest_id, score in cf_list}

        # Step 3: Merge and compute hybrid score
        result = cb_results.copy()
        result["cf_score"] = result["id"].map(lambda x: cf_score_map.get(x, 0.0))

        use_cf = self.cf_available and bool(cf_score_map)

        if use_cf:
            result["hybrid_score"] = (
                CB_WEIGHT * result["cb_score"] + CF_WEIGHT * result["cf_score"]
            )
        else:
            # Pure content-based when CF is unavailable
            result["hybrid_score"] = result["cb_score"]

        # Step 4: Apply small sentiment bonus if column exists
        if "sentiment_score" in result.columns:
            # Normalize sentiment_score to [0, 1] range before bonus
            s = result["sentiment_score"].clip(-1, 1)
            sentiment_bonus = ((s + 1) / 2) * SENTIMENT_BONUS
            result["hybrid_score"] = result["hybrid_score"] + sentiment_bonus

        # Step 5: Final sort
        top = result.nlargest(top_n, "hybrid_score").reset_index(drop=True)
        return top

    def explain(
        self,
        destination_row: pd.Series,
        preferences: dict,
        language: str = "en",
    ) -> str:
        """
        Generate a natural-language explanation for a recommendation.
        Delegates to the response generator (template-based LLM layer).
        """
        from ..chatbot.response import generate_recommendation_explanation
        return generate_recommendation_explanation(destination_row, preferences, language)
