"""
Step 2.3b: hybrid retrieval = vector search + BM25, combined with RRF.

fuse_hits is pure: it takes two lists of chunk hits and returns one fused list.
hybrid_search is a thin wrapper: it runs both searches on the same chunking variant with the
same filter, then calls fuse_hits.

Chunk-level fusion: RRF ranks chunks. Collapse to documents afterwards with
eval.retrieval_eval.to_doc_ranking, which only needs the "doc_id" key that every hit keeps.

Rank convention: vector_rank and bm25_rank are 1-based positions among the distinct chunks of
that retriever's list. A chunk that the retriever did not return has rank None (no invented
rank), and it adds nothing to its RRF score from that list.

Run from the repo root with PYTHONPATH=src, like the other modules.
"""
from rag import bm25, index
from rag.fusion import RRF_K, rrf

# Candidates fetched from each retriever. Keep equal to FETCH_DEPTH in eval/retrieval_eval.py
# (tests/test_hybrid.py checks this) so hybrid is compared with the baselines on the same depth.
HYBRID_FETCH_DEPTH = 50


def _first_hits(hits):
    """chunk_id -> hit, keeping the first occurrence; dict order is the retriever's rank order."""
    first = {}
    for hit in hits:
        first.setdefault(hit["chunk_id"], hit)
    return first


def fuse_hits(vector_hits, bm25_hits, rrf_k=RRF_K):
    """Fuse two ranked chunk-hit lists (best first) into one list of hit dicts, best first.

    Each returned hit is a new dict holding the fields of the original hit(s), so a chunk found by
    both retrievers keeps both "similarity" and "score", plus:
      rrf_score    sum of 1 / (rrf_k + rank) over the lists that returned the chunk
      vector_rank  1-based position in the vector list, or None if absent
      bm25_rank    1-based position in the BM25 list, or None if absent
    Order is rrf_score descending, ties broken by chunk_id ascending (see rag.fusion.rrf).
    The input hits are not modified."""
    vector = _first_hits(vector_hits)
    keyword = _first_hits(bm25_hits)
    vector_rank = {chunk_id: pos for pos, chunk_id in enumerate(vector, start=1)}
    bm25_rank = {chunk_id: pos for pos, chunk_id in enumerate(keyword, start=1)}
    fused = []
    for chunk_id, score in rrf([list(vector), list(keyword)], k=rrf_k):
        hit = {**keyword.get(chunk_id, {}), **vector.get(chunk_id, {})}
        hit["rrf_score"] = score
        hit["vector_rank"] = vector_rank.get(chunk_id)
        hit["bm25_rank"] = bm25_rank.get(chunk_id)
        fused.append(hit)
    return fused


def hybrid_search(client, variant, query, embed_fn, k=5, where=None,
                  fetch_depth=HYBRID_FETCH_DEPTH, rrf_k=RRF_K):
    """Top k fused chunks. Fetches fetch_depth candidates from vector search and from BM25 on the
    same variant, passes the same where filter to both (use a single-key equality filter such as
    {"certification": "Certified"}: Chroma needs "$and" for several keys), then fuses with RRF.

    For document-level evaluation pass k=FETCH_DEPTH (50, from eval/retrieval_eval.py), the same
    depth the baselines use. The default k=5 matches index.search and bm25_search and only suits
    interactive use: five chunks collapse to at most five documents, too few for MRR@10."""
    vector_hits = index.search(client, variant, query, embed_fn, k=fetch_depth, where=where)
    bm25_hits = bm25.bm25_search(variant, query, k=fetch_depth, where=where)
    return fuse_hits(vector_hits, bm25_hits, rrf_k=rrf_k)[:k]
