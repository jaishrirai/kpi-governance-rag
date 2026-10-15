"""
Read-only diagnostics for Step 2.3 (nothing is logged, nothing is tuned).

1. Depth: how many distinct documents are in the fused top FETCH_DEPTH chunks of hybrid retrieval.
   The document-level protocol needs at least 10 (same check as scripts/check_fetch_depth.py).
2. Governance: how often KPI-007-V1 (deprecated churn KPI) and FAQ-01 (conflicting 90-day Active
   Customer definition) appear in the top 5 documents, by retriever, variant and split. Counted over
   answerable questions, like the retrieval metrics. "declared" = the question lists the document
   in expected, conflicting or related-insufficient documents, so the appearance is expected there.

Run from the repo root in the Windows .venv (needs the embedding model):
  $env:PYTHONPATH = "src"
  python scripts/diagnose_hybrid.py
"""
import json
import statistics
import sys

sys.path.insert(0, ".")
from eval.retrieval_eval import FETCH_DEPTH, RECALL_K, to_doc_ranking  # noqa: E402

TARGETS = ("KPI-007-V1", "FAQ-01")
NEEDED = 10
VARIANTS = ("v1", "v2", "v3")
RETRIEVERS = ("vector", "bm25", "hybrid")


def depth_report(rows, search):
    """search(question) -> chunk hits. Distinct documents and chunks returned per question."""
    docs, chunks, short = [], [], []
    for r in rows:
        hits = search(r["question"])
        n = len(to_doc_ranking(hits))
        docs.append(n)
        chunks.append(len(hits))
        if n < NEEDED:
            short.append((r["id"], n, len(hits)))
    return {"min_docs": min(docs), "median_docs": statistics.median(docs), "max_docs": max(docs),
            "min_chunks": min(chunks), "short": short}


def governance_counts(rows, search):
    """Answerable questions only. Per split: n, and per target [in top 5, of which declared]."""
    out = {s: {"n": 0, **{t: [0, 0] for t in TARGETS}} for s in ("dev", "holdout")}
    for r in rows:
        if not r["answerable"]:
            continue
        cell = out["holdout" if r["holdout"] else "dev"]
        cell["n"] += 1
        top5 = to_doc_ranking(search(r["question"]))[:RECALL_K]
        declared = (set(r["expected_doc_ids"]) | set(r.get("conflicting_doc_ids", []))
                    | set(r.get("related_insufficient_doc_ids", [])))
        for t in TARGETS:
            if t in top5:
                cell[t][0] += 1
                if t in declared:
                    cell[t][1] += 1
    return out


def make_searchers(variant, client, embed):
    from rag import bm25, hybrid, index
    return {
        "vector": lambda q: index.search(client, variant, q, embed, k=FETCH_DEPTH),
        "bm25": lambda q: bm25.bm25_search(variant, q, k=FETCH_DEPTH),
        "hybrid": lambda q: hybrid.hybrid_search(client, variant, q, embed, k=FETCH_DEPTH, fetch_depth=FETCH_DEPTH),
    }


def main():
    import chromadb
    from rag import index
    rows = [json.loads(l) for l in open("golden/golden_set.jsonl", encoding="utf-8") if l.strip()]
    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    print(f"FETCH_DEPTH={FETCH_DEPTH} questions={len(rows)} answerable={sum(r['answerable'] for r in rows)}")

    print(f"\n== 1. Hybrid depth: distinct documents in the fused top {FETCH_DEPTH} chunks (need >= {NEEDED}) ==")
    for variant in VARIANTS:
        rep = depth_report(rows, make_searchers(variant, client, embed)["hybrid"])
        print(f"{variant}: docs min={rep['min_docs']} median={rep['median_docs']} max={rep['max_docs']}; "
              f"chunks returned min={rep['min_chunks']}; questions below {NEEDED}: {len(rep['short'])}")
        for qid, n, c in rep["short"][:12]:
            print(f"   {qid}: {n} docs from {c} chunks")

    print(f"\n== 2. Appearances in the top {RECALL_K} documents (count of questions; 'declared' in brackets) ==")
    print(f"{'variant':<8}{'retriever':<10}{'split':<9}{'n':>3}  {'KPI-007-V1':>14}  {'FAQ-01':>12}")
    for variant in VARIANTS:
        searchers = make_searchers(variant, client, embed)
        for retriever in RETRIEVERS:
            counts = governance_counts(rows, searchers[retriever])
            for split in ("dev", "holdout"):
                c = counts[split]
                a, b = c["KPI-007-V1"], c["FAQ-01"]
                print(f"{variant:<8}{retriever:<10}{split:<9}{c['n']:>3}  {a[0]:>9} [{a[1]}]  {b[0]:>7} [{b[1]}]")


if __name__ == "__main__":
    main()
