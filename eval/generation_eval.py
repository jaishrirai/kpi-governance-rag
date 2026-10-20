"""
Step 3.1: generation evaluation. Runs the pipeline on the golden set for one prompt version, then scores
the answers with an LLM judge plus code checks. Run from the repo root with PYTHONPATH=src:

  python -m eval.generation_eval run --version answer_v1 --split dev
  python -m eval.generation_eval judge --input results/generation/answer_v1_dev.jsonl
  python -m eval.generation_eval report --inputs results/generation/answer_v1_dev.judged.jsonl

What is scored (dev and holdout are reported separately):
  key-fact coverage   judge, one yes/no per golden key fact (answerable questions)
  refusal             code: unanswerable questions should be refused, answerable ones should not be
  faithfulness        judge, every claim in the answer must be supported by the retrieved chunks
  citation validity   code, from the pipeline (provenance and consistency only)
  latency, tokens, and cost per query (cost only when prices are given on the command line)

Holdout rule: a prompt version may run on the holdout ONCE. `run` refuses to touch the holdout without
--confirm-holdout, and refuses a second holdout run of the same version (results/generation/holdout_runs.txt).
The holdout is logged as used when the run starts, so a crashed run still counts.
"""
import argparse
import json
import math
import os
import re
from datetime import date
from functools import partial
from pathlib import Path

from rag import generate as gen
from rag import llm, pipeline

GOLDEN = Path("golden/golden_set.jsonl")
OUT_DIR = Path("results/generation")
HOLDOUT_LOG = OUT_DIR / "holdout_runs.txt"
KEYFACTS_PROMPT = "judge_keyfacts_v1"
FAITH_PROMPT = "judge_faithfulness_v1"
JUDGE_MAX_OUTPUT_TOKENS = 2000  # some Gemini models spend part of this on hidden thinking
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


class JudgeError(RuntimeError):
    """The judge reply could not be used."""


# ---------- golden set ----------

def split_of(row):
    return "holdout" if row["holdout"] else "dev"


def load_golden(path=GOLDEN, split="all", ids=None):
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    if ids:
        missing = set(ids) - {row["id"] for row in rows}
        if missing:
            raise ValueError(f"unknown question ids: {sorted(missing)}")
        rows = [row for row in rows if row["id"] in set(ids)]
    if split != "all":
        rows = [row for row in rows if split_of(row) == split]
    return rows


def write_jsonl(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------- holdout guard ----------

def holdout_used(version, log_path=HOLDOUT_LOG):
    log_path = Path(log_path)
    if not log_path.exists():
        return False
    return any(line.split()[:1] == [version] for line in log_path.read_text(encoding="utf-8").splitlines())


def guard_holdout(version, confirmed, log_path=HOLDOUT_LOG):
    if not confirmed:
        raise SystemExit("This run includes holdout questions. Pass --confirm-holdout to proceed.")
    if holdout_used(version, log_path):
        raise SystemExit(f"{version} has already been run on the holdout (see {log_path}). "
                         "Edit that file yourself if you really mean to repeat it.")


def mark_holdout_used(version, out_path, log_path=HOLDOUT_LOG):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{version} {date.today().isoformat()} {out_path}\n")


# ---------- stage 1: run the pipeline ----------

def build_record(row, version, result, hits):
    attempts = result.attempts
    return {
        "id": row["id"], "split": split_of(row), "answerable": row["answerable"], "question": row["question"],
        "key_facts": row["key_facts"], "conflicting_doc_ids": row["conflicting_doc_ids"],
        "prompt_version": version, "chunk_ids": result.chunk_ids,
        "contexts": [{key: hit.get(key) for key in ("chunk_id", "doc_id", "certification", "text")} for hit in hits],
        "answer": result.answer, "citations": result.citations, "refused": result.refused,
        "valid": result.valid, "policy_refusal": result.policy_refusal, "attempt_count": len(attempts),
        "error": result.error,
        "input_tokens": sum(a["input_tokens"] or 0 for a in attempts),
        "output_tokens": sum((a["output_tokens"] or 0) + (a["thinking_tokens"] or 0) for a in attempts),
        "generation_ms": round(sum(a["generation_ms"] for a in attempts), 1),
        "retrieval_ms": round(result.retrieval_ms, 1),
    }


def run_questions(rows, version, retrieve_fn, trace_path, generate_fn=None, progress=print):
    """Run each question through retrieve -> generate -> validate (pipeline.ask). Keeps the retrieved chunk
    text in each record, because the faithfulness judge needs it."""
    generate_fn = generate_fn or partial(gen.generate, prompt_version=version)
    records = []
    for row in rows:
        captured = {}

        def capture(question, _retrieve=retrieve_fn, _captured=captured):
            _captured["hits"] = _retrieve(question)
            return _captured["hits"]

        result = pipeline.ask(row["question"], capture, generate_fn, trace_path=trace_path)
        record = build_record(row, version, result, captured.get("hits", []))
        records.append(record)
        progress(f"{record['id']} [{version}] refused={record['refused']} valid={record['valid']} "
                 f"attempts={record['attempt_count']} error={record['error']}")
    return records


# ---------- stage 2: judge ----------

def parse_json(text):
    try:
        data = json.loads(_FENCE.sub("", text.strip()))
    except json.JSONDecodeError as error:
        raise JudgeError(f"judge reply is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise JudgeError("judge reply is not a JSON object")
    return data


def judge_key_facts(question, answer, key_facts, complete_fn=llm.complete, model=None):
    """One yes/no per key fact, in order. Raises JudgeError if the reply does not match the facts given."""
    numbered = "\n".join(f"{i}. {fact}" for i, fact in enumerate(key_facts, 1))
    user = f"Question: {question}\n\nAnswer:\n{answer}\n\nKey facts:\n{numbered}"
    reply = complete_fn(gen.load_prompt(KEYFACTS_PROMPT), user, model=model, max_output_tokens=JUDGE_MAX_OUTPUT_TOKENS)
    facts = parse_json(reply.text).get("facts")
    if not isinstance(facts, list) or len(facts) != len(key_facts):
        raise JudgeError(f"expected {len(key_facts)} facts in the judge reply")
    verdicts = []
    for item in facts:
        if not isinstance(item, dict) or not isinstance(item.get("covered"), bool):
            raise JudgeError("each fact needs a boolean 'covered'")
        verdicts.append(item["covered"])
    return verdicts


def judge_faithfulness(answer, contexts, complete_fn=llm.complete, model=None):
    """The claims in the answer, each marked supported or not by the retrieved chunks."""
    user = f"Context chunks:\n\n{gen.format_context(contexts)}\n\nAnswer:\n{answer}"
    reply = complete_fn(gen.load_prompt(FAITH_PROMPT), user, model=model, max_output_tokens=JUDGE_MAX_OUTPUT_TOKENS)
    claims = parse_json(reply.text).get("claims")
    if not isinstance(claims, list):
        raise JudgeError("the judge reply has no list of claims")
    out = []
    for item in claims:
        if not isinstance(item, dict) or not isinstance(item.get("supported"), bool):
            raise JudgeError("each claim needs a boolean 'supported'")
        out.append({"claim": str(item.get("claim", "")), "supported": item["supported"]})
    return out


def judge_record(record, complete_fn=llm.complete, model=None):
    """Add a 'judge' block to a run record. A failure is stored in judge.errors and never stops the batch.
    A refused answer makes no claims, so it gets no faithfulness call, and it covers no key facts."""
    judge = {"model": model, "key_facts": None, "claims": None, "errors": []}
    if record["error"]:
        judge["errors"].append("skipped: pipeline error")
        return {**record, "judge": judge}
    if record["answerable"] and record["key_facts"]:
        if record["refused"]:
            judge["key_facts"] = [False] * len(record["key_facts"])
        else:
            try:
                judge["key_facts"] = judge_key_facts(record["question"], record["answer"], record["key_facts"],
                                                     complete_fn, model)
            except Exception as error:
                judge["errors"].append(f"key facts: {type(error).__name__}: {error}")
    if record["refused"]:
        judge["claims"] = []
    else:
        try:
            judge["claims"] = judge_faithfulness(record["answer"], record["contexts"], complete_fn, model)
        except Exception as error:
            judge["errors"].append(f"faithfulness: {type(error).__name__}: {error}")
    return {**record, "judge": judge}


def real_judge_errors(judge):
    """Judge errors that call for a rerun. A skip because of a pipeline error is not one."""
    return [error for error in judge["errors"] if not error.startswith("skipped:")]


def judge_records(records, prior=(), complete_fn=llm.complete, model=None, progress=print):
    """Judge every record. A record judged cleanly before (same id, question, answer and judge model) is kept
    as it is, so a rerun retries only the failures."""
    done = {r["id"]: r for r in prior if r["judge"]["errors"] == []}
    judged = []
    for record in records:
        old = done.get(record["id"])
        if (old and old["question"] == record["question"] and old["answer"] == record["answer"]
                and old["judge"]["model"] == model):
            judged.append(old)
            progress(f"{record['id']} kept (already judged)")
            continue
        result = judge_record(record, complete_fn, model)
        judged.append(result)
        errors = result["judge"]["errors"]
        progress(f"{record['id']} judged errors={errors if errors else 'none'}")
    return judged


def save_judged(judged, out, model):
    """Write the judged records, say how many still have judge errors, and return their ids."""
    write_jsonl(out, judged)
    failed = [r["id"] for r in judged if real_judge_errors(r["judge"])]
    print(f"wrote {len(judged)} records to {out} (judge model {model})")
    if failed:
        print(f"{len(failed)} of {len(judged)} records had judge errors: {failed}. "
              "Rerun the same command to retry only these.")
    else:
        print(f"0 of {len(judged)} records had judge errors.")
    return failed


def judge_model_id():
    llm._load_env()
    model = os.environ.get("JUDGE_MODEL")
    if not model:
        raise SystemExit("JUDGE_MODEL is not set. Put a Gemini model ID in .env.")
    return model


# ---------- stage 3: summarise ----------

def percentile(values, p):
    """Nearest-rank percentile; None for an empty list."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


def _ratio(num, den):
    return num / den if den else None


def _mean(values):
    return sum(values) / len(values) if values else None


def summarise(judged):
    answerable = [r for r in judged if r["answerable"]]
    unanswerable = [r for r in judged if not r["answerable"]]
    live = [r for r in judged if not r["error"]]
    scored = [r for r in answerable if r["judge"]["key_facts"] is not None]
    traps = [r for r in scored if r["conflicting_doc_ids"]]
    answered = [r for r in live if r["judge"]["claims"] is not None and not r["refused"]]
    claims = [c for r in answered for c in r["judge"]["claims"]]
    return {
        "n": len(judged), "answerable": len(answerable), "unanswerable": len(unanswerable),
        "pipeline_errors": len(judged) - len(live),
        "judge_errors": sum(1 for r in live if real_judge_errors(r["judge"])),
        "coverage": _ratio(sum(sum(r["judge"]["key_facts"]) for r in scored),
                           sum(len(r["judge"]["key_facts"]) for r in scored)),
        "full_coverage": _ratio(sum(1 for r in scored if all(r["judge"]["key_facts"])), len(scored)),
        "trap_coverage": _ratio(sum(sum(r["judge"]["key_facts"]) for r in traps),
                                sum(len(r["judge"]["key_facts"]) for r in traps)),
        "wrongly_refused": sum(1 for r in answerable if r["refused"]),
        "correct_refusals": _ratio(sum(1 for r in unanswerable if r["refused"]), len(unanswerable)),
        "faithful_answers": _ratio(sum(1 for r in answered if all(c["supported"] for c in r["judge"]["claims"])),
                                   len(answered)),
        # None, not 0, when no answer was judged: a zero would read like a clean result
        "unsupported_claims": sum(1 for c in claims if not c["supported"]) if answered else None,
        "claims": len(claims) if answered else None,
        "citation_valid": _ratio(sum(1 for r in live if r["valid"]), len(live)),
        "policy_refusals": sum(1 for r in judged if r["policy_refusal"]),
        "retried": sum(1 for r in judged if r["attempt_count"] > 1),
        "gen_ms_p50": percentile([r["generation_ms"] for r in live], 50),
        "gen_ms_p95": percentile([r["generation_ms"] for r in live], 95),
        "retrieval_ms_mean": _mean([r["retrieval_ms"] for r in live]),
        "input_tokens_mean": _mean([r["input_tokens"] for r in live]),
        "output_tokens_mean": _mean([r["output_tokens"] for r in live]),
    }


def cost_per_query(summary, price_in, price_out):
    """Prices are USD per 1M tokens. Output tokens include hidden thinking tokens (billed as output)."""
    if price_in is None or price_out is None or summary["input_tokens_mean"] is None:
        return None
    return (summary["input_tokens_mean"] * price_in + summary["output_tokens_mean"] * price_out) / 1_000_000


def _fmt(value, kind):
    if value is None:
        return "n/a"
    if kind == "pct":
        return f"{value * 100:.1f}%"
    if kind == "int":
        return str(int(value))
    if kind == "usd":
        return f"${value:.6f}"
    return f"{value:.0f}"


REPORT_ROWS = [
    ("questions", "n", "int"), ("answerable", "answerable", "int"), ("unanswerable", "unanswerable", "int"),
    ("pipeline errors", "pipeline_errors", "int"), ("judge errors", "judge_errors", "int"),
    ("key-fact coverage", "coverage", "pct"), ("answers with all key facts", "full_coverage", "pct"),
    ("coverage on trap questions", "trap_coverage", "pct"),
    ("answerable wrongly refused", "wrongly_refused", "int"), ("unanswerable correctly refused", "correct_refusals", "pct"),
    ("faithful answers (no unsupported claim)", "faithful_answers", "pct"),
    ("unsupported claims", "unsupported_claims", "int"), ("claims judged", "claims", "int"),
    ("citation check passed", "citation_valid", "pct"), ("policy refusals", "policy_refusals", "int"),
    ("answers that needed a retry", "retried", "int"),
    ("generation ms p50", "gen_ms_p50", "ms"), ("generation ms p95", "gen_ms_p95", "ms"),
    ("retrieval ms mean", "retrieval_ms_mean", "ms"), ("input tokens mean", "input_tokens_mean", "ms"),
    ("output tokens mean (with thinking)", "output_tokens_mean", "ms"),
]


def format_report(items, price_in=None, price_out=None, price_note=""):
    """items: list of (label, summary). Returns a markdown table with one column per item."""
    header = "| metric | " + " | ".join(label for label, _ in items) + " |"
    lines = [header, "|---|" + "---|" * len(items)]
    for name, key, kind in REPORT_ROWS:
        lines.append(f"| {name} | " + " | ".join(_fmt(s[key], kind) for _, s in items) + " |")
    costs = [cost_per_query(s, price_in, price_out) for _, s in items]
    if any(c is not None for c in costs):
        lines.append("| cost per query | " + " | ".join(_fmt(c, "usd") for c in costs) + " |")
        lines.append("")
        lines.append(f"Cost uses {price_in} USD per 1M input tokens and {price_out} USD per 1M output tokens. {price_note}")
    return "\n".join(lines)


# ---------- CLI ----------

def cmd_run(args):
    rows = load_golden(split=args.split, ids=args.ids.split(",") if args.ids else None)
    if not rows:
        raise SystemExit("no questions selected")
    out = Path(args.out) if args.out else OUT_DIR / f"{args.version}_{args.split}.jsonl"
    if any(split_of(row) == "holdout" for row in rows):
        guard_holdout(args.version, args.confirm_holdout)
        mark_holdout_used(args.version, out)
    retrieve = pipeline.make_retriever()
    records = run_questions(rows, args.version, retrieve, trace_path=out.with_name(f"traces_{out.stem}.jsonl"))
    write_jsonl(out, records)
    print(f"wrote {len(records)} records to {out}")


def cmd_judge(args):
    model = judge_model_id()
    out = Path(args.input).with_suffix(".judged.jsonl")
    prior = read_jsonl(out) if out.exists() else []
    judged = judge_records(read_jsonl(args.input), prior, model=model)
    if save_judged(judged, out, model):
        raise SystemExit(1)


def cmd_report(args):
    items = []
    for path in args.inputs:
        judged = read_jsonl(path)
        for split in ("dev", "holdout"):
            part = [r for r in judged if r["split"] == split]
            if part:
                items.append((f"{Path(path).name.replace('.judged.jsonl', '')} {split}", summarise(part)))
    print(format_report(items, args.price_in, args.price_out, args.price_note))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Step 3.1 generation evaluation")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the pipeline on golden questions")
    run.add_argument("--version", required=True, choices=["answer_v1", "answer_v2"])
    run.add_argument("--split", default="dev", choices=["dev", "holdout", "all"])
    run.add_argument("--ids", help="comma-separated question ids, for example G-018,G-034")
    run.add_argument("--out", help="output file (default results/generation/<version>_<split>.jsonl)")
    run.add_argument("--confirm-holdout", action="store_true")
    run.set_defaults(func=cmd_run)
    judge = sub.add_parser("judge", help="score a run file with the LLM judge (rerun to retry only the failures)")
    judge.add_argument("--input", required=True)
    judge.set_defaults(func=cmd_judge)
    report = sub.add_parser("report", help="summarise one or more judged files")
    report.add_argument("--inputs", nargs="+", required=True)
    report.add_argument("--price-in", type=float, help="USD per 1M input tokens")
    report.add_argument("--price-out", type=float, help="USD per 1M output tokens")
    report.add_argument("--price-note", default="", help="where and when the prices came from")
    report.set_defaults(func=cmd_report)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
