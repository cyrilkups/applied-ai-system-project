"""Retrieval-augmented music recommendation pipeline with reliability checks."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from src.recommender import (
    MODE_ALIASES,
    available_modes,
    load_songs,
    recommend_songs,
    score_song,
)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "for",
    "from",
    "i",
    "im",
    "in",
    "into",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "or",
    "please",
    "play",
    "some",
    "something",
    "that",
    "the",
    "to",
    "want",
    "with",
}

GENRE_KEYWORDS = {
    "ambient": {"ambient"},
    "classical": {"classical", "orchestral", "piano"},
    "country": {"country"},
    "edm": {"edm", "electronic", "club"},
    "folk": {"folk", "acoustic-folk"},
    "hip hop": {"hiphop", "hip-hop", "rap", "bars"},
    "indie pop": {"indie", "indie-pop"},
    "jazz": {"jazz"},
    "latin": {"latin", "reggaeton"},
    "lofi": {"lofi", "lo-fi"},
    "metal": {"metal", "heavy"},
    "pop": {"pop"},
    "r&b": {"r&b", "rnb", "soul"},
    "rock": {"rock"},
    "synthwave": {"synthwave", "retro-wave"},
}

MOOD_KEYWORDS = {
    "aggressive": {"aggressive", "angry", "furious", "rage"},
    "calm": {"calm", "peaceful", "still", "gentle"},
    "celebratory": {"celebratory", "party", "festive"},
    "chill": {"chill", "mellow", "laid-back", "easygoing"},
    "confident": {"confident", "bold", "swagger"},
    "dreamy": {"dreamy", "ethereal", "floating"},
    "focused": {"focused", "focus", "concentration", "productive"},
    "happy": {"happy", "bright", "upbeat", "joyful"},
    "intense": {"intense", "hard", "powerful", "explosive"},
    "moody": {"moody", "brooding", "dark"},
    "nostalgic": {"nostalgic", "memory", "retro"},
    "playful": {"playful", "fun", "bouncy"},
    "relaxed": {"relaxed", "unwind", "easy"},
    "romantic": {"romantic", "love", "intimate"},
    "uplifting": {"uplifting", "hopeful", "inspiring"},
}

ACTIVITY_PROFILES = {
    "coding": {
        "activity_tags": ("coding", "focus", "late-night"),
        "desired_tags": ("focused", "study", "calm"),
        "target_energy": 0.38,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "study": {
        "activity_tags": ("study", "reading", "focus"),
        "desired_tags": ("focused", "calm", "soft"),
        "target_energy": 0.34,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "writing": {
        "activity_tags": ("writing", "focus", "reflection"),
        "desired_tags": ("focused", "warm", "steady"),
        "target_energy": 0.42,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "reading": {
        "activity_tags": ("reading", "calm", "focus"),
        "desired_tags": ("calm", "soft", "acoustic"),
        "target_energy": 0.30,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "sleep": {
        "activity_tags": ("sleep", "meditation", "night"),
        "desired_tags": ("dreamy", "calm", "gentle"),
        "target_energy": 0.18,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "meditation": {
        "activity_tags": ("meditation", "reflection", "stillness"),
        "desired_tags": ("dreamy", "calm", "spacious"),
        "target_energy": 0.16,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
    "workout": {
        "activity_tags": ("workout", "gym", "push"),
        "desired_tags": ("energetic", "driving", "motivational"),
        "target_energy": 0.92,
        "likes_acoustic": False,
        "mode": "energy_focused",
    },
    "run": {
        "activity_tags": ("run", "workout", "drive"),
        "desired_tags": ("energetic", "driving", "uplifting"),
        "target_energy": 0.88,
        "likes_acoustic": False,
        "mode": "energy_focused",
    },
    "party": {
        "activity_tags": ("party", "dance", "celebration"),
        "desired_tags": ("euphoric", "dance", "celebratory"),
        "target_energy": 0.91,
        "likes_acoustic": False,
        "mode": "energy_focused",
    },
    "drive": {
        "activity_tags": ("drive", "commute", "movement"),
        "desired_tags": ("driving", "steady", "motion"),
        "target_energy": 0.68,
        "likes_acoustic": False,
        "mode": "balanced",
    },
    "journaling": {
        "activity_tags": ("journaling", "reflection", "nostalgia"),
        "desired_tags": ("nostalgic", "acoustic", "warm"),
        "target_energy": 0.28,
        "likes_acoustic": True,
        "mode": "mood_first",
    },
}

ACTIVITY_ALIASES = {
    "coding": {"coding", "programming", "developer"},
    "study": {"study", "studying", "homework"},
    "writing": {"writing", "drafting", "essay"},
    "reading": {"reading", "book"},
    "sleep": {"sleep", "sleeping", "bedtime"},
    "meditation": {"meditation", "breathing", "mindful"},
    "workout": {"workout", "gym", "exercise", "lifting", "training", "cardio"},
    "run": {"run", "running", "jog", "jogging"},
    "party": {"party", "dance", "club", "celebration"},
    "drive": {"drive", "driving", "commute", "roadtrip", "road-trip"},
    "journaling": {"journaling", "journal", "diary"},
}

EXCLUDE_KEYWORDS = {
    "instrumental": ("lyrics",),
    "no lyrics": ("lyrics",),
    "not too loud": ("aggressive", "extreme"),
    "not aggressive": ("aggressive", "extreme"),
    "soft acoustic": ("heavy-workout", "aggressive"),
}

NORMAL_DEFAULT_QUERY = "Find balanced recommendations for a general listener"
SONG_RETRIEVAL_WEIGHT = 2.4
SUPPORT_DOC_WEIGHT = 1.15
SUPPORT_DOC_MIN_SCORE = 0.35

RELIABILITY_BENCHMARKS = (
    {
        "name": "Focus Coding",
        "query": "Need calm music for late-night coding",
        "expected_titles": ("Midnight Coding", "Focus Flow", "Library Rain"),
        "expect_warning": False,
    },
    {
        "name": "Workout Boost",
        "query": "Need high-energy music for the gym",
        "expected_titles": ("Gym Hero", "Neon Pulse Circuit", "Iron Riot", "Storm Runner"),
        "expect_warning": False,
    },
    {
        "name": "Nostalgic Journaling",
        "query": "Play nostalgic acoustic music for journaling",
        "expected_titles": ("Fireside Letters", "Coffee Shop Stories", "Library Rain"),
        "expect_warning": False,
    },
    {
        "name": "Conflicted Classical Workout",
        "query": "Need classical music for an intense workout",
        "expected_titles": ("Glass Morning",),
        "expect_warning": True,
    },
)


@dataclass(frozen=True)
class ParsedIntent:
    request: str
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    activity_tags: Tuple[str, ...]
    desired_tags: Tuple[str, ...]
    exclude_tags: Tuple[str, ...]
    mode: str
    parser_notes: Tuple[str, ...]


@dataclass(frozen=True)
class RetrievedEvidence:
    song_id: int
    title: str
    retrieval_score: float
    matched_terms: Tuple[str, ...]
    evidence: Tuple[str, ...]
    descriptor: str


@dataclass(frozen=True)
class SupportDocument:
    document_id: str
    title: str
    keywords: Tuple[str, ...]
    activity_tags: Tuple[str, ...]
    desired_tags: Tuple[str, ...]
    target_energy: float
    likes_acoustic: bool
    mode: str
    evidence: Tuple[str, ...]


@dataclass(frozen=True)
class SupportMatch:
    document_id: str
    title: str
    retrieval_score: float
    matched_terms: Tuple[str, ...]
    activity_tags: Tuple[str, ...]
    desired_tags: Tuple[str, ...]
    target_energy: float
    likes_acoustic: bool
    recommended_mode: str
    evidence: Tuple[str, ...]


@dataclass(frozen=True)
class StyleCard:
    profile: str
    label: str
    match_tags: Tuple[str, ...]
    required_markers: Tuple[str, ...]
    signature_terms: Tuple[str, ...]
    examples: Tuple[str, ...]


@dataclass(frozen=True)
class AgentStep:
    step: int
    name: str
    summary: str
    detail: str


@dataclass(frozen=True)
class RecommendationRecord:
    song: Dict[str, Any]
    base_score: float
    retrieval_score: float
    final_score: float
    matched_terms: Tuple[str, ...]
    evidence: Tuple[str, ...]
    explanation: str
    specialized_explanation: str


@dataclass(frozen=True)
class ReliabilityReport:
    status: str
    grounded: bool
    consistency_ok: bool
    evidence_coverage: float
    warnings: Tuple[str, ...]


@dataclass(frozen=True)
class MusicAIResponse:
    query: str
    intent: ParsedIntent
    support_matches: Tuple[SupportMatch, ...]
    retrieved_items: Tuple[RetrievedEvidence, ...]
    recommendations: Tuple[RecommendationRecord, ...]
    reliability: ReliabilityReport
    agent_steps: Tuple[AgentStep, ...]
    specialization_profile: str
    log_path: str


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    query: str
    top_titles: Tuple[str, ...]
    hit_expected: bool
    expect_warning: bool
    warning_present: bool
    grounded: bool
    consistency_ok: bool


def load_song_knowledge(json_path: str = "data/song_knowledge_base.json") -> Dict[int, Dict[str, Any]]:
    """Load the local retrieval corpus keyed by song id."""
    with open(json_path, encoding="utf-8") as handle:
        raw_items = json.load(handle)
    return {int(item["song_id"]): item for item in raw_items}


def load_support_documents(json_path: str = "data/query_support_documents.json") -> Tuple[SupportDocument, ...]:
    """Load query-level support documents used as a second retrieval source."""
    path = Path(json_path)
    if not path.exists():
        return ()

    raw_items = json.loads(path.read_text(encoding="utf-8"))
    documents = []
    for item in raw_items:
        documents.append(
            SupportDocument(
                document_id=str(item["document_id"]),
                title=str(item["title"]),
                keywords=tuple(_dedupe(item.get("keywords", []))),
                activity_tags=tuple(_dedupe(item.get("activity_tags", []))),
                desired_tags=tuple(_dedupe(item.get("desired_tags", []))),
                target_energy=float(item.get("target_energy", 0.55)),
                likes_acoustic=bool(item.get("likes_acoustic", True)),
                mode=_normalize_mode_name(str(item.get("mode", "balanced"))),
                evidence=tuple(item.get("evidence", [])[:2]),
            )
        )
    return tuple(documents)


def load_style_cards(json_path: str = "data/style_cards.json") -> Tuple[StyleCard, ...]:
    """Load style cards that constrain listener-facing explanation tone."""
    path = Path(json_path)
    if not path.exists():
        return ()

    raw_items = json.loads(path.read_text(encoding="utf-8"))
    cards = []
    for item in raw_items:
        cards.append(
            StyleCard(
                profile=str(item["profile"]),
                label=str(item["label"]),
                match_tags=tuple(_dedupe(item.get("match_tags", []))),
                required_markers=tuple(item.get("required_markers", [])),
                signature_terms=tuple(item.get("signature_terms", [])),
                examples=tuple(item.get("examples", [])[:2]),
            )
        )
    return tuple(cards)


def parse_user_query(query: str, fallback_mode: str = "balanced") -> ParsedIntent:
    """Turn a natural-language request into structured recommendation intent."""
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        cleaned_query = NORMAL_DEFAULT_QUERY
        notes = ["empty request replaced with a balanced default prompt"]
    else:
        notes = []

    tokens = _tokenize_text(cleaned_query)
    favorite_genre = _match_keyword(tokens, GENRE_KEYWORDS)
    favorite_mood = _match_keyword(tokens, MOOD_KEYWORDS)

    activity_tags: List[str] = []
    desired_tags: List[str] = []
    energy_votes: List[float] = []
    acoustic_votes: List[bool] = []
    inferred_mode = _normalize_mode_name(fallback_mode)

    token_set = set(tokens)
    for activity_name, profile in ACTIVITY_PROFILES.items():
        aliases = ACTIVITY_ALIASES.get(activity_name, {activity_name})
        if aliases.intersection(token_set):
            activity_tags.extend(profile["activity_tags"])
            desired_tags.extend(profile["desired_tags"])
            energy_votes.append(float(profile["target_energy"]))
            acoustic_votes.append(bool(profile["likes_acoustic"]))
            inferred_mode = profile["mode"]
            notes.append(f"inferred {activity_name} profile from the request")

    explicit_energy = _infer_energy_from_tokens(tokens)
    if explicit_energy is not None:
        energy_votes.append(explicit_energy)
        notes.append("used explicit energy wording from the request")

    if "acoustic" in tokens or "instrumental" in tokens:
        acoustic_votes.append(True)
        desired_tags.append("acoustic")
        notes.append("request asked for acoustic or instrumental texture")
    if {"gym", "workout", "party", "club"}.intersection(tokens):
        acoustic_votes.append(False)

    exclude_tags = sorted({tag for phrase, tags in EXCLUDE_KEYWORDS.items() if phrase in cleaned_query.lower() for tag in tags})
    if exclude_tags:
        notes.append("captured exclusions from negative wording in the request")

    if favorite_genre:
        notes.append(f"detected genre preference: {favorite_genre}")
    if favorite_mood:
        notes.append(f"detected mood preference: {favorite_mood}")

    target_energy = _clamp(sum(energy_votes) / len(energy_votes), 0.0, 1.0) if energy_votes else 0.55
    likes_acoustic = _majority_vote(acoustic_votes, default=target_energy < 0.5)

    if not favorite_mood:
        if "focused" in desired_tags or "study" in desired_tags:
            favorite_mood = "focused"
        elif "calm" in desired_tags:
            favorite_mood = "chill"
        elif "energetic" in desired_tags or "motivational" in desired_tags:
            favorite_mood = "intense"
        elif "nostalgic" in desired_tags:
            favorite_mood = "nostalgic"
        else:
            favorite_mood = "happy"
        notes.append(f"filled missing mood with inferred default: {favorite_mood}")

    deduped_activities = tuple(_dedupe(activity_tags))
    deduped_desired = tuple(_dedupe([favorite_mood, *desired_tags, *tokens]))

    if favorite_genre and favorite_mood and inferred_mode == "balanced":
        inferred_mode = "genre_first"
    if "focused" in deduped_desired or "nostalgic" in deduped_desired:
        inferred_mode = "mood_first"
    if target_energy >= 0.82:
        inferred_mode = "energy_focused"

    return ParsedIntent(
        request=cleaned_query,
        favorite_genre=favorite_genre,
        favorite_mood=favorite_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
        activity_tags=deduped_activities,
        desired_tags=deduped_desired,
        exclude_tags=tuple(exclude_tags),
        mode=inferred_mode,
        parser_notes=tuple(notes),
    )


def retrieve_support_documents(
    query: str,
    support_documents: Sequence[SupportDocument],
    *,
    intent: Optional[ParsedIntent] = None,
    top_n: int = 3,
) -> List[SupportMatch]:
    """Retrieve support documents that expand ambiguous or synonym-heavy requests."""
    if not support_documents:
        return []

    parsed_intent = intent or parse_user_query(query)
    normalized_query = (query or "").lower()
    query_terms = set(_tokenize_text(query))
    query_terms.update(parsed_intent.activity_tags)
    query_terms.update(parsed_intent.desired_tags)
    if parsed_intent.favorite_genre:
        query_terms.add(parsed_intent.favorite_genre)
    if parsed_intent.favorite_mood:
        query_terms.add(parsed_intent.favorite_mood)

    scored_documents: List[Tuple[float, SupportMatch]] = []
    for document in support_documents:
        doc_terms = _build_support_document_terms(document)
        matched_terms = sorted(term for term in query_terms if term in doc_terms)
        phrase_hits = sum(1 for keyword in document.keywords if keyword.lower() in normalized_query)
        score = (phrase_hits * 1.25) + (len(matched_terms) * 0.45)

        if parsed_intent.favorite_mood and parsed_intent.favorite_mood in document.desired_tags:
            score += 0.25
        if set(parsed_intent.activity_tags).intersection(document.activity_tags):
            score += 0.45

        if score <= 0.0:
            continue

        scored_documents.append(
            (
                score,
                SupportMatch(
                    document_id=document.document_id,
                    title=document.title,
                    retrieval_score=0.0,
                    matched_terms=tuple(matched_terms[:6]),
                    activity_tags=document.activity_tags,
                    desired_tags=document.desired_tags,
                    target_energy=document.target_energy,
                    likes_acoustic=document.likes_acoustic,
                    recommended_mode=document.mode,
                    evidence=document.evidence,
                ),
            )
        )

    max_score = max((score for score, _ in scored_documents), default=0.0)
    results: List[SupportMatch] = []
    for raw_score, item in sorted(scored_documents, key=lambda pair: pair[0], reverse=True)[:top_n]:
        normalized = raw_score / max_score if max_score else 0.0
        results.append(
            SupportMatch(
                document_id=item.document_id,
                title=item.title,
                retrieval_score=normalized,
                matched_terms=item.matched_terms,
                activity_tags=item.activity_tags,
                desired_tags=item.desired_tags,
                target_energy=item.target_energy,
                likes_acoustic=item.likes_acoustic,
                recommended_mode=item.recommended_mode,
                evidence=item.evidence,
            )
        )
    return results


def retrieve_song_evidence(
    query: str,
    songs: Sequence[Dict[str, Any]],
    knowledge_base: Dict[int, Dict[str, Any]],
    *,
    intent: Optional[ParsedIntent] = None,
    top_n: int = 6,
) -> List[RetrievedEvidence]:
    """Retrieve the most relevant supporting song documents for a user request."""
    parsed_intent = intent or parse_user_query(query)
    query_terms = set(_tokenize_text(parsed_intent.request))
    query_terms.update(parsed_intent.activity_tags)
    query_terms.update(parsed_intent.desired_tags)
    if parsed_intent.favorite_genre:
        query_terms.add(parsed_intent.favorite_genre)
    if parsed_intent.favorite_mood:
        query_terms.add(parsed_intent.favorite_mood)

    scored_items: List[Tuple[float, RetrievedEvidence]] = []

    for song in songs:
        doc = knowledge_base.get(int(song["id"]), {})
        doc_terms = set(_build_document_terms(song, doc))
        matched_terms = sorted(term for term in query_terms if term in doc_terms)
        score = 0.0

        if parsed_intent.favorite_genre:
            score += 2.1 if _genre_matches(parsed_intent.favorite_genre, str(song["genre"])) else 0.0
        if parsed_intent.favorite_mood:
            song_tags = set(_tokenize_text(str(song.get("mood_tags", ""))))
            song_tags.add(str(song.get("mood", "")).lower())
            if parsed_intent.favorite_mood in song_tags:
                score += 1.6
        activity_overlap = len(set(parsed_intent.activity_tags).intersection(doc_terms))
        desired_overlap = len(set(parsed_intent.desired_tags).intersection(doc_terms))
        query_overlap = len(matched_terms)
        score += activity_overlap * 1.2
        score += desired_overlap * 0.45
        score += query_overlap * 0.18
        score += _energy_band_alignment(parsed_intent.target_energy, float(song["energy"])) * 0.9

        exclude_overlap = len(set(parsed_intent.exclude_tags).intersection(doc_terms))
        score -= exclude_overlap * 1.35

        evidence_lines = tuple(doc.get("evidence", [])[:2])
        descriptor = str(doc.get("descriptor", ""))

        scored_items.append(
            (
                max(score, 0.0),
                RetrievedEvidence(
                    song_id=int(song["id"]),
                    title=str(song["title"]),
                    retrieval_score=0.0,
                    matched_terms=tuple(matched_terms[:6]),
                    evidence=evidence_lines,
                    descriptor=descriptor,
                ),
            )
        )

    max_score = max((score for score, _ in scored_items), default=0.0)
    retrieved_items: List[RetrievedEvidence] = []
    for raw_score, item in sorted(scored_items, key=lambda pair: pair[0], reverse=True)[:top_n]:
        normalized = raw_score / max_score if max_score else 0.0
        retrieved_items.append(
            RetrievedEvidence(
                song_id=item.song_id,
                title=item.title,
                retrieval_score=normalized,
                matched_terms=item.matched_terms,
                evidence=item.evidence,
                descriptor=item.descriptor,
            )
        )
    return retrieved_items


def run_music_ai_system(
    query: str,
    *,
    songs_path: str = "data/songs.csv",
    knowledge_base_path: str = "data/song_knowledge_base.json",
    top_k: int = 5,
    mode: Optional[str] = None,
    diversity: bool = True,
    log_dir: str = "logs/music_ai_runs",
    enable_logging: bool = True,
    use_support_docs: bool = True,
    support_docs_path: str = "data/query_support_documents.json",
    specialization: str = "off",
    style_cards_path: str = "data/style_cards.json",
    _skip_consistency_check: bool = False,
) -> MusicAIResponse:
    """End-to-end music recommendation pipeline with retrieval and self-checks."""
    safe_top_k = max(1, min(int(top_k), 10))
    songs = load_songs(songs_path)
    knowledge_base = load_song_knowledge(knowledge_base_path)
    support_documents = load_support_documents(support_docs_path) if use_support_docs else ()
    style_cards = load_style_cards(style_cards_path) if specialization != "off" else ()

    agent_steps: List[AgentStep] = []
    initial_intent = parse_user_query(query, fallback_mode=mode or "balanced")
    _append_agent_step(
        agent_steps,
        "parse_query",
        f"Parsed genre={initial_intent.favorite_genre or 'any'}, mood={initial_intent.favorite_mood}, energy={initial_intent.target_energy:.2f}.",
        "; ".join(initial_intent.parser_notes) or "No special parser notes.",
    )

    parsed_intent = initial_intent
    support_matches: List[SupportMatch] = []
    if support_documents:
        support_matches = retrieve_support_documents(
            initial_intent.request,
            support_documents,
            intent=initial_intent,
            top_n=3,
        )
        if support_matches:
            _append_agent_step(
                agent_steps,
                "retrieve_support_docs",
                "Matched extra query-support documents to widen the retrieval context.",
                "; ".join(
                    f"{item.title} ({', '.join(item.matched_terms) or 'phrase match'})"
                    for item in support_matches
                ),
            )
            enriched_intent = _enrich_intent_with_support_docs(initial_intent, support_matches)
            if enriched_intent != initial_intent:
                parsed_intent = enriched_intent
                _append_agent_step(
                    agent_steps,
                    "plan_with_support_docs",
                    f"Expanded the plan to activity tags: {', '.join(parsed_intent.activity_tags) or 'none'}.",
                    f"Mode={parsed_intent.mode}; target_energy={parsed_intent.target_energy:.2f}; likes_acoustic={parsed_intent.likes_acoustic}.",
                )

    active_mode = _normalize_mode_name(mode or parsed_intent.mode)
    if active_mode != parsed_intent.mode:
        _append_agent_step(
            agent_steps,
            "lock_mode",
            f"Using explicit mode override: {active_mode}.",
            "The caller overrode the inferred mode selection.",
        )

    retrieved_items = retrieve_song_evidence(
        parsed_intent.request,
        songs,
        knowledge_base,
        intent=parsed_intent,
        top_n=len(songs),
    )
    _append_agent_step(
        agent_steps,
        "retrieve_song_evidence",
        "Retrieved song-level evidence from the knowledge base.",
        ", ".join(item.title for item in retrieved_items[:3]) or "No evidence hits.",
    )

    support_adjustments, support_reason_lookup = _build_support_song_adjustments(
        songs=songs,
        knowledge_base=knowledge_base,
        support_matches=support_matches,
    )

    score_adjustments: Dict[int, float] = {}
    extra_reason_parts: Dict[int, List[str]] = {}
    retrieval_lookup = {item.song_id: item for item in retrieved_items}

    for item in retrieved_items:
        song_id = item.song_id
        song_bonus = round(SONG_RETRIEVAL_WEIGHT * item.retrieval_score, 4)
        score_adjustments[song_id] = score_adjustments.get(song_id, 0.0) + song_bonus
        matched = ", ".join(item.matched_terms[:4]) if item.matched_terms else "context match"
        evidence_hint = item.evidence[0] if item.evidence else item.descriptor
        extra_reason_parts.setdefault(song_id, []).append(
            f"retrieval evidence bonus (+{song_bonus:.2f}); matched terms: {matched}; evidence: {evidence_hint}"
        )

    for song_id, support_score in support_adjustments.items():
        support_bonus = round(SUPPORT_DOC_WEIGHT * support_score, 4)
        score_adjustments[song_id] = score_adjustments.get(song_id, 0.0) + support_bonus
        guide_titles = ", ".join(support_reason_lookup.get(song_id, ()))
        extra_reason_parts.setdefault(song_id, []).append(
            f"support doc bonus (+{support_bonus:.2f}); guides: {guide_titles or 'support document match'}"
        )

    extra_reasons = {
        song_id: "; ".join(parts)
        for song_id, parts in extra_reason_parts.items()
    }

    user_prefs = {
        "favorite_genre": parsed_intent.favorite_genre,
        "favorite_mood": parsed_intent.favorite_mood,
        "target_energy": parsed_intent.target_energy,
        "likes_acoustic": parsed_intent.likes_acoustic,
    }

    all_ranked = recommend_songs(
        user_prefs,
        songs,
        k=len(songs),
        mode=active_mode,
        diversity=diversity,
        score_adjustments=score_adjustments,
        extra_reasons=extra_reasons,
    )
    ranked = _apply_genre_coverage_safeguard(all_ranked, parsed_intent.favorite_genre, safe_top_k)

    base_score_lookup = {
        int(song["id"]): score_song(user_prefs, song, mode=active_mode)[0]
        for song in songs
    }

    specialization_profile = _resolve_specialization_profile(
        specialization=specialization,
        parsed_intent=parsed_intent,
        style_cards=style_cards,
    )
    style_lookup = {card.profile: card for card in style_cards}

    recommendations: List[RecommendationRecord] = []
    for song, final_score, explanation in ranked:
        evidence_item = retrieval_lookup.get(int(song["id"]))
        retrieval_score = evidence_item.retrieval_score if evidence_item else 0.0
        specialized_explanation = ""
        if specialization_profile != "off":
            style_card = style_lookup.get(specialization_profile)
            specialized_explanation = _compose_specialized_explanation(
                song=song,
                parsed_intent=parsed_intent,
                matched_terms=evidence_item.matched_terms if evidence_item else (),
                evidence=evidence_item.evidence if evidence_item else (),
                style_card=style_card,
            )
        recommendations.append(
            RecommendationRecord(
                song=song,
                base_score=base_score_lookup[int(song["id"])],
                retrieval_score=retrieval_score,
                final_score=final_score,
                matched_terms=evidence_item.matched_terms if evidence_item else (),
                evidence=evidence_item.evidence if evidence_item else (),
                explanation=explanation,
                specialized_explanation=specialized_explanation,
            )
        )

    _append_agent_step(
        agent_steps,
        "rank_recommendations",
        "Fused metadata scoring with song evidence and support-document bonuses.",
        ", ".join(item.song["title"] for item in recommendations[:3]) or "No recommendations generated.",
    )

    if specialization_profile != "off":
        _append_agent_step(
            agent_steps,
            "specialize_explanations",
            f"Applied the {specialization_profile} style card to listener-facing explanations.",
            "Each recommendation now includes constrained Best for / Why it fits / Watch-out phrasing.",
        )

    if not _skip_consistency_check:
        comparison = run_music_ai_system(
            query,
            songs_path=songs_path,
            knowledge_base_path=knowledge_base_path,
            top_k=safe_top_k,
            mode=active_mode,
            diversity=diversity,
            log_dir=log_dir,
            enable_logging=False,
            use_support_docs=use_support_docs,
            support_docs_path=support_docs_path,
            specialization=specialization,
            style_cards_path=style_cards_path,
            _skip_consistency_check=True,
        )
        reliability = _evaluate_reliability(
            parsed_intent=parsed_intent,
            songs=songs,
            recommendations=recommendations,
            comparison_recommendations=comparison.recommendations,
        )
    else:
        reliability = _evaluate_reliability(
            parsed_intent=parsed_intent,
            songs=songs,
            recommendations=recommendations,
            comparison_recommendations=recommendations,
        )

    _append_agent_step(
        agent_steps,
        "self_check",
        f"Reliability status={reliability.status}, grounded={reliability.grounded}, consistent={reliability.consistency_ok}.",
        "; ".join(reliability.warnings) or "No warnings emitted.",
    )

    log_path = ""
    response = MusicAIResponse(
        query=parsed_intent.request,
        intent=parsed_intent,
        support_matches=tuple(support_matches),
        retrieved_items=tuple(retrieved_items),
        recommendations=tuple(recommendations),
        reliability=reliability,
        agent_steps=tuple(agent_steps),
        specialization_profile=specialization_profile,
        log_path=log_path,
    )

    if enable_logging:
        log_path = _write_run_log(response, log_dir)
        response = MusicAIResponse(
            query=response.query,
            intent=response.intent,
            support_matches=response.support_matches,
            retrieved_items=response.retrieved_items,
            recommendations=response.recommendations,
            reliability=response.reliability,
            agent_steps=response.agent_steps,
            specialization_profile=response.specialization_profile,
            log_path=log_path,
        )

    return response


def run_reliability_suite(
    *,
    songs_path: str = "data/songs.csv",
    knowledge_base_path: str = "data/song_knowledge_base.json",
) -> List[BenchmarkResult]:
    """Run benchmark prompts that exercise grounding, warnings, and consistency."""
    results: List[BenchmarkResult] = []
    for benchmark in RELIABILITY_BENCHMARKS:
        response = run_music_ai_system(
            benchmark["query"],
            songs_path=songs_path,
            knowledge_base_path=knowledge_base_path,
            top_k=3,
            enable_logging=False,
        )
        top_titles = tuple(item.song["title"] for item in response.recommendations[:3])
        hit_expected = any(title in benchmark["expected_titles"] for title in top_titles)
        warning_present = bool(response.reliability.warnings)
        results.append(
            BenchmarkResult(
                name=str(benchmark["name"]),
                query=str(benchmark["query"]),
                top_titles=top_titles,
                hit_expected=hit_expected,
                expect_warning=bool(benchmark["expect_warning"]),
                warning_present=warning_present,
                grounded=response.reliability.grounded,
                consistency_ok=response.reliability.consistency_ok,
            )
        )
    return results


def format_intent_summary(intent: ParsedIntent) -> str:
    """Render the parsed intent for terminal output."""
    return (
        f"genre={intent.favorite_genre or 'any'}, "
        f"mood={intent.favorite_mood}, "
        f"energy={intent.target_energy:.2f}, "
        f"likes_acoustic={intent.likes_acoustic}, "
        f"mode={intent.mode}"
    )


def format_support_rows(items: Sequence[SupportMatch]) -> List[Dict[str, str]]:
    """Convert support-document retrieval results into table-ready rows."""
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append(
            {
                "rank": index,
                "document": item.title,
                "score": f"{item.retrieval_score:.2f}",
                "matches": ", ".join(item.matched_terms) or "phrase match",
                "evidence": item.evidence[0] if item.evidence else "No support evidence",
            }
        )
    return rows


def format_retrieval_rows(items: Sequence[RetrievedEvidence]) -> List[Dict[str, str]]:
    """Convert retrieval results into table-ready rows."""
    rows = []
    for index, item in enumerate(items, start=1):
        rows.append(
            {
                "rank": index,
                "song": item.title,
                "score": f"{item.retrieval_score:.2f}",
                "matches": ", ".join(item.matched_terms) or "context match",
                "evidence": item.evidence[0] if item.evidence else item.descriptor,
            }
        )
    return rows


def format_agent_steps(steps: Sequence[AgentStep]) -> List[str]:
    """Render agent steps as readable bullet strings for the CLI."""
    return [f"{step.step}. {step.name}: {step.summary} {step.detail}".strip() for step in steps]


def format_reliability_summary(report: ReliabilityReport) -> str:
    """Render the reliability report for CLI output."""
    warning_text = "; ".join(report.warnings) if report.warnings else "none"
    return (
        f"status={report.status}; grounded={report.grounded}; "
        f"consistency={report.consistency_ok}; evidence_coverage={report.evidence_coverage:.2f}; "
        f"warnings={warning_text}"
    )


def format_benchmark_rows(results: Sequence[BenchmarkResult]) -> List[Dict[str, str]]:
    """Convert reliability benchmark results into table-ready rows."""
    rows = []
    for result in results:
        rows.append(
            {
                "scenario": result.name,
                "expected": "pass" if result.hit_expected else "review",
                "warning": "ok" if result.warning_present == result.expect_warning else "mismatch",
                "grounded": "yes" if result.grounded else "no",
                "consistent": "yes" if result.consistency_ok else "no",
                "top_titles": ", ".join(result.top_titles),
            }
        )
    return rows


def _evaluate_reliability(
    *,
    parsed_intent: ParsedIntent,
    songs: Sequence[Dict[str, Any]],
    recommendations: Sequence[RecommendationRecord],
    comparison_recommendations: Sequence[RecommendationRecord],
) -> ReliabilityReport:
    coverage_hits = sum(1 for item in recommendations if item.evidence)
    evidence_coverage = coverage_hits / len(recommendations) if recommendations else 0.0
    grounded = all("retrieval evidence bonus" in item.explanation for item in recommendations)

    top_ids = tuple(int(item.song["id"]) for item in recommendations)
    comparison_ids = tuple(int(item.song["id"]) for item in comparison_recommendations)
    consistency_ok = top_ids == comparison_ids

    warnings: List[str] = []
    if parsed_intent.favorite_genre and not any(
        _genre_matches(parsed_intent.favorite_genre, str(item.song["genre"])) for item in recommendations
    ):
        warnings.append(
            f"catalog coverage is limited for the requested genre '{parsed_intent.favorite_genre}'"
        )
    if parsed_intent.target_energy >= 0.8 and parsed_intent.likes_acoustic:
        warnings.append("request combines very high energy with acoustic texture, which is sparse in the catalog")
    if evidence_coverage < 1.0:
        warnings.append("some recommendations did not have retrieved evidence attached")
    if any(tag in {"lyrics"} for tag in parsed_intent.exclude_tags):
        lyrical_hits = [
            item.song["title"]
            for item in recommendations
            if float(item.song.get("lyrical_density", 0.0)) > 0.55
        ]
        if lyrical_hits:
            warnings.append(
                "the catalog has limited fully instrumental coverage, so some picks still contain strong lyrics"
            )

    genre_inventory = {
        str(song["genre"]).lower()
        for song in songs
        if parsed_intent.favorite_genre and _genre_matches(parsed_intent.favorite_genre, str(song["genre"]))
    }
    if parsed_intent.favorite_genre and len(genre_inventory) <= 1 and parsed_intent.target_energy >= 0.8:
        warnings.append("the requested genre and energy combination has very thin catalog support")

    status = "pass" if grounded and consistency_ok and not warnings else "review"
    return ReliabilityReport(
        status=status,
        grounded=grounded,
        consistency_ok=consistency_ok,
        evidence_coverage=evidence_coverage,
        warnings=tuple(warnings),
    )


def _write_run_log(response: MusicAIResponse, log_dir: str) -> str:
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = _slugify(response.query)[:40] or "music-run"
    log_path = target_dir / f"{timestamp}-{slug}.json"
    payload = {
        "query": response.query,
        "intent": asdict(response.intent),
        "support_matches": [asdict(item) for item in response.support_matches],
        "retrieved_items": [asdict(item) for item in response.retrieved_items],
        "recommendations": [asdict(item) for item in response.recommendations],
        "reliability": asdict(response.reliability),
        "agent_steps": [asdict(step) for step in response.agent_steps],
        "specialization_profile": response.specialization_profile,
        "available_modes": available_modes(),
    }
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return str(log_path)


def _append_agent_step(steps: List[AgentStep], name: str, summary: str, detail: str) -> None:
    steps.append(
        AgentStep(
            step=len(steps) + 1,
            name=name,
            summary=summary,
            detail=detail,
        )
    )


def _match_keyword(tokens: Iterable[str], keyword_map: Dict[str, set[str]]) -> str:
    token_set = set(tokens)
    for canonical, aliases in keyword_map.items():
        if aliases.intersection(token_set):
            return canonical
    return ""


def _tokenize_text(text: str) -> List[str]:
    raw_tokens = re.findall(r"[a-z0-9&]+", (text or "").lower())
    tokens = [token for token in raw_tokens if token not in STOPWORDS]
    expanded: List[str] = []
    for token in tokens:
        if token == "hip":
            continue
        if token == "hop":
            continue
        expanded.append(token)
    return expanded


def _infer_energy_from_tokens(tokens: Sequence[str]) -> Optional[float]:
    token_set = set(tokens)
    if {"high", "intense", "explosive", "hype", "adrenaline"}.intersection(token_set):
        return 0.92
    if {"upbeat", "bright", "driving", "fast"}.intersection(token_set):
        return 0.76
    if {"calm", "soft", "quiet", "gentle", "sleep"}.intersection(token_set):
        return 0.24
    if {"steady", "focused", "mellow", "nostalgic"}.intersection(token_set):
        return 0.42
    return None


def _majority_vote(values: Sequence[bool], *, default: bool) -> bool:
    if not values:
        return default
    positives = sum(1 for value in values if value)
    negatives = len(values) - positives
    return positives >= negatives


def _normalize_mode_name(mode: str) -> str:
    normalized = (mode or "balanced").strip().lower().replace(" ", "_")
    return MODE_ALIASES.get(normalized, "balanced")


def _dedupe(items: Sequence[str]) -> List[str]:
    seen = set()
    ordered = []
    for item in items:
        cleaned = item.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)
    return ordered


def _build_document_terms(song: Dict[str, Any], document: Dict[str, Any]) -> List[str]:
    fields: List[str] = [
        str(song.get("title", "")),
        str(song.get("artist", "")),
        str(song.get("genre", "")),
        str(song.get("mood", "")),
        str(song.get("mood_tags", "")),
        str(document.get("descriptor", "")),
        " ".join(document.get("activity_tags", [])),
        " ".join(document.get("scene_tags", [])),
        " ".join(document.get("avoid_for", [])),
        " ".join(document.get("evidence", [])),
    ]
    terms: List[str] = []
    for field in fields:
        terms.extend(_tokenize_text(field.replace("-", " ")))
    return terms


def _build_support_document_terms(document: SupportDocument) -> set[str]:
    fields = [
        document.title,
        " ".join(document.keywords),
        " ".join(document.activity_tags),
        " ".join(document.desired_tags),
        " ".join(document.evidence),
    ]
    terms: List[str] = []
    for field in fields:
        terms.extend(_tokenize_text(field.replace("-", " ")))
    return set(terms)


def _enrich_intent_with_support_docs(intent: ParsedIntent, support_matches: Sequence[SupportMatch]) -> ParsedIntent:
    eligible_matches = [item for item in support_matches if item.retrieval_score >= SUPPORT_DOC_MIN_SCORE]
    if not eligible_matches:
        return intent

    notes = list(intent.parser_notes)
    activity_tags = list(intent.activity_tags)
    desired_tags = list(intent.desired_tags)
    weighted_energy = intent.target_energy * 1.4
    total_weight = 1.4
    acoustic_score = 1.2 if intent.likes_acoustic else -1.2
    inferred_mood = intent.favorite_mood
    mood_was_default = any("filled missing mood with inferred default" in note for note in intent.parser_notes)
    mode_votes: List[Tuple[str, float]] = [(intent.mode, 1.0)]

    for match in eligible_matches:
        weight = 0.7 + match.retrieval_score
        activity_tags.extend(match.activity_tags)
        desired_tags.extend(match.desired_tags)
        weighted_energy += match.target_energy * weight
        total_weight += weight
        acoustic_score += weight if match.likes_acoustic else -weight
        mode_votes.append((match.recommended_mode, weight))
        notes.append(f"support doc '{match.title}' expanded the request context")

        if mood_was_default:
            supported_moods = [tag for tag in match.desired_tags if tag in MOOD_KEYWORDS]
            if supported_moods:
                inferred_mood = supported_moods[0]

    active_mode = max(mode_votes, key=lambda item: item[1])[0]
    if inferred_mood != intent.favorite_mood:
        notes.append(f"support docs refined the fallback mood to {inferred_mood}")

    return ParsedIntent(
        request=intent.request,
        favorite_genre=intent.favorite_genre,
        favorite_mood=inferred_mood,
        target_energy=_clamp(weighted_energy / total_weight, 0.0, 1.0),
        likes_acoustic=acoustic_score >= 0.0,
        activity_tags=tuple(_dedupe(activity_tags)),
        desired_tags=tuple(_dedupe([inferred_mood, *desired_tags])),
        exclude_tags=intent.exclude_tags,
        mode=active_mode,
        parser_notes=tuple(_dedupe(notes)),
    )


def _build_support_song_adjustments(
    *,
    songs: Sequence[Dict[str, Any]],
    knowledge_base: Dict[int, Dict[str, Any]],
    support_matches: Sequence[SupportMatch],
) -> Tuple[Dict[int, float], Dict[int, Tuple[str, ...]]]:
    eligible_matches = [item for item in support_matches if item.retrieval_score >= SUPPORT_DOC_MIN_SCORE]
    if not eligible_matches:
        return {}, {}

    raw_scores: Dict[int, float] = {}
    reason_titles: Dict[int, Tuple[str, ...]] = {}
    for song in songs:
        song_id = int(song["id"])
        song_terms = set(_build_document_terms(song, knowledge_base.get(song_id, {})))
        total = 0.0
        supporting_docs: List[str] = []

        for match in eligible_matches:
            support_terms = set(match.activity_tags).union(match.desired_tags).union(match.matched_terms)
            overlap = len(support_terms.intersection(song_terms))
            if overlap == 0:
                continue
            supporting_docs.append(match.title)
            total += match.retrieval_score * (
                (overlap * 0.28) + (_energy_band_alignment(match.target_energy, float(song["energy"])) * 0.55)
            )

        if total > 0.0:
            raw_scores[song_id] = total
            reason_titles[song_id] = tuple(_dedupe(supporting_docs))

    max_score = max(raw_scores.values(), default=0.0)
    if not max_score:
        return {}, {}

    normalized_scores = {
        song_id: raw_score / max_score
        for song_id, raw_score in raw_scores.items()
    }
    return normalized_scores, reason_titles


def _resolve_specialization_profile(
    *,
    specialization: str,
    parsed_intent: ParsedIntent,
    style_cards: Sequence[StyleCard],
) -> str:
    normalized = (specialization or "off").strip().lower().replace("-", "_")
    if normalized in {"off", "none", "baseline"} or not style_cards:
        return "off"

    available_profiles = {card.profile for card in style_cards}
    if normalized != "auto":
        return normalized if normalized in available_profiles else "off"

    request_tags = set(parsed_intent.activity_tags).union(parsed_intent.desired_tags)
    best_card = None
    best_score = 0
    for card in style_cards:
        score = len(request_tags.intersection(card.match_tags))
        if score > best_score:
            best_card = card
            best_score = score

    if best_card is not None and best_score > 0:
        return best_card.profile
    if parsed_intent.target_energy >= 0.82:
        return "hype_trainer" if "hype_trainer" in available_profiles else "off"
    if {"nostalgic", "reflection", "calm", "unwind"}.intersection(request_tags):
        return "reflective_curator" if "reflective_curator" in available_profiles else "off"
    if {"focus", "coding", "study", "late-night"}.intersection(request_tags):
        return "focus_coach" if "focus_coach" in available_profiles else "off"
    return "off"


def _compose_specialized_explanation(
    *,
    song: Dict[str, Any],
    parsed_intent: ParsedIntent,
    matched_terms: Sequence[str],
    evidence: Sequence[str],
    style_card: Optional[StyleCard],
) -> str:
    if style_card is None:
        return ""

    activity_tags = set(parsed_intent.activity_tags)
    evidence_text = evidence[0] if evidence else "metadata alignment and retrieval grounding"
    context_terms = ", ".join(matched_terms[:3]) if matched_terms else parsed_intent.favorite_mood

    if style_card.profile == "focus_coach":
        best_for = "heads-down work, reading, or low-distraction concentration"
        why = (
            f"steady lane energy and low-distraction texture line up with {context_terms}; "
            f"evidence points to reliable focus support"
        )
        watch_out = "if you want a big adrenaline lift, this can feel too gentle"
    elif style_card.profile == "hype_trainer":
        best_for = "high-output movement, intervals, or push-pace momentum"
        why = (
            f"high energy plus driving motion cues match {context_terms}; "
            f"evidence highlights momentum and effort"
        )
        watch_out = "this is a poor fit for quiet study or late-night unwinding"
    else:
        reflective_focus = "memory-rich reflection" if "nostalgic" in parsed_intent.desired_tags else "slow-burn downtime"
        best_for = f"{reflective_focus}, journaling, or a soft evening reset"
        why = (
            f"warm, human-scale texture lines up with {context_terms}; "
            f"evidence emphasizes gentle atmosphere"
        )
        watch_out = "if you need speed or impact, this may drift too softly"

    return (
        f"{style_card.label}. "
        f"Best for: {best_for}. "
        f"Why it fits: {why}. "
        f"Watch-out: {watch_out}. "
        f"Evidence cue: {evidence_text}"
    )


def _energy_band_alignment(requested_energy: float, song_energy: float) -> float:
    return max(0.0, 1 - abs(requested_energy - song_energy))


def _genre_matches(requested_genre: str, song_genre: str) -> bool:
    request = requested_genre.strip().lower()
    candidate = song_genre.strip().lower()
    return bool(request and (request == candidate or request in candidate or candidate in request))


def _apply_genre_coverage_safeguard(
    ranked_items: Sequence[Tuple[Dict[str, Any], float, str]],
    requested_genre: str,
    top_k: int,
) -> List[Tuple[Dict[str, Any], float, str]]:
    selected = list(ranked_items[:top_k])
    if not requested_genre:
        return selected
    if any(_genre_matches(requested_genre, str(song["genre"])) for song, _, _ in selected):
        return selected

    fallback = next(
        (
            item
            for item in ranked_items[top_k:]
            if _genre_matches(requested_genre, str(item[0]["genre"]))
        ),
        None,
    )
    if fallback is None:
        return selected

    song, score, explanation = fallback
    safeguard_reason = (
        f"{explanation}; genre coverage safeguard (+0.00); inserted to preserve the explicit genre request"
    )
    if selected:
        selected[-1] = (song, score, safeguard_reason)
    else:
        selected.append((song, score, safeguard_reason))
    return selected


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "music-run"
