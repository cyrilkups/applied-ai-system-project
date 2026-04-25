# Applied Music AI System

## Overview

This project upgrades the earlier music recommender into a fuller applied AI system.

Instead of only scoring songs from a fixed user profile, the new system accepts a natural-language request such as:

- `Need calm music for late-night coding`
- `Play nostalgic acoustic music for journaling`
- `Need classical music for an intense workout`

It then:

1. parses the request into structured intent
2. retrieves supporting song knowledge from a local evidence base
3. ranks songs with the existing transparent recommender
4. adds retrieval bonuses that actually change ranking behavior
5. explains each recommendation using retrieved evidence
6. runs reliability checks and writes a JSON trace log

The result is an explainable, retrieval-augmented music recommendation system with guardrails and evaluation built into the main workflow.

---

## AI Features Included

This final project fully integrates two advanced AI features into the application logic:

- `Retrieval-Augmented Recommendation`
  The system retrieves song evidence from `data/song_knowledge_base.json` before ranking. Retrieval scores are fused into the final recommendation score, so retrieval changes the output instead of just being displayed beside it.

- `Reliability and Testing System`
  The system reruns itself to check consistency, reports warnings for thin catalog coverage or conflicting requests, logs every run to JSON, and includes both benchmark scenarios and unit tests.

---

## What Problem It Solves

The system helps a user discover songs based on intent, not just labels. A person can describe an activity, mood, or listening goal in plain language, and the system turns that into a grounded recommendation with evidence and caveats.

Examples:

- A student wants low-distraction focus music for coding
- A runner wants high-energy tracks for a workout
- A reflective listener wants nostalgic acoustic music for journaling
- A user makes a contradictory request, and the system still responds while warning about weak catalog support

---

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
