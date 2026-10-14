"""
Check that FETCH_DEPTH chunks are enough to give at least 10 distinct documents (Step 2.2).
Run from the repo root with PYTHONPATH=src:
  python scripts/check_fetch_depth.py --retriever bm25
  python scripts/check_fetch_depth.py --retriever vector     (needs the embedding model, run in the .venv)
Runs every golden question on V1, V2, V3 and reports the number of distinct documents among the
first FETCH_DEPTH chunks: min, median, and the questions that fall below 10.
"""
import argparse
import json
import statistics
import sys

sys.path.insert(0, ".")
from eval.retrieval_eval import FETCH_DEPTH, to_doc_ranking  # noqa: E402

NEEDED = 10


def make_search(retriever):
    if retriever == "bm25":
        from rag.bm25 import bm25_search
        return lambda variant, q: bm25_search(variant, q, k=FETCH_DEPTH)
    import chromadb
    from rag import index
    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    return lambda variant, q: index.search(client, variant, q, embed, k=FETCH_DEPTH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", choices=["bm25", "vector"], default="bm25")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open("golden/golden_set.jsonl", encoding="utf-8") if l.strip()]
    search = make_search(args.retriever)
    print(f"retriever={args.retriever} FETCH_DEPTH={FETCH_DEPTH} questions={len(rows)}")
    for variant in ("v1", "v2", "v3"):
        counts = []
        short = []
        for r in rows:
            hits = search(variant, r["question"])
            n = len(to_doc_ranking(hits))
            counts.append((n, len(hits)))
            if n < NEEDED:
                short.append((r["id"], n, len(hits)))
        docs = [c[0] for c in counts]
        print(f"{variant}: distinct docs min={min(docs)} median={statistics.median(docs)} max={max(docs)}; "
              f"chunks returned min={min(c[1] for c in counts)}; questions below {NEEDED}: {len(short)}")
        for qid, n, chunks in short[:12]:
            print(f"   {qid}: {n} docs from {chunks} chunks")


if __name__ == "__main__":
    main()
