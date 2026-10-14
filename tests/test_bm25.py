"""Tests for src/rag/bm25.py."""
from pathlib import Path

import pytest

from rag import bm25

pytest.importorskip("rank_bm25")


def fake_chunk(doc_id, text, **meta):
    metadata = {"title": "T", "section": "S", "certification": "Certified"}
    metadata.update(meta)
    return {"chunk_id": f"{doc_id}::v2::0", "doc_id": doc_id, "text": text, "metadata": metadata}


def test_tokenizer_keeps_ids_whole_and_lowercases():
    assert bm25.tokenize("KPI-014, KPI-015 (v2)") == ["kpi-014", "kpi-015", "v2"]
    assert bm25.tokenize("kpi-007-v1 Customer 360") == ["kpi-007-v1", "customer", "360"]


def test_stemmer_joins_word_forms_but_leaves_ids_and_short_words():
    assert bm25.stem_word("owns") == bm25.stem_word("owner") == bm25.stem_word("owned") == "own"
    assert bm25.stem_word("kpi-014") == "kpi-014"
    assert bm25.stem_word("360") == "360"
    assert bm25.stem_word("process") == "process"  # double s: not a plural
    assert bm25.stem_word("kpi") == "kpi"


def test_exact_id_ranks_first():
    chunks = [
        fake_chunk("KPI-014", "Customer Acquisition Cost KPI-014 formula"),
        fake_chunk("KPI-015", "Marketing ROI KPI-015 formula"),
        fake_chunk("KPI-007", "Customer Churn Rate KPI-007 formula"),
        fake_chunk("SOP-02", "Requesting a new KPI follows these steps"),
    ]
    hits = bm25.Bm25Index(chunks).search("KPI-014")
    assert hits[0]["doc_id"] == "KPI-014"
    assert len(hits) == 1  # only chunks containing the query word are returned


def test_query_with_no_matching_word_returns_nothing():
    chunks = [fake_chunk("A", "customer churn"), fake_chunk("B", "inventory turnover")]
    assert bm25.Bm25Index(chunks).search("zebra") == []


def test_filter_keeps_only_matching_metadata():
    chunks = [
        fake_chunk("KPI-007-V1", "churn rate old", certification="Deprecated"),
        fake_chunk("KPI-007", "churn rate current", certification="Certified"),
        fake_chunk("OTHER", "inventory turnover"),
    ]
    hits = bm25.Bm25Index(chunks).search("churn", where={"certification": "Certified"})
    assert [h["doc_id"] for h in hits] == ["KPI-007"]


def test_stemming_lets_owns_find_owner():
    chunks = [
        fake_chunk("CAT-02", "Customer 360 Dashboard owner Head of Customer Analytics"),
        fake_chunk("B", "inventory turnover"),
        fake_chunk("C", "returns and refunds policy"),
        fake_chunk("D", "marketing spend by campaign"),
    ]  # 4 chunks: with only 2, a word found in 1 of 2 chunks gets a rarity score of 0
    assert bm25.Bm25Index(chunks, stem=False).search("owns") == []
    assert [h["doc_id"] for h in bm25.Bm25Index(chunks, stem=True).search("owns")] == ["CAT-02"]


CHUNKS_BUILT = Path("data/processed/chunks_v2.jsonl").exists()


@pytest.mark.skipif(not CHUNKS_BUILT, reason="chunks not built")
@pytest.mark.parametrize("variant", ["v1", "v3"])
def test_real_corpus_finds_the_kpi_014_document_by_its_code(variant):
    # Short catalog rows that list KPI-014 outrank the long KPI file (BM25 favours short chunks),
    # so we check the top 5, not the top 1.
    hits = bm25.bm25_search(variant, "KPI-014", k=5)
    assert "KPI-014" in [h["doc_id"] for h in hits]


@pytest.mark.skipif(not CHUNKS_BUILT, reason="chunks not built")
@pytest.mark.xfail(strict=True, reason="V2 chunk text never contains the code KPI-014 (title line dropped, header has no id)")
def test_known_gap_v2_cannot_find_its_own_kpi_by_code():
    hits = bm25.bm25_search("v2", "KPI-014", k=10)
    assert "KPI-014" in [h["doc_id"] for h in hits]
