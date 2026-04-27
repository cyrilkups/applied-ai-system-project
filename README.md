# VibeFinder 2.0: Retrieval-Augmented Music Recommendation System

## Original Project: Transparent Music Recommender (Modules 1-3)

**VibeFinder** began as a content-based music recommendation engine that scored songs using explicit, interpretable rules. It accepted a user's structured preferences (favorite genre, mood, energy level) and returned ranked songs with mathematical reasoning visible at every step. The original system prioritized transparency over personalization—every score decision could be traced to a documented rule.

---

## What This Project Does and Why It Matters

**VibeFinder 2.0** transforms the earlier recommender into a **real-world applied AI system** by adding natural-language understanding, retrieval-augmented reasoning, and built-in reliability checks. Instead of requiring users to fill out structured forms, the system now accepts conversational requests like:

- `"Need calm music for late-night coding"`
- `"Need classical music for an intense workout"`
- `"Play nostalgic acoustic music for journaling"`

It parses these requests, retrieves supporting evidence from a knowledge base, ranks songs with explainable rules, and explains _why_ each recommendation matches the intent. The system also **checks its own consistency** and warns when the catalog is too limited to reliably answer a query.

**Why this matters for employers:** This project demonstrates how to build AI systems that are not just intelligent, but _trustworthy_—combining NLP, retrieval, ranking, and reliability checks in a cohesive pipeline that leaves an audit trail for human review.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Request (Natural Language)               │
│                  "Need calm music for late-night coding"         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Intent Parser (NLP)                           │
│  Extracts: genre, mood, energy, activity_tags, preferences      │
│  Selects: scoring mode (mood_first, energy_focused, etc.)       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Retrieval Layer (Lexical Knowledge Base Lookup)         │
│  Matches user intent against song_knowledge_base.json            │
│  Returns: retrieval_score, matched_evidence, caution_flags      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Transparent Recommender (Explicit Scoring)               │
│  Combines: metadata scoring + retrieval bonuses                  │
│  Applies: genre safeguards, diversity reranking                  │
│  Returns: ranked recommendations with explanation strings        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│        Reliability Layer (Self-Checking)                         │
│  Reruns the pipeline once to compare consistency                 │
│  Emits: warnings (thin catalog, conflicting intent)              │
│  Flags: grounded status, consistency_ok                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            Output: Explained Recommendations                     │
│  - Top 3-5 songs with title, artist, score breakdown            │
│  - Retrieved evidence snippets for each song                     │
│  - Reliability warnings and confidence indicators                │
│  - Full trace log saved to JSON for audit                        │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** Retrieval scores _directly change the final ranking_, not just displayed alongside it. A song's base score might be 0.72, but a retrieval match on "late-night coding" context bumps it higher—making the system context-aware rather than purely statistical.

---

## Setup Instructions

### Prerequisites

- Python 3.8 or later
- pip (Python package manager)

### 1. Clone or Download the Repository

```bash
cd /path/to/applied-ai-system-project
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- `pandas` – data manipulation and song catalog loading
- `pytest` – unit test execution
- `streamlit` – (optional) for interactive demos

### 3. Verify the Data Files Exist

Check that these files are present:

```bash
data/songs.csv                    # 18 songs with structured metadata
data/song_knowledge_base.json     # Retrieval evidence for each song
```

### 4. Run the System (Command-Line)

```bash
python -m src.main
```

This prints:

- Available evaluation profiles
- System recommendations for each profile
- Benchmark results
- Reliability checks and warnings

### 5. Run Unit Tests

```bash
pytest tests/ -v
```

Expected output: All tests pass, confirming that the system behaves as documented.

---

## Sample Interactions

### Example 1: Focus-First Late-Night Coding Session

**Input:**

```
"Need calm music for late-night coding"
```

**System Intent Parsing:**

- Detected mood: `calm`
- Target energy: `0.31` (low, suitable for focus)
- Activity tags: `["coding", "focus", "late-night"]`
- Scoring mode: `mood_first`

**Top Recommendations:**
| Rank | Song | Artist | Genre | Score | Reason |
|------|------|--------|-------|-------|--------|
| 1 | Midnight Coding | Lofi Dev | Lofi | 0.89 | Matches mood (calm), activity (coding), and energy perfectly. Retrieved evidence confirms low distraction. |
| 2 | Focus Flow | Study Beats | Lofi | 0.87 | Calm mood with focused energy. Retrieved evidence emphasizes "useful during heads-down work." |
| 3 | Steady Loop | Ambient Coder | Ambient | 0.84 | Very low energy, calm, instrumentalness helps concentration. Retrieval bonus for "study" tag match. |

**Reliability Status:**

- ✅ Grounded: Yes (catalog has strong focus/coding coverage)
- ✅ Consistent: Yes (comparison rerun returned the same top results)
- ⚠️ Warnings: None

**JSON Log (saved automatically):**
See [20260425-012813-need-calm-music-for-late-night-coding.json](logs/music_ai_runs/20260425-012813-need-calm-music-for-late-night-coding.json) for full trace including parser output, retrieval matches, and scoring details.

---

### Example 2: High-Energy Gym Workout

**Input:**

```
"Need high-energy music for the gym"
```

**System Intent Parsing:**

- Detected mood: `intense`
- Target energy: `0.92` (very high)
- Activity tags: `["workout", "gym", "intense"]`
- Scoring mode: `energy_focused`

**Top Recommendations:**
| Rank | Song | Artist | Genre | Score | Reason |
|------|------|--------|-------|-------|--------|
| 1 | Pulse Rush | Electric Beats | EDM | 0.96 | Highest energy track in catalog (0.94 energy, 0.88 danceability). Matches intense workout mood. |
| 2 | Iron Grip | Power Metal | Metal | 0.93 | Intense mood + high tempo. Retrieved evidence tags: "aggressive," "powerful," "workout." |
| 3 | Rhythm Surge | House Masters | Electronic | 0.91 | High energy and danceability (0.85+). Sustained intensity across the track. |

**Reliability Status:**

- ✅ Grounded: Yes
- ✅ Consistent: Yes
- ⚠️ Warnings: None

---

### Example 3: Edge Case—Classical Music for Intense Workout (Conflicting Requests)

**Input:**

```
"Need classical music for an intense workout"
```

**System Intent Parsing:**

- Detected genre: `classical`
- Detected mood: `intense`
- Target energy: `0.95` (very high)
- **Conflict detected:** Classical music is rarely high-energy and intense in the catalog

**Top Recommendations (with Genre Safeguard Applied):**
| Rank | Song | Artist | Genre | Score | Reason |
|------|------|--------|-------|-------|--------|
| 1 | Pulse Rush | Electric Beats | EDM | 0.94 | Highest raw score for intense workout; genre does not match explicit request. |
| 2 | Iron Grip | Power Metal | Metal | 0.91 | Second-best intensity match. |
| 3 | Glass Morning | Romantic Era | Classical | 0.67 | **Genre coverage safeguard applied.** Classical item included despite lower score to honor explicit genre request. Retrieved evidence: "grand orchestral flourishes," "dramatic intensity." |

**Reliability Status:**

- ⚠️ Grounded: Partially (categorical mismatch)
- ⚠️ Consistent: Yes (but with low confidence)
- 🚨 **Warnings:**
  - `"Thin catalog support for classical + intense: only 1 matching song."`
  - `"Genre coverage safeguard applied: classical request honored despite score penalty."`
  - `"User may be better served by relaxing the genre constraint or choosing a different intensity level."`

**Key insight:** Instead of silently ignoring the genre request or failing to respond, the system _exposes the tradeoff_ and warns the user. This is a hallmark of responsible AI design.

---

## Design Decisions

### 1. **Retrieval-Augmented Ranking (vs. Metadata-Only)**

**Decision:** Retrieval scores are fused directly into final rankings, not shown as auxiliary information.

**Why:** A pure metadata recommender can't understand context like "late-night coding" or "journaling." By maintaining a hand-curated knowledge base with scene descriptions and activity tags, the system becomes context-aware. Retrieval bonuses actually _change_ which songs rank highest.

**Trade-off:** The knowledge base is small and hand-authored, so retrieval is lexical (keyword-based), not semantic (embedding-based). This limits scalability but ensures full transparency and controllability.

---

### 2. **Explicit Parser for Intent (vs. End-to-End Neural Model)**

**Decision:** User queries are parsed into a structured dataclass using rule-based NLP (keyword matching, stopword removal).

**Why:**

- Fully interpretable: every parse decision is traceable and reviewable.
- Testable: behavior is deterministic and unit-testable.
- Aligned with transparency requirement: no black-box embeddings.

**Trade-off:** Parsing is brittle with edge cases and creative phrasing. A neural model would be more robust but less explainable. For this project, explainability wins.

---

### 3. **Genre Safeguard (vs. Optimal Ranking Alone)**

**Decision:** When a user explicitly names a genre, at least one song from that genre appears in the top-5, even if lower-scoring items must be promoted.

**Why:** Users sometimes have strong genre preferences that shouldn't be silently ignored. The safeguard honors intent and prevents the "recommendation surprise" where a user gets playlists they didn't ask for.

**Trade-off:** Top recommendations might have slightly lower scores. But honesty about this tradeoff (through warning flags) is better than silently violating intent.

---

### 4. **Self-Checking Reliability Layer (vs. Single-Pass Inference)**

**Decision:** Every query triggers a comparison rerun of the full pipeline to check consistency.

**Why:**

- Detects regressions or unexpected ranking changes between identical runs.
- Flags when small catalog changes affect rankings significantly.
- Provides a confidence score: "how stable is this recommendation?"

**Trade-off:** Roughly 2x computational cost because each query is evaluated twice. Acceptable for a demonstration system; would need optimization for production.

---

### 5. **JSON Logging Every Run**

**Decision:** Each recommendation triggers a detailed JSON trace log saved to `logs/music_ai_runs/`.

**Why:** Enables post-hoc review and debugging. Future work can analyze patterns across runs (e.g., "which queries cause warnings?").

**Trade-off:** Disk space and I/O overhead. Mitigation: logs are only created during evaluation; users can disable logging.

---

## Reliability and Evaluation

**Short summary:** `11/11` automated tests passed with `pytest tests/ -v`, and the `4/4` benchmark prompts in `python -m src.main reliability` produced the expected hits, warning behavior, grounding, and consistency results. The system is strongest when the request overlaps with known catalog tags like `coding`, `gym`, or `journaling`, and weaker when the phrasing is semantically similar but not lexically matched because retrieval is rule-based and the catalog is small.

### How I Tested It

- **Automated tests:** `tests/test_recommender.py` and `tests/test_music_ai_system.py` verify parsing, ranking, genre safeguards, benchmark behavior, and JSON log writing.
- **Consistency check:** `run_music_ai_system()` reruns the same query once and compares the recommendation IDs to confirm stable output for the deterministic pipeline.
- **Logging:** each run can write a JSON trace to `logs/music_ai_runs/` with the parsed intent, retrieved evidence, final recommendations, and reliability warnings.
- **Human evaluation:** I manually reviewed the coding, workout, journaling, and conflicting-genre outputs to check that the explanations matched the returned songs.

### What Worked

- Intent parsing correctly maps clear prompts like `"Need calm music for late-night coding"` and `"Need high-energy music for the gym"` into sensible moods, energy targets, and activity tags.
- Retrieval bonuses meaningfully affect ranking order instead of sitting beside the results unused.
- The genre safeguard keeps an explicitly requested genre in the top results for contradictory prompts such as classical plus intense workout.
- The reliability suite correctly emits a warning for the conflicting classical-workout scenario while keeping the benchmark results consistent.

### What Didn't Work Yet

- Lexical retrieval misses some semantically similar phrasing, so prompts like `"music for unwinding"` are weaker than keyword-heavy prompts such as `"calm"` or `"relaxed"`.
- The catalog has only `18` songs, which makes some genre plus mood combinations thin and increases the need for warnings or fallback behavior.
- The system does not learn from user feedback or listening history yet, so every query is answered fresh with the same rules.
- The current consistency check is useful for catching regressions, but it is not a probability-based confidence score or a full robustness test under noisy inputs.

### Concrete Results

- `11/11` tests passed locally.
- `4/4` benchmark scenarios passed locally.
- JSON logging worked for both test runs and CLI runs.
- The main failure mode is missing or weak lexical context, not code crashes.

---

## Reflection and Ethics

This project pushed me to think about AI as a system that should be honest about its limits, not just good at producing plausible outputs. The final version is better than the earlier prototype because it does more than rank songs: it parses a natural-language request, retrieves supporting evidence, explains its choices, and warns when the catalog is weak.

### Limitations and Biases

- The catalog is small and hand-curated, so the system reflects my own tagging choices and genre coverage gaps.
- Retrieval is lexical rather than semantic, which means phrasing matters a lot. A request using unfamiliar wording may perform worse even if the intent is reasonable.
- The recommender is not personalized. It does not learn from user history, which keeps it simpler and more transparent, but also less adaptive.

### Misuse and Prevention

This system could be misused if someone treated it like an authority on a user's mood, identity, or mental state. It should only be used as a transparent music recommendation helper, not as a tool for psychological inference or manipulation. To reduce misuse, I kept the scope narrow, surfaced warnings for weak matches, included evidence in the explanations, and saved logs so a human can review how the result was produced.

### What Surprised Me During Reliability Testing

The most surprising result was how stable the system was on well-covered requests like coding or gym prompts, and how quickly its weaknesses showed up on thin or contradictory requests. I expected the scoring formula to be the hardest part, but the bigger issue was data coverage and vocabulary mismatch. Testing made it clear that reliability depends as much on the dataset and retrieval rules as on the ranking logic.

### Collaboration With AI

I used AI as a pair-programming and writing assistant throughout the project. One helpful suggestion was to treat the system as a pipeline with separate parsing, retrieval, ranking, and reliability steps, which made the code easier to test and the behavior easier to explain. One flawed suggestion was an earlier AI-generated draft that described sample outputs and a stronger reliability process than the code actually produced; that mistake reminded me to verify AI suggestions against real runs, tests, and logs before trusting them.

### Key Takeaway

The biggest lesson from this project is that responsible AI is not just about making a system look smart. It is about making its behavior inspectable, testable, and appropriately limited. In practice, that meant building warnings, logs, and verification into the project instead of hiding uncertainty behind polished recommendations.

---

## File Structure

```
applied-ai-system-project/
├── README.md                          # This file
├── model_card.md                      # Formal model documentation
├── reflection.md                      # Developer reflection on lessons learned
├── requirements.txt                   # Python dependencies
│
├── src/
│   ├── __init__.py
│   ├── main.py                        # CLI entry point; runs demo profiles and benchmarks
│   ├── music_ai_system.py             # Core pipeline: parser → retrieval → ranking → reliability
│   └── recommender.py                 # Transparent scoring rules and metadata engine
│
├── tests/
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_music_ai_system.py        # Integration tests for full pipeline
│   └── test_recommender.py            # Unit tests for ranking and scoring
│
├── data/
│   ├── songs.csv                      # Catalog metadata (18 songs)
│   └── song_knowledge_base.json       # Retrieval evidence and scene descriptions
│
├── logs/
│   └── music_ai_runs/                 # JSON trace logs from each run
│
└── assets/
    ├── architecture/                  # System diagram (PNG and SVG)
    └── screenshots/                   # Optional example CLI outputs
```

---

## Running the System

### Quick Start

```bash
python -m src.main
```

This prints the full demo: 4 evaluation profiles with recommendations, retrieval details, benchmark results, and reliability checks.

### With Logging

```bash
python -c "from src.music_ai_system import run_music_ai_system; \
run_music_ai_system('Need calm music for late-night coding', enable_logging=True)"
```

A JSON log is saved to `logs/music_ai_runs/` with timestamp and query hash.

### Run Tests

```bash
pytest tests/ -v
```

### Benchmark Reliability

```bash
python -c "from src.music_ai_system import run_reliability_suite; \
run_reliability_suite()"
```

---

## Model Card and Documentation

See [model_card.md](model_card.md) for formal documentation of:

- Model name and intended use
- Strengths and limitations
- Dataset description
- Bias and fairness considerations

See [reflection.md](reflection.md) for the developer's reflective essay on lessons learned.

---

## Key Technologies

- **Python 3.8+** – Core language
- **Pandas** – Data loading and manipulation
- **Pytest** – Unit and integration testing
- **JSON** – Trace logging and structured data

---

## License

This project is provided as-is for educational and portfolio purposes. Modify and distribute freely with attribution.

---

## Contact & Questions

For questions about the architecture, design decisions, or how specific components work, refer to:

- `src/music_ai_system.py` (well-commented pipeline)
- `model_card.md` (formal technical documentation)
- `reflection.md` (design thinking and lessons learned)

## System Architecture

![Music AI system architecture](assets/architecture/music-ai-system-architecture.svg)

The runtime architecture is:

- `src/main.py`
  CLI entry point for baseline profiles, natural-language queries, and reliability runs

- `src/music_ai_system.py`
  Orchestrates parsing, retrieval, score fusion, explanation generation, consistency checking, and JSON logging

- `src/recommender.py`
  Transparent scoring engine with multiple modes and diversity-aware reranking

- `data/songs.csv`
  Structured catalog used by the recommender

- `data/song_knowledge_base.json`
  Retrieval corpus with activity tags, scene descriptions, evidence snippets, and caution context

- `tests/test_music_ai_system.py`
  Reliability-focused tests for parsing, retrieval behavior, genre safeguards, and logging

---

## How Data Flows Through the System

1. A user enters a natural-language request in the CLI.
2. The parser extracts genre, mood, energy, acoustic preference, activities, and exclusions.
3. The retriever scores song evidence documents against that parsed intent.
4. The recommender computes transparent content-based scores for every song.
5. Retrieval bonuses are added to those scores, then diversity reranking is applied.
6. If an explicit genre request disappears from the top list, a genre-coverage safeguard reintroduces the best matching genre item.
7. The system produces:
   - retrieved evidence
   - ranked recommendations
   - explanation strings
   - reliability warnings
   - a JSON run log
8. A reliability check reruns the pipeline and compares results for consistency.

---

## Trust, Guardrails, and Reliability

The system is designed to be inspectable and cautious:

- `Grounded explanations`
  Recommendations include retrieved evidence text in the explanation string.

- `Consistency check`
  The pipeline reruns the same query and verifies that the top recommendations stay stable.

- `Catalog-gap warnings`
  If the catalog poorly supports a request, the system says so instead of pretending it has strong coverage.

- `Genre-coverage safeguard`
  If a user explicitly asks for a genre and the top list loses it, the system inserts the strongest genre-matching candidate and labels that decision.

- `JSON logging`
  Every query run can be saved to `logs/music_ai_runs/` so a reviewer can inspect the parsed intent, retrieved evidence, final recommendations, and reliability output.

- `Benchmark suite`
  `python -m src.main reliability` runs a small evaluation set that checks expected hits, warning behavior, grounding, and consistency.

---

## Project Structure

```text
assets/
  architecture/
    music-ai-system-architecture.svg
  screenshots/
data/
  songs.csv
  song_knowledge_base.json
logs/
  music_ai_runs/
src/
  main.py
  music_ai_system.py
  recommender.py
tests/
  test_music_ai_system.py
  test_recommender.py
README.md
model_card.md
reflection.md
requirements.txt
```

---

## Setup

1. Create and activate a virtual environment if you want an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the baseline recommender profile suite:

```bash
python -m src.main
```

4. Run the applied AI system with a natural-language request:

```bash
python -m src.main query "Need calm music for late-night coding"
```

5. Run the reliability benchmark suite:

```bash
python -m src.main reliability
```

6. Run unit tests:

```bash
pytest
```

---

## Useful Commands

Baseline scoring modes:

```bash
python -m src.main balanced
python -m src.main genre_first
python -m src.main mood_first
python -m src.main energy_focused
python -m src.main all
python -m src.main balanced --no-diversity
```

Natural-language recommendation queries:

```bash
python -m src.main query "Need high-energy music for the gym"
python -m src.main query "Play nostalgic acoustic music for journaling"
python -m src.main query "Need classical music for an intense workout"
python -m src.main "Need focused music for writing"
```

Optional query controls:

```bash
python -m src.main query "Need upbeat music for a run" --top-k 3
python -m src.main query "Need moody night-drive music" --mode mood_first
python -m src.main query "Need soft acoustic music" --no-diversity
```

---

## Example Reliability Scenarios

The built-in benchmark suite currently checks:

- `Focus Coding`
  expects focus-friendly tracks such as `Midnight Coding` or `Focus Flow`

- `Workout Boost`
  expects high-energy workout tracks such as `Gym Hero` or `Storm Runner`

- `Nostalgic Journaling`
  expects reflective acoustic results such as `Fireside Letters`

- `Conflicted Classical Workout`
  expects a warning and still preserves a classical recommendation through the genre safeguard

---

## Why This Counts as an Applied AI System

This repo now goes beyond a small recommendation script because the AI behavior depends on a multi-step pipeline:

- parse
- retrieve
- rank
- explain
- self-check
- log

That makes it a better example of a professional applied AI artifact: it is reproducible, inspectable, and explicit about what it knows and where it is weak.

---

## Limitations

- The catalog is still tiny and hand-authored.
- Retrieval is lexical and rule-based, not embedding-based.
- The system does not use real streaming behavior or collaborative filtering.
- Some contradictory requests still produce imperfect tradeoffs because the catalog itself is limited.

Those limitations are surfaced in warnings and in the model card rather than hidden.
