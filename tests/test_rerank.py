"""Tests for rag.rerank.rerank. A fake score function stands in for the cross-encoder."""
import pytest

from eval.retrieval_eval import to_doc_ranking
from rag.rerank import rerank


def hit(chunk_id, text):
    return {"chunk_id": chunk_id, "doc_id": chunk_id.split("::")[0], "section": "s",
            "certification": "Certified", "similarity": 0.5, "text": text}


def scorer(table):
    return lambda query, texts: [table[t] for t in texts]


HITS = [hit("A::0", "a"), hit("B::0", "b"), hit("C::0", "c")]


def test_orders_by_score_descending_and_records_both_ranks():
    out = rerank("q", HITS, scorer({"a": 0.1, "b": 0.9, "c": 0.5}))
    assert [h["chunk_id"] for h in out] == ["B::0", "C::0", "A::0"]
    assert [(h["retrieval_rank"], h["rerank_rank"]) for h in out] == [(2, 1), (3, 2), (1, 3)]
    assert out[0]["rerank_score"] == 0.9


def test_original_fields_are_kept_and_inputs_are_not_modified():
    out = rerank("q", HITS, scorer({"a": 0.1, "b": 0.9, "c": 0.5}))
    top = out[0]
    assert (top["doc_id"], top["section"], top["certification"], top["similarity"]) == ("B", "s", "Certified", 0.5)
    assert top["text"] == "b"
    assert all("rerank_score" not in h for h in HITS)


def test_ties_keep_retrieval_order():
    out = rerank("q", HITS, scorer({"a": 0.5, "b": 0.5, "c": 0.5}))
    assert [h["chunk_id"] for h in out] == ["A::0", "B::0", "C::0"]
    partial = rerank("q", HITS, scorer({"a": 0.2, "b": 0.7, "c": 0.7}))
    assert [h["chunk_id"] for h in partial] == ["B::0", "C::0", "A::0"]


def test_empty_hits_return_empty_without_scoring():
    def fail(query, texts):
        raise AssertionError("score_fn must not be called for no candidates")
    assert rerank("q", [], fail) == []


def test_single_hit():
    out = rerank("q", [hit("A::0", "a")], scorer({"a": 0.3}))
    assert [(h["retrieval_rank"], h["rerank_rank"]) for h in out] == [(1, 1)]


def test_score_fn_gets_the_query_and_chunk_texts_in_retrieval_order():
    seen = {}

    def spy(query, texts):
        seen.update(query=query, texts=list(texts))
        return [0.0] * len(texts)

    rerank("what is churn", HITS, spy)
    assert seen == {"query": "what is churn", "texts": ["a", "b", "c"]}


def test_reordering_never_adds_or_drops_candidates():
    out = rerank("q", HITS, scorer({"a": 0.1, "b": 0.9, "c": 0.5}))
    assert sorted(h["chunk_id"] for h in out) == sorted(h["chunk_id"] for h in HITS)


@pytest.mark.parametrize("top_k, expected_len", [(None, 3), (2, 2), (10, 3), (0, 0)])
def test_top_k_cuts_the_reranked_list(top_k, expected_len):
    out = rerank("q", HITS, scorer({"a": 0.1, "b": 0.9, "c": 0.5}), top_k=top_k)
    assert len(out) == expected_len
    if top_k == 2:
        assert [h["chunk_id"] for h in out] == ["B::0", "C::0"]


def test_reranked_hits_work_with_to_doc_ranking():
    hits = [hit("A::0", "a0"), hit("B::0", "b0"), hit("A::1", "a1")]
    out = rerank("q", hits, scorer({"a0": 0.1, "b0": 0.9, "a1": 0.5}))
    assert [h["chunk_id"] for h in out] == ["B::0", "A::1", "A::0"]
    assert to_doc_ranking(out) == ["B", "A"]  # document sits at the position of its best chunk
