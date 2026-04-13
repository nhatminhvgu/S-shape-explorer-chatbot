"""
Bilingual Language Utility
Stores all UI strings in English and Vietnamese.
Usage: get_string('key', 'en') or get_string('key', 'vi')
"""

STRINGS = {
    "en": {
        # Vietnamese-mode notice (shown when user switches to Vietnamese)
        "vi_notice": (
            "ℹ️ **Note:** Due to cost constraints, all recommendations are displayed in English. "
            "Please copy any text and paste it into **Google Translate** to read in Vietnamese. Thank you!"
        ),

        # App title and headers
        "app_title": "Vietnam Travel Chatbot",
        "app_subtitle": "Your personalized Vietnam travel guide",
        "sidebar_header": "Travel Preferences",
        "chat_header": "Chat with your travel assistant",
        "results_header": "Recommended Destinations",

        # Language selector
        "language_label": "Language / Ngôn ngữ",

        # Sidebar preference labels
        "pref_categories": "What interests you?",
        "pref_region": "Preferred region",
        "pref_budget": "Budget level",
        "pref_group": "Traveling as",
        "pref_style": "Travel style",
        "pref_duration": "Trip duration",
        "btn_recommend": "Get Recommendations",
        "btn_clear": "Clear Chat",

        # Category options
        "cat_beach": "Beach",
        "cat_mountain": "Mountain",
        "cat_city": "City",
        "cat_culture": "Culture",
        "cat_food": "Food",
        "cat_nature": "Nature",
        "cat_historical": "Historical",
        "cat_adventure": "Adventure",
        "cat_relaxation": "Relaxation",

        # Region options
        "region_any": "Anywhere in Vietnam",
        "region_north": "North Vietnam",
        "region_central": "Central Vietnam",
        "region_south": "South Vietnam",

        # Budget options
        "budget_any": "Any budget",
        "budget_low": "Budget (affordable)",
        "budget_mid": "Mid-range",
        "budget_high": "Premium",

        # Group options
        "group_solo": "Solo",
        "group_couple": "Couple",
        "group_family": "Family",
        "group_friends": "Friends / Group",

        # Style options
        "style_relax": "Relaxation",
        "style_adventure": "Adventure",
        "style_sightseeing": "Sightseeing",

        # Duration options
        "duration_any": "Flexible",
        "duration_short": "Short trip (1-3 days)",
        "duration_long": "Long trip (4+ days)",

        # Chat messages
        "greeting": (
            "Hello! I am your Vietnam travel assistant. "
            "Tell me what kind of trip you are looking for, or use the "
            "preferences panel on the left and click **Get Recommendations**."
        ),
        "greeting_followup": (
            "You can describe your ideal trip in your own words, for example: "
            '*"I want beaches in central Vietnam with a medium budget"* or '
            '*"adventure trip in the north for a group of friends"*.'
        ),
        "thinking": "Finding the best destinations for you...",
        "no_results": "I could not find destinations matching your criteria. Try broader preferences.",
        "ask_more": "Would you like more details about any of these destinations?",
        "placeholder": "Type your travel preferences here...",
        "results_intro": "Here are my top recommendations for you:",
        "no_preferences": (
            "Please tell me your travel preferences — for example, what region, "
            "budget, or type of experience you are looking for."
        ),
        "clarify_prompt": "Could you tell me a bit more about what you are looking for?",

        # Destination card labels
        "card_rating": "Rating",
        "card_region": "Region",
        "card_price": "Price level",
        "card_best_for": "Best for",
        "card_duration": "Trip duration",
        "card_tags": "Tags",
        "card_why": "Why recommended",
        "price_1": "Budget-friendly",
        "price_2": "Mid-range",
        "price_3": "Premium",

        # Recommendation explanation templates
        "why_category": "Matches your interest in {categories}.",
        "why_region": "Located in {region} Vietnam as you requested.",
        "why_rating": "Highly rated by travelers ({rating}/5).",
        "why_budget": "Fits your {budget} budget.",
        "why_group": "Great destination for {group}.",
        "why_sentiment": "Reviews are overwhelmingly positive.",
    },

    "vi": {
        # Vietnamese-mode notice
        "vi_notice": (
            "ℹ️ **Lưu ý:** Vì vấn đề chi phí, nội dung gợi ý vẫn hiển thị bằng tiếng Anh. "
            "Bạn hãy copy nội dung và dán vào **Google Dịch** để đọc tiếng Việt. Xin cám ơn! 🙏"
        ),

        # App title and headers
        "app_title": "Chatbot Du Lịch Việt Nam",
        "app_subtitle": "Hướng dẫn du lịch Việt Nam cá nhân hóa cho bạn",
        "sidebar_header": "Sở Thích Du Lịch",
        "chat_header": "Trò chuyện với trợ lý du lịch",
        "results_header": "Điểm Đến Được Đề Xuất",

        # Language selector
        "language_label": "Language / Ngôn ngữ",

        # Sidebar preference labels
        "pref_categories": "Bạn quan tâm điều gì?",
        "pref_region": "Miền muốn đến",
        "pref_budget": "Ngân sách",
        "pref_group": "Đi cùng ai",
        "pref_style": "Phong cách du lịch",
        "pref_duration": "Thời gian chuyến đi",
        "btn_recommend": "Tìm Điểm Đến",
        "btn_clear": "Xóa Hội Thoại",

        # Category options
        "cat_beach": "Biển",
        "cat_mountain": "Núi",
        "cat_city": "Thành phố",
        "cat_culture": "Văn hóa",
        "cat_food": "Ẩm thực",
        "cat_nature": "Thiên nhiên",
        "cat_historical": "Lịch sử",
        "cat_adventure": "Phiêu lưu",
        "cat_relaxation": "Thư giãn",

        # Region options
        "region_any": "Cả Việt Nam",
        "region_north": "Miền Bắc",
        "region_central": "Miền Trung",
        "region_south": "Miền Nam",

        # Budget options
        "budget_any": "Mọi mức ngân sách",
        "budget_low": "Tiết kiệm (giá rẻ)",
        "budget_mid": "Tầm trung",
        "budget_high": "Cao cấp",

        # Group options
        "group_solo": "Một mình",
        "group_couple": "Cặp đôi",
        "group_family": "Gia đình",
        "group_friends": "Bạn bè / Nhóm",

        # Style options
        "style_relax": "Thư giãn",
        "style_adventure": "Phiêu lưu",
        "style_sightseeing": "Tham quan",

        # Duration options
        "duration_any": "Linh hoạt",
        "duration_short": "Chuyến ngắn (1-3 ngày)",
        "duration_long": "Chuyến dài (4+ ngày)",

        # Chat messages
        "greeting": (
            "Xin chào! Tôi là trợ lý du lịch Việt Nam của bạn. "
            "Hãy cho tôi biết bạn muốn chuyến đi như thế nào, hoặc dùng bảng "
            "sở thích bên trái và nhấn **Tìm Điểm Đến**."
        ),
        "greeting_followup": (
            "Bạn có thể mô tả chuyến đi lý tưởng theo cách của mình, ví dụ: "
            '*"Tôi muốn đi biển ở miền Trung với ngân sách tầm trung"* hoặc '
            '*"Chuyến phiêu lưu ở miền Bắc cùng nhóm bạn"*.'
        ),
        "thinking": "Đang tìm kiếm những điểm đến tốt nhất cho bạn...",
        "no_results": "Tôi không tìm thấy điểm đến phù hợp. Hãy thử mở rộng tiêu chí tìm kiếm.",
        "ask_more": "Bạn có muốn biết thêm chi tiết về điểm đến nào không?",
        "placeholder": "Nhập sở thích du lịch của bạn...",
        "results_intro": "Đây là những gợi ý hàng đầu của tôi cho bạn:",
        "no_preferences": (
            "Bạn hãy cho tôi biết sở thích du lịch nhé — ví dụ miền nào, "
            "ngân sách bao nhiêu, hay loại trải nghiệm gì bạn muốn."
        ),
        "clarify_prompt": "Bạn có thể cho tôi biết thêm về điều bạn đang tìm kiếm không?",

        # Destination card labels
        "card_rating": "Đánh giá",
        "card_region": "Khu vực",
        "card_price": "Mức giá",
        "card_best_for": "Phù hợp nhất với",
        "card_duration": "Thời gian đi",
        "card_tags": "Loại hình",
        "card_why": "Lý do gợi ý",
        "price_1": "Tiết kiệm",
        "price_2": "Tầm trung",
        "price_3": "Cao cấp",

        # Recommendation explanation templates
        "why_category": "Phù hợp với sở thích {categories} của bạn.",
        "why_region": "Tọa lạc ở miền {region} như bạn yêu cầu.",
        "why_rating": "Được khách du lịch đánh giá cao ({rating}/5).",
        "why_budget": "Phù hợp với ngân sách {budget} của bạn.",
        "why_group": "Điểm đến tuyệt vời cho {group}.",
        "why_sentiment": "Đánh giá từ du khách rất tích cực.",
    }
}

# Maps internal budget codes to display strings
BUDGET_DISPLAY = {
    "en": {"budget": "budget-friendly", "mid": "mid-range", "premium": "premium"},
    "vi": {"budget": "tiết kiệm", "mid": "tầm trung", "premium": "cao cấp"},
}

# Maps internal region codes to display strings
REGION_DISPLAY = {
    "en": {"north": "North", "central": "Central", "south": "South"},
    "vi": {"north": "Bắc", "central": "Trung", "south": "Nam"},
}

# Maps group type codes to display strings
GROUP_DISPLAY = {
    "en": {
        "solo": "solo travelers",
        "couple": "couples",
        "family": "families",
        "friends": "groups of friends",
    },
    "vi": {
        "solo": "khách du lịch một mình",
        "couple": "cặp đôi",
        "family": "gia đình",
        "friends": "nhóm bạn bè",
    },
}


def get_string(key: str, lang: str = "en") -> str:
    """
    Retrieve a UI string by key and language.
    Falls back to English if the key is missing in the target language.
    """
    lang = lang if lang in STRINGS else "en"
    return STRINGS[lang].get(key, STRINGS["en"].get(key, f"[{key}]"))


def get_budget_display(budget_code: str, lang: str = "en") -> str:
    """Return display string for a budget code."""
    return BUDGET_DISPLAY.get(lang, BUDGET_DISPLAY["en"]).get(budget_code, budget_code)


def get_region_display(region_code: str, lang: str = "en") -> str:
    """Return display string for a region code."""
    return REGION_DISPLAY.get(lang, REGION_DISPLAY["en"]).get(region_code, region_code)


def get_group_display(group_code: str, lang: str = "en") -> str:
    """Return display string for a group type code."""
    return GROUP_DISPLAY.get(lang, GROUP_DISPLAY["en"]).get(group_code, group_code)
