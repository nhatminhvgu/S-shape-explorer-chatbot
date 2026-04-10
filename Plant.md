# Plant.md — Project Plan
# Bilingual Travel Recommendation Chatbot for Vietnam

---

## 1. Project Overview

This project builds a bilingual (English / Vietnamese) conversational chatbot that recommends personalized travel destinations in Vietnam. The system understands user preferences through natural language, applies a hybrid recommendation engine (content-based + collaborative filtering), analyzes review sentiment, and explains its suggestions in the user's chosen language via a Streamlit web interface.

---

## 2. Objectives

1. Build a working recommendation system using both content-based and collaborative filtering.
2. Implement NLP components: text cleaning, sentiment analysis on reviews, intent recognition from user input.
3. Create a lightweight "generative" response layer using dynamic template-based natural language generation.
4. Support full bilingual interaction in English and Vietnamese.
5. Deploy the prototype as a runnable Streamlit application.
6. Produce clean, modular, academically submittable code.

---

## 3. Scope

### Included
- 30 curated Vietnam travel destinations across North, Central, and South regions
- 60 mock traveler reviews with sentiment labels
- Simulated user-item ratings matrix (20 users × 30 destinations) for collaborative filtering
- Content-based filtering using TF-IDF + cosine similarity
- Collaborative filtering using TruncatedSVD (matrix factorization)
- Hybrid scoring: weighted combination of both methods + sentiment bonus
- Sentiment analysis: VADER (English), keyword lexicon (Vietnamese)
- Intent recognition: rule-based keyword matching (EN + VI)
- Bilingual chatbot UI with language toggle (English ↔ Tiếng Việt)
- Template-based natural language generation for response variety
- Streamlit web interface with chat + recommendation cards

### Excluded
- Real-time web scraping or live API calls
- Deep learning models or large pre-trained LLMs (not feasible without paid API or GPU)
- User account system or persistent user history
- Map visualization or geolocation features (out of scope for assignment)
- Multi-city itinerary planning

### Simplified for Feasibility
- **Dataset**: Curated mock dataset instead of scraped real data. Justification: no comprehensive free Vietnam travel dataset exists; the algorithm pipeline is identical regardless of data origin.
- **Collaborative Filtering**: Simulated ratings matrix. Justification: no real user interaction data available; SVD algorithm is identical to production use.
- **LLM Layer**: Template-based generation instead of a neural model. Justification: open-source LLMs require GPU/downloads impractical for student deployment; template generation is fast, bilingual-friendly, and controllable.
- **Vietnamese NLP**: Keyword lexicon instead of a trained Vietnamese NLP model. Justification: no free production-grade Vietnamese sentiment library exists that is also lightweight.

---

## 4. Assumptions

- Users interact via typed natural language (English or Vietnamese).
- The system is run locally or on a Streamlit Cloud deployment.
- Data is treated as representative of Vietnam's real travel landscape.
- Ratings are simulated to demonstrate collaborative filtering mechanics.
- Students have Python 3.8+ and internet access for pip install.

---

## 5. Dataset Strategy

**Strategy: Curated Mock Dataset**

**Why this approach:**
- No comprehensive, free, legally-safe Vietnam travel dataset exists on Kaggle or public sources.
- Creating a curated mock dataset is standard academic practice for demonstrating algorithm pipelines.
- The 30 destinations are based on real, well-known Vietnamese tourist locations with realistic attributes.
- The pipeline is fully interchangeable with real data if obtained later.

**Fields used:**

| Field | Purpose |
|-------|---------|
| id, name, name_vi | Destination identity |
| region | North/Central/South filter |
| primary_category | Main type (beach, mountain, city, etc.) |
| tags | Multi-label categories for TF-IDF |
| description, description_vi | Bilingual text for display |
| price_level (1-3) | Budget filter |
| avg_rating | Quality signal |
| best_for | Group type matching |
| trip_duration | Duration filter |

**Cleaning steps:**
1. Fill missing text fields with empty string
2. Normalize numeric fields (rating, price_level)
3. Build TF-IDF profiles by combining tags + category + region + description
4. Preprocess reviews: lowercase, remove punctuation, remove stopwords

---

## 6. Module Breakdown

```
app.py                          Streamlit UI entry point
data/
  destinations.csv              30 Vietnam destination records
  reviews.csv                   60 traveler reviews
  ratings.csv                   Simulated user-item ratings
src/
  data_processing/
    loader.py                   CSV loading and validation
    cleaner.py                  Text cleaning (EN + VI)
    sentiment.py                Sentiment analysis (VADER + lexicon)
  recommender/
    content_based.py            TF-IDF + cosine similarity CBF
    collaborative.py            SVD matrix factorization CF
    hybrid.py                   Weighted hybrid combiner
  chatbot/
    intent.py                   Rule-based intent/preference extraction
    response.py                 Template-based bilingual response generation
    conversation.py             Multi-turn conversation state manager
  utils/
    language.py                 All bilingual UI strings
    helpers.py                  Shared utility functions
report/
  report_outline.md             Academic report structure
```

---

## 7. Implementation Phases

### Phase 1 — Foundation (Week 1)
- Set up repository structure
- Create destinations.csv and reviews.csv datasets
- Implement data loading (loader.py) and text cleaning (cleaner.py)
- **Deliverable:** Clean, loadable dataset with preprocessing pipeline

### Phase 2 — Recommendation Engine (Week 2)
- Implement content-based filtering (content_based.py)
- Implement collaborative filtering with SVD (collaborative.py)
- Implement hybrid combiner (hybrid.py)
- Unit test each recommender with sample inputs
- **Deliverable:** Working hybrid recommender returning ranked destination lists

### Phase 3 — NLP Layer (Week 2-3)
- Implement VADER sentiment analysis for English reviews
- Implement Vietnamese keyword lexicon sentiment
- Add sentiment scores to destination enrichment pipeline
- **Deliverable:** Destinations enriched with sentiment scores from reviews

### Phase 4 — Chatbot Layer (Week 3)
- Implement rule-based intent/preference extraction (intent.py)
- Build bilingual template response generator (response.py)
- Build conversation state manager (conversation.py)
- **Deliverable:** Working chatbot that extracts preferences and generates responses

### Phase 5 — Streamlit UI (Week 4)
- Build bilingual Streamlit interface
- Integrate chat, sidebar preferences, recommendation cards
- Add language toggle (English ↔ Vietnamese)
- End-to-end testing
- **Deliverable:** Runnable Streamlit app with full bilingual support

### Phase 6 — Evaluation & Report (Week 4-5)
- Run evaluation scenarios (test cases)
- Document results and observations
- Write academic report
- **Deliverable:** Evaluation results + completed report

---

## 8. Milestone / Timeline Plan

| Week | Milestone | Status |
|------|-----------|--------|
| 1 | Dataset + data loading + cleaning | ✅ Done |
| 2 | Content-based + collaborative + hybrid recommender | ✅ Done |
| 2-3 | NLP: sentiment analysis + intent recognition | ✅ Done |
| 3 | Chatbot layer: intent, response, conversation | ✅ Done |
| 4 | Streamlit bilingual UI integration | ✅ Done |
| 4-5 | Evaluation + report writing | ⬜ Remaining |

---

## 9. Possible Risks

| Risk | Likelihood | Impact |
|------|-----------|--------|
| NLTK VADER download fails (no internet) | Low | Medium |
| Mock data not representative enough | Medium | Low |
| Collaborative filtering quality low due to sparse simulated data | High | Medium |
| Vietnamese NLP accuracy limited by keyword approach | High | Low |
| Streamlit UI slow on first load (model fitting) | Low | Low |

---

## 10. Mitigation Strategies

| Risk | Mitigation |
|------|-----------|
| VADER download fails | Added try/except fallback; VADER auto-downloads on first run |
| Mock data quality | Destinations are based on real well-known Vietnamese locations |
| CF quality | Hybrid blending (65% CBF) ensures good results even when CF is weak |
| Vietnamese NLP | Keyword lexicon covers the most common travel-review vocabulary |
| Slow first load | Streamlit @st.cache_resource ensures fitting runs only once |

---

## 11. Final Deliverables

- [ ] Working Streamlit application (`streamlit run app.py`)
- [ ] Complete modular Python codebase under `src/`
- [ ] Dataset files in `data/`
- [ ] Academic report in `report/`
- [ ] This project plan (Plant.md)
- [ ] README.md with setup instructions
- [ ] requirements.txt for environment reproducibility
