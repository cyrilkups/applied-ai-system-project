import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ScoreTargets:
    """Target values that shape one scoring mode."""

    popularity: float
    instrumentalness: float
    live_energy: float
    lyrical_density: float
    preferred_decades: Tuple[int, ...] = ()
    bonus_tags: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DiversityConfig:
    """Penalty strengths used during diversity-aware reranking."""

    artist: float
    genre: float


@dataclass(frozen=True)
class ScoringMode:
    """Small strategy object that groups the rules for one ranking mode."""

    name: str
    label: str
    weights: Dict[str, float]
    targets: ScoreTargets
    diversity: DiversityConfig


DEFAULT_SCORING_WEIGHTS = {
    "genre": 2.0,
    "mood": 1.5,
    "energy": 2.0,
    "acoustic": 0.5,
}


MODE_CONFIGS = {
    "balanced": ScoringMode(
        name="balanced",
        label="Balanced",
        weights={
            "genre": 2.0,
            "mood": 1.5,
            "energy": 2.0,
            "acoustic": 0.5,
            "popularity": 0.9,
            "era": 0.8,
            "tags": 1.0,
            "instrumentalness": 0.5,
            "live_energy": 0.6,
            "lyrical_density": 0.6,
        },
        targets=ScoreTargets(
            popularity=65.0,
            instrumentalness=0.45,
            live_energy=0.45,
            lyrical_density=0.55,
            preferred_decades=(),
            bonus_tags=("uplifting", "chill", "focused", "nostalgic", "dreamy"),
        ),
        diversity=DiversityConfig(artist=0.45, genre=0.25),
    ),
    "genre_first": ScoringMode(
        name="genre_first",
        label="Genre-First",
        weights={
            "genre": 3.4,
            "mood": 1.1,
            "energy": 1.5,
            "acoustic": 0.4,
            "popularity": 0.8,
            "era": 0.9,
            "tags": 0.8,
            "instrumentalness": 0.4,
            "live_energy": 0.5,
            "lyrical_density": 0.45,
        },
        targets=ScoreTargets(
            popularity=60.0,
            instrumentalness=0.45,
            live_energy=0.5,
            lyrical_density=0.5,
            preferred_decades=(1990, 2000, 2010, 2020),
            bonus_tags=("anthemic", "uplifting", "driving", "party"),
        ),
        diversity=DiversityConfig(artist=0.5, genre=0.3),
    ),
    "mood_first": ScoringMode(
        name="mood_first",
        label="Mood-First",
        weights={
            "genre": 1.3,
            "mood": 3.1,
            "energy": 1.5,
            "acoustic": 0.7,
            "popularity": 0.7,
            "era": 0.8,
            "tags": 1.8,
            "instrumentalness": 0.5,
            "live_energy": 0.4,
            "lyrical_density": 0.9,
        },
        targets=ScoreTargets(
            popularity=58.0,
            instrumentalness=0.5,
            live_energy=0.35,
            lyrical_density=0.6,
            preferred_decades=(1970, 1980, 1990, 2000),
            bonus_tags=("nostalgic", "dreamy", "calm", "romantic", "focused"),
        ),
        diversity=DiversityConfig(artist=0.45, genre=0.25),
    ),
    "energy_focused": ScoringMode(
        name="energy_focused",
        label="Energy-Focused",
        weights={
            "genre": 1.2,
            "mood": 1.1,
            "energy": 3.7,
            "acoustic": 0.3,
            "popularity": 1.0,
            "era": 0.7,
            "tags": 1.1,
            "instrumentalness": 0.4,
            "live_energy": 1.7,
            "lyrical_density": 0.35,
        },
        targets=ScoreTargets(
            popularity=74.0,
            instrumentalness=0.25,
            live_energy=0.85,
            lyrical_density=0.45,
            preferred_decades=(2000, 2010, 2020),
            bonus_tags=("energetic", "driving", "motivational", "party", "euphoric"),
        ),
        diversity=DiversityConfig(artist=0.6, genre=0.35),
    ),
}

MODE_ALIASES = {
    "balanced": "balanced",
    "genre_first": "genre_first",
    "genre-first": "genre_first",
    "mood_first": "mood_first",
    "mood-first": "mood_first",
    "energy_focused": "energy_focused",
    "energy-focused": "energy_focused",
}


def available_modes() -> Tuple[str, ...]:
    """Return the CLI-visible scoring mode names."""
    return tuple(MODE_CONFIGS.keys())


def get_mode_config(mode: str) -> ScoringMode:
    """Resolve user input into the matching scoring mode configuration."""
    return MODE_CONFIGS[_normalize_mode(mode)]


def get_mode_label(mode: str) -> str:
    """Return the human-readable label for a scoring mode."""
    return get_mode_config(mode).label


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float = 0.0
    release_decade: int = 0
    mood_tags: str = ""
    instrumentalness: float = 0.0
    live_energy: float = 0.0
    lyrical_density: float = 0.0
    era_affinity: float = 0.0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        mode: str = "balanced",
        weights: Optional[Dict[str, float]] = None,
    ) -> List[Song]:
        """Return the top-k songs sorted by match score for one user."""
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        catalog = [_song_to_dict(song) for song in self.songs]
        ranked = recommend_songs(user_prefs, catalog, k=k, weights=weights, mode=mode)
        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[item[0]["id"]] for item in ranked if item[0]["id"] in songs_by_id]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "balanced") -> str:
        """Summarize why one song matches the user's profile."""
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, _song_to_dict(song), mode=mode)
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV and convert numeric fields to usable types."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"].strip().lower(),
                    "mood": row["mood"].strip().lower(),
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    "popularity": float(row.get("popularity", 0) or 0),
                    "release_decade": int(float(row.get("release_decade", 0) or 0)),
                    "mood_tags": row.get("mood_tags", ""),
                    "instrumentalness": float(row.get("instrumentalness", 0) or 0),
                    "live_energy": float(row.get("live_energy", 0) or 0),
                    "lyrical_density": float(row.get("lyrical_density", 0) or 0),
                    "era_affinity": float(row.get("era_affinity", 0) or 0),
                }
            )

    return songs


def score_song(
    user_prefs: Dict,
    song: Dict,
    weights: Optional[Dict[str, float]] = None,
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """Score one song and explain the feature matches behind the score."""
    prefs = _normalize_user_prefs(user_prefs)
    mode_config = get_mode_config(mode)
    active_weights = _resolve_weights(weights, mode_config)
    targets = mode_config.targets

    score = 0.0
    reasons: List[str] = []

    song_genre = _clean_text(song["genre"])
    song_mood = _clean_text(song["mood"])
    user_genre = _clean_text(prefs["favorite_genre"])
    user_mood = _clean_text(prefs["favorite_mood"])

    if song_genre and song_genre == user_genre:
        genre_weight = active_weights["genre"]
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight:.2f})")

    if song_mood and song_mood == user_mood:
        mood_weight = active_weights["mood"]
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight:.2f})")

    energy_score = max(
        0.0,
        active_weights["energy"] * (1 - abs(float(song["energy"]) - prefs["target_energy"])),
    )
    score += energy_score
    reasons.append(f"energy closeness (+{energy_score:.2f})")

    acousticness = float(song["acousticness"])
    if prefs["likes_acoustic"]:
        acoustic_score = active_weights["acoustic"] * acousticness
        reasons.append(f"acoustic preference (+{acoustic_score:.2f})")
    else:
        acoustic_score = active_weights["acoustic"] * (1 - acousticness)
        reasons.append(f"less-acoustic preference (+{acoustic_score:.2f})")
    score += acoustic_score

    popularity_score = _bounded_closeness(
        float(song.get("popularity", 0.0)),
        targets.popularity,
        active_weights["popularity"],
        100.0,
    )
    score += popularity_score
    reasons.append(f"popularity fit (+{popularity_score:.2f})")

    decade_score = _decade_alignment_score(
        int(song.get("release_decade", 0)),
        active_weights["era"],
        targets.preferred_decades,
    )
    era_affinity_score = active_weights["era"] * float(song.get("era_affinity", 0.0))
    score += decade_score + era_affinity_score
    reasons.append(f"release decade fit (+{decade_score:.2f})")
    reasons.append(f"era affinity (+{era_affinity_score:.2f})")

    tag_score = _mood_tag_score(
        song.get("mood_tags", ""),
        active_weights["tags"],
        user_mood,
        targets.bonus_tags,
    )
    score += tag_score
    reasons.append(f"mood tag overlap (+{tag_score:.2f})")

    instrumental_score = active_weights["instrumentalness"] * (
        1 - abs(float(song.get("instrumentalness", 0.0)) - targets.instrumentalness)
    )
    live_energy_score = active_weights["live_energy"] * (
        1 - abs(float(song.get("live_energy", 0.0)) - targets.live_energy)
    )
    lyrical_score = active_weights["lyrical_density"] * (
        1 - abs(float(song.get("lyrical_density", 0.0)) - targets.lyrical_density)
    )
    instrumental_score = max(0.0, instrumental_score)
    live_energy_score = max(0.0, live_energy_score)
    lyrical_score = max(0.0, lyrical_score)
    score += instrumental_score + live_energy_score + lyrical_score
    reasons.append(f"instrumentalness fit (+{instrumental_score:.2f})")
    reasons.append(f"live energy fit (+{live_energy_score:.2f})")
    reasons.append(f"lyrical density fit (+{lyrical_score:.2f})")

    return score, reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Optional[Dict[str, float]] = None,
    mode: str = "balanced",
    diversity: bool = True,
    score_adjustments: Optional[Dict[int, float]] = None,
    extra_reasons: Optional[Dict[int, str]] = None,
) -> List[Tuple[Dict, float, str]]:
    """Score the catalog, rank it, and return the top-k recommendations."""
    scored_recommendations = []
    score_adjustments = score_adjustments or {}
    extra_reasons = extra_reasons or {}

    for song in songs:
        score, reasons = score_song(user_prefs, song, weights=weights, mode=mode)
        song_id = int(song.get("id", -1))
        adjustment = float(score_adjustments.get(song_id, 0.0))
        if adjustment:
            score += adjustment
        extra_reason = extra_reasons.get(song_id)
        if extra_reason:
            reasons.append(extra_reason)
        explanation = "; ".join(reasons)
        scored_recommendations.append((song, score, explanation))

    if diversity:
        return _rerank_with_diversity(scored_recommendations, k, mode)

    ranked_recommendations = sorted(
        scored_recommendations,
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked_recommendations[:k]


def _normalize_user_prefs(user_prefs: Dict) -> Dict:
    """Support both starter keys and expanded profile keys for preferences."""
    return {
        "favorite_genre": user_prefs.get("favorite_genre", user_prefs.get("genre", "")),
        "favorite_mood": user_prefs.get("favorite_mood", user_prefs.get("mood", "")),
        "target_energy": float(user_prefs.get("target_energy", user_prefs.get("energy", 0.5))),
        "likes_acoustic": bool(user_prefs.get("likes_acoustic", user_prefs.get("acousticness", True))),
    }


def _resolve_weights(weights: Optional[Dict[str, float]], mode_config: ScoringMode) -> Dict[str, float]:
    """Merge any experimental weight overrides with the baseline recipe."""
    active_weights = mode_config.weights.copy()
    if weights:
        active_weights.update(weights)
    return active_weights


def _normalize_mode(mode: str) -> str:
    normalized = (mode or "balanced").strip().lower().replace(" ", "_")
    return MODE_ALIASES.get(normalized, "balanced")


def _clean_text(value: str) -> str:
    return (value or "").strip().lower()


def _bounded_closeness(value: float, target: float, weight: float, scale: float) -> float:
    return max(0.0, weight * (1 - abs(value - target) / scale))


def _parse_tags(raw_tags: str) -> List[str]:
    if not raw_tags:
        return []
    return [_clean_text(tag) for tag in raw_tags.split("|") if tag.strip()]


def _decade_alignment_score(song_decade: int, weight: float, preferred_decades: Tuple[int, ...]) -> float:
    if song_decade <= 0 or not preferred_decades:
        return weight * 0.15
    if song_decade in preferred_decades:
        return weight
    if any(abs(song_decade - decade) == 10 for decade in preferred_decades):
        return weight * 0.55
    return weight * 0.1


def _mood_tag_score(
    raw_tags: str,
    weight: float,
    song_mood: str,
    bonus_tags: Tuple[str, ...],
) -> float:
    tags = set(_parse_tags(raw_tags))
    if song_mood:
        tags.add(song_mood)

    if not tags:
        return 0.0

    preferred_tags = {tag for tag in bonus_tags if tag}
    preferred_tags.add(song_mood)
    matches = tags.intersection(preferred_tags)
    overlap_ratio = len(matches) / len(tags)
    return weight * overlap_ratio * 1.6


def _diversity_penalty(
    song: Dict,
    artist_counts: Dict[str, int],
    genre_counts: Dict[str, int],
    mode: str,
) -> Tuple[float, List[str]]:
    penalty_weights = get_mode_config(mode).diversity
    reasons: List[str] = []
    penalty = 0.0

    artist = _clean_text(song.get("artist", ""))
    genre = _clean_text(song.get("genre", ""))

    artist_hits = artist_counts.get(artist, 0)
    if artist_hits:
        artist_penalty = penalty_weights.artist * artist_hits
        penalty += artist_penalty
        reasons.append(f"repeated artist penalty (-{artist_penalty:.2f})")

    genre_hits = genre_counts.get(genre, 0)
    if genre_hits:
        genre_penalty = penalty_weights.genre * genre_hits
        penalty += genre_penalty
        reasons.append(f"repeated genre penalty (-{genre_penalty:.2f})")

    return penalty, reasons


def _rerank_with_diversity(
    scored_items: List[Tuple[Dict, float, str]],
    k: int,
    mode: str,
) -> List[Tuple[Dict, float, str]]:
    remaining = list(scored_items)
    selected: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    while remaining and len(selected) < k:
        best_index = 0
        best_adjusted_score = float("-inf")
        best_penalty_reasons: List[str] = []

        for index, (song, base_score, explanation) in enumerate(remaining):
            penalty, penalty_reasons = _diversity_penalty(song, artist_counts, genre_counts, mode)
            adjusted_score = base_score - penalty
            if adjusted_score > best_adjusted_score:
                best_index = index
                best_adjusted_score = adjusted_score
                best_penalty_reasons = penalty_reasons

        song, base_score, explanation = remaining.pop(best_index)
        final_explanation = explanation
        if best_penalty_reasons:
            final_explanation = f"{explanation}; " + "; ".join(best_penalty_reasons)

        selected.append((song, max(0.0, best_adjusted_score), final_explanation))

        artist = _clean_text(song.get("artist", ""))
        genre = _clean_text(song.get("genre", ""))
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
        genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return selected


def _song_to_dict(song: Song) -> Dict:
    """Convert a Song object into the dict format used by the functional API."""
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
        "popularity": song.popularity,
        "release_decade": song.release_decade,
        "mood_tags": song.mood_tags,
        "instrumentalness": song.instrumentalness,
        "live_energy": song.live_energy,
        "lyrical_density": song.lyrical_density,
        "era_affinity": song.era_affinity,
    }
