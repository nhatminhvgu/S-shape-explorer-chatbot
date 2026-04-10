# Vietnam Travel Recommendation Chatbot

A bilingual (English / Vietnamese) conversational travel recommendation system built with Python and Streamlit.

The chatbot recommends personalized Vietnam travel destinations using a hybrid recommendation engine combining content-based filtering (TF-IDF + cosine similarity) and collaborative filtering (SVD matrix factorization), enriched with sentiment analysis on traveler reviews.

---

## Features

- **Bilingual UI** — Switch between English and Tiếng Việt at any time
- **Hybrid Recommendation** — Content-based (65%) + Collaborative Filtering (35%)
- **Sentiment Analysis** — VADER for English reviews, keyword lexicon for Vietnamese
- **Natural Language Chat** — Type preferences in plain English or Vietnamese
- **Sidebar Filters** — Quick preference selection without typing
- **Explainable Results** — Each recommendation includes a reason why it was suggested

---

## Quick Start

### 1. Clone / download the project

```bash
git clone <repo-url>
cd S-shape-explorer-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python -m streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Project Structure

```
S-shape-explorer-chatbot/
├── app.py                    # Streamlit main application
├── requirements.txt          # Python dependencies
├── Plant.md                  # Full project plan
├── README.md                 # This file
│
├── data/
│   ├── destinations.csv      # 30 Vietnam destination records
│   ├── reviews.csv           # 60 traveler reviews with sentiment
│   └── ratings.csv           # Simulated user-item ratings (20 users)
│
├── src/
│   ├── data_processing/
│   │   ├── loader.py         # CSV data loading and validation
│   │   ├── cleaner.py        # Text cleaning (English + Vietnamese)
│   │   └── sentiment.py      # Sentiment analysis (VADER + lexicon)
│   │
│   ├── recommender/
│   │   ├── content_based.py  # TF-IDF content-based filtering
│   │   ├── collaborative.py  # SVD collaborative filtering
│   │   └── hybrid.py         # Weighted hybrid combiner
│   │
│   ├── chatbot/
│   │   ├── intent.py         # Rule-based preference extraction
│   │   ├── response.py       # Template-based bilingual response generator
│   │   └── conversation.py   # Multi-turn conversation state manager
│   │
│   └── utils/
│       ├── language.py       # Bilingual UI strings (EN + VI)
│       └── helpers.py        # Shared utility functions
│
└── report/
    └── report_outline.md     # Academic report structure
```

---

## How to Use

### Chat input

Type your travel preferences in the chat box:

- _"I want a beach holiday in south Vietnam with a medium budget"_
- _"Adventure trip in the mountains for a group of friends"_
- _"Tôi muốn đi biển miền Trung, ngân sách tầm trung"_

### Sidebar filters

Select preferences using the dropdown menus and multiselect boxes, then click **Get Recommendations**.

### Language toggle

Use the **English / Tiếng Việt** radio button at the top right to switch languages at any time.

---

## System Architecture

```
User Input (chat or sidebar)
        │
        ▼
Intent Recognition (rule-based keyword matching)
        │
        ▼
Hybrid Recommender
  ├── Content-Based: TF-IDF + Cosine Similarity (65%)
  └── Collaborative: SVD Matrix Factorization (35%)
        │
        ▼
Sentiment Enrichment (VADER / keyword lexicon)
        │
        ▼
Response Generator (template-based bilingual NLG)
        │
        ▼
Streamlit UI (chat bubbles + destination cards)
```

---

## Recommendation Methods

| Method                  | Technique                                | Weight  |
| ----------------------- | ---------------------------------------- | ------- |
| Content-Based Filtering | TF-IDF vectorization + Cosine Similarity | 65%     |
| Collaborative Filtering | TruncatedSVD matrix factorization        | 35%     |
| Sentiment Bonus         | VADER (EN) / keyword lexicon (VI)        | +5% max |

---

## Tech Stack

| Component         | Library                                       |
| ----------------- | --------------------------------------------- |
| Web UI            | Streamlit                                     |
| Data handling     | Pandas, NumPy                                 |
| Recommendation    | scikit-learn (TF-IDF, SVD, cosine similarity) |
| Sentiment (EN)    | NLTK VADER                                    |
| NLP preprocessing | Python stdlib + custom cleaners               |
| Visualization     | Matplotlib, Seaborn                           |

---

## Notes for Academic Submission

- The dataset is a curated mock dataset based on real Vietnam destinations. This is academically acceptable for demonstrating the algorithm pipeline.
- Collaborative filtering uses a simulated ratings matrix. The SVD algorithm is identical to what would be used with real data.
- The "LLM layer" is implemented as a dynamic template-based NLG system. This is a deliberate design choice: no paid API, fast, bilingual-friendly, and controllable.
- All modules are independently testable and clearly separated by concern.

---

# streamlit error

Lỗi này do PowerShell không tìm thấy lệnh streamlit. Dùng lệnh này thay thế:

python -m streamlit run app.py
Thêm python -m vào trước là chạy được ngay.

Nếu vẫn lỗi, thử:

py -m streamlit run app.py
