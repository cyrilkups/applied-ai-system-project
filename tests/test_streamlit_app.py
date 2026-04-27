from streamlit.testing.v1 import AppTest


def _load_app() -> AppTest:
    app = AppTest.from_file("streamlit_app.py")
    app.run(timeout=60)
    return app


def _button_by_label(app: AppTest, label: str):
    for button in app.button:
        if button.label == label:
            return button
    raise AssertionError(f"Button with label '{label}' was not found.")


def test_streamlit_app_loads_without_exceptions():
    app = _load_app()

    assert len(app.exception) == 0
    assert len(app.text_area) == 1
    assert len(app.tabs) == 3


def test_streamlit_app_live_demo_form_accepts_query():
    app = _load_app()

    app.text_area[0].input("Need something for debugging at 1am")
    _button_by_label(app, "Run Live Demo").click().run(timeout=60)

    assert len(app.exception) == 0
    assert app.text_area[0].value == "Need something for debugging at 1am"


def test_streamlit_app_preset_button_updates_prompt():
    app = _load_app()

    _button_by_label(app, "Gym Surge").click().run(timeout=60)

    assert len(app.exception) == 0
    assert app.text_area[0].value == "Need high-energy music for the gym"


def test_streamlit_app_benchmarks_and_evaluation_panels_populate():
    app = _load_app()

    _button_by_label(app, "Run Reliability Benchmarks").click().run(timeout=60)
    assert len(app.exception) == 0
    assert len(app.dataframe) == 1

    app = _load_app()
    _button_by_label(app, "Run Optional Feature Evaluation").click().run(timeout=60)
    assert len(app.exception) == 0
    assert len(app.dataframe) == 1
