"""Step 3.3: tests for rag.demo_view (pure helpers). No Streamlit, no network, no model."""
from types import SimpleNamespace

from rag import demo_view as view
from rag import pipeline
from rag.hybrid import HYBRID_FETCH_DEPTH


def hit(chunk_id, title="Some Doc", cert="Certified", section="part 1"):
    doc_id = chunk_id.split("::")[0]
    return {"chunk_id": chunk_id, "doc_id": doc_id, "section": section, "certification": cert,
            "text": f"{title} ({doc_id}) | {section}\nbody"}


def result(**kwargs):
    base = dict(error=None, policy_refusal=False, refused=False, valid=True, answer="a", citations=[],
                chunk_ids=[], generation=None, retrieval_ms=0.0)
    base.update(kwargs)
    return SimpleNamespace(**base)


# --- the answer path is the evaluated one ---

def test_demo_uses_the_default_answer_path():
    assert view.ANSWER_VARIANT == pipeline.DEFAULT_VARIANT == "v1"
    assert view.ANSWER_K == pipeline.DEFAULT_K == 5


# --- titles, status, errors ---

def test_doc_title_comes_from_the_chunk_header_with_a_fallback():
    assert view.doc_title(hit("POL-04::v1::0", title="KPI Glossary Summary")) == "KPI Glossary Summary"
    assert view.doc_title({"chunk_id": "X::v1::0", "doc_id": "X", "text": "no header here"}) == "X"


def test_classify_covers_every_case():
    assert view.classify(result()) == "answered"
    assert view.classify(result(refused=True)) == "not_found"
    assert view.classify(result(policy_refusal=True, refused=True)) == "withheld"
    assert view.classify(result(valid=False)) == "withheld"
    assert view.classify(result(error="generation failed: boom")) == "error"
    assert set(view.STATUS_TEXT) == {"answered", "not_found", "withheld", "error"}


def test_friendly_error_gives_one_plain_line_and_hides_the_stack():
    assert "GEMINI_API_KEY" in view.friendly_error("GEMINI_API_KEY is not set")
    assert "quota" in view.friendly_error("generation failed: ClientError: 429 RESOURCE_EXHAUSTED").lower()
    assert "index" in view.friendly_error("retrieval failed: ValueError: no collection").lower()
    other = view.friendly_error("generation failed: KeyError: 'x'")
    assert "KeyError" not in other and "Traceback" not in other


# --- citations ---

def test_number_citations_matches_the_sources_order():
    text, numbers = view.number_citations("A [POL-04::v1::1]. B [POL-04::v1::1, KPI-007::v1::0].",
                                          ["KPI-007::v1::0", "POL-04::v1::1"])
    assert numbers == {"KPI-007::v1::0": 1, "POL-04::v1::1": 2}
    assert text == "A [2]. B [2] [1]."


def test_number_citations_leaves_other_brackets_alone():
    text, _ = view.number_citations("See [note] and [KPI-001::v1::0].", ["KPI-001::v1::0"])
    assert text == "See [note] and [1]."
    text, _ = view.number_citations("Unknown [ZZZ::v1::0].", ["KPI-001::v1::0"])
    assert text == "Unknown [ZZZ::v1::0]."


def test_source_cards_follow_citation_order_and_skip_unknown_ids():
    hits = [hit("A::v1::0", "Doc A", "Certified"), hit("B::v1::0", "Doc B", "Provisional")]
    cards = view.source_cards(["B::v1::0", "A::v1::0", "GONE::v1::0"], hits)
    assert [(c["number"], c["title"], c["certification"]) for c in cards] == \
        [(1, "Doc B", "Provisional"), (2, "Doc A", "Certified")]


def test_non_certified_note_only_when_needed():
    certified = [{"title": "Doc A", "certification": "Certified"}]
    mixed = certified + [{"title": "FAQ", "certification": "Provisional"}]
    assert view.non_certified_note(certified) is None
    note = view.non_certified_note(mixed)
    assert "not Certified" in note and "FAQ (Provisional)" in note and "Doc A" not in note


def test_usage_line():
    assert view.usage_line(result()) == ""
    generation = SimpleNamespace(input_tokens=2000, output_tokens=90, latency_ms=2500)
    assert view.usage_line(result(generation=generation, retrieval_ms=500)) == "Tokens: 2000 in, 90 out. Time: 3.0 s."


def test_safe_markdown_escapes_dollar_signs():
    assert view.safe_markdown("costs $5 and $6") == "costs \\$5 and \\$6"


# --- the read-only comparison ---

ANSWER_HITS = [hit(f"D{i}::v1::0", f"Doc {i}") for i in range(1, 6)]


def test_inspector_rows_use_the_answers_own_hits():
    bm25_hits = [hit("D3::v1::0"), hit("D1::v1::0")]
    fused = [hit("D3::v1::0"), hit("D1::v1::0"), hit("D2::v1::0")]
    rows = view.inspector_rows(ANSWER_HITS, bm25_hits, fused, ["D2::v1::0"])
    assert [r["Vector rank"] for r in rows] == [1, 2, 3, 4, 5]
    assert "Rank" not in rows[0]
    assert rows[0]["BM25 rank"] == 2 and rows[2]["BM25 rank"] == 1
    assert rows[3]["BM25 rank"] == view.NOT_IN_TOP
    assert rows[1]["Hybrid (RRF) rank"] == 3 and rows[4]["Hybrid (RRF) rank"] == view.NOT_IN_TOP
    assert [r["Used in answer"] for r in rows] == ["", "Yes", "", "", ""]


def test_inspector_rows_say_unavailable_when_the_comparison_failed():
    rows = view.inspector_rows(ANSWER_HITS, None, None, [])
    assert {r["BM25 rank"] for r in rows} == {view.UNAVAILABLE}
    assert {r["Hybrid (RRF) rank"] for r in rows} == {view.UNAVAILABLE}


def test_hybrid_extra_lists_only_chunks_the_answer_did_not_see():
    fused = [hit("D1::v1::0"), hit("NEW::v1::0", "New Doc", "Provisional"), hit("D2::v1::0")]
    extra = view.hybrid_extra(ANSWER_HITS, fused)
    assert [h["chunk_id"] for h in extra] == ["NEW::v1::0"]
    assert view.extra_line(extra) == "Hybrid search would also have surfaced: New Doc, Provisional."
    two = view.extra_line([hit("A::v1::0", "Doc A", "Certified"), hit("B::v1::0", "Doc B", "Provisional")])
    assert two.endswith("Doc A, Certified; Doc B, Provisional.")
    assert "same five" in view.extra_line([])


def test_compare_retrieval_runs_with_the_fetch_depth_and_returns_rows():
    seen = {}

    def vector(question, k):
        seen["vector_k"] = k
        return ANSWER_HITS

    def bm25(question, k):
        seen["bm25_k"] = k
        return [hit("D2::v1::0")]

    comparison = view.compare_retrieval("q", ANSWER_HITS, [], vector, bm25)
    assert comparison.ok and len(comparison.rows) == 5
    assert seen == {"vector_k": HYBRID_FETCH_DEPTH, "bm25_k": HYBRID_FETCH_DEPTH}


def test_compare_retrieval_never_raises():
    def boom(question, k):
        raise RuntimeError("bm25 library missing")

    comparison = view.compare_retrieval("q", ANSWER_HITS, [], lambda q, k: ANSWER_HITS, boom)
    assert comparison.ok is False and "bm25 library missing" in comparison.error
    comparison = view.compare_retrieval("q", ANSWER_HITS, [], boom, lambda q, k: [])
    assert comparison.ok is False
