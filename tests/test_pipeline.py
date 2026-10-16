"""pipeline.ask and the rag.ask CLI with fake retrieval and a fake model: no network, no index."""
import json

import pytest

from rag import ask as cli
from rag import generate as g
from rag import pipeline

HITS = [
    {"chunk_id": "KPI-006::v1::0", "doc_id": "KPI-006", "certification": "Certified", "text": "30 days."},
    {"chunk_id": "FAQ-01::v1::0", "doc_id": "FAQ-01", "certification": "Provisional", "text": "90 days."},
]


def retrieve(question):
    return list(HITS)


def fake_generate(answer="30 days [KPI-006::v1::0].", citations=("KPI-006::v1::0",), refused=False):
    def run(question, hits):
        return g.GenerationResult(answer, list(citations), refused, "answer_v1", model="fake-model",
                                  input_tokens=100, output_tokens=20, thinking_tokens=0, latency_ms=12.5,
                                  chunk_ids=[h["chunk_id"] for h in hits])
    return run


def traces(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_happy_path_returns_answer_and_writes_one_trace(tmp_path):
    path = tmp_path / "traces.jsonl"
    out = pipeline.ask("How many days?", retrieve, fake_generate(), trace_path=path)
    assert (out.answer, out.citations, out.refused, out.valid, out.problems, out.error) == (
        "30 days [KPI-006::v1::0].", ["KPI-006::v1::0"], False, True, [], None)
    assert out.chunk_ids == ["KPI-006::v1::0", "FAQ-01::v1::0"]
    (record,) = traces(path)
    assert record["question"] == "How many days?" and record["valid"] is True and record["error"] is None
    assert record["chunk_ids"] == out.chunk_ids and record["citations"] == ["KPI-006::v1::0"]
    assert (record["variant"], record["retriever"], record["k"], record["prompt_version"]) == ("v1", "vector", 5, "answer_v1")
    assert (record["model"], record["input_tokens"], record["output_tokens"], record["generation_ms"]) == ("fake-model", 100, 20, 12.5)
    assert "timestamp" in record and record["refused"] is False


def test_valid_refusal_passes(tmp_path):
    path = tmp_path / "t.jsonl"
    out = pipeline.ask("CEO?", retrieve, fake_generate(g.REFUSAL_MESSAGE, (), True), trace_path=path)
    assert out.refused is True and out.valid is True and out.citations == []


def test_invalid_citation_is_reported_but_the_answer_is_not_changed(tmp_path):
    path = tmp_path / "t.jsonl"
    out = pipeline.ask("q", retrieve, fake_generate("x [KPI-999::v1::0]", ("KPI-999::v1::0",)), trace_path=path)
    assert out.valid is False and out.answer == "x [KPI-999::v1::0]" and out.citations == ["KPI-999::v1::0"]
    assert len(out.problems) == 1 and "KPI-999::v1::0" in out.problems[0]
    (record,) = traces(path)
    assert record["valid"] is False and record["problems"] == out.problems and record["error"] is None


def test_refused_flag_and_citations_disagreeing_is_flagged(tmp_path):
    out = pipeline.ask("q", retrieve, fake_generate("no", ("KPI-006::v1::0",), True), trace_path=tmp_path / "t.jsonl")
    assert out.valid is False and out.problems == ["refused=True but citations were given"]


def test_generation_error_is_logged_with_the_stage_and_no_answer(tmp_path):
    path = tmp_path / "t.jsonl"

    def broken(question, hits):
        raise g.GenerationError("Reply is not valid JSON")

    out = pipeline.ask("q", retrieve, broken, trace_path=path)
    assert out.valid is False and out.answer == "" and out.generation is None
    assert out.error == "generation failed: GenerationError: Reply is not valid JSON"
    (record,) = traces(path)
    assert record["error"] == out.error and record["chunk_ids"] == out.chunk_ids and record["valid"] is False


def test_retrieval_error_is_logged_and_generation_is_never_called(tmp_path):
    path = tmp_path / "t.jsonl"
    calls = []

    def bad_retrieve(question):
        raise RuntimeError("index missing")

    out = pipeline.ask("q", bad_retrieve, lambda q, h: calls.append(1), trace_path=path)
    assert calls == [] and out.error == "retrieval failed: RuntimeError: index missing"
    assert traces(path)[0]["error"] == out.error


def test_generation_receives_the_retrieved_hits_unchanged(tmp_path):
    seen = {}

    def spy(question, hits):
        seen["args"] = (question, hits)
        return fake_generate()(question, hits)

    pipeline.ask("How many days?", retrieve, spy, trace_path=tmp_path / "t.jsonl")
    assert seen["args"] == ("How many days?", HITS)


def test_traces_append_and_the_folder_is_created(tmp_path):
    path = tmp_path / "results" / "traces.jsonl"
    pipeline.ask("first", retrieve, fake_generate(), trace_path=path)
    pipeline.ask("second", retrieve, fake_generate(), trace_path=path)
    assert [r["question"] for r in traces(path)] == ["first", "second"]


def test_trace_keeps_non_ascii_text_readable(tmp_path):
    path = tmp_path / "t.jsonl"
    pipeline.ask("café?", retrieve, fake_generate(), trace_path=path)
    assert "café" in path.read_text(encoding="utf-8")


def test_empty_retrieval_refuses_without_error(tmp_path):
    out = pipeline.ask("q", lambda q: [], g.generate, trace_path=tmp_path / "t.jsonl")
    assert out.refused is True and out.valid is True and out.chunk_ids == []


def run_cli(args, tmp_path, generate_fn):
    return cli.main(args, retrieve_fn=retrieve, generate_fn=generate_fn, trace_path=tmp_path / "t.jsonl")


def test_cli_prints_answer_validation_and_exits_zero(tmp_path, capsys):
    code = run_cli(["How", "many", "days?"], tmp_path, fake_generate())
    out = capsys.readouterr().out
    assert code == 0 and "answer:    30 days [KPI-006::v1::0]." in out and "validation: OK" in out
    assert "Retrieved: ['KPI-006::v1::0', 'FAQ-01::v1::0']" in out
    assert traces(tmp_path / "t.jsonl")[0]["question"] == "How many days?"


def test_cli_shows_failed_validation_but_still_shows_the_answer(tmp_path, capsys):
    code = run_cli(["q"], tmp_path, fake_generate("x", ("NOPE::v1::0",)))
    out = capsys.readouterr().out
    assert code == 2 and "validation: FAILED" in out and "NOPE::v1::0" in out and "answer:    x" in out


def test_cli_reports_errors_and_exits_one(tmp_path, capsys):
    def broken(question, hits):
        raise RuntimeError("503")
    code = run_cli(["q"], tmp_path, broken)
    captured = capsys.readouterr()
    assert code == 1 and "ERROR: generation failed: RuntimeError: 503" in captured.err


def test_cli_requires_a_question(tmp_path):
    with pytest.raises(SystemExit):
        run_cli([], tmp_path, fake_generate())
