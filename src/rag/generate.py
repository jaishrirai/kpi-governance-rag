"""
Step 2.5: grounded generation. retrieved chunks -> Gemini -> structured answer.

Pieces:
  load_prompt     reads the versioned system prompt from prompts/<version>.txt
  format_context  turns retrieved hits into labelled context blocks the model can cite
  parse_answer    checks the model's JSON has the right shape (answer, citations, refused)
  generate        runs the three steps above plus one model call

Deliberately NOT here yet: checking that cited chunk IDs were really retrieved, governance
checks, retries on bad output, logging. A citation proves a chunk was in the context, not that
it supports the claim; support is judged separately in the evaluation step.

generate() takes the model call as a parameter (default llm.complete) so tests can pass a fake.
Hits come from index.search, hybrid_search or rerank: all keep chunk_id, doc_id, certification, text.
"""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from rag import llm

PROMPT_VERSION = "answer_v1"
PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"
REFUSAL_MESSAGE = "I could not find this in the governed documents."


class GenerationError(ValueError):
    """The model's reply was not the JSON shape the prompt asked for."""


@dataclass
class GenerationResult:
    answer: str
    citations: list
    refused: bool
    prompt_version: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0
    latency_ms: float = 0.0
    chunk_ids: list = field(default_factory=list)  # what the model was shown, in order
    raw_text: str = ""


def load_prompt(version=PROMPT_VERSION, prompts_dir=PROMPTS_DIR):
    return (Path(prompts_dir) / f"{version}.txt").read_text(encoding="utf-8").strip()


def format_context(hits):
    """One block per chunk: '[chunk_id] doc_id | certification' then the chunk text.
    Order is kept as retrieved (governance ordering comes in a later step)."""
    blocks = []
    for hit in hits:
        label = f"[{hit['chunk_id']}] {hit['doc_id']} | {hit.get('certification') or 'unknown status'}"
        blocks.append(f"{label}\n{hit['text'].strip()}")
    return "\n\n".join(blocks)


def build_user_message(question, hits, correction=None):
    message = f"Question: {question}\n\nContext chunks:\n\n{format_context(hits)}"
    return f"{message}\n\n{correction}" if correction else message


def build_correction(invalid_ids, valid_ids, consistency=False):
    """Retry message: name the rejected IDs and the only IDs the model may cite.
    consistency=True adds the refused/citations rule, for answers that broke it."""
    lines = [
        f"These citation IDs were invalid: [{', '.join(invalid_ids) or 'none'}].",
        f"You may cite only these retrieved IDs: [{', '.join(valid_ids) or 'none'}].",
    ]
    if consistency:
        lines.append("Your refused flag and citations did not agree. If you cannot answer from the "
                     "context, set refused to true and give no citations. If you answer, cite at "
                     "least one retrieved ID.")
    return "\n".join(lines)


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_answer(text):
    """Return (answer, citations, refused) from the model's JSON, or raise GenerationError."""
    cleaned = _FENCE.sub("", text.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise GenerationError(f"Reply is not valid JSON ({error}): {text[:200]!r}") from error
    if not isinstance(data, dict):
        raise GenerationError(f"Reply JSON is not an object: {text[:200]!r}")
    answer, citations, refused = data.get("answer"), data.get("citations"), data.get("refused")
    if not isinstance(answer, str):
        raise GenerationError("'answer' must be a string")
    if not isinstance(citations, list) or not all(isinstance(c, str) for c in citations):
        raise GenerationError("'citations' must be a list of strings")
    if not isinstance(refused, bool):
        raise GenerationError("'refused' must be true or false")
    return answer, citations, refused


def generate(question, hits, complete_fn=llm.complete, prompt_version=PROMPT_VERSION, correction=None):
    """Answer the question from the hits only. No hits means refuse without calling the model."""
    if not hits:
        return GenerationResult(REFUSAL_MESSAGE, [], True, prompt_version)
    result = complete_fn(load_prompt(prompt_version), build_user_message(question, hits, correction))
    answer, citations, refused = parse_answer(result.text)
    return GenerationResult(
        answer=answer,
        citations=citations,
        refused=refused,
        prompt_version=prompt_version,
        model=result.model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        thinking_tokens=result.thinking_tokens,
        latency_ms=result.latency_ms,
        chunk_ids=[hit["chunk_id"] for hit in hits],
        raw_text=result.text,
    )
