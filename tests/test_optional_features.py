from src.evaluation import run_feature_evaluation
from src.music_ai_system import run_music_ai_system


def test_support_documents_improve_spin_class_query():
    baseline = run_music_ai_system(
        "Give me music for spin class intervals",
        top_k=3,
        enable_logging=False,
        use_support_docs=False,
    )
    enhanced = run_music_ai_system(
        "Give me music for spin class intervals",
        top_k=3,
        enable_logging=False,
        use_support_docs=True,
    )

    baseline_titles = [item.song["title"] for item in baseline.recommendations]
    enhanced_titles = [item.song["title"] for item in enhanced.recommendations]

    assert "Gym Hero" not in baseline_titles[:2]
    assert "Gym Hero" in enhanced_titles[:2]
    assert enhanced.support_matches
    assert "workout" in enhanced.intent.activity_tags


def test_agent_trace_and_specialization_are_observable():
    response = run_music_ai_system(
        "Need something for debugging at 1am",
        top_k=3,
        enable_logging=False,
        specialization="auto",
    )

    step_names = [step.name for step in response.agent_steps]
    assert step_names == [
        "parse_query",
        "retrieve_support_docs",
        "plan_with_support_docs",
        "retrieve_song_evidence",
        "rank_recommendations",
        "specialize_explanations",
        "self_check",
    ]
    assert response.specialization_profile == "focus_coach"
    assert response.recommendations[0].specialized_explanation
    assert "Best for:" in response.recommendations[0].specialized_explanation
    assert "Why it fits:" in response.recommendations[0].specialized_explanation
    assert "Watch-out:" in response.recommendations[0].specialized_explanation


def test_feature_evaluation_harness_reports_improvement():
    summary = run_feature_evaluation()

    assert summary.rows
    assert summary.enhanced_hits > summary.baseline_hits
    assert summary.style_compliance_rate == 1.0
    assert summary.average_trace_steps >= 6.0
