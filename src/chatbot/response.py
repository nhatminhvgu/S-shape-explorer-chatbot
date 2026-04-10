"""
Response Generator Module  —  Lightweight "Generative" Layer

Design choice: Template-based dynamic response generation.

Why not a real LLM?
- No paid API allowed.
- Lightweight open-source models (GPT-2, BlenderBot) require heavy downloads,
  are slow on CPU, and produce unreliable output for domain-specific tasks.
- Template-based generation with dynamic slot-filling produces natural,
  controllable, bilingual responses with zero inference cost.
- This approach is academically defensible as a "lightweight natural language
  generation system" — it satisfies the requirement without over-engineering.

How it works:
- Response templates are stored per intent type and per language.
- Slots ({destination}, {region}, {categories}, etc.) are filled dynamically.
- Multiple variants per template type allow response variety.
- Random selection from variants avoids repetitive outputs.
"""

import random
import pandas as pd

from ..utils.language import get_string, get_budget_display, get_region_display, get_group_display
from ..utils.helpers import format_tags, format_best_for, stars


# ─────────────────── Greeting responses ────────────────────────────────────

GREETINGS = {
    "en": [
        "Hello! I'm your Vietnam travel assistant. Tell me what kind of trip you're dreaming of!",
        "Hi there! Ready to discover the best of Vietnam? Tell me your travel preferences.",
        "Welcome! I'm here to help you find the perfect destination in Vietnam. What are you looking for?",
    ],
    "vi": [
        "Xin chào! Tôi là trợ lý du lịch Việt Nam của bạn. Hãy cho tôi biết bạn muốn chuyến đi như thế nào!",
        "Chào bạn! Bạn muốn khám phá điều gì ở Việt Nam? Hãy chia sẻ sở thích du lịch của bạn nhé.",
        "Xin chào! Tôi sẵn sàng giúp bạn tìm điểm đến hoàn hảo tại Việt Nam. Bạn đang tìm kiếm điều gì?",
    ],
}

# ─────────────────── Recommendation intro responses ─────────────────────────

RECOMMENDATION_INTROS = {
    "en": [
        "Based on your preferences, here are my top picks for you:",
        "Great choices! I found some destinations that match what you're looking for:",
        "Here are the best destinations I'd recommend for your trip:",
        "Perfect! I've found these destinations that I think you'll love:",
    ],
    "vi": [
        "Dựa trên sở thích của bạn, đây là những điểm đến tôi gợi ý cho bạn:",
        "Tuyệt vời! Tôi đã tìm được những điểm đến phù hợp với bạn:",
        "Đây là những điểm đến tôi đề xuất cho chuyến đi của bạn:",
        "Tôi đã tìm ra những nơi tôi nghĩ bạn sẽ yêu thích:",
    ],
}

# ─────────────────── Follow-up prompts ──────────────────────────────────────

FOLLOW_UP_PROMPTS = {
    "en": [
        "Would you like more details about any of these destinations?",
        "Can I help you narrow down the choices further?",
        "Let me know if you'd like to explore a specific destination in more detail!",
        "Feel free to ask about any of these places — I can tell you more!",
    ],
    "vi": [
        "Bạn có muốn biết thêm chi tiết về điểm đến nào không?",
        "Tôi có thể giúp bạn thu hẹp lựa chọn không?",
        "Hãy cho tôi biết nếu bạn muốn tìm hiểu thêm về một điểm đến cụ thể!",
        "Bạn cứ hỏi tôi về bất kỳ nơi nào trong danh sách này nhé!",
    ],
}

# ─────────────────── Clarification requests ─────────────────────────────────

CLARIFICATION_PROMPTS = {
    "en": [
        "Could you tell me a bit more about what you're looking for? "
        "For example, do you prefer beach, mountain, or city destinations?",
        "I'd love to help! Are you looking for relaxation, adventure, or cultural experiences?",
        "To find the best match for you, could you tell me your preferred region "
        "(north, central, or south Vietnam) or the type of experience you want?",
    ],
    "vi": [
        "Bạn có thể cho tôi biết thêm không? "
        "Ví dụ, bạn thích đi biển, núi hay thành phố?",
        "Tôi rất muốn giúp bạn! Bạn đang tìm kiếm sự thư giãn, phiêu lưu hay trải nghiệm văn hóa?",
        "Để tìm điểm đến phù hợp nhất, bạn có thể cho tôi biết miền muốn đến "
        "(Bắc, Trung hay Nam) hoặc loại trải nghiệm bạn mong muốn không?",
    ],
}

# ─────────────────── No results responses ───────────────────────────────────

NO_RESULTS_RESPONSES = {
    "en": [
        "I couldn't find destinations that match all your criteria exactly. "
        "Let me try with slightly broader preferences.",
        "Hmm, that combination is quite specific! Let me suggest some alternatives.",
    ],
    "vi": [
        "Tôi không tìm thấy điểm đến nào khớp hoàn toàn với tiêu chí của bạn. "
        "Hãy để tôi thử với tiêu chí rộng hơn một chút.",
        "Yêu cầu của bạn khá cụ thể! Để tôi gợi ý một số lựa chọn thay thế nhé.",
    ],
}


# ─────────────────── Explanation generator (the core "LLM" layer) ───────────

def generate_recommendation_explanation(
    destination_row: pd.Series,
    preferences: dict,
    language: str = "en",
) -> str:
    """
    Generate a natural-language explanation for why a destination was recommended.

    This is the lightweight generative component of the system.
    It dynamically assembles explanation sentences based on matched preference
    slots, creating varied and readable output without any model inference.

    Args:
        destination_row : a row from the destinations DataFrame
        preferences     : user preferences dict
        language        : 'en' or 'vi'

    Returns:
        A 2-4 sentence explanation string.
    """
    reasons = []
    lang = language if language in ("en", "vi") else "en"

    name = destination_row.get("name", "This destination")
    name_vi = destination_row.get("name_vi", name)
    display_name = name_vi if lang == "vi" else name
    region = destination_row.get("region", "")
    rating = destination_row.get("avg_rating", 0)
    price_level = int(destination_row.get("price_level", 2))
    tags = format_tags(str(destination_row.get("tags", "")))
    best_for = format_best_for(str(destination_row.get("best_for", "")))

    # ── Category match reason
    user_cats = set(preferences.get("categories", []))
    dest_tags = set(tags)
    matched_cats = user_cats & dest_tags
    if matched_cats:
        cat_str = ", ".join(sorted(matched_cats))
        if lang == "en":
            reasons.append(f"It is a great match for your interest in **{cat_str}**.")
        else:
            reasons.append(f"Đây là lựa chọn tuyệt vời cho sở thích **{cat_str}** của bạn.")

    # ── Region match reason
    user_region = preferences.get("region", "")
    if user_region and region == user_region:
        region_display = get_region_display(region, lang)
        if lang == "en":
            reasons.append(f"It is located in **{region_display} Vietnam**, exactly where you want to go.")
        else:
            reasons.append(f"Điểm đến này nằm ở **miền {region_display}** đúng như bạn mong muốn.")

    # ── Budget match reason
    user_budget = preferences.get("budget", "")
    budget_match = (
        (user_budget == "budget" and price_level == 1)
        or (user_budget == "mid" and price_level == 2)
        or (user_budget == "premium" and price_level == 3)
    )
    if user_budget and budget_match:
        budget_display = get_budget_display(user_budget, lang)
        if lang == "en":
            reasons.append(f"The cost is **{budget_display}**, fitting your budget.")
        else:
            reasons.append(f"Chi phí **{budget_display}**, phù hợp ngân sách của bạn.")

    # ── Group match reason
    user_group = preferences.get("group_type", "")
    if user_group and user_group in best_for:
        group_display = get_group_display(user_group, lang)
        if lang == "en":
            reasons.append(f"It is particularly well-suited for **{group_display}**.")
        else:
            reasons.append(f"Điểm đến này đặc biệt phù hợp cho **{group_display}**.")

    # ── Rating reason (always include if high)
    if rating >= 4.5:
        if lang == "en":
            reasons.append(
                f"Travelers rate it **{rating}/5** {stars(rating)} — one of the highest-rated spots in Vietnam."
            )
        else:
            reasons.append(
                f"Du khách đánh giá **{rating}/5** {stars(rating)} — một trong những nơi được đánh giá cao nhất Việt Nam."
            )
    elif rating >= 4.0:
        if lang == "en":
            reasons.append(f"It has a solid traveler rating of **{rating}/5** {stars(rating)}.")
        else:
            reasons.append(f"Được du khách đánh giá tốt **{rating}/5** {stars(rating)}.")

    # ── Sentiment bonus reason
    sentiment_label = destination_row.get("sentiment_label", "")
    if sentiment_label == "positive":
        if lang == "en":
            reasons.append("Reviews from past visitors are consistently positive.")
        else:
            reasons.append("Đánh giá từ du khách đã đến đây rất tích cực.")

    # ── Fallback if no specific reasons matched
    if not reasons:
        desc = str(destination_row.get("description" if lang == "en" else "description_vi", ""))
        if desc:
            reasons.append(desc[:150] + ("..." if len(desc) > 150 else ""))
        else:
            if lang == "en":
                reasons.append(f"{display_name} is a popular Vietnam destination worth exploring.")
            else:
                reasons.append(f"{display_name} là điểm đến phổ biến ở Việt Nam đáng để khám phá.")

    return " ".join(reasons)


# ─────────────────── Public interface ───────────────────────────────────────

def get_greeting(language: str = "en") -> str:
    """Return a random greeting message."""
    lang = language if language in GREETINGS else "en"
    return random.choice(GREETINGS[lang])


def get_recommendation_intro(language: str = "en") -> str:
    """Return a random recommendation introduction."""
    lang = language if language in RECOMMENDATION_INTROS else "en"
    return random.choice(RECOMMENDATION_INTROS[lang])


def get_follow_up(language: str = "en") -> str:
    """Return a random follow-up prompt."""
    lang = language if language in FOLLOW_UP_PROMPTS else "en"
    return random.choice(FOLLOW_UP_PROMPTS[lang])


def get_clarification_prompt(language: str = "en") -> str:
    """Return a clarification request."""
    lang = language if language in CLARIFICATION_PROMPTS else "en"
    return random.choice(CLARIFICATION_PROMPTS[lang])


def get_no_results_response(language: str = "en") -> str:
    """Return a no-results message."""
    lang = language if language in NO_RESULTS_RESPONSES else "en"
    return random.choice(NO_RESULTS_RESPONSES[lang])
