"""
Read-only question-level comparison of two retrieval configurations (Step 2.4). Nothing is logged.

A config is vector, bm25 or hybrid, optionally followed by +rerank (cross-encoder over the same
FETCH_DEPTH candidates). The script prints each config's summary, then every answerable question
whose recall@5 or reciprocal rank differs, as improved, regressed or mixed.
  $env:PYTHONPATH = "src"
  python scripts/compare_configs.py --variant v1 --a vector --b vector+rerank
Decide on dev. Holdout is printed for the record and is not for tuning.
"""
import argparse
import json
import sys

sys.path.insert(0, ".")
import eval.retrieval_eval as ev  # noqa: E402


def build_search(variant, config):
    retriever, _, rerank = config.partition("+")
    search = ev.make_search(variant, retriever)
    return ev.make_reranked_search(search) if rerank == "rerank" else search


def changes(a_rows, b_rows):
    """Questions whose recall@5 or reciprocal rank differs between two evaluate() per-question lists."""
    b_by_id = {x["id"]: x for x in b_rows}
    out = []
    for a in a_rows:
        b = b_by_id[a["id"]]
        d_recall = b["recall_at_5"] - a["recall_at_5"]
        d_rr = b["rr_at_10"] - a["rr_at_10"]
        if abs(d_recall) < 1e-9 and abs(d_rr) < 1e-9:
            continue
        if d_recall >= -1e-9 and d_rr >= -1e-9:
            verdict = "improved"
        elif d_recall <= 1e-9 and d_rr <= 1e-9:
            verdict = "regressed"
        else:
            verdict = "mixed"
        out.append({"id": a["id"], "split": a["split"], "verdict": verdict, "expected": a["expected"],
                    "recall": (a["recall_at_5"], b["recall_at_5"]), "rr": (a["rr_at_10"], b["rr_at_10"]),
                    "top5_a": a["top5"], "top5_b": b["top5"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["v1", "v2", "v3"], default="v1")
    ap.add_argument("--a", default="vector", help="reference config, e.g. vector")
    ap.add_argument("--b", default="vector+rerank", help="config to compare, e.g. vector+rerank")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(ev.GOLDEN, encoding="utf-8") if l.strip()]
    results = {}
    for name in (args.a, args.b):
        results[name] = ev.evaluate(rows, build_search(args.variant, name))
        print(f"\n{name} (variant {args.variant}, fetch_depth {ev.FETCH_DEPTH})")
        print(f"{'split':<9}{'n':>3}{'recall@5':>10}{'hit@5':>8}{'MRR@10':>9}")
        for split, m in results[name][1].items():
            print(f"{split:<9}{m['n']:>3}{m['recall_at_5']:>10.3f}{m['hit_at_5']:>8.3f}{m['mrr_at_10']:>9.3f}")
    diffs = changes(results[args.a][0], results[args.b][0])
    print(f"\nQuestions that differ, {args.a} -> {args.b} ({len(diffs)}):")
    for split in ("dev", "holdout"):
        print(f"-- {split}")
        for d in (x for x in diffs if x["split"] == split):
            print(f"  {d['id']} {d['verdict']:<9} recall {d['recall'][0]:.2f}->{d['recall'][1]:.2f}  "
                  f"rr {d['rr'][0]:.2f}->{d['rr'][1]:.2f}  expected={d['expected']}")
            print(f"      top5 {args.a}: {d['top5_a']}")
            print(f"      top5 {args.b}: {d['top5_b']}")


if __name__ == "__main__":
    main()
