"""Evaluation harness for optional multi-source, agentic, and specialization features."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap
from typing import Sequence, Tuple

from src.music_ai_system import load_style_cards, run_music_ai_system


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    query: str
    expected_titles: Tuple[str, ...]


@dataclass(frozen=True)
class EvaluationRow:
    name: str
    query: str
    baseline_titles: Tuple[str, ...]
    enhanced_titles: Tuple[str, ...]
    baseline_hit: bool
    enhanced_hit: bool
    enhanced_confidence: float
    trace_steps: int
    specialization_profile: str
    style_compliant: bool


@dataclass(frozen=True)
class EvaluationSummary:
    rows: Tuple[EvaluationRow, ...]
    baseline_hits: int
    enhanced_hits: int
    average_confidence: float
    average_trace_steps: float
    style_compliance_rate: float


def load_evaluation_cases(path: str = "data/evaluation_queries.json") -> Tuple[EvaluationCase, ...]:
    raw_items = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(
        EvaluationCase(
            name=str(item["name"]),
            query=str(item["query"]),
            expected_titles=tuple(item.get("expected_titles", [])),
        )
        for item in raw_items
    )


def run_feature_evaluation(path: str = "data/evaluation_queries.json", top_k: int = 3) -> EvaluationSummary:
    cases = load_evaluation_cases(path)
    style_lookup = {card.profile: card for card in load_style_cards()}

    rows = []
    baseline_hits = 0
    enhanced_hits = 0
    confidence_total = 0.0
    trace_total = 0
    style_hits = 0

    for case in cases:
        baseline = run_music_ai_system(
            case.query,
            top_k=top_k,
            enable_logging=False,
            use_support_docs=False,
            specialization="off",
        )
        enhanced = run_music_ai_system(
            case.query,
            top_k=top_k,
            enable_logging=False,
            use_support_docs=True,
            specialization="auto",
        )

        baseline_titles = tuple(item.song["title"] for item in baseline.recommendations[:top_k])
        enhanced_titles = tuple(item.song["title"] for item in enhanced.recommendations[:top_k])
        baseline_hit = _hits_expected(baseline_titles, case.expected_titles)
        enhanced_hit = _hits_expected(enhanced_titles, case.expected_titles)
        confidence = _confidence_score(enhanced)
        style_card = style_lookup.get(enhanced.specialization_profile)
        specialized_text = enhanced.recommendations[0].specialized_explanation if enhanced.recommendations else ""
        style_compliant = _style_compliance(specialized_text, style_card)

        baseline_hits += int(baseline_hit)
        enhanced_hits += int(enhanced_hit)
        confidence_total += confidence
        trace_total += len(enhanced.agent_steps)
        style_hits += int(style_compliant)

        rows.append(
            EvaluationRow(
                name=case.name,
                query=case.query,
                baseline_titles=baseline_titles,
                enhanced_titles=enhanced_titles,
                baseline_hit=baseline_hit,
                enhanced_hit=enhanced_hit,
                enhanced_confidence=confidence,
                trace_steps=len(enhanced.agent_steps),
                specialization_profile=enhanced.specialization_profile,
                style_compliant=style_compliant,
            )
        )

    total = len(rows) or 1
    return EvaluationSummary(
        rows=tuple(rows),
        baseline_hits=baseline_hits,
        enhanced_hits=enhanced_hits,
        average_confidence=confidence_total / total,
        average_trace_steps=trace_total / total,
        style_compliance_rate=style_hits / total,
    )


def render_evaluation_report(summary: EvaluationSummary) -> str:
    columns = (
        ("Scenario", 24),
        ("Base", 6),
        ("Enh", 6),
        ("Confidence", 10),
        ("Trace", 5),
        ("Style", 10),
        ("Enhanced Top 3", 48),
    )

    rows = []
    for row in summary.rows:
        rows.append(
            {
                "scenario": row.name,
                "base": "pass" if row.baseline_hit else "review",
                "enh": "pass" if row.enhanced_hit else "review",
                "confidence": f"{row.enhanced_confidence:.2f}",
                "trace": str(row.trace_steps),
                "style": "ok" if row.style_compliant else "miss",
                "enhanced_top_3": ", ".join(row.enhanced_titles),
            }
        )

    lines = [
        "=== Optional Feature Evaluation ===",
        (
            f"Multi-source hit@3: {summary.baseline_hits}/{len(summary.rows)} -> "
            f"{summary.enhanced_hits}/{len(summary.rows)} "
            f"({summary.enhanced_hits - summary.baseline_hits:+d})"
        ),
        f"Average enhanced confidence: {summary.average_confidence:.2f}",
        f"Average trace steps: {summary.average_trace_steps:.2f}",
        f"Specialization compliance: {summary.style_compliance_rate:.0%}",
        "",
        _format_table(rows, columns, ("scenario", "base", "enh", "confidence", "trace", "style", "enhanced_top_3")),
    ]
    return "\n".join(lines)


def print_evaluation_report() -> None:
    print(render_evaluation_report(run_feature_evaluation()))


def main() -> None:
    print_evaluation_report()


def _hits_expected(top_titles: Sequence[str], expected_titles: Sequence[str]) -> bool:
    expected = set(expected_titles)
    return any(title in expected for title in top_titles)


def _confidence_score(response) -> float:
    score = 0.45
    score += 0.2 if response.reliability.grounded else 0.0
    score += 0.15 if response.reliability.consistency_ok else 0.0
    score += 0.15 * response.reliability.evidence_coverage
    score -= 0.08 * len(response.reliability.warnings)
    return _clamp(score, 0.0, 1.0)


def _style_compliance(text: str, style_card) -> bool:
    if style_card is None:
        return False
    return all(marker in text for marker in style_card.required_markers)


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


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


if __name__ == "__main__":
    main()
