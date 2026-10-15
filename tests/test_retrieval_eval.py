"""Tests for eval/retrieval_eval.py."""
from eval.retrieval_eval import FETCH_DEPTH, to_doc_ranking


def hits(*doc_ids):
    return [{"chunk_id": f"{d}::v2::{i}", "doc_id": d} for i, d in enumerate(doc_ids)]


def test_duplicates_collapse_to_first_occurrence():
    h = hits("KPI-007", "KPI-007", "KPI-011", "KPI-007", "CAT-02", "KPI-011", "KPI-010")
    assert to_doc_ranking(h) == ["KPI-007", "KPI-011", "CAT-02", "KPI-010"]


def test_order_follows_first_occurrence_not_alphabet_or_count():
    # KPI-001 has three chunks but its best chunk is rank 4, so it ranks after B and A
    assert to_doc_ranking(hits("B", "A", "B", "KPI-001", "KPI-001", "KPI-001")) == ["B", "A", "KPI-001"]


def test_empty_results_give_empty_ranking():
    assert to_doc_ranking([]) == []


def test_already_unique_results_are_unchanged():
    assert to_doc_ranking(hits("A", "B", "C")) == ["A", "B", "C"]


def test_input_is_not_modified_and_extra_fields_ignored():
    h = [{"doc_id": "A", "similarity": 0.9}, {"doc_id": "A", "similarity": 0.8}]
    before = [dict(x) for x in h]
    assert to_doc_ranking(h) == ["A"]
    assert h == before


def test_fetch_depth_is_separate_from_metric_cutoffs():
    assert FETCH_DEPTH == 50


# ---- metrics (2.2c) ----
import pytest  # noqa: E402

from eval.retrieval_eval import hit_at_k, recall_at_k, reciprocal_rank  # noqa: E402

TEN = [f"D{i}" for i in range(1, 11)]  # D1 .. D10


def test_mrr_example_ranks_1_3_missing_2():
    # first correct result at rank 1, 3, not in the top 10, and rank 2
    cases = [(["X", "A", "B"], ["X"]), (["B", "C", "X"], ["X"]), (TEN, ["X"]), (["B", "X", "C"], ["X"])]
    rr = [reciprocal_rank(r, e, 10) for r, e in cases]
    assert rr == [1.0, 1 / 3, 0.0, 0.5]
    assert sum(rr) / len(rr) == pytest.approx(0.4583, abs=1e-4)


def test_reciprocal_rank_uses_the_first_of_several_expected():
    assert reciprocal_rank(["B", "X2", "X1"], ["X1", "X2"], 10) == 0.5


def test_reciprocal_rank_cutoff_just_inside_and_outside():
    ranking = TEN[:9] + ["X"]  # X is at rank 10
    assert reciprocal_rank(ranking, ["X"], 10) == 0.1
    assert reciprocal_rank(ranking, ["X"], 9) == 0.0
    assert reciprocal_rank(TEN[:10] + ["X"], ["X"], 10) == 0.0  # rank 11


def test_recall_cutoff_just_inside_and_outside():
    ranking = TEN[:4] + ["X"] + TEN[4:]  # X at rank 5
    assert recall_at_k(ranking, ["X"], 5) == 1.0
    assert recall_at_k(ranking, ["X"], 4) == 0.0
    ranking6 = TEN[:5] + ["X"]  # X at rank 6
    assert recall_at_k(ranking6, ["X"], 5) == 0.0
    assert recall_at_k(ranking6, ["X"], 6) == 1.0


def test_fractional_recall_with_several_expected_documents():
    assert recall_at_k(["A", "B", "Z"], ["A", "B", "C", "D"], 5) == 0.5
    assert recall_at_k(["A", "B", "C", "D"], ["A", "B", "C", "D"], 5) == 1.0


def test_g008_style_ceiling_six_expected_five_slots():
    expected = [f"CAT-0{i}" for i in range(1, 7)]
    assert recall_at_k(expected, expected, 5) == pytest.approx(5 / 6)  # cannot reach 1.0
    assert recall_at_k(expected, expected, 10) == 1.0


def test_hit_at_k_is_binary_and_differs_from_fractional_recall():
    ranking = ["A", "Z"]
    assert hit_at_k(ranking, ["A", "B"], 5) == 1.0
    assert recall_at_k(ranking, ["A", "B"], 5) == 0.5
    assert hit_at_k(["Z"], ["A", "B"], 5) == 0.0


def test_empty_ranking_scores_zero():
    assert hit_at_k([], ["A"], 5) == 0.0
    assert recall_at_k([], ["A"], 5) == 0.0
    assert reciprocal_rank([], ["A"], 10) == 0.0


def test_no_matching_expected_documents_scores_zero():
    assert recall_at_k(TEN, ["X"], 10) == 0.0
    assert hit_at_k(TEN, ["X"], 10) == 0.0
    assert reciprocal_rank(TEN, ["X"], 10) == 0.0


def test_empty_expected_or_bad_k_is_an_error_not_a_zero():
    for fn in (hit_at_k, recall_at_k, reciprocal_rank):
        with pytest.raises(ValueError):
            fn(["A"], [], 5)
        with pytest.raises(ValueError):
            fn(["A"], ["A"], 0)


def test_metric_cutoff_is_independent_of_fetch_depth():
    # a ranking built from FETCH_DEPTH chunks is only cut by k inside the metric
    long_ranking = [f"D{i}" for i in range(FETCH_DEPTH)]
    assert recall_at_k(long_ranking, ["D7"], 5) == 0.0
    assert recall_at_k(long_ranking, ["D7"], 10) == 1.0


# ---- runner (2.2d) ----
import csv  # noqa: E402

from eval.retrieval_eval import RUN_COLUMNS, append_runs, evaluate, next_run_id  # noqa: E402


def golden_row(qid, expected, holdout=False):
    return {"id": qid, "question": qid, "answerable": bool(expected), "expected_doc_ids": expected,
            "holdout": holdout}


ROWS = [
    golden_row("Q1", ["A"]),                      # dev, hit at rank 1
    golden_row("Q2", ["B", "C"]),                 # dev, finds B at rank 3 only
    golden_row("Q3", ["Z"], holdout=True),        # holdout, miss
    golden_row("Q4", [], holdout=True),           # unanswerable, must be skipped
]
RESULTS = {
    "Q1": ["A", "A", "X"],
    "Q2": ["X", "Y", "B", "B"],
    "Q3": ["X", "Y"],
    "Q4": ["A"],
}


def fake_search(question):
    return [{"doc_id": d} for d in RESULTS[question]]


def test_evaluate_skips_unanswerable_and_splits_dev_and_holdout():
    per_q, summary = evaluate(ROWS, fake_search)
    assert [x["id"] for x in per_q] == ["Q1", "Q2", "Q3"]
    assert summary["dev"]["n"] == 2 and summary["holdout"]["n"] == 1


def test_evaluate_means_are_per_split():
    _, summary = evaluate(ROWS, fake_search)
    dev = summary["dev"]
    assert dev["recall_at_5"] == pytest.approx((1.0 + 0.5) / 2)
    assert dev["hit_at_5"] == pytest.approx(1.0)
    assert dev["mrr_at_10"] == pytest.approx((1.0 + 1 / 3) / 2)
    assert summary["holdout"]["recall_at_5"] == 0.0
    assert summary["holdout"]["mrr_at_10"] == 0.0


def test_append_runs_writes_header_once_and_increments_run_id(tmp_path):
    path = tmp_path / "runs.csv"
    _, summary = evaluate(ROWS, fake_search)
    meta = {"variant": "v1", "retriever": "vector", "rerank": "none", "fetch_depth": 50, "notes": "t"}
    assert append_runs(summary, meta, path) == 1
    assert append_runs(summary, meta, path) == 2
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    assert list(rows[0].keys()) == RUN_COLUMNS
    assert len(rows) == 4  # 2 runs x (dev, holdout)
    assert {r["split"] for r in rows} == {"dev", "holdout"}
    assert next_run_id(path) == 3


def test_real_golden_split_sizes():
    import json
    rows = [json.loads(l) for l in open("golden/golden_set.jsonl", encoding="utf-8") if l.strip()]
    answerable = [r for r in rows if r["answerable"]]
    assert sum(1 for r in answerable if r["holdout"]) == 8
    assert sum(1 for r in answerable if not r["holdout"]) == 24


# ---- run-log sha (fix) ----
import subprocess  # noqa: E402

import eval.retrieval_eval as ev  # noqa: E402


def _git(cwd, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True, capture_output=True)


def test_git_sha_ignores_run_log_changes_but_not_code_changes(tmp_path):
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "runs.csv").write_text("a\n")
    (tmp_path / "code.py").write_text("x = 1\n")
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    clean = ev.git_sha(cwd=tmp_path)
    assert clean != "unknown" and "+dirty" not in clean
    (tmp_path / "results" / "runs.csv").write_text("a\nb\n")  # tracked run log changed
    assert ev.git_sha(cwd=tmp_path) == clean
    (tmp_path / "code.py").write_text("x = 2\n")              # tracked code changed
    assert ev.git_sha(cwd=tmp_path) == clean + "+dirty"


def test_dev_and_holdout_rows_share_one_sha_per_run(tmp_path, monkeypatch):
    calls = iter(["aaa111", "bbb222", "ccc333"])
    monkeypatch.setattr(ev, "git_sha", lambda: next(calls))
    _, summary = evaluate(ROWS, fake_search)
    meta = {"variant": "v1", "retriever": "vector", "rerank": "none", "fetch_depth": 50, "notes": ""}
    path = tmp_path / "runs.csv"
    ev.append_runs(summary, meta, path)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    assert [r["split"] for r in rows] == ["dev", "holdout"]
    assert {r["git_sha"] for r in rows} == {"aaa111"}


import sys  # noqa: E402
import types  # noqa: E402


@pytest.fixture
def stub_models(monkeypatch):
    """Replace chromadb and the embedding model so make_search runs without heavy libraries."""
    from rag import index
    client, embed = object(), object()
    fake_chromadb = types.ModuleType("chromadb")
    fake_chromadb.PersistentClient = lambda path: client
    monkeypatch.setitem(sys.modules, "chromadb", fake_chromadb)
    monkeypatch.setattr(index, "load_model", lambda: "model")
    monkeypatch.setattr(index, "make_embedder", lambda model: embed)
    return client, embed


def test_make_search_hybrid_asks_for_fetch_depth_fused_chunks(monkeypatch, stub_models):
    import rag.hybrid as hybrid
    client, embed = stub_models
    seen = {}

    def fake_hybrid(c, variant, query, e, k=5, where=None, fetch_depth=None, rrf_k=None):
        seen.update(client=c, variant=variant, query=query, embed=e, k=k, fetch_depth=fetch_depth)
        return ["fused"]

    monkeypatch.setattr(hybrid, "hybrid_search", fake_hybrid)
    assert ev.make_search("v2", "hybrid")("churn rate") == ["fused"]
    assert seen == {"client": client, "variant": "v2", "query": "churn rate", "embed": embed,
                    "k": FETCH_DEPTH, "fetch_depth": FETCH_DEPTH}


def test_make_search_vector_is_unchanged_and_never_calls_hybrid(monkeypatch, stub_models):
    import rag.hybrid as hybrid
    from rag import index
    seen = {}

    def fake_vector(c, variant, query, e, k=5, where=None):
        seen.update(variant=variant, k=k)
        return ["vec"]

    def fail(*args, **kwargs):
        raise AssertionError("hybrid_search must not run for the vector retriever")

    monkeypatch.setattr(index, "search", fake_vector)
    monkeypatch.setattr(hybrid, "hybrid_search", fail)
    assert ev.make_search("v1", "vector")("q") == ["vec"]
    assert seen == {"variant": "v1", "k": FETCH_DEPTH}


def test_make_search_bm25_is_unchanged(monkeypatch):
    import rag.bm25 as bm25
    seen = {}

    def fake_bm25(variant, query, k=5, where=None, stem=False):
        seen.update(variant=variant, k=k)
        return ["kw"]

    monkeypatch.setattr(bm25, "bm25_search", fake_bm25)
    assert ev.make_search("v3", "bm25")("q") == ["kw"]
    assert seen == {"variant": "v3", "k": FETCH_DEPTH}


def test_cli_accepts_hybrid_and_passes_it_to_make_search(monkeypatch, capsys):
    seen = {}

    def fake_make_search(variant, retriever):
        seen["args"] = (variant, retriever)
        return lambda question: []

    monkeypatch.setattr(ev, "make_search", fake_make_search)
    monkeypatch.setattr(sys, "argv", ["retrieval_eval", "--variant", "v2", "--retriever", "hybrid", "--no-log"])
    ev.main()
    assert seen["args"] == ("v2", "hybrid")
    assert "retriever=hybrid" in capsys.readouterr().out


def test_cli_rejects_unknown_retriever(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["retrieval_eval", "--retriever", "rerank", "--no-log"])
    with pytest.raises(SystemExit):
        ev.main()


def test_make_reranked_search_reorders_the_candidates_of_any_search(monkeypatch):
    import rag.rerank as rr
    monkeypatch.setattr(rr, "load_reranker", lambda: (lambda query, texts: [len(t) for t in texts]))
    asked = []

    def base(question):
        asked.append(question)
        return [{"chunk_id": "A::0", "doc_id": "A", "text": "x"}, {"chunk_id": "B::0", "doc_id": "B", "text": "xxx"}]

    search = ev.make_reranked_search(base)
    assert [h["chunk_id"] for h in search("q")] == ["B::0", "A::0"]
    assert asked == ["q"]  # candidates come from the base search; reranking does not search again


def test_cli_rerank_flag_wraps_the_search_and_logs_the_model(monkeypatch):
    import rag.rerank as rr
    seen = {}

    def fake_wrap(search_fn):
        seen["wrapped"] = True
        return search_fn

    def fake_append(summary, meta):
        seen["meta"] = meta
        return 99

    monkeypatch.setattr(ev, "make_search", lambda variant, retriever: (lambda q: []))
    monkeypatch.setattr(ev, "make_reranked_search", fake_wrap)
    monkeypatch.setattr(ev, "append_runs", fake_append)
    monkeypatch.setattr(sys, "argv", ["retrieval_eval", "--variant", "v1", "--retriever", "vector",
                                      "--rerank", "cross-encoder", "--notes", "t"])
    ev.main()
    assert seen["wrapped"] is True
    assert seen["meta"]["rerank"] == rr.RERANK_MODEL
    assert seen["meta"]["retriever"] == "vector" and seen["meta"]["fetch_depth"] == FETCH_DEPTH


def test_cli_without_rerank_flag_is_unchanged(monkeypatch):
    seen = {}

    def fail(search_fn):
        raise AssertionError("reranking must be off by default")

    def fake_append(summary, meta):
        seen["meta"] = meta
        return 99

    monkeypatch.setattr(ev, "make_search", lambda variant, retriever: (lambda q: []))
    monkeypatch.setattr(ev, "make_reranked_search", fail)
    monkeypatch.setattr(ev, "append_runs", fake_append)
    monkeypatch.setattr(sys, "argv", ["retrieval_eval", "--variant", "v1", "--retriever", "vector"])
    ev.main()
    assert seen["meta"]["rerank"] == "none"


def test_cli_rejects_unknown_rerank_choice(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["retrieval_eval", "--rerank", "bge", "--no-log"])
    with pytest.raises(SystemExit):
        ev.main()
