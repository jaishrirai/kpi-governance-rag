"""Tests for rag.hybrid, using fake hits and fake searchers (no model, no index)."""
import pytest

from eval.retrieval_eval import FETCH_DEPTH, MRR_K, to_doc_ranking
from rag import bm25, hybrid, index
from rag.hybrid import HYBRID_FETCH_DEPTH, fuse_hits, hybrid_search


def vhit(chunk_id):
    return {"chunk_id": chunk_id, "doc_id": chunk_id.split("::")[0], "similarity": 0.5, "text": "t"}


def bhit(chunk_id):
    return {"chunk_id": chunk_id, "doc_id": chunk_id.split("::")[0], "score": 3.0, "text": "t"}


def by_id(hits):
    return {h["chunk_id"]: h for h in hits}


def test_overlap_scores_ranks_and_order():
    vector = [vhit("A::0"), vhit("A::1"), vhit("B::0")]
    keyword = [bhit("B::0"), bhit("A::1")]
    fused = fuse_hits(vector, keyword)
    # B::0 = 1/63 + 1/61, A::1 = 1/62 + 1/62, A::0 = 1/61
    assert [h["chunk_id"] for h in fused] == ["B::0", "A::1", "A::0"]
    found = by_id(fused)
    assert found["B::0"]["rrf_score"] == pytest.approx(1 / 63 + 1 / 61, abs=1e-6)
    assert found["A::1"]["rrf_score"] == pytest.approx(2 / 62, abs=1e-6)
    assert (found["B::0"]["vector_rank"], found["B::0"]["bm25_rank"]) == (3, 1)
    assert (found["A::1"]["vector_rank"], found["A::1"]["bm25_rank"]) == (2, 2)


def test_chunk_missing_from_one_list_has_rank_none_and_one_contribution():
    fused = by_id(fuse_hits([vhit("A::0")], [bhit("D::0")]))
    assert fused["A::0"]["bm25_rank"] is None
    assert fused["A::0"]["vector_rank"] == 1
    assert fused["A::0"]["rrf_score"] == pytest.approx(1 / 61, abs=1e-6)
    assert fused["D::0"]["vector_rank"] is None
    assert fused["D::0"]["bm25_rank"] == 1


def test_original_fields_are_preserved_and_inputs_not_modified():
    vector = [vhit("B::0")]
    keyword = [bhit("B::0")]
    fused = fuse_hits(vector, keyword)[0]
    assert fused["similarity"] == 0.5 and fused["score"] == 3.0  # both retrievers' fields kept
    assert fused["doc_id"] == "B" and fused["text"] == "t"
    assert "rrf_score" not in vector[0] and "rrf_score" not in keyword[0]


def test_duplicate_chunks_in_one_list_count_once_and_do_not_shift_ranks():
    fused = fuse_hits([vhit("A::0"), vhit("A::0"), vhit("B::0")], [])
    assert [h["chunk_id"] for h in fused] == ["A::0", "B::0"]
    assert [h["vector_rank"] for h in fused] == [1, 2]


def test_ties_are_ordered_by_chunk_id_regardless_of_list_order():
    forward = fuse_hits([vhit("B::0")], [bhit("A::0")])
    swapped = fuse_hits([vhit("A::0")], [bhit("B::0")])
    assert [h["chunk_id"] for h in forward] == ["A::0", "B::0"]
    assert [h["chunk_id"] for h in swapped] == ["A::0", "B::0"]


def test_empty_inputs():
    assert fuse_hits([], []) == []
    only_bm25 = fuse_hits([], [bhit("A::0")])
    assert only_bm25[0]["vector_rank"] is None and only_bm25[0]["bm25_rank"] == 1


def test_fused_hits_work_with_to_doc_ranking():
    fused = fuse_hits([vhit("A::0"), vhit("A::1"), vhit("B::0")], [bhit("B::0"), bhit("A::1")])
    assert to_doc_ranking(fused) == ["B", "A"]


def test_hybrid_fetch_depth_matches_eval_fetch_depth():
    assert HYBRID_FETCH_DEPTH == FETCH_DEPTH


@pytest.fixture
def fake_searchers(monkeypatch):
    calls = {}

    def fake_vector(client, variant, query, embed_fn, k=5, where=None):
        calls["vector"] = {"variant": variant, "query": query, "k": k, "where": where}
        return [vhit("A::0"), vhit("A::1"), vhit("B::0")]

    def fake_bm25(variant, query, k=5, where=None, stem=False):
        calls["bm25"] = {"variant": variant, "query": query, "k": k, "where": where}
        return [bhit("B::0"), bhit("A::1")]

    monkeypatch.setattr(index, "search", fake_vector)
    monkeypatch.setattr(bm25, "bm25_search", fake_bm25)
    return calls


def test_hybrid_search_uses_same_variant_query_depth_and_filter_for_both(fake_searchers):
    where = {"certification": "Certified"}
    hybrid_search(None, "v2", "churn rate", None, k=3, where=where, fetch_depth=20)
    assert fake_searchers["vector"] == {"variant": "v2", "query": "churn rate", "k": 20, "where": where}
    assert fake_searchers["bm25"] == {"variant": "v2", "query": "churn rate", "k": 20, "where": where}


def test_hybrid_search_defaults_to_fetch_depth_and_no_filter(fake_searchers):
    hybrid_search(None, "v1", "q", None)
    assert fake_searchers["vector"]["k"] == HYBRID_FETCH_DEPTH
    assert fake_searchers["bm25"]["k"] == HYBRID_FETCH_DEPTH
    assert fake_searchers["vector"]["where"] is None and fake_searchers["bm25"]["where"] is None


def test_hybrid_search_returns_top_k_fused_hits(fake_searchers):
    hits = hybrid_search(None, "v2", "q", None, k=2)
    assert [h["chunk_id"] for h in hits] == ["B::0", "A::1"]
    assert to_doc_ranking(hits) == ["B", "A"]


@pytest.fixture
def deep_searchers(monkeypatch):
    """Fake searchers with 60 chunks each (two per document), honouring k like the real ones."""
    calls = {}
    vector_pool = [vhit(f"D{d:02d}::{c}") for d in range(0, 30) for c in range(2)]
    bm25_pool = [bhit(f"D{d:02d}::{c}") for d in range(15, 45) for c in range(2)]

    def fake_vector(client, variant, query, embed_fn, k=5, where=None):
        calls["vector_k"] = k
        return vector_pool[:k]

    def fake_bm25(variant, query, k=5, where=None, stem=False):
        calls["bm25_k"] = k
        return bm25_pool[:k]

    monkeypatch.setattr(index, "search", fake_vector)
    monkeypatch.setattr(bm25, "bm25_search", fake_bm25)
    return calls


def test_evaluation_depth_gives_fetch_depth_fused_chunks_and_enough_documents(deep_searchers):
    hits = hybrid_search(None, "v2", "q", None, k=FETCH_DEPTH)
    assert len(hits) == FETCH_DEPTH
    assert deep_searchers == {"vector_k": FETCH_DEPTH, "bm25_k": FETCH_DEPTH}
    # the document-level protocol needs at least MRR_K distinct documents in the fetched chunks
    assert len(to_doc_ranking(hits)) >= MRR_K


def test_default_depth_is_too_shallow_for_document_level_evaluation(deep_searchers):
    hits = hybrid_search(None, "v2", "q", None)
    assert len(hits) == 5
    assert len(to_doc_ranking(hits)) < MRR_K
