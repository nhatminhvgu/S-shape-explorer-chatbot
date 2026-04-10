"""
app.py  —  Bilingual Vietnam Travel Recommendation Chatbot
Streamlit entry point.

Run with:  streamlit run app.py
"""

import os
import sys
import streamlit as st
import pandas as pd

# Make sure src/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from src.data_processing.loader import load_all
from src.data_processing.sentiment import add_sentiment_scores
from src.recommender.hybrid import HybridRecommender
from src.chatbot.conversation import ConversationManager
from src.utils.language import get_string
from src.utils.helpers import format_tags, format_best_for, price_level_label, region_label, stars


# ─────────────────────────────── Page config ────────────────────────────────

st.set_page_config(
    page_title="Vietnam Travel Chatbot",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────── Custom CSS ──────────────────────────────────

st.markdown("""
<style>
.dest-card {
    background: #f8f9fa;
    border-left: 4px solid #e63946;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.dest-card h3 { margin: 0 0 6px 0; color: #1d3557; }
.dest-card .tags span {
    background: #457b9d; color: white;
    border-radius: 12px; padding: 2px 10px;
    font-size: 0.78em; margin-right: 4px;
}
.why-box {
    background: #eaf4fb; border-radius: 6px;
    padding: 8px 12px; font-size: 0.9em;
    margin-top: 8px; color: #1d3557;
}
.user-bubble {
    background: #457b9d; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px; margin: 6px 0 6px 60px;
    display: inline-block; max-width: 80%;
}
.bot-bubble {
    background: #f1faee; color: #1d3557;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 16px; margin: 6px 60px 6px 0;
    display: inline-block; max-width: 80%;
    border: 1px solid #a8dadc;
}
.chat-wrap { padding: 8px 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── Data & model loading ────────────────────────────

@st.cache_resource(show_spinner="Loading data and building recommendation models...")
def load_models():
    """Load data and fit the hybrid recommender — cached for the session."""
    destinations, reviews, ratings = load_all()
    destinations = add_sentiment_scores(destinations, reviews)
    recommender = HybridRecommender()
    recommender.fit(destinations, ratings)
    return destinations, reviews, ratings, recommender


# ─────────────────────────── Session state init ──────────────────────────────

def init_session():
    defaults = {
        "language": "en",
        "messages": [],
        "preferences": {
            "categories": [], "region": "", "budget": "",
            "group_type": "", "travel_style": [], "trip_duration": "",
        },
        "results": None,
        "greeted": False,
        "conversation": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────── UI helpers ─────────────────────────────────────

def add_message(role: str, text: str):
    st.session_state.messages.append({"role": role, "text": text})


def render_chat():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-wrap"><div class="user-bubble">{msg["text"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-wrap"><div class="bot-bubble">{msg["text"]}</div></div>',
                unsafe_allow_html=True,
            )


def render_destination_card(row: pd.Series, explanation: str, lang: str, rank: int):
    name = row.get("name_vi", row["name"]) if lang == "vi" else row["name"]
    description = (
        row.get("description_vi", "") if lang == "vi" else row.get("description", "")
    )
    tags = format_tags(str(row.get("tags", "")))
    best_for_list = format_best_for(str(row.get("best_for", "")))
    rating = float(row.get("avg_rating", 0))
    price = int(row.get("price_level", 2))
    region_code = str(row.get("region", ""))

    tag_html = "".join(f"<span>{t}</span>" for t in tags)
    best_for_str = ", ".join(best_for_list)
    price_str = price_level_label(price, lang)
    region_str = region_label(region_code, lang)

    st.markdown(f"""
<div class="dest-card">
  <h3>#{rank} — {name} &nbsp; {stars(rating)} {rating}/5</h3>
  <p style="color:#555; margin:4px 0;">{str(description)[:200]}{"..." if len(str(description))>200 else ""}</p>
  <p>
    <strong>{get_string("card_region", lang)}:</strong> {region_str} &nbsp;|&nbsp;
    <strong>{get_string("card_price", lang)}:</strong> {price_str} &nbsp;|&nbsp;
    <strong>{get_string("card_best_for", lang)}:</strong> {best_for_str}
  </p>
  <div class="tags">{tag_html}</div>
  <div class="why-box"><strong>{get_string("card_why", lang)}:</strong> {explanation}</div>
</div>
""", unsafe_allow_html=True)


def build_sidebar_preferences(lang: str) -> dict:
    cat_options = {
        get_string("cat_beach", lang): "beach",
        get_string("cat_mountain", lang): "mountain",
        get_string("cat_city", lang): "city",
        get_string("cat_culture", lang): "culture",
        get_string("cat_food", lang): "food",
        get_string("cat_nature", lang): "nature",
        get_string("cat_historical", lang): "historical",
        get_string("cat_adventure", lang): "adventure",
        get_string("cat_relaxation", lang): "relaxation",
    }
    selected_cat_labels = st.multiselect(
        get_string("pref_categories", lang), list(cat_options.keys()), key="sb_cats"
    )
    categories = [cat_options[l] for l in selected_cat_labels]

    region_options = {
        get_string("region_any", lang): "",
        get_string("region_north", lang): "north",
        get_string("region_central", lang): "central",
        get_string("region_south", lang): "south",
    }
    region = region_options[
        st.selectbox(get_string("pref_region", lang), list(region_options.keys()), key="sb_region")
    ]

    budget_options = {
        get_string("budget_any", lang): "",
        get_string("budget_low", lang): "budget",
        get_string("budget_mid", lang): "mid",
        get_string("budget_high", lang): "premium",
    }
    budget = budget_options[
        st.selectbox(get_string("pref_budget", lang), list(budget_options.keys()), key="sb_budget")
    ]

    group_options = {
        "—": "",
        get_string("group_solo", lang): "solo",
        get_string("group_couple", lang): "couple",
        get_string("group_family", lang): "family",
        get_string("group_friends", lang): "friends",
    }
    group_type = group_options[
        st.selectbox(get_string("pref_group", lang), list(group_options.keys()), key="sb_group")
    ]

    style_options = {
        get_string("style_relax", lang): "relaxation",
        get_string("style_adventure", lang): "adventure",
        get_string("style_sightseeing", lang): "sightseeing",
    }
    selected_style_labels = st.multiselect(
        get_string("pref_style", lang), list(style_options.keys()), key="sb_style"
    )
    travel_style = [style_options[l] for l in selected_style_labels]

    duration_options = {
        get_string("duration_any", lang): "",
        get_string("duration_short", lang): "short",
        get_string("duration_long", lang): "long",
    }
    trip_duration = duration_options[
        st.selectbox(
            get_string("pref_duration", lang), list(duration_options.keys()), key="sb_duration"
        )
    ]

    return {
        "categories": categories,
        "region": region,
        "budget": budget,
        "group_type": group_type,
        "travel_style": travel_style,
        "trip_duration": trip_duration,
    }


# ─────────────────────────────── Main ────────────────────────────────────────

def main():
    init_session()
    *_, recommender = load_models()

    # Language toggle — top right
    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
        lang_choice = st.radio(
            "Lang",
            options=["English", "Tiếng Việt"],
            index=0 if st.session_state.language == "en" else 1,
            horizontal=True,
            key="lang_radio",
            label_visibility="collapsed",
        )
        new_lang = "en" if lang_choice == "English" else "vi"
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            if st.session_state.conversation:
                st.session_state.conversation.set_language(new_lang)

    lang = st.session_state.language

    with top_col1:
        st.title(get_string("app_title", lang))
        st.caption(get_string("app_subtitle", lang))

    # Init conversation manager once
    if st.session_state.conversation is None:
        st.session_state.conversation = ConversationManager(recommender, lang)
    conv: ConversationManager = st.session_state.conversation
    conv.set_language(lang)

    # Sidebar
    with st.sidebar:
        st.header(get_string("sidebar_header", lang))
        sidebar_prefs = build_sidebar_preferences(lang)
        st.divider()
        btn_recommend = st.button(
            get_string("btn_recommend", lang), type="primary", use_container_width=True
        )
        btn_clear = st.button(get_string("btn_clear", lang), use_container_width=True)
        st.divider()
        st.caption(
            "📊 30 destinations · 60 reviews · Hybrid CBF+CF+Sentiment"
            if lang == "en"
            else "📊 30 điểm đến · 60 đánh giá · CBF+CF+Phân tích cảm xúc"
        )

    # Clear handler
    if btn_clear:
        st.session_state.messages = []
        st.session_state.results = None
        st.session_state.greeted = False
        conv.reset()
        conv.set_language(lang)
        st.rerun()

    # Greeting (once)
    if not st.session_state.greeted:
        greeting = conv.get_greeting()
        add_message("bot", greeting)
        add_message("bot", get_string("greeting_followup", lang))
        st.session_state.greeted = True

    # Two-column layout
    chat_col, result_col = st.columns([1, 1], gap="large")

    # ── Chat column
    with chat_col:
        st.subheader(get_string("chat_header", lang))
        render_chat()

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "msg",
                placeholder=get_string("placeholder", lang),
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Send ➤" if lang == "en" else "Gửi ➤")

        if submitted and user_input.strip():
            add_message("user", user_input)
            with st.spinner(get_string("thinking", lang)):
                bot_msg, results = conv.process_turn(user_input, sidebar_prefs)
            add_message("bot", bot_msg)
            if results is not None:
                st.session_state.results = results
            st.rerun()

    # ── Sidebar recommend button
    if btn_recommend:
        has_any = any([
            sidebar_prefs["categories"], sidebar_prefs["region"],
            sidebar_prefs["budget"], sidebar_prefs["group_type"],
            sidebar_prefs["travel_style"], sidebar_prefs["trip_duration"],
        ])
        if not has_any:
            add_message("bot", get_string("no_preferences", lang))
        else:
            with st.spinner(get_string("thinking", lang)):
                bot_msg, results = conv.process_sidebar_request(sidebar_prefs)
            add_message("bot", bot_msg)
            if results is not None:
                st.session_state.results = results
        st.rerun()

    # ── Results column
    with result_col:
        st.subheader(get_string("results_header", lang))
        if st.session_state.results is not None:
            st.markdown(f"*{get_string('results_intro', lang)}*")
            for rank, (_, row) in enumerate(st.session_state.results.iterrows(), start=1):
                explanation = conv.get_explanation(row)
                render_destination_card(row, explanation, lang, rank)
        else:
            st.info(
                "Your recommendations will appear here."
                if lang == "en"
                else "Gợi ý của bạn sẽ xuất hiện ở đây."
            )


if __name__ == "__main__":
    main()
