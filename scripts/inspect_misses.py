"""
Read-only diagnostic (Step 2.2e): where do the expected documents rank for chosen questions?
For each question and variant it prints the vector rank and best-chunk similarity of every expected
document within FETCH_DEPTH chunks, and the similarity of the 5th document for comparison.
  $env:PYTHONPATH = "src"
  python scripts/inspect_misses.py G-005 G-001 G-015 G-023 G-006
"""
import json
import sys

import chromadb

sys.path.insert(0, ".")
from eval.retrieval_eval import FETCH_DEPTH  # noqa: E402
from rag import index  # noqa: E402


def doc_rank(hits):
    best = {}
    for h in hits:
        best.setdefault(h["doc_id"], (len(best) + 1, h["similarity"], h["section"]))
    return best


def main(ids):
    rows = {json.loads(l)["id"]: json.loads(l) for l in open("golden/golden_set.jsonl", encoding="utf-8") if l.strip()}
    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    for qid in ids:
        r = rows[qid]
        print(f"\n{qid}: {r['question']}\n  expected: {r['expected_doc_ids']}")
        for v in ("v1", "v2", "v3"):
            best = doc_rank(index.search(client, v, r["question"], embed, k=FETCH_DEPTH))
            fifth = [d for d, x in best.items() if x[0] == 5]
            fifth_sim = f"{best[fifth[0]][1]:.3f}" if fifth else "n/a"
            parts = []
            for d in r["expected_doc_ids"]:
                x = best.get(d)
                parts.append(f"{d}: " + (f"rank {x[0]} sim {x[1]:.3f} [{x[2]}]" if x else "not in top 50 chunks"))
            print(f"  {v}: doc#5 sim {fifth_sim} | " + " | ".join(parts))


if __name__ == "__main__":
    main(sys.argv[1:])
