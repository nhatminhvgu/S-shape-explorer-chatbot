#!/usr/bin/env python3
"""
build_dataset.py
================
Converts a raw Kaggle Vietnam-tourism CSV into the three CSVs that the
S-Shape Explorer chatbot expects:

    data/destinations.csv   — 30-N destination rows
    data/reviews.csv        — 2 synthetic reviews per destination
    data/ratings.csv        — empty header only  (CF is disabled)

Usage
-----
    python scripts/build_dataset.py --input data/raw/<your_kaggle_file>.csv

Options
-------
    --input   PATH   Path to the Kaggle CSV file            (required)
    --max     INT    Maximum destinations to keep           (default: 60)
    --out_dir PATH   Folder for output CSVs                 (default: data/)

The script auto-detects column names using common aliases so it should work
with most Vietnam-tourism Kaggle datasets without manual edits.

Design choices applied
----------------------
  Issue 2 — price_level:   any source scale → 1 (budget) / 2 (mid) / 3 (premium)
  Issue 3 — tags/category: rule-based keyword matching on name + description
  Issue 4 — best_for/trip_duration: rule-based from primary_category
  Issue 5 — CF disabled:   ratings.csv is written with headers only
  Issue 6 — sentiment:     derived from rating (>=4 positive, 3 neutral, <3 negative)
"""

import argparse
import os
import sys
import re
import random
import pandas as pd

random.seed(42)

# ──────────────────────────────────────────────────────────────────────────────
# REGION MAPPING
# ──────────────────────────────────────────────────────────────────────────────

NORTH_KEYWORDS = [
    'ha noi', 'hanoi', 'ha giang', 'cao bang', 'bac kan', 'lang son',
    'tuyen quang', 'thai nguyen', 'quang ninh', 'bac giang', 'phu tho',
    'lao cai', 'yen bai', 'son la', 'dien bien', 'lai chau', 'hoa binh',
    'bac ninh', 'ha nam', 'hung yen', 'hai duong', 'hai phong',
    'thai binh', 'nam dinh', 'ninh binh', 'vinh phuc',
    'thanh hoa', 'nghe an', 'ha tinh',
    # popular destinations
    'moc chau', 'sa pa', 'sapa', 'ha long', 'ba be', 'mai chau',
    'bai tu long', 'cao bang', 'ba vi',
]

CENTRAL_KEYWORDS = [
    'quang binh', 'quang tri', 'thua thien', 'hue',
    'da nang', 'quang nam', 'quang ngai',
    'binh dinh', 'phu yen', 'khanh hoa',
    'ninh thuan', 'binh thuan',
    'gia lai', 'kon tum', 'dak lak', 'dak nong', 'lam dong',
    # popular destinations
    'da lat', 'dalat', 'nha trang', 'hoi an', 'phong nha',
    'my son', 'lang co', 'quy nhon', 'ba na', 'bach ma',
]

SOUTH_KEYWORDS = [
    'ho chi minh', 'saigon', 'dong nai', 'binh duong', 'ba ria',
    'vung tau', 'tay ninh', 'binh phuoc', 'long an', 'tien giang',
    'ben tre', 'tra vinh', 'vinh long', 'dong thap', 'an giang',
    'kien giang', 'can tho', 'hau giang', 'soc trang', 'bac lieu', 'ca mau',
    # popular destinations
    'phu quoc', 'con dao', 'mekong', 'mui ne', 'cu chi', 'cat tien',
    'can tho', 'vung tau',
]


def detect_region(text: str) -> str:
    """Map any location / name string to north / central / south."""
    if not isinstance(text, str) or not text.strip():
        return 'central'
    t = text.lower()
    for kw in SOUTH_KEYWORDS:
        if kw in t:
            return 'south'
    for kw in CENTRAL_KEYWORDS:
        if kw in t:
            return 'central'
    for kw in NORTH_KEYWORDS:
        if kw in t:
            return 'north'
    return 'central'


# ──────────────────────────────────────────────────────────────────────────────
# CATEGORY / TAGS  (rule-based, Issue 3-B)
# ──────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    'beach':      ['beach', 'bay', 'island', 'coast', 'sea', 'ocean', 'sand',
                   'coral', 'snorkel', 'dive', 'biển', 'đảo', 'vịnh'],
    'mountain':   ['mountain', 'hill', 'peak', 'highland', 'trek', 'trekking',
                   'pass', 'plateau', 'summit', 'núi', 'đèo', 'cao nguyên'],
    'city':       ['city', 'town', 'urban', 'capital', 'quarter', 'street',
                   'thành phố', 'phố', 'khu phố'],
    'culture':    ['culture', 'cultural', 'ethnic', 'traditional', 'minority',
                   'festival', 'village', 'stilt house', 'văn hóa', 'dân tộc',
                   'truyền thống', 'làng'],
    'food':       ['food', 'cuisine', 'market', 'dish', 'culinary', 'street food',
                   'ẩm thực', 'chợ', 'món ăn', 'đặc sản'],
    'nature':     ['nature', 'national park', 'waterfall', 'lake', 'forest',
                   'wildlife', 'jungle', 'river', 'vườn quốc gia', 'thác',
                   'hồ', 'rừng', 'sông'],
    'historical': ['historic', 'history', 'ancient', 'temple', 'citadel', 'war',
                   'museum', 'ruin', 'heritage', 'lịch sử', 'cổ', 'đền',
                   'thánh địa', 'bảo tàng', 'lăng'],
    'adventure':  ['adventure', 'cave', 'kayak', 'climb', 'diving', 'surfing',
                   'zipline', 'phiêu lưu', 'hang', 'lặn', 'leo'],
    'relaxation': ['resort', 'relax', 'spa', 'peaceful', 'tranquil', 'retreat',
                   'quiet', 'nghỉ dưỡng', 'thư giãn', 'yên bình'],
}

CATEGORY_BEST_FOR = {
    'beach':      'couple|family|friends',
    'mountain':   'solo|friends',
    'city':       'solo|couple|family|friends',
    'culture':    'couple|family|solo',
    'food':       'solo|couple|family|friends',
    'nature':     'family|friends|solo',
    'historical': 'solo|couple|family',
    'adventure':  'solo|friends',
    'relaxation': 'couple|family',
}

CATEGORY_DURATION = {
    'beach':      'short|long',
    'mountain':   'long',
    'city':       'short|long',
    'culture':    'short',
    'food':       'short',
    'nature':     'short|long',
    'historical': 'short',
    'adventure':  'long',
    'relaxation': 'short|long',
}


def classify_destination(name: str, description: str = '', raw_category: str = '') -> dict:
    """Assign primary_category, tags, best_for, trip_duration by keyword rules."""
    combined = (name + ' ' + description + ' ' + raw_category).lower()

    scores = {cat: sum(1 for kw in kws if kw in combined)
              for cat, kws in CATEGORY_KEYWORDS.items()}

    # If raw_category already contains a known category word, boost it
    for cat in CATEGORY_KEYWORDS:
        if cat in raw_category.lower():
            scores[cat] += 3

    primary = max(scores, key=scores.get) if any(scores.values()) else 'nature'

    # Tags = all categories with at least 1 hit, capped at 5, primary first
    tags = sorted([c for c, s in scores.items() if s > 0],
                  key=lambda c: scores[c], reverse=True)[:5]
    if primary not in tags:
        tags.insert(0, primary)
    if not tags:
        tags = [primary]

    return {
        'primary_category': primary,
        'tags':             ','.join(tags),
        'best_for':         CATEGORY_BEST_FOR.get(primary, 'solo|couple|family|friends'),
        'trip_duration':    CATEGORY_DURATION.get(primary, 'short|long'),
    }


# ──────────────────────────────────────────────────────────────────────────────
# PRICE LEVEL  (Issue 2-A: any scale → 1 / 2 / 3)
# ──────────────────────────────────────────────────────────────────────────────

def map_price_level(raw) -> int:
    if pd.isna(raw):
        return 2
    if isinstance(raw, (int, float)):
        v = float(raw)
        if v <= 1:    return 1
        elif v <= 2:  return 2
        else:         return 3
    s = str(raw).lower().strip()
    if any(x in s for x in ['0', '1', 'free', 'budget', 'cheap', 'low', 'afford', '$']):
        return 1
    if any(x in s for x in ['3', '4', 'expens', 'premium', 'luxury', 'high', '$$$']):
        return 3
    if '$$' in s:
        return 2
    return 2


# ──────────────────────────────────────────────────────────────────────────────
# SENTIMENT  (Issue 6-A: from rating)
# ──────────────────────────────────────────────────────────────────────────────

def rating_to_sentiment(rating) -> str:
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return 'neutral'
    if r >= 4.0:  return 'positive'
    if r >= 3.0:  return 'neutral'
    return 'negative'


# ──────────────────────────────────────────────────────────────────────────────
# SYNTHETIC REVIEWS  (2 per destination, derived from rating)
# ──────────────────────────────────────────────────────────────────────────────

POS_REVIEWS = [
    "An incredible destination — absolutely worth the visit. Highly recommend!",
    "One of the highlights of my Vietnam trip. Beautiful scenery and great atmosphere.",
    "Exceeded all my expectations. The experience was memorable and unique.",
    "A must-visit place. Stunning views and welcoming locals.",
    "Wonderful destination with so much to see and do. Would visit again.",
]
NEU_REVIEWS = [
    "A decent destination. Some parts are touristy but still enjoyable overall.",
    "Nice place to visit, though it gets crowded in peak season.",
    "Good experience overall. Worth a half-day trip if you are in the area.",
    "Interesting spot. Not the most dramatic but pleasant enough.",
]
NEG_REVIEWS = [
    "Somewhat disappointing — overhyped compared to the reality.",
    "Not as impressive as photos suggest. Might suit some travellers better.",
]


def make_reviews(dest_id: int, avg_rating: float, review_id_start: int) -> list[dict]:
    """Generate 2 synthetic reviews for a destination."""
    sentiment = rating_to_sentiment(avg_rating)
    pool = POS_REVIEWS if sentiment == 'positive' else (
           NEG_REVIEWS if sentiment == 'negative' else NEU_REVIEWS)
    chosen = random.sample(pool, min(2, len(pool)))
    rows = []
    for i, text in enumerate(chosen):
        rows.append({
            'review_id':      review_id_start + i,
            'destination_id': dest_id,
            'user_id':        (dest_id * 7 + i) % 20 + 1,   # pseudo user 1-20
            'rating':         max(1, min(5, round(avg_rating + random.uniform(-0.5, 0.5)))),
            'review_text':    text,
            'language':       'en',
            'sentiment':      sentiment,
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# COLUMN AUTO-DETECTION
# ──────────────────────────────────────────────────────────────────────────────

COL_ALIASES = {
    'name':        ['name', 'place', 'destination', 'title', 'attraction',
                    'location_name', 'spot', 'placename'],
    'location':    ['province', 'location', 'city', 'address', 'region',
                    'area', 'state', 'district', 'locality'],
    'description': ['description', 'about', 'info', 'detail', 'summary',
                    'overview', 'content', 'text'],
    'rating':      ['rating', 'score', 'stars', 'avg_rating', 'average_rating',
                    'rate', 'avgrating', 'averagerating'],
    'num_reviews': ['num_reviews', 'review_count', 'reviews_count',
                    'total_reviews', 'numreviews', 'reviewcount',
                    'number_of_reviews', 'totalreviews'],
    'price_level': ['price_level', 'price', 'cost', 'budget', 'pricelevel',
                    'price_range'],
    'category':    ['category', 'type', 'kind', 'genre', 'tag', 'tags',
                    'attraction_type'],
}


def find_col(df: pd.DataFrame, field: str) -> str | None:
    """Return the actual column name in df that best matches the field."""
    cols_lower = {c.lower().replace(' ', '_'): c for c in df.columns}
    for alias in COL_ALIASES.get(field, [field]):
        key = alias.lower().replace(' ', '_')
        if key in cols_lower:
            return cols_lower[key]
    # fuzzy: partial containment
    for alias in COL_ALIASES.get(field, [field]):
        for col_key, col_orig in cols_lower.items():
            if alias.lower() in col_key or col_key in alias.lower():
                return col_orig
    return None


# ──────────────────────────────────────────────────────────────────────────────
# MAIN BUILD LOGIC
# ──────────────────────────────────────────────────────────────────────────────

def build(input_path: str, out_dir: str, max_rows: int) -> None:
    print(f"\n[build_dataset] Reading: {input_path}")
    raw = pd.read_csv(input_path, encoding='utf-8', on_bad_lines='skip')
    print(f"[build_dataset] Loaded {len(raw)} rows, columns: {list(raw.columns)}")

    # ── detect columns
    col = {field: find_col(raw, field) for field in COL_ALIASES}
    print("[build_dataset] Column mapping detected:")
    for field, found in col.items():
        print(f"   {field:12s} → {found}")

    missing = [f for f in ['name'] if col[f] is None]
    if missing:
        sys.exit(f"\n[ERROR] Could not find required column(s): {missing}.\n"
                 f"Available columns: {list(raw.columns)}\n"
                 f"Rename the destination-name column to 'name' and retry.")

    # ── deduplicate on name
    name_col = col['name']
    raw = raw.dropna(subset=[name_col])
    raw = raw.drop_duplicates(subset=[name_col]).reset_index(drop=True)

    # ── keep top-N by rating (or just first N)
    rating_col = col['rating']
    if rating_col:
        raw['_rating_num'] = pd.to_numeric(raw[rating_col], errors='coerce').fillna(0)
        raw = raw.sort_values('_rating_num', ascending=False)
    raw = raw.head(max_rows).reset_index(drop=True)
    print(f"[build_dataset] Keeping {len(raw)} destinations after dedup/sort.")

    # ── build destinations rows
    dest_rows = []
    review_rows = []
    review_id_counter = 1

    for idx, row in raw.iterrows():
        dest_id = idx + 1

        name        = str(row[name_col]).strip()
        location    = str(row[col['location']]).strip()  if col['location']    else ''
        description = str(row[col['description']]).strip() if col['description'] else ''
        raw_cat     = str(row[col['category']]).strip()  if col['category']    else ''

        # rating
        avg_rating = 4.0
        if rating_col:
            v = pd.to_numeric(row[rating_col], errors='coerce')
            if not pd.isna(v):
                # normalise: if scale looks like 0-10, divide by 2
                avg_rating = round(float(v) / 2, 1) if float(v) > 5 else round(float(v), 1)
                avg_rating = max(1.0, min(5.0, avg_rating))

        # num_reviews
        num_reviews = 100
        if col['num_reviews']:
            v = pd.to_numeric(row[col['num_reviews']], errors='coerce')
            if not pd.isna(v):
                num_reviews = int(v)

        # price_level
        price_level = map_price_level(row[col['price_level']] if col['price_level'] else None)

        # region
        region = detect_region(location + ' ' + name)

        # category / tags / best_for / trip_duration
        classified = classify_destination(name, description, raw_cat)

        dest_rows.append({
            'id':               dest_id,
            'name':             name,
            'name_vi':          name,          # English kept — popup shown for VI users
            'region':           region,
            'primary_category': classified['primary_category'],
            'tags':             classified['tags'],
            'description':      description if description else f"{name} is a popular destination in Vietnam.",
            'description_vi':   description if description else f"{name} is a popular destination in Vietnam.",
            'price_level':      price_level,
            'avg_rating':       avg_rating,
            'num_reviews':      num_reviews,
            'best_for':         classified['best_for'],
            'trip_duration':    classified['trip_duration'],
        })

        # synthetic reviews
        reviews = make_reviews(dest_id, avg_rating, review_id_counter)
        review_rows.extend(reviews)
        review_id_counter += len(reviews)

    destinations_df = pd.DataFrame(dest_rows)
    reviews_df      = pd.DataFrame(review_rows)
    ratings_df      = pd.DataFrame(columns=['user_id', 'destination_id', 'rating'])  # CF disabled

    # ── write outputs
    os.makedirs(out_dir, exist_ok=True)

    dest_path    = os.path.join(out_dir, 'destinations.csv')
    reviews_path = os.path.join(out_dir, 'reviews.csv')
    ratings_path = os.path.join(out_dir, 'ratings.csv')

    destinations_df.to_csv(dest_path,    index=False)
    reviews_df.to_csv(reviews_path,       index=False)
    ratings_df.to_csv(ratings_path,       index=False)

    print(f"\n[build_dataset] ✓ Written {len(destinations_df)} destinations → {dest_path}")
    print(f"[build_dataset] ✓ Written {len(reviews_df)} reviews        → {reviews_path}")
    print(f"[build_dataset] ✓ Written empty ratings (CF disabled)    → {ratings_path}")
    print("\n[build_dataset] Done! Run:  streamlit run app.py\n")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Build chatbot CSVs from a Kaggle dataset.')
    parser.add_argument('--input',   required=True,          help='Path to the raw Kaggle CSV')
    parser.add_argument('--max',     type=int, default=60,   help='Max destinations to keep (default 60)')
    parser.add_argument('--out_dir', default='data',         help='Output directory (default: data/)')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        sys.exit(f"[ERROR] File not found: {args.input}")

    build(args.input, args.out_dir, args.max)


if __name__ == '__main__':
    main()
