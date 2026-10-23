"""Fakes for the demo page tests. They replay REAL recorded answers and retrieved chunks from the Step 3.1
runs (results/generation), so the page is tested on the same shapes the live app will see.
Environment switches (set by the tests): DEMO_TEST_TRACE, DEMO_TEST_BM25_FAIL, DEMO_TEST_NO_KEY."""
import json
import os
from pathlib import Path

from rag.demo_ui import Deps
from rag.generate import GenerationResult

ROOT = Path(__file__).resolve().parents[1]
RECORDED = ("answer_v1_dev.judged.jsonl", "answer_v1_holdout.judged.jsonl")


def recorded_by_question():
    records = {}
    for name in RECORDED:
        path = ROOT / "results" / "generation" / name
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                record = json.loads(line)
                records[record["question"]] = record
    return records


def to_hits(record):
    return [{"chunk_id": c["chunk_id"], "doc_id": c["doc_id"], "certification": c["certification"],
             "section": "part 1", "text": c["text"], "similarity": 0.5} for c in record["contexts"]]


def make_deps():
    records = recorded_by_question()

    def retrieve(question):
        return to_hits(records[question])

    def generate(question, hits, correction=None):
        record = records[question]
        return GenerationResult(record["answer"], record["citations"], record["refused"], "answer_v1",
                                model="fake-model", input_tokens=1900, output_tokens=95, latency_ms=1500.0,
                                chunk_ids=[h["chunk_id"] for h in hits])

    def vector_search(question, k):
        return to_hits(records[question])

    def bm25_search(question, k):
        if os.environ.get("DEMO_TEST_BM25_FAIL"):
            raise RuntimeError("bm25 index unavailable")
        extra = {"chunk_id": "EXTRA::v1::0", "doc_id": "EXTRA", "certification": "Certified",
                 "section": "part 1", "text": "Extra Doc (EXTRA) | part 1\nbody", "score": 3.0}
        # Keyword search finds the extra chunk first and misses the last chunks vector search found.
        return [extra] + to_hits(records[question])[:3]

    no_key = bool(os.environ.get("DEMO_TEST_NO_KEY"))
    return Deps(retrieve=retrieve, generate=generate, vector_search=vector_search, bm25_search=bm25_search,
                key_present=lambda: not no_key, trace_path=Path(os.environ["DEMO_TEST_TRACE"]))
