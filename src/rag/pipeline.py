"""
Step 2.5: the end-to-end pipeline.  retrieve -> generate -> validate (retry once) -> log.

ask() is glue with one policy. It retries once, and only for citation provenance or consistency
failures: a cited ID that was not retrieved, or refused=True with citations, or answering with none.
If the first answer fails that check, the model is asked once more, naming the rejected IDs and listing
the only IDs it may cite. If the second answer also fails, the answer is replaced by the refusal
sentence (policy_refusal=True). Every model answer, rejected ones included, is kept in attempts and
written to the trace. Support, completeness, retrieval and governance failures are never retried.
A retrieval or generation error, including an error on the retry, ends the call with error set.

Retrieval and generation are passed in as functions, so tests run with fakes and no network.
make_retriever() builds the real one (vector search on chunking V1, top 5). Run from the repo root
with PYTHONPATH=src, because the index and trace paths are relative.

One JSON line per call is appended to results/traces.jsonl (also on failure, with an "error").
"""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from rag import generate as gen
from rag.validate import unknown_citations, validate_citations

TRACES = Path("results/traces.jsonl")
DEFAULT_VARIANT = "v1"
DEFAULT_K = 5
RETRIEVER_NAME = "vector"
MAX_ATTEMPTS = 2  # the first answer plus one retry after a failed citation check


@dataclass
class PipelineResult:
    question: str
    answer: str = ""
    citations: list = field(default_factory=list)
    refused: bool = False
    valid: bool = False  # False on error, failed citation check, or policy refusal
    problems: list = field(default_factory=list)  # problems of the last model answer
    chunk_ids: list = field(default_factory=list)
    generation: object = None  # the last GenerationResult, None on error
    retrieval_ms: float = 0.0
    error: str = None
    attempts: list = field(default_factory=list)  # every model answer, rejected ones included
    policy_refusal: bool = False  # True when the refusal replaced an answer that failed twice


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


def _inconsistent(citations, refused):
    """True when refused and the citations disagree (refused with citations, or answering with none)."""
    return (refused and bool(citations)) or (not refused and not citations)


def ask(question, retrieve_fn, generate_fn=gen.generate, trace_path=TRACES,
        variant=DEFAULT_VARIANT, k=DEFAULT_K):
    """Run one question through retrieve -> generate -> validate (retry once) and log a trace."""
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
                      retrieval_ms=round(result.retrieval_ms, 1), attempts=result.attempts,
                      attempt_count=len(result.attempts), policy_refusal=result.policy_refusal)
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

    correction = None
    generation = None
    for number in range(1, MAX_ATTEMPTS + 1):
        try:
            if correction is None:
                generation = generate_fn(question, hits)
            else:
                generation = generate_fn(question, hits, correction=correction)
        except Exception as error:
            # An error on the retry is reported as it is. There is no third call: MAX_ATTEMPTS is the limit.
            stage = "generation failed" if number == 1 else "retry generation failed"
            result.error = record["error"] = f"{stage}: {type(error).__name__}: {error}"
            return finish()

        problems = validate_citations(generation.citations, generation.refused, result.chunk_ids)
        result.attempts.append({
            "attempt": number, "answer": generation.answer, "citations": generation.citations,
            "refused": generation.refused, "problems": problems, "model": generation.model,
            "input_tokens": generation.input_tokens, "output_tokens": generation.output_tokens,
            "thinking_tokens": generation.thinking_tokens, "generation_ms": round(generation.latency_ms, 1),
        })
        if not problems:
            break
        if number < MAX_ATTEMPTS:
            correction = gen.build_correction(
                unknown_citations(generation.citations, result.chunk_ids), result.chunk_ids,
                consistency=_inconsistent(generation.citations, generation.refused))

    result.generation = generation
    result.problems = result.attempts[-1]["problems"]
    if result.problems:
        result.policy_refusal = True
        result.answer, result.citations, result.refused = gen.REFUSAL_MESSAGE, [], True
        result.valid = False
    else:
        result.answer, result.citations, result.refused = (
            generation.answer, generation.citations, generation.refused)
        result.valid = True
    record.update(
        model=generation.model, answer=result.answer, citations=result.citations, refused=result.refused,
        input_tokens=generation.input_tokens, output_tokens=generation.output_tokens,
        thinking_tokens=generation.thinking_tokens, generation_ms=round(generation.latency_ms, 1),
    )
    return finish()
