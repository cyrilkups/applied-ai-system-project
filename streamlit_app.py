"""Dark-mode Streamlit demo for the VibeFinder platform."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from src.evaluation import run_feature_evaluation
from src.music_ai_system import run_music_ai_system, run_reliability_suite


DEMO_PRESETS: Dict[str, str] = {
    "Late-Night Focus": "Need calm music for late-night coding",
    "Gym Surge": "Need high-energy music for the gym",
    "Reflective Journaling": "Play nostalgic acoustic music for journaling",
    "Conflicted Edge": "Need classical music for an intense workout",
    "Debugging at 1am": "Need something for debugging at 1am",
}

SPECIALIZATION_OPTIONS = {
    "Off": "off",
    "Auto": "auto",
    "Focus Coach": "focus_coach",
    "Hype Trainer": "hype_trainer",
    "Reflective Curator": "reflective_curator",
}

MODE_OPTIONS = {
    "Auto infer": "",
    "Balanced": "balanced",
    "Genre-First": "genre_first",
    "Mood-First": "mood_first",
    "Energy-Focused": "energy_focused",
}


st.set_page_config(
    page_title="VibeFinder Demo",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main() -> None:
    _apply_theme()
    _seed_session_state()
    _ensure_initial_demo()

    with st.sidebar:
        _render_sidebar()

    _render_app()


def _seed_session_state() -> None:
    st.session_state.setdefault("query", DEMO_PRESETS["Late-Night Focus"])
    st.session_state.setdefault("draft_query", DEMO_PRESETS["Late-Night Focus"])
    st.session_state.setdefault("last_response", None)
    st.session_state.setdefault("last_query", "")
    st.session_state.setdefault("evaluation_summary", None)
    st.session_state.setdefault("reliability_rows", None)
    st.session_state.setdefault("ui_mode", "Auto infer")
    st.session_state.setdefault("ui_specialization", "Auto")
    st.session_state.setdefault("ui_top_k", 5)
    st.session_state.setdefault("ui_diversity", True)
    st.session_state.setdefault("ui_support", True)
    st.session_state.setdefault("ui_show_specialized", True)


def _ensure_initial_demo() -> None:
    if st.session_state.last_response is None:
        _run_query(st.session_state.query)


def _run_query(query: Optional[str] = None) -> None:
    active_query = (query or st.session_state.draft_query).strip() or DEMO_PRESETS["Late-Night Focus"]
    st.session_state.query = active_query

    specialization = (
        SPECIALIZATION_OPTIONS[st.session_state.ui_specialization]
        if st.session_state.ui_show_specialized
        else "off"
    )

    response = run_music_ai_system(
        active_query,
        mode=MODE_OPTIONS[st.session_state.ui_mode] or None,
        top_k=int(st.session_state.ui_top_k),
        diversity=bool(st.session_state.ui_diversity),
        use_support_docs=bool(st.session_state.ui_support),
        specialization=specialization,
    )
    st.session_state.last_response = response
    st.session_state.last_query = active_query


def _apply_preset(query: str) -> None:
    st.session_state.draft_query = query
    _run_query(query)


def _apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg-top: #070b13;
          --bg-bottom: #04070c;
          --panel: rgba(14, 19, 31, 0.78);
          --panel-strong: rgba(18, 25, 40, 0.92);
          --panel-soft: rgba(19, 27, 44, 0.62);
          --border: rgba(255, 255, 255, 0.08);
          --border-strong: rgba(255, 255, 255, 0.12);
          --text: #f5f7fb;
          --muted: #9aa7bb;
          --muted-2: #7a8699;
          --blue: #0a84ff;
          --blue-soft: #64d2ff;
          --green: #30d158;
          --orange: #ff9f0a;
          --red: #ff453a;
          --shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
          --radius-xl: 32px;
          --radius-lg: 24px;
          --radius-md: 18px;
        }

        .stApp {
          color: var(--text);
          font-family: "SF Pro Display", "SF Pro Text", -apple-system, BlinkMacSystemFont, sans-serif;
          background:
            radial-gradient(circle at 12% 8%, rgba(10, 132, 255, 0.22), transparent 26%),
            radial-gradient(circle at 88% 10%, rgba(100, 210, 255, 0.16), transparent 18%),
            radial-gradient(circle at 50% 120%, rgba(48, 209, 88, 0.10), transparent 18%),
            linear-gradient(180deg, var(--bg-top) 0%, #07101a 38%, var(--bg-bottom) 100%);
        }

        .stApp [data-testid="stHeader"] {
          background: transparent;
        }

        .stApp [data-testid="stSidebar"] {
          background: linear-gradient(180deg, rgba(10, 14, 22, 0.96) 0%, rgba(8, 12, 19, 0.98) 100%);
          border-right: 1px solid var(--border);
          backdrop-filter: blur(22px);
        }

        .block-container {
          padding-top: 1.6rem;
          padding-bottom: 3rem;
        }

        h1, h2, h3, h4, p, label, span, div {
          color: inherit;
        }

        .vf-hero {
          position: relative;
          overflow: hidden;
          padding: 38px 40px;
          border-radius: var(--radius-xl);
          background:
            linear-gradient(135deg, rgba(18, 26, 42, 0.96) 0%, rgba(9, 15, 25, 0.92) 48%, rgba(7, 12, 20, 0.98) 100%);
          border: 1px solid var(--border-strong);
          box-shadow: var(--shadow);
          margin-bottom: 1rem;
        }

        .vf-hero:before {
          content: "";
          position: absolute;
          width: 380px;
          height: 380px;
          border-radius: 999px;
          top: -150px;
          right: -120px;
          background: radial-gradient(circle, rgba(10, 132, 255, 0.30), rgba(10, 132, 255, 0) 70%);
        }

        .vf-hero:after {
          content: "";
          position: absolute;
          width: 260px;
          height: 260px;
          border-radius: 999px;
          bottom: -120px;
          left: -60px;
          background: radial-gradient(circle, rgba(48, 209, 88, 0.14), rgba(48, 209, 88, 0) 72%);
        }

        .vf-eyebrow {
          display: inline-block;
          padding: 0.35rem 0.7rem;
          border-radius: 999px;
          background: rgba(10, 132, 255, 0.14);
          border: 1px solid rgba(100, 210, 255, 0.18);
          color: #9fdcff;
          font-size: 0.74rem;
          font-weight: 700;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          margin-bottom: 0.9rem;
        }

        .vf-title {
          font-size: clamp(2.8rem, 6vw, 5.4rem);
          line-height: 0.94;
          letter-spacing: -0.06em;
          font-weight: 700;
          margin: 0 0 0.8rem 0;
          max-width: 8.6ch;
        }

        .vf-subtitle {
          font-size: 1.08rem;
          line-height: 1.65;
          color: var(--muted);
          max-width: 58ch;
          margin-bottom: 1.1rem;
        }

        .vf-badge-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.7rem;
        }

        .vf-badge {
          padding: 0.62rem 0.88rem;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #dce8f7;
          font-size: 0.9rem;
        }

        .vf-spotlight {
          padding: 1.1rem 1.15rem 1rem 1.15rem;
          border-radius: 26px;
          background:
            linear-gradient(180deg, rgba(15, 24, 39, 0.88) 0%, rgba(11, 18, 30, 0.92) 100%);
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }

        .vf-spotlight-label {
          color: #8fd1ff;
          font-size: 0.76rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.14em;
          margin-bottom: 0.6rem;
        }

        .vf-spotlight-title {
          font-size: 1.3rem;
          font-weight: 700;
          letter-spacing: -0.04em;
          margin-bottom: 0.15rem;
        }

        .vf-spotlight-meta {
          color: var(--muted);
          font-size: 0.94rem;
          margin-bottom: 0.8rem;
        }

        .vf-shell-title {
          font-size: 1.2rem;
          font-weight: 700;
          letter-spacing: -0.03em;
          margin: 0.2rem 0 0.25rem 0;
        }

        .vf-shell-copy {
          color: var(--muted);
          font-size: 0.96rem;
          line-height: 1.58;
          margin-bottom: 0.9rem;
        }

        .vf-panel {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow);
          padding: 1.15rem;
          backdrop-filter: blur(18px);
        }

        .vf-panel-strong {
          background: var(--panel-strong);
          border: 1px solid var(--border-strong);
          border-radius: var(--radius-xl);
          box-shadow: var(--shadow);
          padding: 1.35rem;
          backdrop-filter: blur(22px);
        }

        .vf-panel-soft {
          background: var(--panel-soft);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: var(--radius-md);
          padding: 1rem;
        }

        .vf-stage-label {
          color: #8fd1ff;
          font-size: 0.74rem;
          letter-spacing: 0.14em;
          font-weight: 700;
          text-transform: uppercase;
          margin-bottom: 0.45rem;
        }

        .vf-stage-title {
          font-size: 1.35rem;
          font-weight: 700;
          letter-spacing: -0.035em;
          margin-bottom: 0.25rem;
        }

        .vf-stage-copy {
          color: var(--muted);
          font-size: 0.95rem;
          line-height: 1.6;
        }

        .vf-metric-row {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 0.8rem;
          margin-bottom: 1rem;
        }

        .vf-metric {
          padding: 1rem;
          border-radius: 22px;
          background: linear-gradient(180deg, rgba(23, 33, 52, 0.94) 0%, rgba(12, 18, 28, 0.94) 100%);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .vf-metric-label {
          color: var(--muted);
          font-size: 0.76rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.12em;
          margin-bottom: 0.4rem;
        }

        .vf-metric-value {
          font-size: 1.55rem;
          line-height: 1.04;
          letter-spacing: -0.05em;
          font-weight: 700;
          margin-bottom: 0.18rem;
        }

        .vf-metric-note {
          color: var(--muted);
          font-size: 0.88rem;
        }

        .vf-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.55rem;
          margin-top: 0.75rem;
        }

        .vf-chip {
          padding: 0.44rem 0.74rem;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.07);
          color: #d7e3f5;
          font-size: 0.88rem;
        }

        .vf-chip.dim {
          color: var(--muted);
        }

        .vf-status {
          display: inline-flex;
          align-items: center;
          gap: 0.42rem;
          padding: 0.44rem 0.82rem;
          border-radius: 999px;
          font-weight: 600;
          font-size: 0.88rem;
          border: 1px solid transparent;
        }

        .vf-status.ok {
          color: #8ff0b1;
          background: rgba(48, 209, 88, 0.12);
          border-color: rgba(48, 209, 88, 0.22);
        }

        .vf-status.warn {
          color: #ffd07e;
          background: rgba(255, 159, 10, 0.12);
          border-color: rgba(255, 159, 10, 0.20);
        }

        .vf-status.alert {
          color: #ff9b92;
          background: rgba(255, 69, 58, 0.12);
          border-color: rgba(255, 69, 58, 0.20);
        }

        .vf-rec-hero {
          position: relative;
          overflow: hidden;
          padding: 1.35rem;
          border-radius: 28px;
          background:
            linear-gradient(135deg, rgba(17, 28, 46, 0.98) 0%, rgba(12, 18, 29, 0.96) 52%, rgba(7, 12, 20, 0.98) 100%);
          border: 1px solid rgba(255, 255, 255, 0.09);
          box-shadow: var(--shadow);
          margin-bottom: 1rem;
        }

        .vf-rec-hero:before {
          content: "";
          position: absolute;
          width: 220px;
          height: 220px;
          border-radius: 999px;
          right: -80px;
          top: -70px;
          background: radial-gradient(circle, rgba(10, 132, 255, 0.22), rgba(10, 132, 255, 0) 68%);
        }

        .vf-rank {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 2.3rem;
          height: 2.3rem;
          border-radius: 999px;
          background: linear-gradient(135deg, rgba(10, 132, 255, 0.22), rgba(100, 210, 255, 0.10));
          color: #9bd9ff;
          font-weight: 700;
          font-size: 0.96rem;
        }

        .vf-song-title {
          font-size: 1.45rem;
          font-weight: 700;
          letter-spacing: -0.04em;
          margin-bottom: 0.12rem;
        }

        .vf-song-title.big {
          font-size: 2.2rem;
          letter-spacing: -0.06em;
        }

        .vf-song-meta {
          color: var(--muted);
          font-size: 0.95rem;
        }

        .vf-copy {
          color: #d6e1f0;
          font-size: 0.97rem;
          line-height: 1.66;
        }

        .vf-caption {
          color: var(--muted);
          font-size: 0.84rem;
          line-height: 1.55;
        }

        .vf-kpi-row {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.7rem;
          margin: 1rem 0;
        }

        .vf-kpi {
          padding: 0.85rem;
          border-radius: 18px;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .vf-kpi small {
          display: block;
          color: var(--muted);
          text-transform: uppercase;
          font-weight: 700;
          font-size: 0.7rem;
          letter-spacing: 0.10em;
          margin-bottom: 0.28rem;
        }

        .vf-kpi strong {
          display: block;
          font-size: 1.04rem;
          font-weight: 700;
        }

        .vf-rec-card {
          padding: 1.12rem;
          border-radius: 24px;
          background: linear-gradient(180deg, rgba(17, 24, 38, 0.94) 0%, rgba(10, 15, 24, 0.96) 100%);
          border: 1px solid rgba(255, 255, 255, 0.08);
          box-shadow: var(--shadow);
          height: 100%;
        }

        .vf-mini-list {
          display: grid;
          gap: 0.75rem;
        }

        .vf-mini-item {
          padding: 0.95rem 1rem;
          border-radius: 20px;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .vf-trace-item {
          position: relative;
          padding: 0.95rem 1rem 0.95rem 1.35rem;
          border-radius: 20px;
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.05);
          margin-bottom: 0.8rem;
        }

        .vf-trace-item:before {
          content: "";
          position: absolute;
          left: 0.7rem;
          top: 1.1rem;
          width: 0.36rem;
          height: 0.36rem;
          border-radius: 999px;
          background: #7fd6ff;
          box-shadow: 0 0 0 6px rgba(10, 132, 255, 0.10);
        }

        .vf-trace-title {
          font-size: 0.95rem;
          font-weight: 700;
          margin-bottom: 0.2rem;
        }

        .vf-section-gap {
          height: 0.9rem;
        }

        .vf-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.10) 18%, rgba(255,255,255,0.10) 82%, transparent 100%);
          margin: 1.15rem 0 1rem 0;
        }

        [data-testid="stForm"] {
          background: linear-gradient(180deg, rgba(16, 23, 36, 0.94) 0%, rgba(11, 16, 26, 0.96) 100%);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 28px;
          padding: 1.1rem 1.15rem 0.8rem 1.15rem;
          box-shadow: var(--shadow);
        }

        .stTextArea textarea,
        .stTextInput input,
        .stNumberInput input {
          background: rgba(255, 255, 255, 0.04) !important;
          color: var(--text) !important;
          border: 1px solid rgba(255, 255, 255, 0.08) !important;
          border-radius: 18px !important;
        }

        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {
          color: #738094 !important;
        }

        div[data-baseweb="select"] > div {
          background: rgba(255, 255, 255, 0.04) !important;
          border: 1px solid rgba(255, 255, 255, 0.08) !important;
          border-radius: 18px !important;
          color: var(--text) !important;
        }

        .stButton > button,
        .stDownloadButton > button {
          border-radius: 999px;
          border: 1px solid rgba(255, 255, 255, 0.08);
          background: linear-gradient(180deg, rgba(25, 33, 49, 0.94) 0%, rgba(14, 20, 32, 0.98) 100%);
          color: var(--text);
          font-weight: 600;
          padding: 0.62rem 0.95rem;
          box-shadow: 0 10px 24px rgba(0, 0, 0, 0.28);
        }

        .stButton > button[kind="primary"] {
          background: linear-gradient(180deg, #1b93ff 0%, #0a84ff 100%);
          color: white;
          border: 1px solid rgba(100, 210, 255, 0.28);
        }

        [data-testid="stTabs"] button {
          color: var(--muted);
          font-weight: 600;
        }

        [data-testid="stTabs"] button[aria-selected="true"] {
          color: var(--text);
        }

        .stAlert {
          background: rgba(17, 24, 38, 0.82);
          color: var(--text);
          border: 1px solid rgba(255, 255, 255, 0.08);
        }

        @media (max-width: 920px) {
          .vf-title {
            max-width: 100%;
          }

          .vf-metric-row {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }

          .vf-kpi-row {
            grid-template-columns: 1fr;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> None:
    st.markdown("### Control Room")
    st.caption("Secondary tools for grading and diagnostics.")

    st.markdown("#### Quick scenes")
    for label, query in DEMO_PRESETS.items():
        if st.button(label, width="stretch", key=f"sidebar-{label}"):
            _apply_preset(query)

    st.markdown("---")
    st.markdown("#### Diagnostics")
    if st.button("Run Reliability Benchmarks", width="stretch"):
        with st.spinner("Running reliability suite..."):
            st.session_state.reliability_rows = run_reliability_suite()

    if st.button("Run Optional Feature Evaluation", width="stretch"):
        with st.spinner("Comparing baseline and enhanced retrieval..."):
            st.session_state.evaluation_summary = run_feature_evaluation()

    st.markdown("---")
    st.caption(
        "This frontend uses the same recommender core as the CLI: multi-source retrieval, specialization, agent trace steps, and self-checking."
    )


def _render_app() -> None:
    response = st.session_state.last_response
    _render_hero(response)
    _render_preset_row()
    _render_query_stage()

    if response is None:
        st.info("Write a prompt and run the demo to see live recommendations.")
        return

    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    _render_overview_strip(response)

    main_left, main_right = st.columns([1.55, 0.95], gap="large")
    with main_left:
        _render_recommendation_stage(response)
    with main_right:
        _render_system_panels(response)

    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    _render_retrieval_stage(response)

    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    _render_labs_stage()


def _render_hero(response) -> None:
    top_song = response.recommendations[0] if response and response.recommendations else None
    preview_markup = """
      <div class="vf-spotlight">
        <div class="vf-spotlight-label">Ready to demo</div>
        <div class="vf-spotlight-title">Live music reasoning</div>
        <div class="vf-spotlight-meta">Natural language in. Multi-step retrieval, ranking, and reliability checks out.</div>
        <div class="vf-chip-row">
          <div class="vf-chip">Dark demo mode</div>
          <div class="vf-chip">Live query composer</div>
          <div class="vf-chip">Grading-friendly diagnostics</div>
        </div>
      </div>
    """
    if top_song is not None:
        preview_markup = f"""
        <div class="vf-spotlight">
          <div class="vf-spotlight-label">Current top match</div>
          <div class="vf-spotlight-title">{_escape(top_song.song["title"])}</div>
          <div class="vf-spotlight-meta">{_escape(top_song.song["artist"])} · {_escape(top_song.song["genre"].title())}</div>
          <div class="vf-chip-row">
            <div class="vf-chip">Final {top_song.final_score:.2f}</div>
            <div class="vf-chip">RAG {top_song.retrieval_score:.2f}</div>
            <div class="vf-chip">{_escape(", ".join(top_song.matched_terms[:2]) or "context")}</div>
          </div>
        </div>
        """

    left, right = st.columns([1.35, 0.8], gap="large")
    with left:
        st.markdown(
            """
            <div class="vf-hero">
              <div class="vf-eyebrow">Applied AI Platform Demo</div>
              <div class="vf-title">VibeFinder in a darker, sharper stage.</div>
              <div class="vf-subtitle">
                This interface is built for live demos. The recommendation result leads, the reasoning stays visible,
                and the reliability story is close at hand instead of buried behind a flat dashboard.
              </div>
              <div class="vf-badge-row">
                <div class="vf-badge">Multi-source retrieval</div>
                <div class="vf-badge">Observable agent trace</div>
                <div class="vf-badge">Specialized explanation styles</div>
                <div class="vf-badge">Reliability suite</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(preview_markup, unsafe_allow_html=True)


def _render_preset_row() -> None:
    st.markdown(
        """
        <div class="vf-stage-label">Quick scenes</div>
        <div class="vf-stage-title">Launch a polished demo in one click.</div>
        <div class="vf-stage-copy">These presets immediately run the platform with good grading examples.</div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(len(DEMO_PRESETS), gap="small")
    for column, (label, query) in zip(cols, DEMO_PRESETS.items()):
        with column:
            if st.button(label, width="stretch", key=f"main-{label}"):
                _apply_preset(query)


def _render_query_stage() -> None:
    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="vf-stage-label">Composer</div>
        <div class="vf-stage-title">Control the run without leaving the main stage.</div>
        <div class="vf-stage-copy">Prompt, mode, retrieval, and explanation style all stay together so the demo feels intentional.</div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("vf-query-form", clear_on_submit=False):
        st.text_area(
            "Describe the listening moment",
            key="draft_query",
            label_visibility="collapsed",
            height=130,
            placeholder="Need calm music for late-night coding",
        )
        controls = st.columns([1.15, 1.15, 0.7, 0.9, 1.0, 1.0], gap="small")
        with controls[0]:
            st.selectbox("Mode", list(MODE_OPTIONS.keys()), key="ui_mode")
        with controls[1]:
            st.selectbox("Style", list(SPECIALIZATION_OPTIONS.keys()), key="ui_specialization")
        with controls[2]:
            st.number_input("Top K", min_value=3, max_value=8, step=1, key="ui_top_k")
        with controls[3]:
            st.toggle("Diversity", key="ui_diversity")
        with controls[4]:
            st.toggle("Multi-source", key="ui_support")
        with controls[5]:
            st.toggle("Styled output", key="ui_show_specialized")

        submitted = st.form_submit_button("Run Live Demo", type="primary", width="stretch")

    if submitted:
        with st.spinner("Running retrieval, ranking, specialization, and reliability checks..."):
            _run_query()


def _render_overview_strip(response) -> None:
    confidence = _confidence_score(response)
    support_hits = len(response.support_matches)
    trace_steps = len(response.agent_steps)
    warnings = len(response.reliability.warnings)
    specialization = response.specialization_profile.replace("_", " ") if response.specialization_profile != "off" else "plain"

    st.markdown(
        f"""
        <div class="vf-metric-row">
          <div class="vf-metric">
            <div class="vf-metric-label">Confidence</div>
            <div class="vf-metric-value">{confidence:.0%}</div>
            <div class="vf-metric-note">Grounding + consistency + coverage</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Support docs</div>
            <div class="vf-metric-value">{support_hits}</div>
            <div class="vf-metric-note">Extra query guides that matched</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Trace steps</div>
            <div class="vf-metric-value">{trace_steps}</div>
            <div class="vf-metric-note">Visible planning and retrieval chain</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Style layer</div>
            <div class="vf-metric-value">{_escape(specialization.title())}</div>
            <div class="vf-metric-note">{warnings} active warning(s) in this run</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_recommendation_stage(response) -> None:
    if not response.recommendations:
        st.warning("No recommendations were returned for this run.")
        return

    st.markdown(
        """
        <div class="vf-stage-label">Recommendations</div>
        <div class="vf-stage-title">Lead with the output, not the plumbing.</div>
        <div class="vf-stage-copy">The top match gets the spotlight. Supporting picks stay easy to compare without turning into a spreadsheet.</div>
        """,
        unsafe_allow_html=True,
    )

    top_pick = response.recommendations[0]
    specialization_markup = ""
    if top_pick.specialized_explanation:
        specialization_markup = (
            f'<div class="vf-caption" style="margin-top:0.8rem;"><strong>Styled explanation.</strong> {_escape(top_pick.specialized_explanation)}</div>'
        )

    evidence_markup = "".join(f"<li>{_escape(item)}</li>" for item in top_pick.evidence[:2]) or "<li>No evidence attached</li>"
    st.markdown(
        f"""
        <div class="vf-rec-hero">
          <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
            <div style="display:flex; gap:0.95rem;">
              <div class="vf-rank">1</div>
              <div>
                <div class="vf-song-title big">{_escape(top_pick.song["title"])}</div>
                <div class="vf-song-meta">{_escape(top_pick.song["artist"])} · {_escape(top_pick.song["genre"].title())}</div>
              </div>
            </div>
            <div class="vf-status ok">Final {top_pick.final_score:.2f}</div>
          </div>

          <div class="vf-kpi-row">
            <div class="vf-kpi"><small>Base</small><strong>{top_pick.base_score:.2f}</strong></div>
            <div class="vf-kpi"><small>RAG</small><strong>{top_pick.retrieval_score:.2f}</strong></div>
            <div class="vf-kpi"><small>Terms</small><strong>{_escape(", ".join(top_pick.matched_terms[:3]) or "context")}</strong></div>
          </div>

          <div class="vf-copy"><strong>Why it won.</strong> {_escape(top_pick.explanation)}</div>
          {specialization_markup}
          <div class="vf-divider"></div>
          <div class="vf-caption">Evidence cues</div>
          <ul class="vf-copy" style="margin:0.5rem 0 0 1.1rem;">{evidence_markup}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    secondary = response.recommendations[1:3]
    if secondary:
        cols = st.columns(len(secondary), gap="large")
        for column, item in zip(cols, secondary):
            with column:
                styled = ""
                if item.specialized_explanation:
                    styled = f'<div class="vf-caption"><strong>Style.</strong> {_escape(item.specialized_explanation)}</div>'
                st.markdown(
                    f"""
                    <div class="vf-rec-card">
                      <div style="display:flex; justify-content:space-between; gap:0.8rem;">
                        <div>
                          <div class="vf-song-title">{_escape(item.song["title"])}</div>
                          <div class="vf-song-meta">{_escape(item.song["artist"])} · {_escape(item.song["genre"].title())}</div>
                        </div>
                        <div class="vf-status ok">{item.final_score:.2f}</div>
                      </div>
                      <div class="vf-kpi-row">
                        <div class="vf-kpi"><small>Base</small><strong>{item.base_score:.2f}</strong></div>
                        <div class="vf-kpi"><small>RAG</small><strong>{item.retrieval_score:.2f}</strong></div>
                        <div class="vf-kpi"><small>Terms</small><strong>{_escape(", ".join(item.matched_terms[:2]) or "context")}</strong></div>
                      </div>
                      <div class="vf-copy">{_escape(item.explanation)}</div>
                      {styled}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    remaining = response.recommendations[3:]
    if remaining:
        st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="vf-stage-label">More picks</div>
            <div class="vf-stage-copy">Secondary candidates stay compact for comparison without overcrowding the hero results.</div>
            """,
            unsafe_allow_html=True,
        )
        for index, item in enumerate(remaining, start=4):
            st.markdown(
                f"""
                <div class="vf-mini-item">
                  <div style="display:flex; justify-content:space-between; gap:0.9rem; align-items:flex-start;">
                    <div>
                      <div class="vf-song-title" style="font-size:1.08rem;">{index}. {_escape(item.song["title"])}</div>
                      <div class="vf-song-meta">{_escape(item.song["artist"])} · {_escape(item.song["genre"].title())}</div>
                    </div>
                    <div class="vf-status ok">{item.final_score:.2f}</div>
                  </div>
                  <div class="vf-caption" style="margin-top:0.45rem;">{_escape(item.explanation)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_system_panels(response) -> None:
    warning_class = _status_class(response.reliability.status, len(response.reliability.warnings))
    warnings_markup = "".join(
        f'<li>{_escape(item)}</li>'
        for item in (response.reliability.warnings or ("No warnings emitted.",))
    )
    parser_notes = "".join(f"<li>{_escape(note)}</li>" for note in response.intent.parser_notes[:6]) or "<li>No parser notes.</li>"
    tags_markup = "".join(f'<div class="vf-chip">{_escape(tag)}</div>' for tag in response.intent.activity_tags[:8])
    desired_markup = "".join(f'<div class="vf-chip dim">{_escape(tag)}</div>' for tag in response.intent.desired_tags[:8])

    st.markdown(
        f"""
        <div class="vf-panel-strong">
          <div class="vf-stage-label">System lens</div>
          <div class="vf-stage-title">Reliability stays adjacent to the answer.</div>
          <div style="display:flex; flex-wrap:wrap; gap:0.7rem; margin-top:0.9rem; margin-bottom:0.85rem;">
            <div class="vf-status {warning_class}">{_escape(response.reliability.status.title())}</div>
            <div class="vf-status ok">Grounded: {_escape(str(response.reliability.grounded))}</div>
            <div class="vf-status ok">Consistent: {_escape(str(response.reliability.consistency_ok))}</div>
          </div>
          <div class="vf-copy">Evidence coverage: {response.reliability.evidence_coverage:.2f}. The system reruns the pipeline and checks whether output stays grounded in retrieved evidence.</div>
          <div class="vf-divider"></div>
          <div class="vf-stage-label">Warnings</div>
          <ul class="vf-copy" style="margin:0.5rem 0 0 1.1rem;">{warnings_markup}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="vf-panel">
          <div class="vf-stage-label">Intent decode</div>
          <div class="vf-stage-title">What the parser decided.</div>
          <div class="vf-stage-copy">Mode: {_escape(response.intent.mode)} · Mood: {_escape(response.intent.favorite_mood)} · Energy: {response.intent.target_energy:.2f}</div>
          <div class="vf-chip-row">{tags_markup or '<div class="vf-chip dim">No activity tags</div>'}</div>
          <div class="vf-chip-row" style="margin-top:0.55rem;">{desired_markup or '<div class="vf-chip dim">No desired tags</div>'}</div>
          <div class="vf-divider"></div>
          <div class="vf-stage-label">Parser notes</div>
          <ul class="vf-caption" style="margin:0.45rem 0 0 1.1rem;">{parser_notes or '<li>No parser notes.</li>'}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="vf-panel">
          <div class="vf-stage-label">Agent trace</div>
          <div class="vf-stage-title">Intermediate reasoning stays visible.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for step in response.agent_steps:
        st.markdown(
            f"""
            <div class="vf-trace-item">
              <div class="vf-trace-title">{step.step}. {_escape(step.name)}</div>
              <div class="vf-copy">{_escape(step.summary)}</div>
              <div class="vf-caption">{_escape(step.detail)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_retrieval_stage(response) -> None:
    st.markdown(
        """
        <div class="vf-stage-label">Retrieval surfaces</div>
        <div class="vf-stage-title">Show the evidence without drowning the result.</div>
        <div class="vf-stage-copy">Support docs explain how ambiguous language was widened. Song evidence shows what directly affected ranking.</div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([0.95, 1.15], gap="large")

    with left:
        st.markdown('<div class="vf-panel-strong">', unsafe_allow_html=True)
        st.markdown('<div class="vf-stage-label">Support documents</div>', unsafe_allow_html=True)
        st.markdown('<div class="vf-stage-copy">Query-level guides that reinterpret synonym-heavy prompts into stronger activity and mood signals.</div>', unsafe_allow_html=True)
        if response.support_matches:
            st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
            for item in response.support_matches:
                st.markdown(
                    f"""
                    <div class="vf-mini-item">
                      <div class="vf-song-title" style="font-size:1rem;">{_escape(item.title)}</div>
                      <div class="vf-song-meta">Score {item.retrieval_score:.2f} · {_escape(', '.join(item.matched_terms) or 'phrase match')}</div>
                      <div class="vf-caption">{_escape(item.evidence[0] if item.evidence else 'No evidence')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No support documents matched this run.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="vf-panel-strong">', unsafe_allow_html=True)
        st.markdown('<div class="vf-stage-label">Song evidence</div>', unsafe_allow_html=True)
        st.markdown('<div class="vf-stage-copy">These retrieval matches flow directly into the final ranking and explanation chain.</div>', unsafe_allow_html=True)
        st.markdown('<div class="vf-section-gap"></div>', unsafe_allow_html=True)
        for item in response.retrieved_items[:6]:
            st.markdown(
                f"""
                <div class="vf-mini-item">
                  <div style="display:flex; justify-content:space-between; gap:0.8rem; align-items:flex-start;">
                    <div>
                      <div class="vf-song-title" style="font-size:1rem;">{_escape(item.title)}</div>
                      <div class="vf-song-meta">RAG {item.retrieval_score:.2f} · {_escape(', '.join(item.matched_terms) or 'context match')}</div>
                    </div>
                  </div>
                  <div class="vf-caption">{_escape(item.evidence[0] if item.evidence else item.descriptor)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def _render_labs_stage() -> None:
    st.markdown(
        """
        <div class="vf-stage-label">Lab views</div>
        <div class="vf-stage-title">Keep grading and validation tools nearby, but off the critical path.</div>
        <div class="vf-stage-copy">These tabs support the demo without stealing focus from the recommendations.</div>
        """,
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["Benchmarks", "Evaluation", "Architecture"])
    with tabs[0]:
        _render_benchmarks_panel()
    with tabs[1]:
        _render_evaluation_panel()
    with tabs[2]:
        _render_architecture_panel()


def _render_benchmarks_panel() -> None:
    st.markdown(
        """
        <div class="vf-panel-strong">
          <div class="vf-stage-label">Reliability benchmarks</div>
          <div class="vf-stage-title">Scenario checks for consistency and warning behavior.</div>
          <div class="vf-stage-copy">Use the sidebar button to populate the benchmark table with live results.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rows = st.session_state.reliability_rows
    if not rows:
        st.info("Run `Reliability Benchmarks` from the sidebar to populate this table.")
        return

    benchmark_data = [
        {
            "Scenario": row.name,
            "Top Titles": ", ".join(row.top_titles),
            "Expected Hit": "pass" if row.hit_expected else "review",
            "Warning Behavior": "ok" if row.warning_present == row.expect_warning else "mismatch",
            "Grounded": row.grounded,
            "Consistent": row.consistency_ok,
        }
        for row in rows
    ]
    st.dataframe(benchmark_data, width="stretch", hide_index=True)


def _render_evaluation_panel() -> None:
    st.markdown(
        """
        <div class="vf-panel-strong">
          <div class="vf-stage-label">Optional feature evaluation</div>
          <div class="vf-stage-title">Baseline versus enhanced retrieval, measured directly.</div>
          <div class="vf-stage-copy">Use the sidebar button to compare single-source retrieval against the multi-source version.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    summary = st.session_state.evaluation_summary
    if summary is None:
        st.info("Run `Optional Feature Evaluation` from the sidebar to generate the comparison report.")
        return

    st.markdown(
        f"""
        <div class="vf-metric-row" style="margin-top:1rem;">
          <div class="vf-metric">
            <div class="vf-metric-label">Hit@3 uplift</div>
            <div class="vf-metric-value">{summary.baseline_hits}/{len(summary.rows)} -> {summary.enhanced_hits}/{len(summary.rows)}</div>
            <div class="vf-metric-note">baseline to enhanced</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Avg confidence</div>
            <div class="vf-metric-value">{summary.average_confidence:.2f}</div>
            <div class="vf-metric-note">enhanced runs only</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Trace depth</div>
            <div class="vf-metric-value">{summary.average_trace_steps:.2f}</div>
            <div class="vf-metric-note">observable chain depth</div>
          </div>
          <div class="vf-metric">
            <div class="vf-metric-label">Style compliance</div>
            <div class="vf-metric-value">{summary.style_compliance_rate:.0%}</div>
            <div class="vf-metric-note">specialized output checks</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    evaluation_data = [
        {
            "Scenario": row.name,
            "Baseline": "pass" if row.baseline_hit else "review",
            "Enhanced": "pass" if row.enhanced_hit else "review",
            "Confidence": f"{row.enhanced_confidence:.2f}",
            "Trace": row.trace_steps,
            "Specialization": row.specialization_profile,
            "Enhanced Top 3": ", ".join(row.enhanced_titles),
        }
        for row in summary.rows
    ]
    st.dataframe(evaluation_data, width="stretch", hide_index=True)


def _render_architecture_panel() -> None:
    st.markdown(
        """
        <div class="vf-panel-strong">
          <div class="vf-stage-label">Architecture</div>
          <div class="vf-stage-title">The same pipeline shown in the paper trail.</div>
          <div class="vf-stage-copy">This keeps the live demo aligned with the README, tests, and grading rubric.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    image_path = Path("assets/architecture/music-ai-system-architecture.png")
    if image_path.exists():
        st.image(str(image_path), width="stretch", caption="VibeFinder runtime architecture")
    else:
        st.info("Architecture image not found.")


def _confidence_score(response) -> float:
    score = 0.45
    score += 0.2 if response.reliability.grounded else 0.0
    score += 0.15 if response.reliability.consistency_ok else 0.0
    score += 0.15 * response.reliability.evidence_coverage
    score -= 0.08 * len(response.reliability.warnings)
    return max(0.0, min(1.0, score))


def _status_class(status: str, warning_count: int) -> str:
    if warning_count >= 2:
        return "alert"
    if status != "pass" or warning_count > 0:
        return "warn"
    return "ok"


def _escape(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


if __name__ == "__main__":
    main()
