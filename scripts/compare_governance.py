"""
Read-only governance comparison (Step 2.4): vector-only against vector + rerank on one variant.
Nothing is logged and no ranking logic is changed. It measures how the two governance documents
behave; it does not try to fix them.

  KPI-007-V1  the deprecated churn KPI
  FAQ-01      the FAQ with the conflicting 90-day Active Customer definition

Prints, per split (counted over answerable questions, like the metrics):
  1. how many questions have each document in the top 5 ("declared" in brackets = the question
     lists it as expected, conflicting or related, so its presence is expected there)
  2. for questions where both KPI-007 and KPI-007-V1 are in the top 10, how often the deprecated
     one is ranked above the current one
then, for chosen questions, the top 10 documents of each config
(* = expected for that question, ! = KPI-007-V1, FAQ-01 or a declared conflicting document).
  $env:PYTHONPATH = "src"
  python scripts/compare_governance.py
"""
import argparse
import json
import sys

sys.path.insert(0, ".")
sys.path.insert(0, "scripts")
import compare_configs as cc  # noqa: E402
import diagnose_hybrid as dh  # noqa: E402
import eval.retrieval_eval as ev  # noqa: E402

CONFIGS = ("vector", "vector+rerank")
QUESTIONS = ("G-013", "G-003", "G-004", "G-015", "G-027")
DEPRECATED, CURRENT = "KPI-007-V1", "KPI-007"


def cached(search):
    """Search once per question: the same results feed every table below."""
    memo = {}

    def run(question):
        if question not in memo:
            memo[question] = search(question)
        return memo[question]

    return run


def deprecated_vs_current(rows, search):
    """Per split: questions with both KPI-007 and KPI-007-V1 in the top 10, and how many rank the
    deprecated one above the current one."""
    out = {s: {"both": 0, "deprecated_first": 0} for s in ("dev", "holdout")}
    for r in rows:
        if not r["answerable"]:
            continue
        ranking = ev.to_doc_ranking(search(r["question"]))[:10]
        if DEPRECATED in ranking and CURRENT in ranking:
            cell = out["holdout" if r["holdout"] else "dev"]
            cell["both"] += 1
            cell["deprecated_first"] += int(ranking.index(DEPRECATED) < ranking.index(CURRENT))
    return out


def annotated_top10(row, search):
    """Top 10 documents as text, marking expected (*) and governance (!) documents."""
    expected = set(row["expected_doc_ids"])
    flagged = set(dh.TARGETS) | set(row.get("conflicting_doc_ids", []))
    ranking = ev.to_doc_ranking(search(row["question"]))[:10]
    return [doc + ("*" if doc in expected else "") + ("!" if doc in flagged else "") for doc in ranking]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["v1", "v2", "v3"], default="v1")
    ap.add_argument("--questions", nargs="*", default=list(QUESTIONS))
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(ev.GOLDEN, encoding="utf-8") if l.strip()]
    searches = {name: cached(cc.build_search(args.variant, name)) for name in CONFIGS}

    print(f"variant={args.variant} fetch_depth={ev.FETCH_DEPTH} top {ev.RECALL_K} unless stated")
    print(f"\n{'config':<15}{'split':<9}{'n':>3}  {'KPI-007-V1 top5':>16}  {'FAQ-01 top5':>12}  "
          f"{'deprecated above current':>26}")
    for name in CONFIGS:
        counts = dh.governance_counts(rows, searches[name])
        order = deprecated_vs_current(rows, searches[name])
        for split in ("dev", "holdout"):
            c, o = counts[split], order[split]
            a, b = c[DEPRECATED], c["FAQ-01"]
            print(f"{name:<15}{split:<9}{c['n']:>3}  {a[0]:>11} [{a[1]}]  {b[0]:>7} [{b[1]}]  "
                  f"{o['deprecated_first']:>14} of {o['both']} with both")

    by_id = {r["id"]: r for r in rows}
    print("\nTop 10 documents for chosen questions (* expected, ! governance document)")
    for qid in args.questions:
        r = by_id[qid]
        split = "holdout" if r["holdout"] else "dev"
        print(f"\n{qid} [{split}] {r['question']}")
        print(f"  expected={r['expected_doc_ids']} conflicting={r.get('conflicting_doc_ids', [])}")
        for name in CONFIGS:
            print(f"  {name:<14} {' '.join(annotated_top10(r, searches[name]))}")


if __name__ == "__main__":
    main()
