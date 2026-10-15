"""
Step 2.3: Reciprocal Rank Fusion (RRF).

RRF combines ranked lists by position, not by raw score:
    RRF(d) = sum over lists r of 1 / (k + rank_r(d))

Rules:
  - ranks are 1-based positions in each list, best first
  - a document missing from a list contributes nothing to that list
  - a document repeated inside one list counts only at its first occurrence
  - output is sorted by score (highest first), with ties broken by ID ascending,
    so the same input always gives the same order

Input IDs must be chunk IDs taken from the same index variant, so one chunk has
the same ID in the vector and BM25 lists. Collapse to document IDs afterwards
with eval.retrieval_eval.to_doc_ranking, which needs the chunk hit dicts.
"""
from collections import defaultdict

RRF_K = 60


def rrf(ranked_lists, k=RRF_K):
    """Return [(id, score), ...] sorted by score descending, then id ascending."""
    if k < 1:
        raise ValueError("k must be at least 1")
    scores = defaultdict(float)
    for ranking in ranked_lists:
        seen = set()
        rank = 0
        for item in ranking:
            if item in seen:
                continue
            seen.add(item)
            rank += 1
            scores[item] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
