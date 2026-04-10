"""
Conversation Manager Module

Manages the state of a multi-turn conversation session.
Tracks:
  - conversation history (list of message dicts)
  - accumulated user preferences (extracted across turns)
  - last recommendation results
  - whether the bot has greeted the user

This module is the "brain" that connects user input, intent recognition,
the hybrid recommender, and the response generator.
"""

from typing import Optional
import pandas as pd

from ..chatbot.intent import extract_preferences, merge_preferences, has_enough_preferences
from ..chatbot.response import (
    get_greeting,
    get_recommendation_intro,
    get_follow_up,
    get_clarification_prompt,
    get_no_results_response,
    generate_recommendation_explanation,
)


class ConversationManager:
    """
    Manages chatbot conversation state and turn processing.

    Usage:
        manager = ConversationManager(recommender, language='en')
        response, results_df = manager.process_turn("I want beaches in south Vietnam")
    """

    def __init__(self, recommender, language: str = "en"):
        """
        Args:
            recommender : a fitted HybridRecommender instance
            language    : 'en' or 'vi'
        """
        self.recommender = recommender
        self.language = language
        self.history = []          # list of {"role": "user"|"bot", "text": str}
        self.preferences = {       # accumulated preference slots
            "categories": [],
            "region": "",
            "budget": "",
            "group_type": "",
            "travel_style": [],
            "trip_duration": "",
        }
        self.last_results = None   # last DataFrame of recommendations
        self.greeted = False
        self.liked_destinations = []  # destination IDs user has expressed interest in

    def set_language(self, language: str):
        """Update the conversation language."""
        self.language = language

    def reset(self):
        """Clear conversation history and preferences (start over)."""
        self.history = []
        self.preferences = {
            "categories": [],
            "region": "",
            "budget": "",
            "group_type": "",
            "travel_style": [],
            "trip_duration": "",
        }
        self.last_results = None
        self.greeted = False
        self.liked_destinations = []

    def get_greeting(self) -> str:
        """Return greeting message and mark bot as having greeted."""
        self.greeted = True
        msg = get_greeting(self.language)
        self._add_bot_message(msg)
        return msg

    def process_turn(
        self,
        user_text: str,
        sidebar_preferences: Optional[dict] = None,
    ) -> tuple:
        """
        Process one conversation turn.

        Args:
            user_text          : raw text input from the user
            sidebar_preferences: preferences from the Streamlit sidebar (optional)
                                 These take priority over chat-extracted preferences.

        Returns:
            (bot_response: str, recommendations: pd.DataFrame or None)
        """
        # Record user message
        self._add_user_message(user_text)

        # Extract preferences from free-text input
        extracted = extract_preferences(user_text)

        # Merge with accumulated preferences (chat-extracted)
        self.preferences = merge_preferences(self.preferences, extracted)

        # Override with sidebar preferences if provided
        if sidebar_preferences:
            self.preferences = merge_preferences(self.preferences, sidebar_preferences)

        # Decide next action
        if not has_enough_preferences(self.preferences) and not sidebar_preferences:
            # Not enough info to recommend — ask for clarification
            bot_msg = get_clarification_prompt(self.language)
            self._add_bot_message(bot_msg)
            return bot_msg, None

        # Generate recommendations
        results = self.recommender.recommend(
            preferences=self.preferences,
            liked_destination_ids=self.liked_destinations,
            top_n=5,
        )

        if results is None or len(results) == 0:
            bot_msg = get_no_results_response(self.language)
            self._add_bot_message(bot_msg)
            return bot_msg, None

        self.last_results = results

        # Build bot response
        intro = get_recommendation_intro(self.language)
        follow_up = get_follow_up(self.language)
        bot_msg = f"{intro}\n\n{follow_up}"
        self._add_bot_message(bot_msg)

        return bot_msg, results

    def process_sidebar_request(self, sidebar_preferences: dict) -> tuple:
        """
        Process a recommendation request triggered directly from the sidebar
        (without a user text message).
        """
        # Update preferences from sidebar
        self.preferences = merge_preferences(self.preferences, sidebar_preferences)

        results = self.recommender.recommend(
            preferences=self.preferences,
            liked_destination_ids=self.liked_destinations,
            top_n=5,
        )

        if results is None or len(results) == 0:
            bot_msg = get_no_results_response(self.language)
            self._add_bot_message(bot_msg)
            return bot_msg, None

        self.last_results = results

        intro = get_recommendation_intro(self.language)
        follow_up = get_follow_up(self.language)
        bot_msg = f"{intro}\n\n{follow_up}"
        self._add_bot_message(bot_msg)

        return bot_msg, results

    def add_liked_destination(self, destination_id: int):
        """Record that the user has shown interest in a destination."""
        if destination_id not in self.liked_destinations:
            self.liked_destinations.append(destination_id)

    def get_explanation(self, destination_row: pd.Series) -> str:
        """Generate explanation for a single destination."""
        return generate_recommendation_explanation(
            destination_row, self.preferences, self.language
        )

    def get_history(self) -> list:
        """Return the full conversation history."""
        return self.history

    # ── Private helpers ──────────────────────────────────────────────────────

    def _add_user_message(self, text: str):
        self.history.append({"role": "user", "text": text})

    def _add_bot_message(self, text: str):
        self.history.append({"role": "bot", "text": text})
