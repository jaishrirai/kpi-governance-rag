"""
Judge sanity check (Step 3.1): can the judge say no? Feeds the two judge prompts answers with known
problems, plus positive controls, and compares the verdicts with what a careful human would say.

Contexts and questions come from a saved run file (the 3-question smoke run holds G-013 and G-018), so no
index or retrieval is needed. Costs about 10 judge calls. Run from the repo root with PYTHONPATH=src:
  python -m eval.judge_sanity
  python -m eval.judge_sanity --run results/generation/smoke_answer_v1.jsonl

A case PASSES when the judge agrees with the expected verdict. INFO cases have no right answer: they record
a known limit of the faithfulness judge (it checks support by the chunks, not whether a source is
authoritative). Exits with status 1 if any case fails or the judge errors. Results are saved to
results/generation/judge_sanity_<model>.json, one file per judge model. Use --judge-model to test another
model and --pause SECONDS to stay under a per-minute limit.
"""
import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from eval import generation_eval as ge
from rag import llm

DEFAULT_RUN = Path("results/generation/smoke_answer_v1.jsonl")
OUT_TEMPLATE = "results/generation/judge_sanity_{model}.json"

GOOD_G013 = ("Customer Churn Rate is calculated as the percentage of customers in the start base with no purchase "
             "for 180 days by quarter end divided by customers in the start base, multiplied by 100 [KPI-007::v1::0]. "
             "It is used in the Customer 360 Dashboard and the Executive KPI Pack [KPI-007::v1::0].")


@dataclass
class Case:
    name: str
    kind: str  # "facts" (key-fact judge) or "claims" (faithfulness judge)
    record: dict  # a run record: question, key_facts, contexts
    answer: str
    expect: object  # facts: list of bools. claims: "all_supported" or "some_unsupported". None: INFO only


def build_cases(records):
    """records: run records by id. Needs G-013 (churn) and G-018 (active customer)."""
    g13, g18 = records["G-013"], records["G-018"]
    return [
        Case("facts: complete answer covers every fact (positive control)", "facts", g13, GOOD_G013, [True, True, True]),
        Case("facts: vague answer covers none", "facts", g13,
             "Customer Churn Rate measures customers who stop buying [KPI-007::v1::0].", [False, False, False]),
        Case("facts: Executive KPI Pack left out", "facts", g13,
             "Customer Churn Rate counts customers in the start base with no purchase for 180 days by quarter end. "
             "It is used in the Customer 360 Dashboard [KPI-007::v1::0].", [True, True, False]),
        Case("facts: FAQ 90-day figure given as the rule", "facts", g18,
             "An Active Customer is counted using a 90-day window [FAQ-01::v1::0].", [False, False]),
        Case("facts: clear authority wording (positive control)", "facts", g18,
             "The 30-day window is the only certified definition [KPI-006::v1::0]. Informal definitions such as the "
             "90-day figure in the team FAQ have no standing and must not be used [FAQ-01::v1::0].", [True, True]),
        Case("claims: faithful answer (positive control)", "claims", g13, GOOD_G013, "all_supported"),
        Case("claims: invented dashboard", "claims", g13,
             "Customer Churn Rate is used in the Customer 360 Dashboard and the Finance Cockpit dashboard "
             "[KPI-007::v1::0].", "some_unsupported"),
        Case("claims: wrong owner", "claims", g13,
             "Customer Churn Rate is owned by the Head of Finance [KPI-007::v1::0].", "some_unsupported"),
        Case("claims: invented number", "claims", g18,
             "An Active Customer is anyone who completed a purchase in the last 45 days [KPI-006::v1::0].",
             "some_unsupported"),
        Case("INFO claims: FAQ 90-day figure as the rule (support is not authority)", "claims", g18,
             "An Active Customer is anyone who bought something in the last 90 days [FAQ-01::v1::0].", None),
    ]


def run_case(case, complete_fn=llm.complete, model=None):
    """Returns (passed, got). passed is True, False, or None for an INFO case. Judge errors are raised."""
    rec = case.record
    if case.kind == "facts":
        got = ge.judge_key_facts(rec["question"], case.answer, rec["key_facts"], complete_fn, model)
        return (got == case.expect if case.expect is not None else None), got
    claims = ge.judge_faithfulness(case.answer, rec["contexts"], complete_fn, model)
    everything_supported = all(c["supported"] for c in claims)
    got = [("supported" if c["supported"] else "UNSUPPORTED") + ": " + c["claim"] for c in claims]
    if case.expect is None:
        return None, got
    return (everything_supported if case.expect == "all_supported" else not everything_supported), got


def run_all(cases, complete_fn=llm.complete, model=None, progress=print):
    results = []
    for case in cases:
        try:
            passed, got = run_case(case, complete_fn, model)
            error = None
        except Exception as exc:
            passed, got, error = False, None, f"{type(exc).__name__}: {exc}"
        verdict = "INFO" if passed is None else ("PASS" if passed else "FAIL")
        progress(f"[{verdict}] {case.name}\n      expected: {case.expect}\n      got:      {error or got}")
        results.append({"case": case.name, "expected": case.expect, "got": error or got, "verdict": verdict})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Judge sanity check")
    parser.add_argument("--run", default=str(DEFAULT_RUN))
    parser.add_argument("--judge-model", help="Gemini model ID to test (default: JUDGE_MODEL in .env)")
    parser.add_argument("--pause", type=float, default=0, help="seconds between model calls")
    args = parser.parse_args(argv)
    records = {r["id"]: r for r in ge.read_jsonl(args.run)}
    model = ge.judge_model_id(args.judge_model)
    results = run_all(build_cases(records), ge.paced(llm.complete, args.pause), model)
    failed = [r for r in results if r["verdict"] == "FAIL"]
    scored = [r for r in results if r["verdict"] != "INFO"]
    out = Path(OUT_TEMPLATE.format(model=model))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"judge_model": model, "results": results}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(scored) - len(failed)} of {len(scored)} scored cases passed (judge model {model}). Saved to {out}.")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
