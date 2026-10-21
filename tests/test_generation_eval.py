"""generation_eval with fake retrieval, a fake model and a fake judge: no network, no index."""
import json
from types import SimpleNamespace

import pytest

from eval import generation_eval as ge
from rag import generate as g

ROWS = [
    {"id": "T-1", "question": "q1", "answerable": True, "holdout": False,
     "key_facts": ["30 days", "only certified"], "conflicting_doc_ids": ["FAQ-01"]},
    {"id": "T-2", "question": "q2", "answerable": False, "holdout": False, "key_facts": [], "conflicting_doc_ids": []},
    {"id": "T-3", "question": "q3", "answerable": True, "holdout": True,
     "key_facts": ["x"], "conflicting_doc_ids": []},
]
HITS = [{"chunk_id": "KPI-006::v1::0", "doc_id": "KPI-006", "certification": "Certified", "text": "30 days."}]


def reply(answer, citations, refused=False, tokens=(100, 20, 5), ms=10.0):
    return g.GenerationResult(answer, list(citations), refused, "answer_v1", model="fake",
                              input_tokens=tokens[0], output_tokens=tokens[1], thinking_tokens=tokens[2], latency_ms=ms)


def fake_generate(outcomes):
    """outcomes: {question: [GenerationResult, ...]} in call order."""
    seen = {}

    def run(question, hits, correction=None):
        seen[question] = seen.get(question, 0) + 1
        return outcomes[question][seen[question] - 1]

    return run


def judge_reply(payload):
    return SimpleNamespace(text=json.dumps(payload))


def fake_judge(facts=None, claims=None):
    """Key-fact prompt mentions 'key fact'; the faithfulness prompt does not."""
    calls = []

    def run(system, user, **kwargs):
        kind = "facts" if "key fact" in system else "claims"
        calls.append(kind)
        return judge_reply({"facts": facts} if kind == "facts" else {"claims": claims})

    return run, calls


def run_records(tmp_path):
    outcomes = {
        "q1": [reply("30 days [KPI-006::v1::0].", ["KPI-006::v1::0"])],
        "q2": [reply(g.REFUSAL_MESSAGE, [], True)],
        "q3": [reply("bad [NOPE::v1::0].", ["NOPE::v1::0"]), reply("bad [NOPE::v1::0].", ["NOPE::v1::0"])],
    }
    return ge.run_questions(ROWS, "answer_v1", lambda q: list(HITS), tmp_path / "t.jsonl",
                            generate_fn=fake_generate(outcomes), progress=lambda line: None)


def test_load_golden_splits_and_ids(tmp_path):
    path = tmp_path / "g.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in ROWS), encoding="utf-8")
    assert [r["id"] for r in ge.load_golden(path, "dev")] == ["T-1", "T-2"]
    assert [r["id"] for r in ge.load_golden(path, "holdout")] == ["T-3"]
    assert [r["id"] for r in ge.load_golden(path, "all", ids=["T-3", "T-1"])] == ["T-1", "T-3"]
    with pytest.raises(ValueError):
        ge.load_golden(path, "all", ids=["T-9"])


def test_run_questions_records_context_split_and_summed_tokens(tmp_path):
    first, refusal, retried = run_records(tmp_path)
    assert (first["split"], first["valid"], first["attempt_count"]) == ("dev", True, 1)
    assert first["contexts"] == HITS and first["chunk_ids"] == ["KPI-006::v1::0"]
    assert refusal["refused"] is True and refusal["valid"] is True
    assert retried["split"] == "holdout" and retried["attempt_count"] == 2 and retried["policy_refusal"] is True
    assert retried["input_tokens"] == 200 and retried["output_tokens"] == 50  # two attempts, thinking included
    assert retried["generation_ms"] == 20.0


def test_judge_key_facts_parses_and_checks_the_count():
    run, _ = fake_judge(facts=[{"fact": "a", "covered": True}, {"fact": "b", "covered": False}])
    assert ge.judge_key_facts("q", "a", ["a", "b"], run) == [True, False]
    with pytest.raises(ge.JudgeError):
        ge.judge_key_facts("q", "a", ["a", "b", "c"], run)
    bad, _ = fake_judge(facts=[{"fact": "a", "covered": "yes"}])
    with pytest.raises(ge.JudgeError):
        ge.judge_key_facts("q", "a", ["a"], bad)


def test_judge_accepts_fenced_json():
    run = lambda system, user, **kw: SimpleNamespace(text='```json\n{"claims": []}\n```')
    assert ge.judge_faithfulness("a", HITS, run) == []


def test_judge_record_skips_refusals_and_pipeline_errors():
    refused = {"error": None, "answerable": True, "key_facts": ["x"], "refused": True,
               "question": "q", "answer": "no", "contexts": HITS}
    run, calls = fake_judge()
    out = ge.judge_record(refused, run)
    assert calls == [] and out["judge"]["key_facts"] == [False] and out["judge"]["claims"] == []
    broken = {**refused, "error": "retrieval failed: boom"}
    assert ge.judge_record(broken, run)["judge"]["errors"] == ["skipped: pipeline error"]


def test_judge_record_keeps_going_after_a_judge_failure():
    record = {"error": None, "answerable": True, "key_facts": ["x"], "refused": False,
              "question": "q", "answer": "a [KPI-006::v1::0].", "contexts": HITS}

    def flaky(system, user, **kwargs):
        if "key fact" in system:
            raise RuntimeError("503")
        return judge_reply({"claims": [{"claim": "a", "supported": True}]})

    out = ge.judge_record(record, flaky)["judge"]
    assert out["key_facts"] is None and out["errors"] == ["key facts: RuntimeError: 503"]
    assert out["claims"] == [{"claim": "a", "supported": True}]


def judged_set():
    base = dict(error=None, valid=True, policy_refusal=False, attempt_count=1, refused=False, retrieval_ms=10.0,
                input_tokens=100, output_tokens=20, generation_ms=1000.0, conflicting_doc_ids=[])
    return [
        {**base, "id": "a", "split": "dev", "answerable": True, "conflicting_doc_ids": ["FAQ-01"],
         "judge": {"errors": [], "key_facts": [True, True], "claims": [{"claim": "c", "supported": True}]}},
        {**base, "id": "b", "split": "dev", "answerable": True, "generation_ms": 3000.0,
         "judge": {"errors": [], "key_facts": [True, False, False],
                   "claims": [{"claim": "c", "supported": True}, {"claim": "d", "supported": False}]}},
        {**base, "id": "c", "split": "dev", "answerable": False, "refused": True,
         "judge": {"errors": [], "key_facts": None, "claims": []}},
        {**base, "id": "d", "split": "dev", "answerable": False, "refused": False, "attempt_count": 2,
         "judge": {"errors": [], "key_facts": None, "claims": [{"claim": "e", "supported": False}]}},
        {**base, "id": "e", "split": "dev", "answerable": True, "refused": True, "policy_refusal": True, "valid": False,
         "judge": {"errors": [], "key_facts": [False], "claims": []}},
    ]


def test_summarise_counts_and_rates():
    s = ge.summarise(judged_set())
    assert (s["n"], s["answerable"], s["unanswerable"]) == (5, 3, 2)
    assert s["coverage"] == pytest.approx(3 / 6) and s["full_coverage"] == pytest.approx(1 / 3)
    assert s["trap_coverage"] == 1.0
    assert s["wrongly_refused"] == 1 and s["correct_refusals"] == 0.5
    assert s["faithful_answers"] == pytest.approx(1 / 3)  # a, b, d answered; only a has no unsupported claim
    assert (s["unsupported_claims"], s["claims"]) == (2, 4)
    assert s["citation_valid"] == pytest.approx(4 / 5)
    assert (s["policy_refusals"], s["retried"]) == (1, 1)
    assert (s["gen_ms_p50"], s["gen_ms_p95"]) == (1000.0, 3000.0)


def test_percentile_and_cost():
    assert ge.percentile([], 50) is None
    assert ge.percentile([4, 1, 3, 2], 50) == 2 and ge.percentile([4, 1, 3, 2], 95) == 4
    s = ge.summarise(judged_set())
    assert ge.cost_per_query(s, None, 1.0) is None
    assert ge.cost_per_query(s, 1.0, 2.0) == pytest.approx((100 * 1.0 + 20 * 2.0) / 1_000_000)


def test_report_has_one_column_per_item_and_a_price_note():
    table = ge.format_report([("v1 dev", ge.summarise(judged_set()))], 1.0, 2.0, "test prices")
    assert "| metric | v1 dev |" in table and "key-fact coverage | 50.0%" in table
    assert "| cost per query |" in table and "test prices" in table


def test_holdout_guard(tmp_path):
    log = tmp_path / "holdout_runs.txt"
    with pytest.raises(SystemExit):
        ge.guard_holdout("answer_v1", False, log)  # not confirmed
    ge.guard_holdout("answer_v1", True, log)  # first run is allowed
    ge.mark_holdout_used("answer_v1", "out.jsonl", log)
    assert ge.holdout_used("answer_v1", log) and not ge.holdout_used("answer_v2", log)
    with pytest.raises(SystemExit):
        ge.guard_holdout("answer_v1", True, log)  # second run of the same version is refused
    ge.guard_holdout("answer_v2", True, log)  # other versions are unaffected


def run_record(rid, answer="a [KPI-006::v1::0]."):
    return {"id": rid, "question": f"q {rid}", "answer": answer, "error": None, "answerable": True,
            "key_facts": ["x"], "refused": False, "contexts": HITS}


def clean_judgment(model="m"):
    return {"model": model, "key_facts": [True], "claims": [], "errors": []}


def test_judge_records_keeps_clean_results_and_retries_only_failures():
    records = [run_record("A"), run_record("B")]
    prior = [{**records[0], "judge": clean_judgment()},
             {**records[1], "judge": {**clean_judgment(), "key_facts": None, "errors": ["ConnectError"]}}]
    run, calls = fake_judge(facts=[{"fact": "x", "covered": True}], claims=[])
    judged = ge.judge_records(records, prior, run, "m", progress=lambda line: None)
    assert calls == ["facts", "claims"]  # B only: A was kept
    assert judged[0]["judge"] == clean_judgment() and judged[1]["judge"]["errors"] == []
    assert judged[1]["judge"]["key_facts"] == [True]


def test_judge_records_rejudges_when_answer_or_judge_model_changed():
    prior = [{**run_record("A"), "judge": clean_judgment("old-model")}]
    run, calls = fake_judge(facts=[{"fact": "x", "covered": True}], claims=[])
    ge.judge_records([run_record("A")], prior, run, "new-model", progress=lambda line: None)
    assert calls == ["facts", "claims"]  # different judge model
    calls.clear()
    prior = [{**run_record("A", answer="old answer"), "judge": clean_judgment("m")}]
    ge.judge_records([run_record("A")], prior, run, "m", progress=lambda line: None)
    assert calls == ["facts", "claims"]  # the answer changed


def test_save_judged_reports_failures_and_ignores_pipeline_skips(tmp_path, capsys):
    ok = {**run_record("A"), "judge": clean_judgment()}
    skipped = {**run_record("B"), "error": "retrieval failed", "judge": {**clean_judgment(), "errors": ["skipped: pipeline error"]}}
    failed = {**run_record("C"), "judge": {**clean_judgment(), "errors": ["key facts: ConnectError: x"]}}
    assert ge.save_judged([ok, skipped], tmp_path / "j.jsonl", "m") == []
    assert ge.save_judged([ok, failed], tmp_path / "j.jsonl", "m") == ["C"]
    assert "1 of 2 records had judge errors: ['C']" in capsys.readouterr().out


def test_summarise_shows_none_not_zero_when_no_answer_was_judged():
    base = dict(error=None, valid=True, policy_refusal=False, attempt_count=1, refused=False, retrieval_ms=1.0,
                input_tokens=1, output_tokens=1, generation_ms=1.0, conflicting_doc_ids=[], split="dev", answerable=True)
    failed = {**base, "id": "a", "judge": {"errors": ["faithfulness: ConnectError: x"], "key_facts": None, "claims": None}}
    s = ge.summarise([failed])
    assert s["claims"] is None and s["unsupported_claims"] is None and s["faithful_answers"] is None
    assert s["judge_errors"] == 1
    assert "| unsupported claims | n/a |" in ge.format_report([("x", s)])


DAILY_ERR = RuntimeError("ClientError: 429 RESOURCE_EXHAUSTED GenerateRequestsPerDayPerProjectPerModel-FreeTier "
                         "Please retry in 23h30m35.5s.")


def test_daily_quota_stops_the_judge_batch_and_keeps_clean_earlier_results():
    records = [run_record("A"), run_record("B"), run_record("C")]
    prior = [{**records[2], "judge": clean_judgment("m")}]
    calls = []

    def quota(system, user, **kwargs):
        calls.append(1)
        raise DAILY_ERR

    judged = ge.judge_records(records, prior, quota, "m", progress=lambda line: None)
    assert len(calls) == 2  # A: key facts and faithfulness both tried, then the batch stopped
    assert judged[1]["judge"]["errors"] == ["not attempted: daily quota exhausted"]
    assert judged[2]["judge"] == clean_judgment("m")  # a clean earlier result is kept
    assert "resets in about 23h 30m" in ge.quota_note(judged)
    assert ge.quota_note([{"judge": {"errors": []}}]) is None


def test_run_questions_stops_when_the_daily_quota_is_used_up(tmp_path):
    def quota(question, hits, correction=None):
        raise DAILY_ERR

    records = ge.run_questions(ROWS, "answer_v1", lambda q: list(HITS), tmp_path / "t.jsonl", generate_fn=quota,
                               progress=lambda line: None)
    assert len(records) == 1 and "429" in records[0]["error"]


def test_paced_sleeps_between_calls_but_not_before_the_first():
    sleeps = []
    fn = ge.paced(lambda *a, **k: "r", 5, sleeps.append)
    assert [fn(), fn(), fn()] == ["r", "r", "r"] and sleeps == [5, 5]
    assert ge.paced(len, 0) is len


def test_judge_model_override_and_cli_flags():
    assert ge.judge_model_id("gemini-3.5-flash-lite") == "gemini-3.5-flash-lite"
    args = ge.build_parser().parse_args(["judge", "--input", "f.jsonl", "--pause", "5", "--judge-model", "m"])
    assert args.pause == 5.0 and args.judge_model == "m"
    assert ge.build_parser().parse_args(["run", "--version", "answer_v1"]).pause == 0
