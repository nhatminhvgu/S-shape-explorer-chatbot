#!/usr/bin/env python3
"""
enrich_descriptions.py
======================
Enriches data/destinations.csv with real Vietnamese descriptions
extracted from data/raw/valid_vietnam_tourism.csv (Kaggle dataset).

Strategy
--------
- Keeps the original 30 destinations, reviews, and ratings intact.
- For each destination, finds all relevant Kaggle articles by keyword matching
  on the article title (Vietnamese/English destination name).
- Parses the 'paragraphs' JSON field and extracts the context text.
- Writes enriched Vietnamese text into the `description_vi` column.
- Optionally updates `description` (English) with a summary sentence
  derived from the first Vietnamese paragraph.
- Only overwrites `description_vi`; all other columns are preserved as-is.

Usage
-----
    python scripts/enrich_descriptions.py

Output: data/destinations.csv  (updated in-place)
"""

import ast
import os
import sys
import re
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

KAGGLE_PATH = 'data/raw/valid_vietnam_tourism.csv'
DEST_PATH   = 'data/destinations.csv'

# Max characters for description_vi (app truncates at 200 in the card,
# but the full text is used in content-based TF-IDF)
MAX_VI_CHARS = 600

# ──────────────────────────────────────────────────────────────────────────────
# Mapping: destination name → list of Vietnamese/English keywords
# that should appear in an article TITLE to be considered relevant.
# Keys must match the 'name' column in destinations.csv exactly.
# ──────────────────────────────────────────────────────────────────────────────
DEST_KEYWORDS = {
    'Ha Long Bay':            ['Vịnh Hạ Long', 'Hạ Long', 'Ha Long', 'Đảo Cát Bà'],
    'Sapa':                   ['Sa Pa', 'Sapa', 'Fansipan', 'Trekking các bản làng'],
    'Hanoi':                  ['Hà Nội', 'Hanoi', 'Hoàn Kiếm', 'Phố cổ Hà Nội',
                               'Văn Miếu', 'Lăng Chủ tịch', 'Múa rối nước'],
    'Ninh Binh':              ['Ninh Bình', 'Tràng An', 'Tam Cốc', 'Hang Múa'],
    'Ha Giang':               ['Hà Giang', 'Mã Pì Lèng', 'Lũng Cú', 'vòng Hà Giang'],
    'Mai Chau':               ['Mai Châu'],
    'Ba Be Lake':             ['Ba Bể'],
    'Moc Chau':               ['Mộc Châu', 'Mù Cang Chải'],
    'Bai Tu Long Bay':        ['Bái Tử Long', 'Cát Bà', 'Đảo Cát Bà'],
    'Cao Bang':               ['Cao Bằng', 'Bản Giốc', 'biên giới Trung Quốc'],
    'Hoi An':                 ['Hội An', 'Chùa Cầu', 'may đo', 'đèn lồng Hội An',
                               'Cù Lao Chàm'],
    'Da Nang':                ['Đà Nẵng', 'Mỹ Khê', 'Sơn Trà', 'Ngũ Hành Sơn'],
    'Hue':                    ['Huế', 'Đại Nội', 'sông Hương', 'Lăng tẩm',
                               'Chùa Thiên Mụ', 'triều Nguyễn'],
    'Phong Nha':              ['Phong Nha', 'Sơn Đoòng', 'hang động', 'Kẻ Bàng',
                               'Động Thiên Đường'],
    'My Son Sanctuary':       ['Mỹ Sơn', 'Chăm Pa'],
    'Quy Nhon':               ['Quy Nhơn'],
    'Ba Na Hills':            ['Bà Nà Hills', 'Cầu Vàng'],
    'Bach Ma National Park':  ['Bạch Mã'],
    'Nha Trang':              ['Nha Trang', 'Tháp Bà Ponagar', 'đảo Nha Trang'],
    'Lang Co Beach':          ['Lăng Cô'],
    'Ho Chi Minh City':       ['Hồ Chí Minh', 'Sài Gòn', 'Saigon', 'Dinh Độc Lập',
                               'Bảo tàng Chứng tích', 'Bến Thành'],
    'Phu Quoc Island':        ['Phú Quốc'],
    'Da Lat':                 ['Đà Lạt', 'Hồ Xuân Hương', 'thác nước ở Đà Lạt',
                               'Ga xe lửa cổ Đà Lạt'],
    'Con Dao Islands':        ['Côn Đảo'],
    'Mekong Delta':           ['Cửu Long', 'Đồng bằng sông', 'miệt vườn',
                               'Bến Tre', 'Rừng tràm Trà Sư'],
    'Vung Tau':               ['Vũng Tàu'],
    'Can Tho':                ['Cần Thơ', 'Cái Răng'],
    'Cat Tien National Park': ['Cát Tiên'],
    'Mui Ne':                 ['Mũi Né', 'Suối Tiên'],
    'Cu Chi Tunnels':         ['Củ Chi', 'địa đạo'],
}


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def parse_paragraphs(raw: str) -> list[str]:
    """Parse '[{"context": "..."}]' string → list of context strings."""
    if not isinstance(raw, str) or not raw.strip():
        return []
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            return [item['context'] for item in data
                    if isinstance(item, dict) and 'context' in item]
    except Exception:
        pass
    # Fallback: regex extract
    return re.findall(r"'context':\s*'(.*?)'(?:,\s*'|\})", raw, re.DOTALL)


def clean_sentence(text: str) -> str:
    """Remove excess whitespace from a paragraph."""
    return re.sub(r'\s+', ' ', text).strip()


def build_description_vi(contexts: list[str], max_chars: int = MAX_VI_CHARS) -> str:
    """Join contexts into a single description, respecting max_chars."""
    combined = ' '.join(clean_sentence(c) for c in contexts if c.strip())
    if len(combined) > max_chars:
        # Truncate at last sentence boundary before limit
        cut = combined[:max_chars]
        last_dot = max(cut.rfind('. '), cut.rfind('! '), cut.rfind('? '))
        if last_dot > max_chars // 2:
            combined = cut[:last_dot + 1]
        else:
            combined = cut.rstrip() + '...'
    return combined


def title_matches(title: str, keywords: list[str]) -> bool:
    """Return True if any keyword is found as a whole word/phrase in the title.
    Uses word-boundary regex to avoid false substring matches in Vietnamese
    (e.g. 'Huế' must not match inside 'thuế').
    """
    for kw in keywords:
        pattern = r'(?<!\w)' + re.escape(kw.lower()) + r'(?!\w)'
        if re.search(pattern, title.lower()):
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    # ── Load files
    if not os.path.isfile(KAGGLE_PATH):
        sys.exit(f'[ERROR] Kaggle file not found: {KAGGLE_PATH}')
    if not os.path.isfile(DEST_PATH):
        sys.exit(f'[ERROR] destinations.csv not found: {DEST_PATH}')

    kaggle_df = pd.read_csv(KAGGLE_PATH, on_bad_lines='skip')
    dest_df   = pd.read_csv(DEST_PATH)

    print(f'[enrich] Loaded {len(kaggle_df)} Kaggle articles')
    print(f'[enrich] Loaded {len(dest_df)} destinations\n')

    # Pre-parse all paragraphs once
    kaggle_df['_contexts'] = kaggle_df['paragraphs'].apply(parse_paragraphs)

    enriched_count = 0

    for idx, dest_row in dest_df.iterrows():
        dest_name = dest_row['name']
        keywords  = DEST_KEYWORDS.get(dest_name)

        if not keywords:
            print(f'  [SKIP]  {dest_name:35s} — no keyword mapping defined')
            continue

        # Find all matching articles
        matching = kaggle_df[kaggle_df['title'].apply(
            lambda t: title_matches(str(t), keywords)
        )]

        if matching.empty:
            print(f'  [MISS]  {dest_name:35s} — no matching article found')
            continue

        # Collect all contexts from matching articles
        all_contexts = []
        for _, art_row in matching.iterrows():
            all_contexts.extend(art_row['_contexts'])

        if not all_contexts:
            print(f'  [MISS]  {dest_name:35s} — articles found but paragraphs empty')
            continue

        description_vi = build_description_vi(all_contexts)
        dest_df.at[idx, 'description_vi'] = description_vi
        enriched_count += 1

        matched_titles = matching['title'].tolist()
        print(f'  [OK]    {dest_name:35s} ← {len(matched_titles)} article(s): '
              f'{[t[:40] for t in matched_titles]}')

    # ── Save
    dest_df.to_csv(DEST_PATH, index=False)
    print(f'\n[enrich] ✓ Enriched {enriched_count}/{len(dest_df)} destinations')
    print(f'[enrich] ✓ Saved → {DEST_PATH}\n')


if __name__ == '__main__':
    main()
