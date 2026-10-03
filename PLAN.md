# PLAN.md: 3-day build plan

Each `###` step becomes one GitHub issue (label = its day). Tick boxes as you go.
Already done before Claude Code: repo skeleton, `requirements.txt`, `.gitignore`, `.env.example`, `docs/decisions.md`, `scripts/smoke_test.py`.

---

## Day 0: GitHub setup (30 min, first session only)

### 0.1 Git and GitHub basics
- [ ] Check `git --version` and `gh --version` (install Git for Windows and GitHub CLI if missing)
- [ ] `git config` name and email; `gh auth login` (browser login)
- [ ] `git init`, first commit of the skeleton (check that `.env` is NOT tracked)
- [ ] `gh repo create kpi-governance-rag --private --source . --push`
- [ ] Create the labels `day-1`, `day-2`, `day-3` and one issue per step below; create a Project board (To do / Doing / Done)
- Explain-it-back: what is the difference between commit and push? Why is `.env` in `.gitignore`?

---

## Day 1: Data to searchable index

### 1.1 Environment + smoke test
- [ ] venv, torch CPU, `pip install -r requirements.txt`, `.env` filled
- [ ] `python scripts/smoke_test.py`: 384 dims, churn vs attrition similarity, token counts at temp 0 and 1
- Concepts: Token, Context window, Temperature, Embedding, Cosine similarity

### 1.2 Synthetic corpus (Low focus, Claude generates)
- [ ] `data/corpus_manifest.csv` (all docs with metadata)
- [ ] 20 KPI files, 15-row catalog CSV, 8 SOPs, PDFs via reportlab (2 with tables), 2 traps
- [ ] `scripts/check_corpus.py`: consistency checks (ids, owners, linked KPIs, dashboards, size under 1,800 chars)
- [ ] I skim 10 files and fix anything odd
- Concepts: Hallucination (via consistency checks), Structured output

### 1.3 Loaders
- [ ] `src/rag/ingest.py`: markdown + YAML, CSV rows, PDF pages, written to `data/processed/documents.jsonl`
- [ ] Print counts by doc_type; inspect the PDF table text and note its quality in the log

### 1.4 Chunking V1 / V2 / V3 (High)
- [ ] `src/rag/chunking.py` + `tests/test_chunking.py` (caps, unique ids, overlap, V3 = 1 chunk per KPI)
- [ ] Stats table per variant: count, average tokens, max tokens
- Concepts: Chunking, Overlap, Parent-child retrieval (say "I would")

### 1.5 Embeddings + Chroma (High / Medium)
- [ ] `src/rag/index.py`: 3 collections, `python -m rag.index --variant all`
- [ ] Sanity queries: "how is churn calculated", "KPI-014", "who owns the customer 360 dashboard"
- Concepts: Vector store, HNSW, distance vs similarity

### 1.6 BM25 (High)
- [ ] `bm25_search()` with the code-preserving tokenizer and filters
- [ ] Compare against vector search on "KPI-014": which wins and why?
- Concepts: Keyword search, BM25, TF-IDF intuition

### 1.7 Golden set, part 1 (my homework, before any tuning)
- [ ] I write ~15 questions in `golden/golden_set.jsonl`, without looking at retrieval results

---

## Day 2: Retrieval quality + grounded answers (core day)

### 2.1 Golden set, part 2
- [ ] Claude drafts the remaining ~25 (traps, unanswerables, codes, typos, abbreviations); I review
- [ ] Validation script: 40 total, 8 unanswerable, 10 holdout, every expected doc_id exists

### 2.2 Retrieval eval (Very High)
- [ ] `eval/retrieval_eval.py`: recall@5, MRR@10 at document level, dev vs holdout, appended to `results/runs.csv`
- [ ] Work out MRR by hand for ranks 1, 3, missing, 2 before coding
- [ ] Baseline: V1 + vector

### 2.3 Hybrid RRF (Very High)
- [ ] Work one RRF example by hand (rank 1 vector + rank 4 BM25 = 1/61 + 1/64)
- [ ] `rrf()` + `hybrid_search()` + filter tests
- [ ] Grid: 3 variants x {vector, BM25, hybrid}, runs 1-9
- [ ] Error analysis of the 5 worst misses in `results/experiments.md`

### 2.4 Reranker (Very High)
- [ ] `rerank()` with the cross-encoder; runs 10-11 on the best 2 configs; log the added latency
- Concepts: Bi-encoder vs cross-encoder, "retrieve wide, rerank narrow"

### 2.5 Grounded generation (High)
- [ ] `src/rag/llm.py`, `src/rag/generate.py`, `prompts/answer_v1.txt`
- [ ] Pydantic validation, citation check in code, one retry, refusal, `results/traces.jsonl`
- [ ] `src/rag/pipeline.py` + CLI `python -m rag.ask "..."`
- [ ] Hand test 6 questions: 2 definitions, 1 KPI code, Churn trap, 2 unanswerable
- Concepts: Grounding, Prompt versioning, Structured output

---

## Day 3: Evaluation, ship, demo

### 3.1 Generation eval (Very High)
- [ ] `eval/generation_eval.py` + judge prompts (correctness, faithfulness); test on 3 questions first
- [ ] Full run: best config vs baseline on all 40
- [ ] I hand-grade 10 answers **before** reading the judge; compute agreement
- [ ] Cost per query (note price and date used), p50 / p95 latency

### 3.2 FastAPI
- [ ] `api/app.py`: `POST /ask`, `GET /health`, models loaded once at startup; 20 calls for latency

### 3.3 Streamlit demo
- [ ] `app/streamlit_app.py`: question box, filters, config picker, **Retrieval Inspector** table (vector rank, BM25 rank, RRF score, rerank score), answer with clickable citations, tokens and latency
- [ ] Record a 2-min demo video (question that works, Churn trap, refusal)

### 3.4 Production architecture (Very High, my extension)
- [ ] `docs/production_architecture.md` + diagram: AWS mapping (Bedrock, OpenSearch / Bedrock Knowledge Bases, Lambda / ECS, S3), ingestion pipeline, access control via metadata, caching, guardrails, observability, eval in CI, cost controls, failure modes

### 3.5 Write-up and publish
- [ ] Final `results/experiments.md`: grid, generation table, cost and latency, 3-5 findings, failures, limits
- [ ] README (what, problem, diagram, how to run, results, trade-offs, limits)
- [ ] Secrets check, then make the repo public
- [ ] Interview line filled with my own numbers (brief section 14)

---

## Cut list (if behind)
- Must: corpus, 3 chunkings, vector + BM25 + hybrid, golden set, retrieval grid, grounded answers with citations and refusal, Streamlit demo
- Should: reranker, judge eval, hand grades, FastAPI, cost and latency
- Could (later): query rewriting, parent-child retrieval, the bge query-prefix test, Ragas
