"""
Step 3.3: launcher for the demo. From the repo root:
  $env:PYTHONPATH = "src"
  streamlit run app/streamlit_app.py

Needs data/index (python -m rag.index --variant all) and GEMINI_API_KEY in .env.
All page logic is in src/rag/demo_ui.py and src/rag/demo_view.py.
"""
import os

import streamlit as st

from rag import demo_ui
from rag import demo_view as view


demo_ui.configure_page()  # first Streamlit call: the spinner below would otherwise come first


@st.cache_resource(show_spinner="Loading the search index and model (first time only)...")
def load_deps():
    from dotenv import load_dotenv

    load_dotenv()
    import chromadb

    from rag import bm25, index

    client = chromadb.PersistentClient(path="data/index")
    embed = index.make_embedder(index.load_model())
    variant = view.ANSWER_VARIANT
    try:
        bm25.build_index(variant)  # build the keyword index once; the comparison reuses it
    except Exception:
        pass  # the comparison reports its own failure; the answer path does not need BM25
    return demo_ui.Deps(
        retrieve=lambda question: index.search(client, variant, question, embed, k=view.ANSWER_K),
        vector_search=lambda question, k: index.search(client, variant, question, embed, k=k),
        bm25_search=lambda question, k: bm25.bm25_search(variant, question, k=k),
        key_present=lambda: bool(os.environ.get("GEMINI_API_KEY")),
    )


try:
    deps = load_deps()
except Exception as error:  # missing index, missing packages, or the model could not load
    demo_ui.run_error_page("Build the search index first with `python -m rag.index --variant all`, "
                           "and run this from the repo root with `PYTHONPATH=src`.",
                           f"{type(error).__name__}: {error}")
else:
    demo_ui.run_app(deps)
