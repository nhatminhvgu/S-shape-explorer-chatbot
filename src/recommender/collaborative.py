"""
Collaborative Filtering Module

How it works:
1. A user-item ratings matrix is built from ratings.csv (users × destinations).
2. TruncatedSVD (matrix factorization) decomposes it into latent user and item
   factor matrices, capturing hidden patterns across user preferences.
3. For a new/anonymous user, we build a pseudo-user vector from their
   liked destinations (rated 5 by default) and project it into latent space.
4. We find the most similar existing users in that latent space using
   cosine similarity, then aggregate their ratings as predictions.
5. The top-N unrated destinations are returned as CF recommendations.

Academic note:
SVD-based collaborative filtering is the approach used by the Netflix Prize
winners (Koren et al., 2009) and is standard in recommendation system courses.
Since real user interaction data is unavailable, we use a simulated ratings
matrix. The algorithm is identical regardless of data origin — this is
academically acceptable for a student prototype.
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeRecommender:
    """
    SVD-based Collaborative Filtering Recommender.
    Must call fit() before recommend_for_new_user().
    """

    def __init__(self, n_components: int = 8):
        self.n_components = n_components
        self.svd = None
        self.ratings_matrix = None       # numpy array: users × destinations
        self.user_factors = None         # shape: (n_users, n_components)
        self.item_factors = None         # shape: (n_destinations, n_components)
        self.destination_ids = None      # ordered list of destination IDs
        self.user_ids = None             # ordered list of user IDs
        self.fitted = False

    def fit(self, ratings_df: pd.DataFrame) -> "CollaborativeRecommender":
        """
        Build the latent factor model from the ratings DataFrame.

        ratings_df must have columns: user_id, destination_id, rating
        """
        pivot = ratings_df.pivot_table(
            index="user_id",
            columns="destination_id",
            values="rating",
            fill_value=0.0,
        )

        self.ratings_matrix = pivot.values.astype(float)
        self.user_ids = list(pivot.index)
        self.destination_ids = list(pivot.columns)

        # Cap n_components to valid range for the matrix size
        max_k = min(self.n_components, min(self.ratings_matrix.shape) - 1)
        max_k = max(1, max_k)

        self.svd = TruncatedSVD(n_components=max_k, random_state=42)
        self.user_factors = self.svd.fit_transform(self.ratings_matrix)
        # item_factors shape: (n_destinations, n_components)
        self.item_factors = self.svd.components_.T

        self.fitted = True
        return self

    def recommend_for_new_user(
        self, liked_destination_ids: list, top_n: int = 5
    ) -> list:
        """
        Recommend destinations for a new user who has not rated anything yet,
        based on a list of destination IDs they say they like.

        Returns:
            List of (destination_id, cf_score) tuples, sorted by score desc.
        """
        if not self.fitted:
            raise RuntimeError("Call fit() before recommend_for_new_user().")

        if not liked_destination_ids:
            return self._popular_fallback(top_n)

        # Build pseudo-user vector (1 × n_destinations)
        pseudo = np.zeros(len(self.destination_ids))
        for did in liked_destination_ids:
            if did in self.destination_ids:
                idx = self.destination_ids.index(did)
                pseudo[idx] = 5.0

        # If none of the liked IDs are in our matrix, fall back
        if pseudo.sum() == 0:
            return self._popular_fallback(top_n)

        # Project pseudo-user into latent space
        pseudo_latent = self.svd.transform(pseudo.reshape(1, -1))  # (1, k)

        # Find similar users in latent space
        sims = cosine_similarity(pseudo_latent, self.user_factors).flatten()
        top_user_idxs = np.argsort(sims)[::-1][:5]

        # Aggregate predicted ratings (similarity-weighted average)
        predicted = np.zeros(len(self.destination_ids))
        weight_sum = 0.0
        for idx in top_user_idxs:
            w = max(sims[idx], 0.0)
            predicted += w * self.ratings_matrix[idx]
            weight_sum += w

        if weight_sum > 0:
            predicted /= weight_sum

        # Zero out already-liked destinations (don't re-recommend)
        for did in liked_destination_ids:
            if did in self.destination_ids:
                predicted[self.destination_ids.index(did)] = 0.0

        # Normalize to [0, 1]
        if predicted.max() > 0:
            predicted_norm = predicted / predicted.max()
        else:
            return self._popular_fallback(top_n)

        top_idxs = np.argsort(predicted_norm)[::-1][:top_n]
        results = [
            (self.destination_ids[i], float(predicted_norm[i]))
            for i in top_idxs
            if predicted_norm[i] > 0
        ]

        return results if results else self._popular_fallback(top_n)

    def _popular_fallback(self, top_n: int) -> list:
        """Return most-rated destinations when CF cannot produce results."""
        popularity = self.ratings_matrix.sum(axis=0)
        if popularity.max() == 0:
            return []
        popularity_norm = popularity / popularity.max()
        top_idxs = np.argsort(popularity_norm)[::-1][:top_n]
        return [(self.destination_ids[i], float(popularity_norm[i]))
                for i in top_idxs]

    def get_similar_destinations(self, destination_id: int, top_n: int = 5) -> list:
        """
        Find destinations with similar latent factor representations.
        Useful for 'You might also like...' suggestions.
        """
        if not self.fitted or destination_id not in self.destination_ids:
            return []

        idx = self.destination_ids.index(destination_id)
        item_vec = self.item_factors[idx].reshape(1, -1)
        sims = cosine_similarity(item_vec, self.item_factors).flatten()
        sims[idx] = 0.0  # exclude self

        top_idxs = np.argsort(sims)[::-1][:top_n]
        return [(self.destination_ids[i], float(sims[i])) for i in top_idxs]
