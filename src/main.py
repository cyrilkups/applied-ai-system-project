"""Command line runner for the music recommender and applied AI system."""

from __future__ import annotations

import sys
from textwrap import wrap

from src.music_ai_system import (
    format_agent_steps,
    format_benchmark_rows,
    format_intent_summary,
    format_reliability_summary,
    format_retrieval_rows,
    format_support_rows,
    run_music_ai_system,
    run_reliability_suite,
)
from src.recommender import MODE_CONFIGS, available_modes, get_mode_label, load_songs, recommend_songs


EVALUATION_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "likes_acoustic": False,
    },
    "Conflicted Edge Case": {
        "favorite_genre": "classical",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": True,
    },
}

PROFILE_COLUMNS = (
    ("#", 3),
    ("Song", 20),
    ("Artist", 16),
    ("Genre", 12),
    ("Score", 8),
    ("Reasons", 64),
)

PIPELINE_COLUMNS = (
    ("#", 3),
    ("Song", 18),
    ("Artist", 14),
    ("Final", 7),
    ("Base", 7),
    ("RAG", 5),
    ("Reasons", 72),
)

RETRIEVAL_COLUMNS = (
    ("#", 3),
    ("Song", 20),
    ("RAG", 6),
    ("Matches", 28),
    ("Evidence", 64),
)

SUPPORT_COLUMNS = (
    ("#", 3),
    ("Guide", 24),
    ("Score", 6),
    ("Matches", 28),
    ("Evidence", 64),
)

BENCHMARK_COLUMNS = (
    ("Scenario", 24),
    ("Expected", 8),
    ("Warning", 8),
    ("Grounded", 8),
    ("Consistent", 10),
    ("Top Titles", 48),
)


def _format_profile_summary(prefs: dict) -> str:
    return (
        f"genre={prefs['favorite_genre']}, "
        f"mood={prefs['favorite_mood']}, "
        f"energy={prefs['target_energy']:.2f}, "
        f"likes_acoustic={prefs['likes_acoustic']}"
    )


def _wrap_cell(value: str, width: int) -> list[str]:
    text = "" if value is None else str(value)
    lines = []
    for raw_line in text.splitlines() or [""]:
        wrapped = wrap(raw_line, width=width) or [""]
        lines.extend(wrapped)
    return lines or [""]


def _format_table(rows: list[dict], columns: tuple[tuple[str, int], ...], keys: tuple[str, ...]) -> str:
    header = "| " + " | ".join(label.ljust(width) for label, width in columns) + " |"
    separator = "+-" + "-+-".join("-" * width for _, width in columns) + "-+"
    table_lines = [separator, header, separator]

    for row in rows:
        cell_lines = [_wrap_cell(str(row.get(key, "")), width) for key, (_, width) in zip(keys, columns)]
        row_height = max(len(lines) for lines in cell_lines) if cell_lines else 1
        for line_index in range(row_height):
            rendered_cells = []
            for lines, (_, width) in zip(cell_lines, columns):
                rendered_cells.append(lines[line_index].ljust(width) if line_index < len(lines) else " " * width)
            table_lines.append("| " + " | ".join(rendered_cells) + " |")
        table_lines.append(separator)

    return "\n".join(table_lines)


def _build_table_rows(recommendations: list) -> list[dict]:
    rows = []
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append(
            {
                "rank": index,
                "song": song["title"],
                "artist": song["artist"],
                "genre": song["genre"],
                "score": f"{score:.2f}",
                "reasons": explanation,
            }
        )
    return rows


def _build_pipeline_rows(response) -> list[dict]:
    rows = []
    for index, item in enumerate(response.recommendations, start=1):
        rows.append(
            {
                "rank": index,
                "song": item.song["title"],
                "artist": item.song["artist"],
                "final": f"{item.final_score:.2f}",
                "base": f"{item.base_score:.2f}",
                "rag": f"{item.retrieval_score:.2f}",
                "reasons": item.explanation,
            }
        )
    return rows


def _normalize_mode_input(raw_mode: str) -> str:
    normalized = (raw_mode or "balanced").strip().lower().replace("-", "_")
    return normalized if normalized in MODE_CONFIGS else "balanced"


def _normalize_specialization_input(raw_value: str) -> str:
    normalized = (raw_value or "off").strip().lower().replace("-", "_")
    allowed = {"off", "auto", "focus_coach", "hype_trainer", "reflective_curator"}
    return normalized if normalized in allowed else "off"


def _parse_runtime_options(argv: list[str]) -> tuple[list[str], bool]:
    args = argv[1:]
    diversity = "--no-diversity" not in args
    filtered_args = [arg for arg in args if arg != "--no-diversity"]

    if not filtered_args:
        return ["balanced"], diversity
    if filtered_args[0].lower() == "all":
        return list(available_modes()), diversity
    return [_normalize_mode_input(filtered_args[0])], diversity


def _parse_query_options(args: list[str]) -> dict:
    options = {
        "mode": "",
        "top_k": 5,
        "diversity": True,
        "query": "",
        "show_trace": False,
        "use_support_docs": True,
        "specialization": "off",
    }
    query_parts: list[str] = []

    index = 0
    while index < len(args):
        token = args[index]
        if token == "--no-diversity":
            options["diversity"] = False
        elif token == "--show-trace":
            options["show_trace"] = True
        elif token == "--single-source":
            options["use_support_docs"] = False
        elif token == "--mode" and index + 1 < len(args):
            options["mode"] = _normalize_mode_input(args[index + 1])
            index += 1
        elif token.startswith("--mode="):
            options["mode"] = _normalize_mode_input(token.split("=", 1)[1])
        elif token == "--top-k" and index + 1 < len(args):
            try:
                options["top_k"] = max(1, min(int(args[index + 1]), 10))
            except ValueError:
                options["top_k"] = 5
            index += 1
        elif token.startswith("--top-k="):
            try:
                options["top_k"] = max(1, min(int(token.split("=", 1)[1]), 10))
            except ValueError:
                options["top_k"] = 5
        elif token == "--specialization" and index + 1 < len(args):
            options["specialization"] = _normalize_specialization_input(args[index + 1])
            index += 1
        elif token.startswith("--specialization="):
            options["specialization"] = _normalize_specialization_input(token.split("=", 1)[1])
        else:
            query_parts.append(token)
        index += 1

    options["query"] = " ".join(query_parts).strip()
    return options


def print_profile_report(name: str, prefs: dict, recommendations: list, mode: str, diversity: bool) -> None:
    """Print one baseline recommendation block in a readable terminal format."""
    print(f"\n=== {name} | Mode: {get_mode_label(mode)} ===")
    print(f"Profile: {_format_profile_summary(prefs)}")
    print(f"Diversity penalty: {'on' if diversity else 'off'}")
    print(_format_table(_build_table_rows(recommendations), PROFILE_COLUMNS, ("rank", "song", "artist", "genre", "score", "reasons")))


def run_mode(mode: str, diversity: bool, songs: list[dict]) -> None:
    print(f"\nRecommendation runs for mode: {get_mode_label(mode)}")
    for name, prefs in EVALUATION_PROFILES.items():
        recommendations = recommend_songs(
            prefs,
            songs,
            k=5,
            mode=mode,
            diversity=diversity,
        )
        print_profile_report(name, prefs, recommendations, mode=mode, diversity=diversity)


def _print_music_ai_report(response, *, show_trace: bool = False) -> None:
    print("\n=== Applied Music AI Music Recommender ===")
    print(f"Request: {response.query}")
    print(f"Parsed intent: {format_intent_summary(response.intent)}")
    if response.intent.activity_tags:
        print(f"Activity tags: {', '.join(response.intent.activity_tags)}")
    if response.intent.parser_notes:
        print(f"Parser notes: {'; '.join(response.intent.parser_notes)}")

    if response.support_matches:
        print("\nSupport documents")
        support_rows = format_support_rows(response.support_matches)
        print(_format_table(support_rows, SUPPORT_COLUMNS, ("rank", "document", "score", "matches", "evidence")))

    print("\nRetrieved evidence")
    retrieval_rows = format_retrieval_rows(response.retrieved_items[:5])
    print(_format_table(retrieval_rows, RETRIEVAL_COLUMNS, ("rank", "song", "score", "matches", "evidence")))

    print("\nRecommendations")
    print(_format_table(_build_pipeline_rows(response), PIPELINE_COLUMNS, ("rank", "song", "artist", "final", "base", "rag", "reasons")))

    if response.specialization_profile != "off":
        print(f"\nSpecialized explanations ({response.specialization_profile})")
        for index, item in enumerate(response.recommendations[:3], start=1):
            print(f"{index}. {item.song['title']}: {item.specialized_explanation}")

    if show_trace:
        print("\nAgent trace")
        for line in format_agent_steps(response.agent_steps):
            print(f"- {line}")

    print(f"\nReliability: {format_reliability_summary(response.reliability)}")
    if response.log_path:
        print(f"Run log: {response.log_path}")


def _print_reliability_suite() -> None:
    results = run_reliability_suite()
    print("\n=== Reliability Suite ===")
    print(_format_table(format_benchmark_rows(results), BENCHMARK_COLUMNS, ("scenario", "expected", "warning", "grounded", "consistent", "top_titles")))


def _print_feature_evaluation() -> None:
    from src.evaluation import print_evaluation_report

    print_evaluation_report()


def _print_usage() -> None:
    print("Usage:")
    print("  python -m src.main")
    print("  python -m src.main [balanced|genre_first|mood_first|energy_focused|all] [--no-diversity]")
    print("  python -m src.main query \"Need calm music for late-night coding\" [--mode mood_first] [--top-k 5] [--no-diversity]")
    print("  python -m src.main query \"Need something for debugging at 1am\" [--show-trace] [--specialization auto] [--single-source]")
    print("  python -m src.main reliability")
    print("  python -m src.main evaluate")
    print("  python -m src.main \"Need upbeat music for a workout\"")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        modes, diversity = _parse_runtime_options(sys.argv)
        songs = load_songs("data/songs.csv")
        print(f"Available modes: {', '.join(available_modes())}")
        print("Default run shows the baseline profile evaluation suite.")
        print("Use `query` for the retrieval-augmented system, `reliability` for benchmark checks, or `evaluate` for the optional feature harness.")
        for mode in modes:
            run_mode(mode, diversity=diversity, songs=songs)
        return

    first = args[0].lower()
    if first in {"help", "--help", "-h"}:
        _print_usage()
        return

    if first == "reliability":
        _print_reliability_suite()
        return

    if first == "evaluate":
        _print_feature_evaluation()
        return

    if first == "query":
        options = _parse_query_options(args[1:])
        response = run_music_ai_system(
            options["query"],
            mode=options["mode"] or None,
            top_k=options["top_k"],
            diversity=options["diversity"],
            use_support_docs=options["use_support_docs"],
            specialization=options["specialization"],
        )
        _print_music_ai_report(response, show_trace=options["show_trace"])
        return

    if first in MODE_CONFIGS or first == "all" or first == "--no-diversity":
        modes, diversity = _parse_runtime_options(sys.argv)
        songs = load_songs("data/songs.csv")
        print(f"Available modes: {', '.join(available_modes())}")
        for mode in modes:
            run_mode(mode, diversity=diversity, songs=songs)
        return

    options = _parse_query_options(args)
    response = run_music_ai_system(
        options["query"],
        mode=options["mode"] or None,
        top_k=options["top_k"],
        diversity=options["diversity"],
        use_support_docs=options["use_support_docs"],
        specialization=options["specialization"],
    )
    _print_music_ai_report(response, show_trace=options["show_trace"])


if __name__ == "__main__":
    main()
