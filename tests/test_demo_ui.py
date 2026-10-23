"""Step 3.3: the Streamlit page, run headless with Streamlit's AppTest and recorded answers (no network).
Skipped when streamlit is not installed."""
import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from rag import demo_view as view  # noqa: E402
from tests.demo_fakes import ROOT  # noqa: E402

pytestmark = pytest.mark.skipif(
    not (ROOT / "results" / "generation" / "answer_v1_holdout.judged.jsonl").exists(),
    reason="recorded Step 3.1 results are needed")


def script():
    from rag.demo_ui import run_app
    from tests.demo_fakes import make_deps

    run_app(make_deps())


def open_page(monkeypatch, tmp_path, example=None, builder=False, bm25_fail=False, no_key=False):
    monkeypatch.setenv("DEMO_TEST_TRACE", str(tmp_path / "demo_traces.jsonl"))
    if bm25_fail:
        monkeypatch.setenv("DEMO_TEST_BM25_FAIL", "1")
    if no_key:
        monkeypatch.setenv("DEMO_TEST_NO_KEY", "1")
    at = AppTest.from_function(script, default_timeout=30).run()
    if example is not None:
        at.selectbox(key="example").select(view.EXAMPLES[example][0]).run()
    if builder:
        at.toggle[0].set_value(True).run()
    return at


def ask(at):
    at.button[0].click().run()
    assert not at.exception
    return at


def texts(elements):
    return " ".join(str(e.value) for e in elements)


def test_the_page_opens_with_a_simple_title_and_no_answer(monkeypatch, tmp_path):
    at = open_page(monkeypatch, tmp_path)
    assert not at.exception
    assert at.title[0].value == "KPI Governance Assistant"
    assert "fictional" in texts(at.caption)
    assert len(at.success) == 0 and len(at.error) == 0


def test_example_picker_fills_the_question_box(monkeypatch, tmp_path):
    at = open_page(monkeypatch, tmp_path, example=5)
    assert at.text_area(key="question").value == view.EXAMPLES[5][1]


def test_example_1_normal_answer_with_numbered_sources(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=0))
    assert at.success[0].value == "Answered from governed documents"
    body = texts(at.markdown)
    assert "[1]" in body and "Sources" in body and "KPI-007::v1::0" in body
    assert len(at.warning) == 0  # every cited source is Certified


def test_example_2_deprecated_source_shows_the_yellow_note(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=4))
    assert at.success[0].value == "Answered from governed documents"
    assert "not Certified" in texts(at.warning) and "Deprecated" in texts(at.warning)


def test_example_3_unanswerable_question_is_a_clear_not_found(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=5))
    assert at.info[0].value == "Not found in the governed documents"
    assert len(at.success) == 0
    assert "does not guess" in texts(at.markdown)


def test_example_4_known_limit_answers_without_inventing_an_owner(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=6))
    assert at.success[0].value == "Answered from governed documents"
    assert "does not state who owns KPI-020" in texts(at.markdown)


def test_example_5_process_question_answers_with_no_yellow_note(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=1))
    assert at.success[0].value == "Answered from governed documents"
    assert len(at.warning) == 0


def test_example_6_governance_rule_answers_and_flags_the_provisional_source(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=2))
    assert at.success[0].value == "Answered from governed documents"
    assert "not Certified" in texts(at.warning) and "Provisional" in texts(at.warning)


def test_example_7_conflicting_sources_flags_the_informal_faq(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=3))
    assert at.success[0].value == "Answered from governed documents"
    assert "not Certified" in texts(at.warning) and "Provisional" in texts(at.warning)


def test_how_it_works_is_hidden_by_default_and_shown_on_request(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=6))
    assert len(at.subheader) == 0 and len(at.dataframe) == 0
    at = ask(open_page(monkeypatch, tmp_path, example=6, builder=True))
    assert at.subheader[0].value == "How it works"
    assert len(at.dataframe) == 1
    frame = at.dataframe[0].value
    assert list(frame["Vector rank"]) == ["1", "2", "3", "4", "5"]
    assert "Rank" not in frame.columns
    assert "comparison only" in texts(at.info)
    assert "would also have surfaced: Extra Doc, Certified" in texts(at.caption)
    assert view.NOT_IN_TOP in set(frame["BM25 rank"])
    assert all(isinstance(v, str) for v in frame["BM25 rank"])


def test_a_failed_comparison_cannot_break_the_answer(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=0, builder=True, bm25_fail=True))
    assert at.success[0].value == "Answered from governed documents"
    assert "unavailable" in texts(at.caption)
    assert set(at.dataframe[0].value["BM25 rank"]) == {view.UNAVAILABLE}


def test_missing_key_gives_a_plain_message_and_no_model_call(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path, example=0, no_key=True))
    assert "GEMINI_API_KEY" in texts(at.error)
    assert not (tmp_path / "demo_traces.jsonl").exists()


def test_demo_questions_are_logged_to_the_demo_trace_not_the_evidence_trace(monkeypatch, tmp_path):
    ask(open_page(monkeypatch, tmp_path, example=0))
    assert (tmp_path / "demo_traces.jsonl").read_text(encoding="utf-8").count("\n") == 1


def test_an_empty_question_asks_for_text(monkeypatch, tmp_path):
    at = ask(open_page(monkeypatch, tmp_path))
    assert "Type a question first" in texts(at.warning)


def test_launcher_shows_a_plain_error_page_when_the_index_cannot_load(monkeypatch):
    try:
        import chromadb  # noqa: F401
    except ImportError:
        pass
    else:
        pytest.skip("chromadb is installed here; this test needs it missing to force the error page")
    at = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py"), default_timeout=30).run()
    assert not at.exception
    assert at.error[0].value == "The assistant could not start."
    assert "rag.index" in texts(at.markdown)
