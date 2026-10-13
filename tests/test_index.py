"""Tests for src/rag/index.py. Use a fake embedder, so no model download is needed."""
import pytest

from rag import index

chromadb = pytest.importorskip("chromadb")


def fake_chunk(n, text, **meta):
    metadata = {"title": "T", "section": "S", "certification": "Certified", "variant": "v2"}
    metadata.update(meta)
    return {"chunk_id": f"DOC-{n}::v2::0", "doc_id": f"DOC-{n}", "text": text, "metadata": metadata}


def word_embedder(texts):
    """Tiny deterministic embedder: 3 dimensions, one per topic word. Vectors have length 1."""
    topics = ["churn", "revenue", "inventory"]
    vectors = []
    for text in texts:
        raw = [float(text.lower().count(t)) for t in topics]
        norm = sum(x * x for x in raw) ** 0.5 or 1.0
        vectors.append([x / norm for x in raw])
    return vectors


def test_clean_metadata_drops_none_and_stringifies_other_types():
    chunk = fake_chunk(1, "x", owner=None, tags=["a", "b"], version=2)
    clean = index.clean_metadata(chunk)
    assert "owner" not in clean
    assert clean["tags"] == "['a', 'b']"
    assert clean["version"] == 2
    assert clean["doc_id"] == "DOC-1"


def test_count_over_limit_reports_positions_of_long_texts():
    texts = ["short", "x" * 600, "also short"]
    assert index.count_over_limit(texts, lambda t: len(t), limit=512) == [1]


def test_build_stores_one_vector_per_chunk_and_rebuild_does_not_duplicate(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path))
    chunks = [fake_chunk(i, f"churn text {i}") for i in range(70)]  # 70 > two batches of 32
    index.build_collection(client, "v2", chunks, word_embedder)
    col = index.build_collection(client, "v2", chunks, word_embedder)  # second run
    assert col.count() == 70


def test_search_uses_cosine_similarity_and_returns_best_match_first(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path))
    chunks = [fake_chunk(1, "churn churn"), fake_chunk(2, "revenue revenue")]
    index.build_collection(client, "v2", chunks, word_embedder)
    hits = index.search(client, "v2", "churn", word_embedder, k=2)
    assert hits[0]["doc_id"] == "DOC-1"
    assert hits[0]["similarity"] == pytest.approx(1.0, abs=1e-4)
    # orthogonal vectors: cosine similarity 0 (with L2 distance this would not be 0)
    assert hits[1]["similarity"] == pytest.approx(0.0, abs=1e-4)


def test_search_filter_keeps_only_matching_metadata(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path))
    chunks = [
        fake_chunk(1, "churn old", certification="Deprecated"),
        fake_chunk(2, "churn new", certification="Certified"),
    ]
    index.build_collection(client, "v2", chunks, word_embedder)
    hits = index.search(client, "v2", "churn", word_embedder, k=5, where={"certification": "Certified"})
    assert [h["doc_id"] for h in hits] == ["DOC-2"]
