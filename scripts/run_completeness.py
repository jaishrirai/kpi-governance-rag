"""Step 2.6B completeness experiment: the five dev questions, one prompt version, one run, real Gemini.

Dev questions only. The holdout set is never run here. Run from the repo root with PYTHONPATH=src.
Each run is saved separately, so repeats can be compared:
  python scripts/run_completeness.py answer_v1 2
  python scripts/run_completeness.py answer_v2 2

Arguments: prompt version (answer_v1 or answer_v2) and run number (default 1).
Writes results/completeness/<version>_run<N>.jsonl, one line per question, with the true prompt_version.
Trace lines go to results/completeness/traces_<version>_run<N>.jsonl. Those lines carry the default
prompt_version (answer_v1) for both versions, because pipeline.py records gen.PROMPT_VERSION. Use the
results file, not the trace, to tell the versions apart.
"""
import json
import sys
from functools import partial
from pathlib import Path

from rag import generate as gen
from rag import pipeline

DEV_QUESTIONS = [
    ("G-018", "How many days do we use to count an Active Customer?"),
    ("G-013", "Customer churn rate - how is that calculated? What dashboards use it?"),
    ("G-002", "What KPIs around customer churn which are enabled right now?"),
    ("G-017", "What is NRR and how is it different from churn?"),
    ("G-001", "What are key KPIs and Dashboards serving Customer Domain. Give me strcutured asnwer."),
]
OUT_DIR = Path("results/completeness")
VERSIONS = ("answer_v1", "answer_v2")


def main(version, run):
    if version not in VERSIONS:
        raise SystemExit(f"unknown prompt version: {version}")
    if run < 1:
        raise SystemExit("run number must be 1 or more")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    retrieve = pipeline.make_retriever()
    generate_fn = partial(gen.generate, prompt_version=version)
    tag = f"{version}_run{run}"
    trace = OUT_DIR / f"traces_{tag}.jsonl"
    with (OUT_DIR / f"{tag}.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for gid, question in DEV_QUESTIONS:
            result = pipeline.ask(question, retrieve, generate_fn, trace_path=trace)
            record = {
                "run": run, "id": gid, "question": question,
                "prompt_version": result.generation.prompt_version if result.generation else None,
                "chunk_ids": result.chunk_ids, "answer": result.answer, "citations": result.citations,
                "refused": result.refused, "valid": result.valid,
                "attempt_count": len(result.attempts), "error": result.error,
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"{gid} [{record['prompt_version']} run {run}] valid={record['valid']} "
                  f"attempts={record['attempt_count']} error={record['error']}")
            print(f"   {record['answer']}\n")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python scripts/run_completeness.py answer_v1|answer_v2 [run_number]")
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) == 3 else 1)
