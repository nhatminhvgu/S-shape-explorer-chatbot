# Academic Report Outline
# Bilingual Travel Recommendation Chatbot for Vietnam

**Course:** [Course Name]  
**Team:** [Team Member Names]  
**Institution:** [University Name]  
**Date:** [Submission Date]

---

## Abstract (200–300 words)

Brief summary covering: problem, approach, key techniques, and main findings.

---

## 1. Introduction

### 1.1 Background and Motivation
- Travel information overload problem
- Need for personalized, conversational travel recommendation
- Why Vietnam as the focus domain
- The bilingual requirement (English + Vietnamese)

### 1.2 Problem Statement
Travelers struggle to find Vietnam destinations that match their personal preferences, budget, travel style, and group type. Existing platforms give repetitive, ad-influenced, and non-conversational recommendations. This project addresses the gap with a conversational, personalized, and explainable recommendation system.

### 1.3 Project Objectives
1. Build a hybrid recommendation system (CBF + CF)
2. Implement NLP: sentiment analysis and intent recognition
3. Create a lightweight natural language generation layer
4. Deliver a bilingual (EN/VI) Streamlit prototype

### 1.4 Report Structure
Overview of remaining sections.

---

## 2. Background and Literature Review

### 2.1 Recommendation Systems
- Content-based filtering: overview, TF-IDF, cosine similarity
- Collaborative filtering: overview, matrix factorization, SVD (Koren et al., 2009)
- Hybrid approaches: Burke (2002) taxonomy

### 2.2 Conversational Recommender Systems
- Overview of chatbot-based recommendation
- Rule-based vs. neural approaches
- Justification for rule-based approach at student scale

### 2.3 Sentiment Analysis
- VADER (Hutto & Gilbert, 2014) for English
- Lexicon-based approaches for low-resource languages
- Relevance to travel domain

### 2.4 Natural Language Generation
- Template-based NLG: overview and academic use
- Why template NLG is appropriate for this scope
- Comparison with LLM-based generation (trade-offs)

### 2.5 Related Work
- Survey of travel recommendation systems
- Existing Vietnam travel apps and their limitations
- Gap addressed by this project

---

## 3. Dataset

### 3.1 Data Strategy and Justification
- Why curated mock dataset was chosen
- Comparison with alternatives (Kaggle scraping, API crawling)
- Academic acceptability of simulated data for algorithm demonstration

### 3.2 Destination Dataset
- 30 Vietnam destinations: fields, distribution by region and category
- Table: sample records
- Statistics: rating distribution, price level distribution, category distribution

### 3.3 Review Dataset
- 60 traveler reviews: 2 per destination
- Language distribution (all English in current version)
- Sentiment label distribution (positive / neutral / negative)

### 3.4 Ratings Dataset
- Simulated user-item matrix: 20 users × 30 destinations, ~120 ratings
- Sparsity analysis
- Rating distribution

### 3.5 Data Limitations
- Mock data vs. real scraped data
- Limited number of reviews per destination
- Simulated vs. real user interaction patterns

---

## 4. Methodology

### 4.1 System Architecture
Diagram and description of the full pipeline:
Data → Preprocessing → Sentiment Enrichment → Hybrid Recommender → Chatbot Layer → Bilingual UI

### 4.2 Data Preprocessing
- Text cleaning pipeline (English: VADER-compatible; Vietnamese: diacritic-preserving)
- Stopword removal
- Destination text profile construction for TF-IDF

### 4.3 Sentiment Analysis
- English: VADER compound score thresholds (>0.05 positive, <-0.05 negative)
- Vietnamese: keyword lexicon — positive/negative word counting, score normalization
- Aggregation: per-destination average sentiment score and label
- Integration: sentiment_score used as a 5% bonus in hybrid scoring

### 4.4 Content-Based Filtering
- TF-IDF vectorization of destination profiles (tags × 2 + category × 2 + region + description)
- User query construction from extracted preferences
- Cosine similarity computation
- Hard filters: region, budget (relaxed if fewer than 3 results)
- Rating blending: 90% similarity + 10% normalized rating

### 4.5 Collaborative Filtering
- User-item matrix construction (pivot table)
- TruncatedSVD decomposition (k=8 latent factors)
- New-user projection: pseudo-user vector → latent space
- Similar-user aggregation with cosine similarity weighting
- Fallback: popularity-based recommendation when no CF signal

### 4.6 Hybrid Combination
- Weighted linear combination: 0.65 × CB score + 0.35 × CF score
- Sentiment bonus: up to 0.05 for positively-reviewed destinations
- Fallback to pure CBF when CF has insufficient data

### 4.7 Intent Recognition
- Rule-based keyword matching with 9 category types, 3 regions, 3 budget levels, 4 group types, 3 travel styles
- Bilingual keyword tables (English + Vietnamese)
- Preference merging across conversation turns
- Confidence threshold: recommend only when at least 1 slot is filled

### 4.8 Natural Language Generation (LLM Layer)
- Design decision: template-based dynamic NLG over neural LLM
- Response types: greeting, recommendation intro, explanation, follow-up, clarification, no-results
- Slot-filling mechanism in explanation generator
- Multiple variants per template type (random selection for variety)
- Bilingual output: separate template sets for EN and VI

### 4.9 Bilingual Interface Design
- Language toggle: Streamlit radio button (English / Tiếng Việt)
- String externalization: all UI text stored in language.py dictionary
- Instant language switch: preferences and chat persist, labels update
- Vietnamese description field used when VI mode is active

---

## 5. Implementation

### 5.1 Technology Stack
Table: component → library → version

### 5.2 Repository Structure
Directory tree with module descriptions

### 5.3 Key Implementation Details
- Streamlit @st.cache_resource for one-time model fitting
- Session state management for multi-turn conversation
- Preference accumulation across chat turns and sidebar
- HTML/CSS custom styling for destination cards

### 5.4 Challenges and Solutions
- Vietnamese text handling without a dedicated NLP library
- Sparse ratings matrix and SVD stability
- Streamlit session state synchronization between chat and sidebar
- Template response variety without repetition

---

## 6. Evaluation

### 6.1 Evaluation Strategy
(Note: formal metrics require a held-out test set with ground truth labels. For this prototype, we use practical evaluation: scenario testing, manual relevance assessment, and user observation.)

### 6.2 Recommendation Relevance (Manual Assessment)
- Method: 5 test scenarios with defined ground truth (expected top destinations)
- Metric: top-5 precision (how many of the top 5 are relevant)
- Results: [fill in after running scenarios]

| Scenario | Query | Expected | Returned | Precision@5 |
|----------|-------|----------|----------|------------|
| Beach south | Beach, south, couple | Phu Quoc, Con Dao, Mui Ne | ... | ... |
| Mountain north | Mountain, north, adventure | Ha Giang, Sapa, Cao Bang | ... | ... |
| Budget culture | Culture, budget | Hanoi, Hue, Hoi An | ... | ... |
| Family relaxation | Relaxation, family | Ha Long, Da Lat, Ba Na Hills | ... | ... |
| Food city south | Food, city, south | HCMC, Can Tho, Mekong Delta | ... | ... |

### 6.3 NLP Component Evaluation
- Sentiment: accuracy on the 60 labeled reviews (compare predicted vs. stored label)
- Intent: precision/recall on 10 hand-crafted test sentences

### 6.4 Bilingual Usability
- Manual check: all UI strings correctly translated
- Vietnamese input processing: 5 test queries in Vietnamese

### 6.5 Chatbot Response Quality
- Qualitative review of generated explanations for 10 sample recommendations
- Check: relevance, naturalness, bilingual consistency

### 6.6 Performance
- First-load time (model fitting): measured
- Per-query response time: measured

---

## 7. Results and Discussion

### 7.1 Recommendation Quality
- Summary of precision scores from evaluation scenarios
- Comparison: pure CBF vs. pure CF vs. hybrid
- Effect of sentiment bonus

### 7.2 NLP Results
- Sentiment accuracy per language
- Intent extraction accuracy

### 7.3 Bilingual Usability
- Assessment of Vietnamese translation quality
- User feedback (if any)

### 7.4 Comparison of Methods
Table comparing CBF, CF, and Hybrid on test scenarios

### 7.5 Discussion
- When does the hybrid outperform pure CBF?
- How does the simulated ratings matrix affect CF quality?
- Trade-offs of template NLG vs. neural LLM

---

## 8. Limitations

1. **Mock dataset**: The 30 destinations and 60 reviews are curated, not scraped from real traveler platforms. Results may not generalize to the full diversity of Vietnamese travel.
2. **Simulated ratings**: Collaborative filtering is demonstrated on synthetic data. Real user-item interaction data would significantly improve CF quality.
3. **Vietnamese NLP**: Keyword lexicon is limited compared to a trained Vietnamese sentiment model. Nuanced expressions and negations are not handled.
4. **No user memory**: The system does not persist user history across sessions.
5. **Template NLG**: Responses follow fixed patterns. A real LLM would generate more varied and contextually rich explanations.
6. **Evaluation scope**: Formal offline evaluation (precision@k, NDCG) is limited by the small dataset size.
7. **Single language per review**: Reviews are only in English; a truly bilingual NLP pipeline requires Vietnamese review data.

---

## 9. Conclusion

Summary of what was achieved:
- Hybrid CBF+CF recommendation system demonstrated and evaluated
- Sentiment analysis integrated as a quality signal
- Rule-based intent recognition working in both languages
- Template-based NLG providing natural bilingual explanations
- Full Streamlit prototype deployed and runnable

The project demonstrates that a meaningful, explainable recommendation chatbot can be built at student scale without paid APIs, production infrastructure, or large pre-trained models — using sound, academically-grounded methods.

---

## 10. Future Work

1. **Real data**: Integrate TripAdvisor/Google Maps public review data via legal means.
2. **Vietnamese NLP model**: Use PhoBERT (Vietnamese BERT) for better sentiment and intent.
3. **Implicit feedback**: Track clicks and session behavior for better CF signals.
4. **Neural CF**: Replace SVD with neural collaborative filtering (NCF).
5. **Real LLM**: Integrate a small local model (e.g., Mistral 7B via Ollama) for richer generation.
6. **Itinerary planning**: Extend from single-destination to multi-stop trip planning.
7. **Map visualization**: Add interactive map showing recommended destinations.
8. **User accounts**: Allow users to save favorites and return for personalized history.

---

## References

- Burke, R. (2002). Hybrid Recommender Systems: Survey and Experiments. *User Modeling and User-Adapted Interaction*, 12(4), 331–370.
- Hutto, C. J., & Gilbert, E. (2014). VADER: A Parsimonious Rule-Based Model for Sentiment Analysis of Social Media Text. *ICWSM*.
- Koren, Y., Bell, R., & Volinsky, C. (2009). Matrix Factorization Techniques for Recommender Systems. *IEEE Computer*, 42(8), 30–37.
- Ricci, F., Rokach, L., & Shapira, B. (2015). *Recommender Systems Handbook* (2nd ed.). Springer.
- Pazzani, M. J., & Billsus, D. (2007). Content-Based Recommendation Systems. *The Adaptive Web*, 325–341.
- Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval. *Information Processing & Management*, 24(5), 513–523.
- [Add additional references as needed for your specific course requirements]
