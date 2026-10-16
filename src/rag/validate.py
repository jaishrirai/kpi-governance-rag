"""
Step 2.5: citation validation (V1 contract). A pure function: no I/O, no model, no retrieval.

It checks the FORM of the model's output against what was actually retrieved:
  1. every cited ID must be one of the retrieved chunk IDs (exact match, no fuzzy matching)
  2. refused=True  -> no citations
  3. refused=False -> at least one citation

It does NOT check that a cited chunk supports the claim (that is judged in the evaluation step),
that the [ids] in the answer text match the citations list, or that every sentence is cited.
Returning a list of problems (instead of raising) lets the caller log all of them at once and
decide what to do, for example retry later.
"""


def validate_citations(citations, refused, retrieved_chunk_ids):
    """Return a list of problem strings. An empty list means the output follows the contract.

    citations: list of cited chunk IDs from the model.  refused: the model's refused flag.
    retrieved_chunk_ids: chunk IDs that were actually shown to the model.
    Only full chunk IDs are valid (KPI-006::v1::0), never document IDs (KPI-006).
    Duplicate citations are allowed. Each unknown ID is reported once, in first-seen order.
    """
    problems = []
    retrieved = set(retrieved_chunk_ids)
    for chunk_id in dict.fromkeys(citations):
        if chunk_id not in retrieved:
            problems.append(f"cited chunk was not retrieved: {chunk_id!r}")
    if refused and citations:
        problems.append("refused=True but citations were given")
    if not refused and not citations:
        problems.append("refused=False but no citations were given")
    return problems
