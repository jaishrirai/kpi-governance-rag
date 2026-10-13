# Reading guide: what is in this repo and what to read

Read this file first. It tells you which files matter, in what order, and what to look for.
All paths are relative to the repo folder `P1 RAG\kpi-governance-rag`.

## How the project works in one line

Documents go in, get cut into chunks, get turned into numbers (embeddings) and keyword indexes (BM25),
then a question finds the best chunks, and the LLM answers only from those chunks, with citations.

## Read these files, in this order (about 30 minutes)

| # | File | What it is | What to look for |
| --- | --- | --- | --- |
| 1 | `PLAN.md` | The step-by-step map | Which steps are done and what is next |
| 2 | `docs/decisions.md` | The 7 choices we made, with reasons | Why local embeddings, Chroma and Gemini |
| 3 | `data/corpus_manifest.csv` | The master list of all 50 documents | Owner and status of each document. Everything is checked against this file |
| 4 | `data/raw/kpis/kpi-010_net_revenue_retention.md` | One KPI document | The YAML block at the top, then 7 `##` headings. Chunking cuts on these headings |
| 5 | `data/raw/kpis/kpi-007-v1_customer_churn_rate.md` | The deprecated trap | Its formula differs from v2 |
| 6 | `data/raw/faq/faq-01_customer_team_faq.md` | The informal trap | Defines Active Customer as 90 days. The certified definition is 30 days |
| 7 | `src/rag/ingest.py` | The loader | Read only the 4 small helper functions |
| 8 | `data/processed/documents.jsonl` | The loader's output: 50 documents, one per line | Generated and git-ignored, so it is not committed |
| 9 | `golden/golden_set.jsonl` | The 11 test questions written so far | What the system will be tested on |
| 10 | `docs/CONCEPTS.md` | Your own concept notes | Your words, to reuse in interviews |

## Files you do not need to read yet

- `.env`: holds the secret API key. Never open it in a shared place.
- `.venv/`: installed Python packages.
- `scripts/make_pdfs.py`, `scripts/check_corpus.py`: the generators and checker. Know they exist.
- `requirements.txt`, `.gitignore`, `.env.example`: setup files.

## Milestones and what each one produces

| Milestone | Steps | Output you can point to |
| --- | --- | --- |
| M1: searchable index | 1.4 chunking, 1.5 embeddings and Chroma, 1.6 BM25 | `src/rag/chunking.py`, `src/rag/index.py`, `src/rag/bm25.py`; three chunk files; a stats table |
| M2: retrieval scores | 2.1 golden set part 2, 2.2 metrics, 2.3 hybrid RRF | `eval/retrieval_eval.py`, `results/runs.csv` |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | `src/rag/rerank.py`, `src/rag/generate.py`, `results/traces.jsonl` |
| M4: shipped | 3.1 generation eval, 3.3 demo, 3.5 README | `results/experiments.md`, `app/streamlit_app.py`, `README.md` |

## Your routine after each milestone (about 25 minutes)

1. Claude explains the job of each new file in one sentence.
2. Claude walks through the 3 key lines.
3. You predict one output before anything runs.
4. You answer one question in your own words.
5. Claude saves a short walkthrough in `docs/walkthroughs/` and you answer 3 interview questions.
