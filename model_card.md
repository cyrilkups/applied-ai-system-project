# Model Card: VibeFinder 2.0

## 1. Model Name

**VibeFinder 2.0: Retrieval-Augmented Music Recommendation System**

---

## 2. Intended Use

**Primary Task**  
Recommend songs from a small catalog based on a natural-language request, while explaining the recommendation with retrieved supporting evidence.

**Intended Users**  
Students, instructors, and reviewers who want to inspect how an applied AI system can combine retrieval, ranking, explanation, and reliability checks.

**Appropriate Use**  
- classroom demos
- explainable recommendation experiments
- small-scale AI system design projects

**Not Appropriate For**  
- production music platforms
- psychological or emotional diagnosis
- representing a user's full or stable music identity

---

## 3. System Description

This system has two main reasoning layers:

1. **Retriever**
   Looks up song evidence from a local knowledge base using genre, mood, activity, and energy cues from the user's request.

2. **Transparent recommender**
   Scores each song with explicit math-based rules using genre, mood, energy, acousticness, popularity, release decade, mood tags, instrumentalness, live energy, lyrical density, and era affinity.

The final ranking fuses the recommender score with a retrieval bonus. The system then:

- applies diversity-aware reranking
- preserves explicit genre requests when possible
- generates grounded explanation strings
- reruns itself to check consistency
- emits reliability warnings and a JSON trace log

---

## 4. Data

### Catalog Data

`data/songs.csv` contains the structured song catalog. Each row includes:

- title
- artist
- genre
- mood
- energy
- tempo
- valence
- danceability
- acousticness
- popularity
- release decade
- mood tags
- instrumentalness
- live energy
- lyrical density
- era affinity

### Retrieval Data

`data/song_knowledge_base.json` adds richer context per song:

- scene descriptions
- activity tags
- evidence snippets
- caution and mismatch context

This retrieval layer is important because it lets the system respond to requests like `late-night coding`, `journaling`, or `workout`, which are not fully captured by basic metadata alone.

---

## 5. Strengths

- The reasoning path is inspectable because the scoring rules are explicit.
- Recommendations are more useful than the earlier version because natural-language intent is supported.
- Retrieved evidence directly changes ranking behavior instead of sitting beside it unused.
- The system is honest about thin coverage and contradictory requests.
- Reliability checks and JSON logs make review easier.

---

## 6. Limitations and Risks

- The catalog is very small and hand-authored.
- Retrieval is rule-based and lexical, so it can miss subtle semantic phrasing.
- The genre safeguard improves trustworthiness, but it can surface a lower-scoring item in a contradictory query.
- Because the data is curated by a human, the tags and evidence reflect human labeling choices and bias.
- Results are only as good as the catalog coverage. A user with niche tastes may receive weak approximations.

---

## 7. Reliability Strategy

The project includes multiple reliability layers:

- `Consistency check`
  The pipeline reruns the same request and verifies that the top recommendations stay the same.

- `Grounding check`
  The explanation output is expected to contain retrieval-backed evidence for the recommended songs.

- `Warning system`
  The system warns when the requested genre or combination of constraints has weak support in the catalog.

- `Benchmark suite`
  `run_reliability_suite()` tests focus, workout, nostalgia, and conflict scenarios.

- `Unit tests`
  Pytest covers parsing, retrieval-driven ranking, the genre safeguard, and log generation.

---

## 8. Evaluation Summary

The benchmark scenarios currently cover:

- focus-oriented coding requests
- high-energy workout requests
- nostalgic acoustic journaling requests
- contradictory classical-plus-workout requests

The strongest evidence of success is not only that the top songs feel reasonable, but that:

- the expected songs appear in the top results
- the system stays consistent across reruns
- warnings appear when they should
- explicit genre intent is not silently dropped in conflicting cases

---

## 9. Ethical Notes

- This system should be treated as a recommendation helper, not as an authority on taste or mood.
- It should not be used to infer mental state, health, or personality.
- Explanations are grounded in local metadata and curated evidence, but they are still shaped by the dataset designer's choices.

---

## 10. Future Work

- Add a larger and more balanced music catalog.
- Replace lexical retrieval with embedding-based similarity.
- Add richer user controls such as dislike signals, tempo bands, or explanation styles.
- Add a lightweight UI for easier human evaluation.
- Track benchmark metrics over time as the catalog changes.
