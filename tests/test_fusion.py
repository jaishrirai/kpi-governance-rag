"""Tests for rag.fusion.rrf (Step 2.3). Scores are compared approximately."""
import pytest

from eval.retrieval_eval import to_doc_ranking
from rag.fusion import rrf


def score_of(result, doc_id):
    return dict(result)[doc_id]


def test_example_1_document_in_both_lists():
    # A: vector 1, BM25 4. B: vector 3, BM25 1. C: vector 2 only.
    # Filler docs D, E, F fill the empty ranks so the ranks match the worked example.
    vector = ["A", "C", "B"]
    bm25 = ["B", "D", "E", "A"]
    result = rrf([vector, bm25])
    assert score_of(result, "A") == pytest.approx(1 / 61 + 1 / 64, abs=1e-6)
    assert score_of(result, "B") == pytest.approx(1 / 63 + 1 / 61, abs=1e-6)
    assert score_of(result, "C") == pytest.approx(1 / 62, abs=1e-6)
    assert score_of(result, "B") > score_of(result, "A")


def test_example_2_missing_documents_contribute_nothing():
    # X: vector 1 only. Y: vector 3, BM25 2. Z: BM25 1 only. V is a filler at vector rank 2.
    vector = ["X", "V", "Y"]
    bm25 = ["Z", "Y"]
    result = rrf([vector, bm25])
    assert score_of(result, "Y") == pytest.approx(1 / 63 + 1 / 62, abs=1e-6)
    assert score_of(result, "X") == pytest.approx(1 / 61, abs=1e-6)
    assert score_of(result, "Z") == pytest.approx(1 / 61, abs=1e-6)
    assert result[0][0] == "Y"


def test_example_3_first_in_both_lists_beats_first_in_one():
    # P: rank 1 in both lists. Q: rank 1 in one list, absent from the other.
    result = rrf([["P"], ["P"], ["Q"]])
    assert score_of(result, "P") == pytest.approx(2 / 61, abs=1e-6)
    assert score_of(result, "Q") == pytest.approx(1 / 61, abs=1e-6)
    assert [doc for doc, _ in result] == ["P", "Q"]


def test_absent_list_adds_nothing():
    # A appears only in the first list, so its score is exactly one contribution.
    result = rrf([["A", "B"], ["C"]])
    assert score_of(result, "A") == pytest.approx(1 / 61, abs=1e-6)
    assert score_of(result, "B") == pytest.approx(1 / 62, abs=1e-6)


def test_empty_input_gives_empty_result():
    assert rrf([]) == []


def test_empty_lists_give_empty_result():
    assert rrf([[], []]) == []


def test_single_ranking_keeps_order_and_scores():
    result = rrf([["A", "B", "C"]])
    assert [doc for doc, _ in result] == ["A", "B", "C"]
    assert result[0][1] == pytest.approx(1 / 61, abs=1e-6)
    assert result[1][1] == pytest.approx(1 / 62, abs=1e-6)
    assert result[2][1] == pytest.approx(1 / 63, abs=1e-6)


def test_ties_are_ordered_by_id_regardless_of_list_order():
    # A and B both get 1/61 from opposite lists; the order must not depend on input order.
    assert rrf([["B"], ["A"]]) == rrf([["A"], ["B"]])
    assert [doc for doc, _ in rrf([["B"], ["A"]])] == ["A", "B"]


def test_duplicate_inside_one_list_counts_once_at_first_occurrence():
    result = rrf([["A", "A", "B"]])
    assert score_of(result, "A") == pytest.approx(1 / 61, abs=1e-6)
    assert score_of(result, "B") == pytest.approx(1 / 62, abs=1e-6)


def test_non_positive_k_is_rejected():
    with pytest.raises(ValueError):
        rrf([["A"]], k=0)


def test_fused_chunk_ids_map_back_to_hits_for_document_collapse():
    # Chunk-level fusion, then document-level collapse through the existing hit dicts.
    vector_hits = [
        {"chunk_id": "A::v2::0", "doc_id": "A"},
        {"chunk_id": "A::v2::1", "doc_id": "A"},
        {"chunk_id": "B::v2::0", "doc_id": "B"},
    ]
    bm25_hits = [
        {"chunk_id": "B::v2::0", "doc_id": "B"},
        {"chunk_id": "A::v2::1", "doc_id": "A"},
    ]
    hit_by_chunk = {h["chunk_id"]: h for h in vector_hits + bm25_hits}
    fused = rrf([[h["chunk_id"] for h in vector_hits], [h["chunk_id"] for h in bm25_hits]])
    fused_hits = [hit_by_chunk[chunk_id] for chunk_id, _ in fused]
    # B::v2::0 (1/63 + 1/61) beats A::v2::1 (1/62 + 1/62), which beats A::v2::0 (1/61)
    assert [h["chunk_id"] for h in fused_hits] == ["B::v2::0", "A::v2::1", "A::v2::0"]
    assert to_doc_ranking(fused_hits) == ["B", "A"]
