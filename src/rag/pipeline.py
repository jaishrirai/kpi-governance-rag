"""
Step 2.5, Stage 3: the end-to-end pipeline.  retrieve -> generate -> validate -> log.

ask() is glue only. It adds no policy: it never edits, hides or retries an answer. If citation
validation fails, the answer is returned as the model gave it, with the problems listed, and the
failure is written to the trace. Retries and governance checks come in later steps.

Retrieval and generation are passed in as functions, so tests run with fakes and no network.
make_retriever() builds the real one (vector search on chunking V1, top 5). Run from the repo
root with PYTHONPATH=src, because the index and trace paths are relative.

One JSON line per call is appended to results/traces.jsonl (also on failure, with an "error").
"""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from rag import generate as gen
from rag.validate import validate_citations

TRACES = Path("results/traces.jsonl")
DEFAULT_VARIANT = "v1"
DEFAULT_K = 5
RETRIEVER_NAME = "vector"


@dataclass
class PipelineResult:
    question: str
    answer: str = ""
    citations: list = field(default_factory=list)
    refused: bool = False
    valid: bool = False  # False when there was an error or citation validation failed
    problems: list = field(default_factory=list)
    chunk_ids: list = field(default_factory=list)
    generation: object = None  # the GenerationResult, None on error
    retrieval_ms: float = 0.0
    error: str = None


def make_retriever(variant=DEFAULT_VARIANT, k=DEFAULT_K):
    """Real retriever: embed the question, vector search the chosen chunking. Loads the model once."""
    import chromadb

    from rag import index

    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    return lambda question: index.search(client, variant, question, embed, k=k)


def write_trace(record, path=TRACES):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def ask(question, retrieve_fn, generate_fn=gen.generate, trace_path=TRACES,
        variant=DEFAULT_VARIANT, k=DEFAULT_K):
    """Run one question through retrieve -> generate -> validate and log a trace."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "question": question,
        "variant": variant,
        "retriever": RETRIEVER_NAME,
        "k": k,
        "prompt_version": gen.PROMPT_VERSION,
        "error": None,
    }
    result = PipelineResult(question=question)

    def finish():
        record.update(valid=result.valid, problems=result.problems, chunk_ids=result.chunk_ids,
                      retrieval_ms=round(result.retrieval_ms, 1))
        write_trace(record, trace_path)
        return result

    start = time.perf_counter()
    try:
        hits = retrieve_fn(question)
    except Exception as error:  # logged and reported; the trace shows which stage failed
        result.retrieval_ms = (time.perf_counter() - start) * 1000
        result.error = record["error"] = f"retrieval failed: {type(error).__name__}: {error}"
        return finish()
    result.retrieval_ms = (time.perf_counter() - start) * 1000
    result.chunk_ids = [hit["chunk_id"] for hit in hits]

    try:
        generation = generate_fn(question, hits)
    except Exception as error:
        result.error = record["error"] = f"generation failed: {type(error).__name__}: {error}"
        return finish()

    result.generation = generation
    result.answer, result.citations, result.refused = generation.answer, generation.citations, generation.refused
    result.problems = validate_citations(generation.citations, generation.refused, result.chunk_ids)
    result.valid = not result.problems
    record.update(
        model=generation.model, answer=generation.answer, citations=generation.citations,
        refused=generation.refused, input_tokens=generation.input_tokens,
        output_tokens=generation.output_tokens, thinking_tokens=generation.thinking_tokens,
        generation_ms=round(generation.latency_ms, 1),
    )
    return finish()
