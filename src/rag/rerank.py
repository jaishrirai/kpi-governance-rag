"""
Step 2.4: cross-encoder reranking.

Retrieval (vector, BM25 or hybrid) scores the query and each chunk separately: fast but rough.
A cross-encoder reads the query and one chunk TOGETHER and scores how well that chunk answers the
question: slower and usually more precise. So it only reorders a candidate list that retrieval has
already produced. It cannot find a chunk retrieval missed, so the candidate depth is its ceiling.

rerank() is pure once it is given a score function, so it is tested without any model.
load_reranker() builds the real score function (needs the model download, run in the Windows .venv).
No governance filter is applied here; that is a separate decision for the grounding step.
"""

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def load_reranker(model_name=RERANK_MODEL):
    """Return score_fn(query, texts) -> list of floats, higher = more relevant to the query."""
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(model_name, max_length=512)

    def score_fn(query, texts):
        return [float(s) for s in model.predict([(query, text) for text in texts])]

    return score_fn


def rerank(query, hits, score_fn, top_k=None):
    """Reorder chunk hits by cross-encoder score, best first.

    hits: chunk hit dicts from any retriever, each with a "text" key. Each returned hit is a new
    dict with every original field (chunk_id, doc_id, section, ...) plus:
      rerank_score    the score_fn value; only meaningful for ordering
      retrieval_rank  1-based position before reranking
      rerank_rank     1-based position after reranking
    Ties keep their retrieval order. Nothing is added or dropped unless top_k cuts the list."""
    if not hits:
        return []
    scores = score_fn(query, [hit["text"] for hit in hits])
    order = sorted(range(len(hits)), key=lambda i: (-scores[i], i))
    reranked = []
    for new_rank, i in enumerate(order, start=1):
        hit = dict(hits[i])
        hit.update(rerank_score=scores[i], retrieval_rank=i + 1, rerank_rank=new_rank)
        reranked.append(hit)
    return reranked if top_k is None else reranked[:top_k]
