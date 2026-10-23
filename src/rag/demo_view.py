"""
Step 3.3: pure helpers for the Streamlit demo. No Streamlit, no network, no model here, so every
function is tested with fakes (tests/test_demo_view.py).

What the demo shows, and what it must not blur:
  - The ANSWER always comes from the default path: vector search, chunking V1, top 5, prompt answer_v1.
  - BM25 and hybrid (RRF) are COMPARISON ONLY, shown under "How it works". They never feed the answer.
  - A failure in the comparison must never break the answer: compare_retrieval() catches everything.

Run from the repo root with PYTHONPATH=src, like the other modules.
"""
import re
from dataclasses import dataclass

from rag.hybrid import HYBRID_FETCH_DEPTH, fuse_hits

ANSWER_VARIANT = "v1"
ANSWER_K = 5
NOT_IN_TOP = f"not in top {HYBRID_FETCH_DEPTH}"
UNAVAILABLE = "unavailable"

# Chunk text starts with "{title} ({doc_id}) | {section}" (decision 8 in docs/decisions.md).
TITLE_RE = re.compile(r"^(?P<title>.+?) \((?P<doc_id>[A-Za-z0-9-]+)\) \|")
CITATION_GROUP_RE = re.compile(r"\[([^\[\]]+)\]")

EXAMPLES = [
    ("Customer churn: how it is calculated and where it is used",
     "Customer churn rate - how is that calculated? What dashboards use it?"),
    ("How a KPI becomes Certified (a process question)",
     "How does a KPI go from Provisional to Certified?"),
    ("Can a Provisional KPI go on the Executive pack? (a governance rule)",
     "Can I put Basket Size on the Executive KPI Pack?"),
    ("Two sources disagree (certified rule versus an informal FAQ)",
     "How many days do we use to count an Active Customer?"),
    ("Old churn definition (a deprecated source)",
     "What did the old churn rate (v1) measure and why was it replaced?"),
    ("A question the documents cannot answer",
     "Who is the CEO of Kestrel Retail Group?"),
    ("A known limit: the KPI-020 owner",
     "Who owns KPI-020 and what has to be fixed before it can be certified?"),
]

STATUS_TEXT = {
    "answered": ("Answered from governed documents", ""),
    "not_found": ("Not found in the governed documents",
                  "The assistant does not guess when the documents do not say. "
                  "Try rephrasing, or ask the Data Governance team."),
    "withheld": ("Answer withheld",
                 "The answer's sources could not be verified, so it was not shown."),
    "error": ("Something went wrong", ""),
}


def doc_title(hit):
    """Readable document title from the chunk header; the doc id if the header is missing."""
    match = TITLE_RE.match(hit.get("text", "").strip())
    return match.group("title") if match else hit.get("doc_id", hit.get("chunk_id", "?"))


def classify(result):
    """One of: answered, not_found, withheld, error."""
    if result.error:
        return "error"
    if result.policy_refusal:
        return "withheld"
    if result.refused:
        return "not_found"
    if not result.valid:
        return "withheld"
    return "answered"


def friendly_error(message):
    """One plain line for the user. The technical text stays in the builder view."""
    text = (message or "").lower()
    if "api_key" in text:
        return "No Gemini key was found. Add GEMINI_API_KEY to your .env file."
    if "429" in text or "quota" in text or "resource_exhausted" in text:
        return "The model is busy or the free quota is used up. Wait a minute and try again."
    if text.startswith("retrieval failed"):
        return "The document search failed. Check that the search index has been built."
    return "Could not get an answer from the model. Check your key and connection, then try again."


def number_citations(answer, cited_ids):
    """Replace bracketed chunk IDs in the answer with numbered tags like [1] that match the Sources list.
    The order of cited_ids decides the numbers. Returns (text, {chunk_id: number})."""
    numbers = {chunk_id: n for n, chunk_id in enumerate(dict.fromkeys(cited_ids), start=1)}

    def replace(match):
        ids = [part.strip() for part in match.group(1).split(",")]
        if not ids or any(i not in numbers for i in ids):
            return match.group(0)  # not a citation group: leave it alone
        return " ".join(f"[{numbers[i]}]" for i in dict.fromkeys(ids))

    return CITATION_GROUP_RE.sub(replace, answer), numbers


def source_cards(cited_ids, hits):
    """One card per cited chunk, in citation order: number, title, section, certification, chunk id."""
    by_id = {hit["chunk_id"]: hit for hit in hits}
    cards = []
    for number, chunk_id in enumerate(dict.fromkeys(cited_ids), start=1):
        hit = by_id.get(chunk_id)
        if hit is None:
            continue
        cards.append({"number": number, "title": doc_title(hit), "section": hit.get("section", ""),
                      "certification": hit.get("certification", ""), "chunk_id": chunk_id})
    return cards


def non_certified_note(cards):
    """The yellow governance note, or None when every cited source is Certified."""
    weak = [c for c in cards if c["certification"] != "Certified"]
    if not weak:
        return None
    names = ", ".join(f"{c['title']} ({c['certification'] or 'unknown'})" for c in weak)
    return f"This answer uses a source that is not Certified: {names}."


def usage_line(result):
    """Tokens and time on one line, or empty when the model was not called."""
    g = result.generation
    if g is None:
        return ""
    seconds = (result.retrieval_ms + g.latency_ms) / 1000
    return f"Tokens: {g.input_tokens} in, {g.output_tokens} out. Time: {seconds:.1f} s."


def inspector_rows(answer_hits, bm25_hits, fused_hits, cited_ids):
    """Rows for the 'How it works' table. The rows are the answer's own five vector hits, so the table
    matches what the model was shown. BM25 and Hybrid ranks come from the comparison lists; pass None
    for both when the comparison failed, and those cells say 'unavailable'."""
    bm25_rank = None if bm25_hits is None else {h["chunk_id"]: n for n, h in enumerate(bm25_hits, start=1)}
    hybrid_rank = None if fused_hits is None else {h["chunk_id"]: n for n, h in enumerate(fused_hits, start=1)}
    cited = set(cited_ids)
    rows = []
    for rank, hit in enumerate(answer_hits, start=1):
        chunk_id = hit["chunk_id"]
        rows.append({
            "Document": doc_title(hit),
            "Status": hit.get("certification", ""),
            "Used in answer": "Yes" if chunk_id in cited else "",
            "Vector rank": rank,
            "BM25 rank": UNAVAILABLE if bm25_rank is None else bm25_rank.get(chunk_id, NOT_IN_TOP),
            "Hybrid (RRF) rank": UNAVAILABLE if hybrid_rank is None else hybrid_rank.get(chunk_id, NOT_IN_TOP),
            "Chunk": chunk_id,
        })
    return rows


def hybrid_extra(answer_hits, fused_hits, k=ANSWER_K):
    """Chunks hybrid's top k holds that the answer's vector top k does not."""
    shown = {hit["chunk_id"] for hit in answer_hits}
    return [hit for hit in fused_hits[:k] if hit["chunk_id"] not in shown]


def extra_line(extra):
    if not extra:
        return "Hybrid search would have returned the same five passages."
    names = "; ".join(f"{doc_title(h)}, {h.get('certification') or 'unknown'}" for h in extra)
    return f"Hybrid search would also have surfaced: {names}."


@dataclass
class Comparison:
    ok: bool
    rows: list = None
    extra: list = None
    error: str = ""


def compare_retrieval(question, answer_hits, cited_ids, vector_search, bm25_search, depth=HYBRID_FETCH_DEPTH):
    """Read-only comparison. vector_search(question, k) and bm25_search(question, k) return hit lists.
    Never raises: any failure becomes Comparison(ok=False), and the answer is untouched."""
    try:
        vector_hits = vector_search(question, depth)
        bm25_hits = bm25_search(question, depth)
        fused = fuse_hits(vector_hits, bm25_hits)
        return Comparison(True, inspector_rows(answer_hits, bm25_hits, fused, cited_ids),
                          hybrid_extra(answer_hits, fused))
    except Exception as error:  # the comparison is optional by design
        return Comparison(False, error=f"{type(error).__name__}: {error}")


def safe_markdown(text):
    """Stop '$' from turning answer text into math in Streamlit markdown."""
    return text.replace("$", "\\$")
