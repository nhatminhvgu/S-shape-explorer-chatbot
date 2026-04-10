"""
Intent Recognition Module

Rule-based intent extraction from natural language user input.
Supports both English and Vietnamese via keyword mapping tables.

Extracted slots:
    categories    : list of matched interest categories
    region        : 'north' | 'central' | 'south' | ''
    budget        : 'budget' | 'mid' | 'premium' | ''
    group_type    : 'solo' | 'couple' | 'family' | 'friends' | ''
    travel_style  : list of matched styles
    trip_duration : 'short' | 'long' | ''

This approach is transparent, fast, and requires no model downloads —
academically appropriate for a student-level NLP implementation.
"""

import re
from typing import Dict, List


# ─────────────────────────────── Keyword tables ────────────────────────────

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "beach": [
        "beach", "sea", "ocean", "coast", "island", "snorkel", "dive", "diving",
        "swimming", "surf", "surfing", "sandy",
        "biển", "bãi biển", "đảo", "lặn biển", "bơi lội", "lướt sóng",
    ],
    "mountain": [
        "mountain", "hill", "trek", "trekking", "hiking", "hike", "peak",
        "summit", "valley", "highland", "altitude",
        "núi", "leo núi", "đồi", "trekking", "đỉnh núi", "thung lũng", "miền núi",
    ],
    "city": [
        "city", "urban", "street", "market", "shopping", "nightlife", "downtown",
        "metropolitan",
        "thành phố", "phố", "chợ", "mua sắm", "đêm", "đô thị",
    ],
    "culture": [
        "culture", "cultural", "tradition", "temple", "pagoda", "museum",
        "village", "ethnic", "heritage", "art", "craft",
        "văn hóa", "truyền thống", "đền", "chùa", "bảo tàng", "làng", "dân tộc",
    ],
    "food": [
        "food", "cuisine", "eat", "eating", "restaurant", "street food",
        "local food", "dish", "dishes", "cooking", "culinary", "taste",
        "ăn", "ẩm thực", "món ăn", "nhà hàng", "đồ ăn", "ăn uống", "thưởng thức",
    ],
    "nature": [
        "nature", "forest", "park", "wildlife", "lake", "waterfall", "cave",
        "jungle", "eco", "green", "scenic", "landscape",
        "thiên nhiên", "rừng", "công viên", "hồ", "thác nước", "hang động",
        "suối", "cảnh", "sinh thái",
    ],
    "historical": [
        "history", "historical", "ancient", "heritage", "ruin", "ruins",
        "war", "monument", "historic", "old town", "dynasty",
        "lịch sử", "cổ", "di sản", "tàn tích", "chiến tranh", "đài tưởng niệm",
        "phố cổ", "triều đại",
    ],
    "adventure": [
        "adventure", "extreme", "zip line", "kayak", "kayaking", "rafting",
        "rock climbing", "motorbike", "offroad", "backpack",
        "phiêu lưu", "mạo hiểm", "chèo thuyền", "leo núi đá", "xe máy",
    ],
    "relaxation": [
        "relax", "relaxing", "relaxation", "peaceful", "quiet", "calm",
        "spa", "resort", "chill", "rest", "unwind", "tranquil",
        "thư giãn", "nghỉ ngơi", "bình yên", "yên tĩnh", "spa", "resort",
    ],
}

REGION_KEYWORDS: Dict[str, List[str]] = {
    "north": [
        "north", "northern", "hanoi", "ha noi", "ha long", "halong", "sapa",
        "sa pa", "ha giang", "ninh binh", "bac",
        "bắc", "miền bắc", "hà nội", "hạ long", "sa pa", "hà giang", "ninh bình",
    ],
    "central": [
        "central", "da nang", "danang", "hoi an", "hoian", "hue", "nha trang",
        "phong nha", "quy nhon",
        "trung", "miền trung", "đà nẵng", "hội an", "huế", "nha trang",
        "phong nha", "quy nhơn",
    ],
    "south": [
        "south", "southern", "ho chi minh", "saigon", "sai gon", "phu quoc",
        "da lat", "dalat", "mekong", "vung tau", "can tho",
        "nam", "miền nam", "hồ chí minh", "sài gòn", "phú quốc", "đà lạt",
        "mekong", "vũng tàu", "cần thơ",
    ],
}

BUDGET_KEYWORDS: Dict[str, List[str]] = {
    # 'mid' is checked first so "medium budget" maps here, not to 'budget'
    "mid": [
        "mid", "middle", "moderate", "reasonable", "average", "mid range",
        "medium", "medium budget", "standard",
        "tầm trung", "vừa phải", "phải chăng", "trung bình",
    ],
    "budget": [
        "cheap", "affordable", "low cost", "backpacker",
        "economical", "inexpensive", "low budget", "on a budget",
        "rẻ", "tiết kiệm", "giá rẻ", "bụi đời", "bình dân", "ít tiền",
    ],
    "premium": [
        "luxury", "premium", "expensive", "high end", "upscale", "5 star",
        "five star", "fancy",
        "sang trọng", "cao cấp", "đắt tiền", "hạng sang", "5 sao",
    ],
}

GROUP_KEYWORDS: Dict[str, List[str]] = {
    "solo": [
        "solo", "alone", "myself", "by myself", "backpacking", "single traveler",
        "một mình", "solo", "du lịch một mình",
    ],
    "couple": [
        "couple", "partner", "romantic", "honeymoon", "anniversary",
        "boyfriend", "girlfriend", "husband", "wife",
        "cặp đôi", "vợ chồng", "lãng mạn", "trăng mật", "bạn trai", "bạn gái",
    ],
    "family": [
        "family", "kids", "children", "parents", "grandparents",
        "child friendly", "family friendly",
        "gia đình", "trẻ em", "con cái", "bố mẹ", "ông bà",
    ],
    "friends": [
        "friends", "group", "gang", "crew", "mates", "squad",
        "bạn bè", "nhóm bạn", "hội bạn", "cả nhóm", "đám bạn",
    ],
}

TRAVEL_STYLE_KEYWORDS: Dict[str, List[str]] = {
    "relaxation": [
        "relax", "relaxing", "peaceful", "quiet", "calm", "rest", "chill",
        "thư giãn", "nghỉ ngơi", "bình yên",
    ],
    "adventure": [
        "adventure", "active", "extreme", "sport", "outdoor", "thrill",
        "phiêu lưu", "mạo hiểm", "thể thao", "ngoài trời",
    ],
    "sightseeing": [
        "sightseeing", "tour", "explore", "visit", "landmark", "tourist",
        "see", "discover",
        "tham quan", "khám phá", "du lịch", "điểm đến", "thắng cảnh",
    ],
}

DURATION_KEYWORDS: Dict[str, List[str]] = {
    "short": [
        "short", "weekend", "1 day", "2 day", "2 days", "quick", "day trip",
        "ngắn", "cuối tuần", "1 ngày", "2 ngày", "nhanh",
    ],
    "long": [
        "long", "week", "month", "extended", "slow travel", "multiple days",
        "dài", "một tuần", "nhiều ngày", "dài ngày",
    ],
}


# ─────────────────────────── Helper function ────────────────────────────────

def _match_keywords(text: str, keyword_map: Dict[str, List[str]]) -> list:
    """Return all keys whose keyword list has at least one match in text."""
    text_lower = text.lower()
    matches = []
    for key, keywords in keyword_map.items():
        for kw in keywords:
            # Use word boundary matching for single words
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_lower):
                matches.append(key)
                break
    return matches


def _match_first(text: str, keyword_map: Dict[str, List[str]]) -> str:
    """Return the first key that matches in text, or empty string."""
    matches = _match_keywords(text, keyword_map)
    return matches[0] if matches else ""


# ─────────────────────────── Main extractor ─────────────────────────────────

def extract_preferences(user_text: str) -> dict:
    """
    Extract travel preference slots from free-form user input.

    Args:
        user_text: raw text from the user (English or Vietnamese)

    Returns:
        dict with keys: categories, region, budget, group_type,
                        travel_style, trip_duration
    """
    categories = _match_keywords(user_text, CATEGORY_KEYWORDS)
    region = _match_first(user_text, REGION_KEYWORDS)
    budget = _match_first(user_text, BUDGET_KEYWORDS)
    group_type = _match_first(user_text, GROUP_KEYWORDS)
    travel_style = _match_keywords(user_text, TRAVEL_STYLE_KEYWORDS)
    trip_duration = _match_first(user_text, DURATION_KEYWORDS)

    return {
        "categories": categories,
        "region": region,
        "budget": budget,
        "group_type": group_type,
        "travel_style": travel_style,
        "trip_duration": trip_duration,
    }


def merge_preferences(existing: dict, new_extract: dict) -> dict:
    """
    Merge newly extracted preferences into existing ones.
    New values override existing ones; empty new values are ignored.
    """
    merged = existing.copy()

    if new_extract.get("categories"):
        merged["categories"] = new_extract["categories"]
    if new_extract.get("region"):
        merged["region"] = new_extract["region"]
    if new_extract.get("budget"):
        merged["budget"] = new_extract["budget"]
    if new_extract.get("group_type"):
        merged["group_type"] = new_extract["group_type"]
    if new_extract.get("travel_style"):
        merged["travel_style"] = new_extract["travel_style"]
    if new_extract.get("trip_duration"):
        merged["trip_duration"] = new_extract["trip_duration"]

    return merged


def has_enough_preferences(preferences: dict) -> bool:
    """
    Check whether we have enough slots filled to make a recommendation.
    Requires at least one of: categories, region, travel_style.
    """
    return bool(
        preferences.get("categories")
        or preferences.get("region")
        or preferences.get("travel_style")
        or preferences.get("group_type")
    )
