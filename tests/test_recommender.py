from src.main import print_profile_report
from src.recommender import Recommender, Song, UserProfile, load_songs, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
    assert "popularity fit" in explanation
    assert "release decade fit" in explanation
    assert "mood tag overlap" in explanation


def test_load_songs_includes_advanced_attributes():
    songs = load_songs("data/songs.csv")

    first_song = songs[0]
    assert first_song["popularity"] > 0
    assert first_song["release_decade"] >= 1900
    assert "|" in first_song["mood_tags"]
    assert 0.0 <= first_song["instrumentalness"] <= 1.0
    assert 0.0 <= first_song["live_energy"] <= 1.0
    assert 0.0 <= first_song["lyrical_density"] <= 1.0
    assert 0.0 <= first_song["era_affinity"] <= 1.0


def test_diversity_penalty_spreads_out_repeated_artists():
    songs = [
        {
            "id": 1,
            "title": "Pop Sprint",
            "artist": "Repeat Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.92,
            "tempo_bpm": 128,
            "valence": 0.82,
            "danceability": 0.86,
            "acousticness": 0.08,
            "popularity": 92,
            "release_decade": 2020,
            "mood_tags": "happy|uplifting|bright",
            "instrumentalness": 0.10,
            "live_energy": 0.86,
            "lyrical_density": 0.70,
            "era_affinity": 0.90,
        },
        {
            "id": 2,
            "title": "Pop Encore",
            "artist": "Repeat Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.80,
            "tempo_bpm": 124,
            "valence": 0.80,
            "danceability": 0.82,
            "acousticness": 0.12,
            "popularity": 82,
            "release_decade": 2010,
            "mood_tags": "happy|uplifting|bright",
            "instrumentalness": 0.18,
            "live_energy": 0.70,
            "lyrical_density": 0.60,
            "era_affinity": 0.82,
        },
        {
            "id": 3,
            "title": "Fresh Detour",
            "artist": "New Voice",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.79,
            "tempo_bpm": 121,
            "valence": 0.79,
            "danceability": 0.78,
            "acousticness": 0.15,
            "popularity": 80,
            "release_decade": 2010,
            "mood_tags": "happy|bright",
            "instrumentalness": 0.16,
            "live_energy": 0.72,
            "lyrical_density": 0.62,
            "era_affinity": 0.80,
        },
    ]
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "likes_acoustic": False,
    }

    without_diversity = recommend_songs(
        prefs,
        songs,
        k=3,
        mode="genre_first",
        diversity=False,
    )
    with_diversity = recommend_songs(
        prefs,
        songs,
        k=3,
        mode="genre_first",
        diversity=True,
    )

    assert without_diversity[0][0]["artist"] == "Repeat Artist"
    assert without_diversity[1][0]["artist"] == "Repeat Artist"
    assert with_diversity[0][0]["artist"] == "Repeat Artist"
    assert with_diversity[1][0]["artist"] == "New Voice"
    assert "repeated artist penalty" in with_diversity[2][2]


def test_scoring_modes_can_change_the_top_recommendation():
    songs = [
        {
            "id": 1,
            "title": "Genre Anchor",
            "artist": "The Genre Club",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.40,
            "tempo_bpm": 112,
            "valence": 0.80,
            "danceability": 0.75,
            "acousticness": 0.10,
            "popularity": 76,
            "release_decade": 2010,
            "mood_tags": "happy|uplifting|bright",
            "instrumentalness": 0.15,
            "live_energy": 0.40,
            "lyrical_density": 0.72,
            "era_affinity": 0.80,
        },
        {
            "id": 2,
            "title": "Energy Rocket",
            "artist": "Voltage Crew",
            "genre": "edm",
            "mood": "celebratory",
            "energy": 0.95,
            "tempo_bpm": 128,
            "valence": 0.84,
            "danceability": 0.91,
            "acousticness": 0.05,
            "popularity": 74,
            "release_decade": 2020,
            "mood_tags": "energetic|party|euphoric",
            "instrumentalness": 0.25,
            "live_energy": 0.86,
            "lyrical_density": 0.42,
            "era_affinity": 0.92,
        },
    ]
    prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.95,
        "likes_acoustic": False,
    }

    genre_first = recommend_songs(prefs, songs, k=2, mode="genre_first", diversity=False)
    energy_focused = recommend_songs(prefs, songs, k=2, mode="energy_focused", diversity=False)

    assert genre_first[0][0]["title"] == "Genre Anchor"
    assert energy_focused[0][0]["title"] == "Energy Rocket"


def test_profile_report_renders_reasons_in_ascii_table(capsys):
    recommendations = [
        (
            {"title": "Sunrise City", "artist": "Neon Echo", "genre": "pop"},
            9.60,
            "genre match (+2.00); popularity fit (+0.66)",
        )
    ]

    print_profile_report(
        "High-Energy Pop",
        {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.85,
            "likes_acoustic": False,
        },
        recommendations,
        mode="balanced",
        diversity=True,
    )

    output = capsys.readouterr().out
    assert "| Reasons" in output
    assert "genre match (+2.00)" in output
    assert "Diversity penalty: on" in output
