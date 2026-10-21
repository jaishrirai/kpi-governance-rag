"""
Step 3.1: blind hand-grading of 10 answers, then agreement with the LLM judge.

  python -m eval.handgrade sheet       build the sheet, the CSV to fill in, and a private version mapping
  python -m eval.handgrade agreement   compare your grades with the judge (run AFTER you finish grading)

The sheet shows 10 answers from 10 different dev questions (3 trap questions, 7 others), 5 from each prompt
version, shuffled, with no version label and no judge output. Do not open the judged files, run the report
command, or open mapping_private.json until the CSV is finished.

How to grade (the same rubric the judge uses):
  key fact       y only if the answer clearly states it; a paraphrase counts if the meaning is the same.
                 Do not give credit for a hint. Ignore extra facts, style and typos.
  faithfulness   y only if every claim in the answer is supported by the context chunks shown on the sheet
                 (a fact, number, date, name or relationship that no chunk states makes it n).

Bar, set before any number was seen: at least 85% agreement on key facts and at least 8 of 10 on
faithfulness. Disagreements are reviewed one by one. Refused answers are not graded (refusal is a code check).
"""
import argparse
import csv
import json
import random
from pathlib import Path

from eval import generation_eval as ge

DIR = Path("results/generation/handgrade")
SHEET, TEMPLATE, MAPPING = DIR / "handgrade_sheet.md", DIR / "handgrade_template.csv", DIR / "mapping_private.json"
RUNS = {"answer_v1": Path("results/generation/answer_v1_dev.jsonl"), "answer_v2": Path("results/generation/answer_v2_dev.jsonl")}
SEED = 20261020
N_TRAPS, N_TOTAL = 3, 10
FACT_BAR, FAITH_BAR = 0.85, 8
FAITH_TEXT = "Every claim in the answer is supported by the context chunks"
HOW_TO = """# Hand-grading sheet

How to grade (the same rubric the judge uses):
- Key fact: y only if the answer clearly states it. A paraphrase counts if the meaning is the same. Do not give credit for a hint. Ignore extra facts, style and typos.
- Faithfulness: y only if every claim in the answer is supported by the context chunks shown below. A fact, number, date, name or relationship that no chunk states makes it n.

Fill in handgrade_template.csv, column 'answer': y or n. One row per key fact, plus one faithfulness row per answer.
"""


def pick_items(v1, v2, seed=SEED, n_traps=N_TRAPS, n_total=N_TOTAL):
    """v1, v2: run records by id. Questions answerable and answered (not refused, no error) in both versions."""
    rng = random.Random(seed)
    ids = sorted(i for i in v1 if i in v2 and all(
        r[i]["answerable"] and not r[i]["refused"] and not r[i]["error"] for r in (v1, v2)))
    traps = [i for i in ids if v1[i]["conflicting_doc_ids"]]
    others = [i for i in ids if not v1[i]["conflicting_doc_ids"]]
    chosen = rng.sample(traps, min(n_traps, len(traps)))
    chosen += rng.sample(others, n_total - len(chosen))
    rng.shuffle(chosen)
    versions = ["answer_v1"] * (n_total // 2) + ["answer_v2"] * (n_total - n_total // 2)
    rng.shuffle(versions)
    return [{"code": f"H{n:02d}", "id": qid, "version": version,
             "record": (v1 if version == "answer_v1" else v2)[qid]}
            for n, (qid, version) in enumerate(zip(chosen, versions), 1)]


def sheet_markdown(items):
    out = [HOW_TO]
    for item in items:
        rec = item["record"]
        out += [f"\n---\n\n## {item['code']}\n", f"**Question:** {rec['question']}\n", f"**Answer:** {rec['answer']}\n",
                "**Key facts to check:**"] + [f"{n}. {fact}" for n, fact in enumerate(rec["key_facts"], 1)]
        out += ["", "**Context chunks the answer was given:**\n"]
        for ctx in rec["contexts"]:
            out += [f"- `{ctx['chunk_id']}` ({ctx['certification']}): {ctx['text'].strip()}\n"]
    return "\n".join(out) + "\n"


def template_rows(items):
    rows = []
    for item in items:
        for fact in item["record"]["key_facts"]:
            rows.append({"code": item["code"], "kind": "fact", "item": fact, "answer": "", "notes": ""})
        rows.append({"code": item["code"], "kind": "faithful", "item": FAITH_TEXT, "answer": "", "notes": ""})
    return rows


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["code", "kind", "item", "answer", "notes"])
        writer.writeheader()
        writer.writerows(rows)


def read_grades(path):
    """Returns {code: {"facts": [bool, ...], "faithful": bool}}. Raises ValueError on any blank or non y/n cell."""
    grades, bad = {}, []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for n, row in enumerate(csv.DictReader(handle), 2):
            value = row["answer"].strip().lower()
            if value not in ("y", "n"):
                bad.append(f"row {n} ({row['code']} {row['kind']})")
                continue
            entry = grades.setdefault(row["code"], {"facts": [], "faithful": None})
            if row["kind"] == "fact":
                entry["facts"].append(value == "y")
            else:
                entry["faithful"] = value == "y"
    if bad:
        raise ValueError("answer must be y or n in: " + ", ".join(bad))
    return grades


def kappa(pairs):
    """Cohen's kappa for (human, judge) boolean pairs; None when chance agreement is total."""
    n = len(pairs)
    observed = sum(h == j for h, j in pairs) / n
    h_yes, j_yes = sum(h for h, _ in pairs) / n, sum(j for _, j in pairs) / n
    chance = h_yes * j_yes + (1 - h_yes) * (1 - j_yes)
    return None if chance == 1 else (observed - chance) / (1 - chance)


def compare(items, grades, judged):
    """judged: {version: {id: judged record}}. Returns the agreement numbers and the list of disagreements."""
    fact_pairs, faith_pairs, disagreements, usable = [], [], [], 0
    by_version = {}
    for item in items:
        rec = judged[item["version"]][item["id"]]
        human, judge = grades[item["code"]], rec["judge"]
        if judge["errors"] or judge["key_facts"] is None or judge["claims"] is None:
            disagreements.append(f"{item['code']} ({item['id']}): judge has errors, not compared")
            continue
        usable += 1
        for fact, h, j in zip(rec["key_facts"], human["facts"], judge["key_facts"]):
            fact_pairs.append((h, j))
            if h != j:
                disagreements.append(f"{item['code']} ({item['id']}) key fact '{fact}': human={'y' if h else 'n'} judge={'y' if j else 'n'}")
        judge_faithful = all(c["supported"] for c in judge["claims"])
        faith_pairs.append((human["faithful"], judge_faithful))
        if human["faithful"] != judge_faithful:
            unsupported = [c["claim"] for c in judge["claims"] if not c["supported"]]
            disagreements.append(f"{item['code']} ({item['id']}) faithfulness: human={'y' if human['faithful'] else 'n'} "
                                 f"judge={'y' if judge_faithful else 'n'} unsupported by judge: {unsupported}")
        stats = by_version.setdefault(item["version"], {"human": 0, "judge": 0, "total": 0})
        stats["human"] += sum(human["facts"])
        stats["judge"] += sum(judge["key_facts"])
        stats["total"] += len(human["facts"])
    fact_agree = sum(h == j for h, j in fact_pairs) / len(fact_pairs) if fact_pairs else None
    faith_agree = sum(h == j for h, j in faith_pairs)
    return {"answers_compared": usable, "fact_pairs": len(fact_pairs), "fact_agreement": fact_agree,
            "fact_kappa": kappa(fact_pairs) if fact_pairs else None,
            "human_yes_judge_no": sum(1 for h, j in fact_pairs if h and not j),
            "human_no_judge_yes": sum(1 for h, j in fact_pairs if j and not h),
            "faith_agree": faith_agree, "faith_total": len(faith_pairs),
            "meets_bar": bool(fact_agree is not None and fact_agree >= FACT_BAR and faith_agree >= FAITH_BAR
                              and len(faith_pairs) == N_TOTAL),
            "disagreements": disagreements, "by_version": by_version}


def cmd_sheet(args):
    if TEMPLATE.exists() and not args.force:
        raise SystemExit(f"{TEMPLATE} already exists. Not overwriting your grades. Use --force only to start over.")
    v1 = {r["id"]: r for r in ge.read_jsonl(RUNS["answer_v1"])}
    v2 = {r["id"]: r for r in ge.read_jsonl(RUNS["answer_v2"])}
    items = pick_items(v1, v2)
    DIR.mkdir(parents=True, exist_ok=True)
    SHEET.write_text(sheet_markdown(items), encoding="utf-8")
    write_csv(TEMPLATE, template_rows(items))
    MAPPING.write_text(json.dumps({i["code"]: {"id": i["id"], "version": i["version"]} for i in items}, indent=1), encoding="utf-8")
    print(f"wrote {SHEET}, {TEMPLATE} and a private mapping ({len(items)} answers). Do not open the mapping until you finish.")


def cmd_agreement(args):
    items_map = json.loads(MAPPING.read_text(encoding="utf-8"))
    judged = {v: {r["id"]: r for r in ge.read_jsonl(RUNS[v].with_suffix(".judged.jsonl"))} for v in RUNS}
    items = [{"code": code, "id": m["id"], "version": m["version"]} for code, m in items_map.items()]
    result = compare(items, read_grades(TEMPLATE), judged)
    pct = lambda x: "n/a" if x is None else f"{x * 100:.1f}%"
    print(f"answers compared: {result['answers_compared']} of {len(items)}")
    print(f"key-fact agreement: {pct(result['fact_agreement'])} over {result['fact_pairs']} facts "
          f"(bar {FACT_BAR * 100:.0f}%), kappa {result['fact_kappa'] if result['fact_kappa'] is None else round(result['fact_kappa'], 2)}")
    print(f"  human yes / judge no: {result['human_yes_judge_no']}   human no / judge yes: {result['human_no_judge_yes']}")
    print(f"faithfulness agreement: {result['faith_agree']} of {result['faith_total']} (bar {FAITH_BAR})")
    print("BAR MET" if result["meets_bar"] else "BAR NOT MET (or not all answers compared)")
    for line in result["disagreements"]:
        print("  -", line)
    print("per version, key facts covered (human vs judge):")
    for version, s in sorted(result["by_version"].items()):
        print(f"  {version}: human {s['human']}/{s['total']}  judge {s['judge']}/{s['total']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Blind hand-grading and judge agreement")
    sub = parser.add_subparsers(dest="command", required=True)
    sheet = sub.add_parser("sheet")
    sheet.add_argument("--force", action="store_true")
    sheet.set_defaults(func=cmd_sheet)
    sub.add_parser("agreement").set_defaults(func=cmd_agreement)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
