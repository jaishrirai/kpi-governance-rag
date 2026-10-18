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
GOOD = ("30 days [KPI-006::v1::0].", ("KPI-006::v1::0",), False)
BAD = ("x [KPI-999::v1::0].", ("KPI-999::v1::0",), False)


def retrieve(question):
    return list(HITS)


def reply(answer, citations, refused=False):
    return g.GenerationResult(answer, list(citations), refused, "answer_v1", model="fake-model",
                              input_tokens=100, output_tokens=20, thinking_tokens=0, latency_ms=12.5)


def fake_generate(answer=GOOD[0], citations=GOOD[1], refused=False):
    def run(question, hits, correction=None):
        return reply(answer, citations, refused)
    return run


def scripted(*outcomes):
    """Model replies in order (or raises an exception); records what each call was sent."""
    calls = []

    def run(question, hits, correction=None):
        calls.append({"correction": correction, "hits": hits})
        outcome = outcomes[len(calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return reply(*outcome)

    return run, calls


def traces(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_happy_path_one_attempt_no_retry(tmp_path):
    path = tmp_path / "traces.jsonl"
    run, calls = scripted(GOOD)
    out = pipeline.ask("How many days?", retrieve, run, trace_path=path)
    assert (out.answer, out.citations, out.refused, out.valid, out.problems, out.error) == (
        "30 days [KPI-006::v1::0].", ["KPI-006::v1::0"], False, True, [], None)
    assert out.chunk_ids == ["KPI-006::v1::0", "FAQ-01::v1::0"]
    assert len(calls) == 1 and calls[0]["correction"] is None and len(out.attempts) == 1
    (record,) = traces(path)
    assert record["question"] == "How many days?" and record["valid"] is True and record["error"] is None
    assert record["attempt_count"] == 1 and record["policy_refusal"] is False
    assert (record["variant"], record["retriever"], record["k"], record["prompt_version"]) == ("v1", "vector", 5, "answer_v1")
    assert (record["model"], record["input_tokens"], record["output_tokens"], record["generation_ms"]) == ("fake-model", 100, 20, 12.5)


def test_valid_refusal_passes_without_retry(tmp_path):
    run, calls = scripted((g.REFUSAL_MESSAGE, (), True))
    out = pipeline.ask("CEO?", retrieve, run, trace_path=tmp_path / "t.jsonl")
    assert out.refused is True and out.valid is True and out.citations == [] and len(calls) == 1


def test_invalid_citation_then_valid_retry_recovers(tmp_path):
    path = tmp_path / "t.jsonl"
    run, calls = scripted(BAD, GOOD)
    out = pipeline.ask("q", retrieve, run, trace_path=path)
    (record,) = traces(path)  # both attempts are in the trace; the recovered answer is the final one
    assert record["attempt_count"] == 2 and record["policy_refusal"] is False and record["valid"] is True
    assert [a["answer"] for a in record["attempts"]] == [BAD[0], GOOD[0]]
    assert record["answer"] == GOOD[0] and record["citations"] == ["KPI-006::v1::0"]
    assert out.valid is True and out.policy_refusal is False and out.answer == GOOD[0]
    assert len(out.attempts) == 2 and out.attempts[0]["problems"] and out.attempts[1]["problems"] == []
    assert out.attempts[0]["answer"] == BAD[0]  # the rejected answer is kept
    assert calls[0]["correction"] is None
    correction = calls[1]["correction"]
    assert "These citation IDs were invalid: [KPI-999::v1::0]." in correction
    assert "You may cite only these retrieved IDs: [KPI-006::v1::0, FAQ-01::v1::0]." in correction


def test_retry_sends_the_same_chunks_again(tmp_path):
    run, calls = scripted(BAD, GOOD)
    pipeline.ask("q", retrieve, run, trace_path=tmp_path / "t.jsonl")
    assert calls[0]["hits"] == calls[1]["hits"] == HITS


def test_retrieval_runs_once_even_when_the_answer_is_retried(tmp_path):
    seen = []

    def counting_retrieve(question):
        seen.append(question)
        return list(HITS)

    run, _ = scripted(BAD, GOOD)
    pipeline.ask("q", counting_retrieve, run, trace_path=tmp_path / "t.jsonl")
    assert seen == ["q"]


def test_invalid_twice_returns_refusal_and_keeps_both_attempts(tmp_path):
    path = tmp_path / "t.jsonl"
    run, calls = scripted(BAD, BAD)
    out = pipeline.ask("q", retrieve, run, trace_path=path)
    assert len(calls) == 2
    assert out.answer == g.REFUSAL_MESSAGE and out.citations == [] and out.refused is True
    assert out.valid is False and out.policy_refusal is True
    assert [a["answer"] for a in out.attempts] == [BAD[0], BAD[0]]
    (record,) = traces(path)
    assert record["answer"] == g.REFUSAL_MESSAGE and record["attempt_count"] == 2
    assert record["policy_refusal"] is True and len(record["attempts"]) == 2


def test_refused_with_citations_is_retried_with_the_consistency_rule(tmp_path):
    run, calls = scripted(("no", ("KPI-006::v1::0",), True), GOOD)
    out = pipeline.ask("q", retrieve, run, trace_path=tmp_path / "t.jsonl")
    assert out.valid is True and out.answer == GOOD[0]
    assert "Your refused flag and citations did not agree." in calls[1]["correction"]


def test_answer_with_no_citations_is_retried(tmp_path):
    run, calls = scripted(("30 days.", (), False), GOOD)
    out = pipeline.ask("q", retrieve, run, trace_path=tmp_path / "t.jsonl")
    assert out.valid is True and len(calls) == 2
    assert "Your refused flag and citations did not agree." in calls[1]["correction"]


def test_retry_error_is_logged_as_a_retry_failure(tmp_path):
    path = tmp_path / "t.jsonl"
    run, calls = scripted(BAD, RuntimeError("503"))
    out = pipeline.ask("q", retrieve, run, trace_path=path)
    assert len(calls) == 2  # the failed retry is the last call: no third attempt
    assert out.error == "retry generation failed: RuntimeError: 503"
    assert out.valid is False and out.answer == "" and len(out.attempts) == 1
    (record,) = traces(path)
    assert record["error"] == out.error and record["attempt_count"] == 1


def test_generation_error_is_logged_with_the_stage_and_no_answer(tmp_path):
    path = tmp_path / "t.jsonl"

    def broken(question, hits, correction=None):
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

    out = pipeline.ask("q", bad_retrieve, lambda q, h, correction=None: calls.append(1), trace_path=path)
    assert calls == [] and out.error == "retrieval failed: RuntimeError: index missing"
    assert traces(path)[0]["error"] == out.error


def test_generation_receives_the_retrieved_hits_unchanged(tmp_path):
    seen = {}

    def spy(question, hits, correction=None):
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


def test_cli_shows_policy_refusal_when_both_answers_fail(tmp_path, capsys):
    code = run_cli(["q"], tmp_path, fake_generate("x", ("NOPE::v1::0",)))
    out = capsys.readouterr().out
    assert code == 2 and "validation: FAILED" in out and "NOPE::v1::0" in out
    assert "answer:    I could not find this in the governed documents." in out
    assert "returned by policy" in out


def test_cli_reports_errors_and_exits_one(tmp_path, capsys):
    def broken(question, hits, correction=None):
        raise RuntimeError("503")
    code = run_cli(["q"], tmp_path, broken)
    captured = capsys.readouterr()
    assert code == 1 and "ERROR: generation failed: RuntimeError: 503" in captured.err


def test_cli_requires_a_question(tmp_path):
    with pytest.raises(SystemExit):
        run_cli([], tmp_path, fake_generate())
