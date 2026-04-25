import json
from pathlib import Path

from src.music_ai_system import parse_user_query, run_music_ai_system, run_reliability_suite


def test_parse_user_query_infers_workout_profile_from_gym_keyword():
    intent = parse_user_query("Need high-energy music for the gym")

    assert intent.mode == "energy_focused"
    assert intent.favorite_mood == "intense"
    assert intent.likes_acoustic is False
    assert "workout" in intent.activity_tags
    assert "gym" in intent.activity_tags


def test_music_ai_system_ranks_focus_tracks_for_coding_query():
    response = run_music_ai_system(
        "Need calm music for late-night coding",
        top_k=3,
        enable_logging=False,
    )

    top_titles = [item.song["title"] for item in response.recommendations]
    assert "Midnight Coding" in top_titles[:2]
    assert "Focus Flow" in top_titles[:3]
    assert response.reliability.grounded is True
    assert response.reliability.consistency_ok is True


def test_music_ai_system_preserves_explicit_genre_with_safeguard():
    response = run_music_ai_system(
        "Need classical music for an intense workout",
        top_k=5,
        enable_logging=False,
    )

    top_titles = [item.song["title"] for item in response.recommendations]
    assert "Glass Morning" in top_titles
    assert any("genre coverage safeguard" in item.explanation for item in response.recommendations)
    assert any("thin catalog support" in warning for warning in response.reliability.warnings)


def test_music_ai_system_writes_a_json_log(tmp_path):
    response = run_music_ai_system(
        "Play nostalgic acoustic music for journaling",
        top_k=3,
        log_dir=str(tmp_path / "music-logs"),
        enable_logging=True,
    )

    log_path = Path(response.log_path)
    assert log_path.exists()

    payload = json.loads(log_path.read_text(encoding="utf-8"))
    assert payload["query"] == "Play nostalgic acoustic music for journaling"
    assert payload["recommendations"]
    assert payload["reliability"]["consistency_ok"] is True


def test_reliability_suite_scenarios_pass_expected_checks():
    results = run_reliability_suite()

    assert results
    assert all(result.hit_expected for result in results)
    assert all(result.grounded for result in results)
    assert all(result.consistency_ok for result in results)
    assert all(result.warning_present == result.expect_warning for result in results)
