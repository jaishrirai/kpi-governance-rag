"""
Step 3.3: the Streamlit page. Thin on purpose: all decisions live in rag.demo_view (tested with fakes).

Answer path: pipeline.ask() with vector search on chunking V1, top 5, prompt answer_v1. The same path the
evaluation used. BM25 and hybrid (RRF) appear only under "Show how it works", as read-only comparison.

run_app(deps) takes its dependencies as an argument, so tests can run the page with fakes.
Launch from the repo root (see app/streamlit_app.py):
  $env:PYTHONPATH = "src"
  streamlit run app/streamlit_app.py
Demo questions are logged to results/demo_traces.jsonl (git-ignored), never to results/traces.jsonl.
"""
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

from rag import demo_view as view
from rag import generate as gen
from rag import pipeline

DEMO_TRACES = Path("results/demo_traces.jsonl")
TITLE = "KPI Governance Assistant"
DESCRIPTION = ("Ask about Kestrel Retail Group's KPIs, dashboards and data policies. You get an answer with "
               "the documents it came from, or a clear 'not found' if the documents do not cover it.")
RANK_COLUMNS = ["Vector rank", "BM25 rank", "Hybrid (RRF) rank"]
CERT_COLOURS = {"Certified": "green", "Provisional": "orange", "Deprecated": "red"}
EXAMPLE_PROMPT = "Choose an example, or type your own question below"


@dataclass
class Deps:
    retrieve: object                  # question -> hits (the answer path: vector, V1, top 5)
    generate: object = gen.generate   # (question, hits, correction=None) -> GenerationResult
    vector_search: object = None      # (question, k) -> hits, comparison only
    bm25_search: object = None        # (question, k) -> hits, comparison only
    key_present: object = None        # () -> bool; None means "do not check"
    trace_path: Path = DEMO_TRACES


def ask_question(question, deps):
    """Run the answer path, then the read-only comparison. The comparison cannot affect the answer."""
    captured = {}

    def retrieve(text):
        captured["hits"] = deps.retrieve(text)
        return captured["hits"]

    result = pipeline.ask(question, retrieve, generate_fn=deps.generate, trace_path=deps.trace_path)
    hits = captured.get("hits", [])
    comparison = None
    if deps.vector_search and deps.bm25_search and hits:
        comparison = view.compare_retrieval(question, hits, result.citations, deps.vector_search, deps.bm25_search)
    return {"question": question, "result": result, "hits": hits, "comparison": comparison}


def raw_record(state):
    result = state["result"]
    generation = result.generation
    return {
        "question": state["question"], "status": view.classify(result), "answer": result.answer,
        "citations": result.citations, "chunk_ids": result.chunk_ids, "valid": result.valid,
        "problems": result.problems, "policy_refusal": result.policy_refusal,
        "attempts": len(result.attempts), "retrieval_ms": round(result.retrieval_ms, 1),
        "model": getattr(generation, "model", ""), "prompt_version": getattr(generation, "prompt_version", ""),
        "error": result.error,
    }


def render_sources(cards):
    st.markdown("**Sources**")
    for card in cards:
        colour = CERT_COLOURS.get(card["certification"], "gray")
        status = card["certification"] or "unknown"
        section = f" · {card['section']}" if card["section"] else ""
        st.markdown(f"**[{card['number']}] {card['title']}**{section} · :{colour}[{status}] · `{card['chunk_id']}`")


def render_answer(state, builder):
    result = state["result"]
    kind = view.classify(result)
    badge, note = view.STATUS_TEXT[kind]
    {"answered": st.success, "not_found": st.info, "withheld": st.warning, "error": st.error}[kind](badge)
    if kind == "answered":
        text, _ = view.number_citations(result.answer, result.citations)
        st.markdown(view.safe_markdown(text))
        cards = view.source_cards(result.citations, state["hits"])
        if cards:
            render_sources(cards)
        governance_note = view.non_certified_note(cards)
        if governance_note:
            st.warning(governance_note)
    elif kind == "error":
        st.markdown(view.friendly_error(result.error))
        if builder:
            with st.expander("Technical detail"):
                st.code(result.error or "")
    else:
        st.markdown(note)
    usage = view.usage_line(result)
    if usage:
        st.caption(usage)


def render_how_it_works(state):
    st.subheader("How it works")
    st.markdown("The five passages retrieved by the default vector search, with their retrieval details.")
    st.info("The answer above was generated using the V1 vector retriever. "
            "BM25 and hybrid (RRF) are shown for comparison only.")
    comparison = state["comparison"]
    cited = state["result"].citations
    if comparison is not None and comparison.ok:
        rows, extra = comparison.rows, comparison.extra
    else:
        rows = view.inspector_rows(state["hits"], None, None, cited)
        extra = None
        if comparison is not None:
            st.caption("The BM25 and hybrid comparison is unavailable for this question. The answer is not affected.")
    if rows:
        show_chunks = st.checkbox("Show chunk IDs", value=False)
        frame = pd.DataFrame(rows)
        for column in RANK_COLUMNS:  # text, so numbers and "not in top 50" line up the same way
            frame[column] = frame[column].astype(str)
        if not show_chunks:
            frame = frame.drop(columns=["Chunk"])
        st.dataframe(frame, hide_index=True)
        if extra is not None:
            st.caption(view.extra_line(extra))
    else:
        st.caption("No passages were retrieved.")
    with st.expander("Raw record"):
        st.json(raw_record(state))


def use_example():
    chosen = st.session_state.get("example")
    for label, question in view.EXAMPLES:
        if label == chosen:
            st.session_state["question"] = question


def configure_page():
    """Must be the first Streamlit call of the script, so the launcher calls it before loading anything."""
    st.set_page_config(page_title=TITLE, layout="wide")


def run_app(deps):
    with st.sidebar:
        st.header("Options")
        builder = st.toggle("Show how it works", value=False)
        st.caption("Search: vector, V1 chunking, top 5 passages. Prompt: answer_v1.")
        st.caption("Built as a portfolio project. Answers come only from the governed documents, "
                   "and every answer cites its sources or says it cannot find them.")

    st.title(TITLE)
    st.write(DESCRIPTION)
    st.caption("Demo built on fictional company documents.")

    labels = [label for label, _ in view.EXAMPLES]
    st.selectbox("Try an example question", [EXAMPLE_PROMPT] + labels, key="example", on_change=use_example)
    st.text_area("Your question", key="question", height=80,
                 placeholder="For example: Who owns the Customer 360 Dashboard?")

    if st.button("Ask", type="primary"):
        question = st.session_state.get("question", "").strip()
        if not question:
            st.warning("Type a question first.")
        elif deps.key_present is not None and not deps.key_present():
            st.session_state["state"] = None
            st.error(view.friendly_error("GEMINI_API_KEY is not set"))
        else:
            with st.spinner("Searching the documents and writing the answer..."):
                st.session_state["state"] = ask_question(question, deps)

    state = st.session_state.get("state")
    if state:
        st.divider()
        st.caption(f"Question: {state['question']}")
        render_answer(state, builder)
        if builder:
            render_how_it_works(state)


def run_error_page(message, detail=""):
    """Shown when the search index or model could not be loaded."""
    st.title(TITLE)
    st.error("The assistant could not start.")
    st.markdown(message)
    if detail:
        with st.expander("Technical detail"):
            st.code(detail)
