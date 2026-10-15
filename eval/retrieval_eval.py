"""
Retrieval evaluation (Step 2.2), document level, answerable questions only.

Metric definitions (per question, then averaged over the questions in a split):
  recall@5  expected documents found in the top 5 / number of expected documents   (headline)
  hit@5     1 if any expected document is in the top 5, else 0
  MRR@10    1 / rank of the first expected document in the top 10, else 0
Unanswerable questions have no expected documents and are scored as refusals in Step 3.1, never here.

Pieces: to_doc_ranking (chunks -> distinct documents), hit_at_k / recall_at_k / reciprocal_rank,
evaluate (one retriever over the golden set), run_and_log (CLI, appends to results/runs.csv).
Run from the repo root:
  $env:PYTHONPATH = "src"
  python -m eval.retrieval_eval --variant v1 --retriever vector --notes "baseline"
  python -m eval.retrieval_eval --variant v1 --retriever hybrid --notes "hybrid RRF k=60"
  python -m eval.retrieval_eval --variant v1 --retriever vector --rerank cross-encoder --notes "rerank 50"
Retrievers: vector, bm25, hybrid (RRF over the vector and BM25 chunk lists, see rag.hybrid).
"""
import argparse
import csv
import json
import subprocess
import time
from datetime import date
from pathlib import Path

GOLDEN = Path("golden/golden_set.jsonl")
RUNS = Path("results/runs.csv")
RUN_COLUMNS = ["run_id", "date", "git_sha", "variant", "retriever", "rerank", "fetch_depth", "split", "n",
               "recall_at_5", "hit_at_5", "mrr_at_10", "avg_latency_ms", "notes"]
RECALL_K, MRR_K = 5, 10

# How many chunks to fetch from a retriever before collapsing to documents. This is NOT the metric
# cutoff: recall@5 and MRR@10 take their own k later. It only has to be large enough that 10 distinct
# documents survive deduplication, even for V2 where one document has many chunks.
FETCH_DEPTH = 50


def _check(expected, k):
    if k < 1:
        raise ValueError("k must be at least 1")
    if not expected:
        # unanswerable questions have no expected documents; they are scored as refusals (3.1),
        # never in retrieval metrics, so an empty set is a bug in the caller, not a score of 0
        raise ValueError("expected must not be empty")


def hit_at_k(ranked_docs, expected, k):
    """Binary per-question success: 1.0 if ANY expected document is in the top k, else 0.0.
    This is the definition the project brief calls "recall@5"."""
    _check(expected, k)
    return 1.0 if set(ranked_docs[:k]) & set(expected) else 0.0


def recall_at_k(ranked_docs, expected, k):
    """Fractional recall: share of the expected documents found in the top k.
    1 expected doc: same as hit_at_k. 6 expected docs with 5 slots: at most 5/6.
    ranked_docs must already be deduplicated (see to_doc_ranking)."""
    _check(expected, k)
    expected = set(expected)
    return len(set(ranked_docs[:k]) & expected) / len(expected)


def reciprocal_rank(ranked_docs, expected, k):
    """1 / rank of the first expected document within the top k, or 0.0 if none is there.
    The mean of this over questions is MRR@k."""
    _check(expected, k)
    expected = set(expected)
    for rank, doc_id in enumerate(ranked_docs[:k], start=1):
        if doc_id in expected:
            return 1.0 / rank
    return 0.0


def to_doc_ranking(hits):
    """Collapse ranked chunk hits into a ranked list of distinct document ids.

    hits: chunk results, best first, each a dict with a "doc_id" key (the output of
    rag.index.search or Bm25Index.search). A document sits at the position of its best chunk, so the
    first occurrence of a doc_id is kept and later chunks of the same document are dropped.
    Returns a list of doc_id strings, best first. Does not cut the list: the metric applies k.
    """
    ranking = []
    seen = set()
    for hit in hits:
        doc_id = hit["doc_id"]
        if doc_id not in seen:
            seen.add(doc_id)
            ranking.append(doc_id)
    return ranking


def evaluate(rows, search_fn):
    """Run search_fn(question) -> chunk hits over the answerable golden rows.
    Returns (per_question, summary). per_question: list of dicts. summary: {"dev": {...}, "holdout": {...}}
    with n, recall_at_5, hit_at_5, mrr_at_10, avg_latency_ms. Unanswerable rows are skipped."""
    per_question = []
    for r in rows:
        if not r["answerable"]:
            continue
        start = time.perf_counter()
        hits = search_fn(r["question"])
        latency_ms = (time.perf_counter() - start) * 1000
        ranking = to_doc_ranking(hits)
        expected = r["expected_doc_ids"]
        per_question.append({
            "id": r["id"], "split": "holdout" if r["holdout"] else "dev", "expected": expected,
            "top5": ranking[:RECALL_K],
            "recall_at_5": recall_at_k(ranking, expected, RECALL_K),
            "hit_at_5": hit_at_k(ranking, expected, RECALL_K),
            "rr_at_10": reciprocal_rank(ranking, expected, MRR_K),
            "latency_ms": latency_ms,
        })
    summary = {}
    for split in ("dev", "holdout"):
        q = [x for x in per_question if x["split"] == split]
        if not q:
            continue
        mean = lambda key: sum(x[key] for x in q) / len(q)  # noqa: E731
        summary[split] = {"n": len(q), "recall_at_5": mean("recall_at_5"), "hit_at_5": mean("hit_at_5"),
                          "mrr_at_10": mean("rr_at_10"), "avg_latency_ms": mean("latency_ms")}
    return per_question, summary


def git_sha(cwd=None):
    """Short HEAD sha, plus "+dirty" if tracked files other than the run log itself have changes.
    results/runs.csv is excluded: appending a run must not mark the code as dirty."""
    try:
        run = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, check=True, cwd=cwd).stdout.strip()  # noqa: E731
        sha = run("rev-parse", "--short", "HEAD")
        dirty = run("status", "--porcelain", "--untracked-files=no", "--", ".", f":(exclude){RUNS.as_posix()}")
        return sha + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def next_run_id(path=RUNS):
    if not Path(path).exists():
        return 1
    with open(path, newline="", encoding="utf-8") as f:
        ids = [int(r["run_id"]) for r in csv.DictReader(f) if r.get("run_id", "").isdigit()]
    return max(ids, default=0) + 1


def append_runs(summary, meta, path=RUNS):
    """Append one row per split. meta: variant, retriever, rerank, fetch_depth, notes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    run_id = next_run_id(path)
    sha = git_sha()  # once per experiment, so the dev and holdout rows always carry the same sha
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RUN_COLUMNS)
        if new_file:
            w.writeheader()
        for split, m in summary.items():
            w.writerow({"run_id": run_id, "date": date.today().isoformat(), "git_sha": sha,
                        "split": split, "n": m["n"], "recall_at_5": round(m["recall_at_5"], 4),
                        "hit_at_5": round(m["hit_at_5"], 4), "mrr_at_10": round(m["mrr_at_10"], 4),
                        "avg_latency_ms": round(m["avg_latency_ms"], 1), **meta})
    return run_id


def make_search(variant, retriever):
    if retriever == "bm25":
        from rag.bm25 import bm25_search
        return lambda q: bm25_search(variant, q, k=FETCH_DEPTH)
    import chromadb
    from rag import index
    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    if retriever == "hybrid":
        # Ask for FETCH_DEPTH fused chunks (and fetch that many from each retriever) so the
        # document-level protocol sees the same depth as the vector and BM25 baselines.
        from rag.hybrid import hybrid_search
        return lambda q: hybrid_search(client, variant, q, embed, k=FETCH_DEPTH, fetch_depth=FETCH_DEPTH)
    return lambda q: index.search(client, variant, q, embed, k=FETCH_DEPTH)


def make_reranked_search(search_fn):
    """Wrap any search function: its FETCH_DEPTH candidates are reordered by the cross-encoder and
    all of them are returned, so document-level evaluation sees the same depth as without reranking."""
    from rag.rerank import load_reranker, rerank
    score_fn = load_reranker()
    return lambda q: rerank(q, search_fn(q), score_fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["v1", "v2", "v3"], default="v1")
    ap.add_argument("--retriever", choices=["vector", "bm25", "hybrid"], default="vector")
    ap.add_argument("--rerank", choices=["none", "cross-encoder"], default="none",
                    help="reorder the retrieved candidates with a cross-encoder (rag.rerank)")
    ap.add_argument("--notes", default="")
    ap.add_argument("--no-log", action="store_true", help="print only, do not append to results/runs.csv")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(GOLDEN, encoding="utf-8") if l.strip()]
    search = make_search(args.variant, args.retriever)
    rerank_name = "none"
    if args.rerank == "cross-encoder":
        from rag.rerank import RERANK_MODEL
        search, rerank_name = make_reranked_search(search), RERANK_MODEL
    per_question, summary = evaluate(rows, search)
    print(f"variant={args.variant} retriever={args.retriever} rerank={rerank_name} fetch_depth={FETCH_DEPTH} "
          f"answerable={len(per_question)} (unanswerable skipped: {len(rows) - len(per_question)})")
    print(f"{'split':<9}{'n':>3}{'recall@5':>10}{'hit@5':>8}{'MRR@10':>9}{'ms/query':>10}")
    for split, m in summary.items():
        print(f"{split:<9}{m['n']:>3}{m['recall_at_5']:>10.3f}{m['hit_at_5']:>8.3f}{m['mrr_at_10']:>9.3f}{m['avg_latency_ms']:>10.0f}")
    print("\nQuestions with recall@5 < 1 (read these by hand, Step 2.2e):")
    for x in per_question:
        if x["recall_at_5"] < 1:
            print(f"  {x['id']} [{x['split']}] recall={x['recall_at_5']:.2f} rr={x['rr_at_10']:.2f} "
                  f"expected={x['expected']} top5={x['top5']}")
    if not args.no_log:
        meta = {"variant": args.variant, "retriever": args.retriever, "rerank": rerank_name,
                "fetch_depth": FETCH_DEPTH, "notes": args.notes}
        print(f"\nlogged as run {append_runs(summary, meta)} in {RUNS}")


if __name__ == "__main__":
    main()
