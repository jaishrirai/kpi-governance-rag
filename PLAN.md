# PLAN.md: 2-day build plan (revised after the 5-day break)

Each `###` step is one GitHub issue. Tick boxes as you go.
Already done before Claude Code: repo skeleton, `requirements.txt`, `.gitignore`, `.env.example`, `docs/decisions.md`, `scripts/smoke_test.py`.

**Time budget:** 2 days at 5-6 hours. Day 2 is a stretch (about 6h20 planned).
**Cut order if behind:** (1) demo video, (2) judge faithfulness score (keep correctness), (3) Streamlit extras.
**Changes vs the 3-day plan:**
- FastAPI (3.2) moved to the agents project. Streamlit calls the pipeline directly.
- Production architecture doc (3.4) written by me outside Claude Code. README links to it and has a ~10-line "how this would scale" section.
- Golden set: I write 10, Claude drafts 30 (still 40 total, 8 unanswerable, 10 holdout).
- Generation eval on 20 questions: all 10 holdout, at least 4 unanswerable, both traps. Only best config and baseline.
- Corpus skim is 5 files, done BEFORE I write my golden questions (no searches before the questions exist).
- Explain-it-back is 1 question on Low and Medium steps (1.3, 1.5, 3.3), 2-3 on High and Very High steps.
- **Wrap-up rule (required, every day):** batched CONCEPTS.md notes (5 lines each, my words, AIF-C01 domain tagged, approved by me) are written BEFORE the commit.
- Gemini key: get it before Day 1 so Step 2.5 is not blocked.

---

## Day 0: GitHub setup (done)

### 0.1 Git and GitHub basics
- [x] Check `git --version` and `gh --version` (install Git for Windows and GitHub CLI if missing)
- [x] `git config` name and email; `gh auth login` (browser login)
- [x] `git init`, first commit of the skeleton (check that `.env` is NOT tracked)
- [x] `gh repo create kpi-governance-rag --private --source . --push`
- [x] Create the labels `day-1`, `day-2`, `day-3` and one issue per step below; create a Project board (To do / Doing / Done)

---

## Day 1: Data to searchable index + golden set (about 5h35)

### 1.1 Environment + smoke test
- [x] venv, torch CPU, `pip install -r requirements.txt`, `.env` filled
- [x] `python scripts/smoke_test.py` Part A only: 384 dims, churn vs attrition similarity (LLM part moves to Step 2.5)

### 1.2 Synthetic corpus (Low focus, Claude generates) (0:40)
- [x] `data/corpus_manifest.csv` (all docs with metadata)
- [x] 20 KPI files, 15-row catalog CSV, 8 SOPs, PDFs via reportlab (2 with tables), 2 traps
- [x] Answer the 2 YAML/manifest questions (quoted `version: "1.4"`; glossary built from the manifest)
- [x] `scripts/check_corpus.py`: consistency checks (ids, owners, linked KPIs, dashboards, size under 1,800 chars)
- [x] I skim 5 files: Churn v1 trap, FAQ trap, one PDF with a table, the catalog CSV, one KPI file
- Concepts: Hallucination (via consistency checks), Structured output

### 1.7 Golden set, part 1 (my homework) (0:20)
- [x] After the skim and BEFORE any search or retrieval run, I write 10 questions in `golden/golden_set.jsonl` (done: 11 written, G-001 to G-011; Claude drafts 29 more in Step 2.1)

### 1.3 Loaders (0:35)
- [x] `src/rag/ingest.py`: markdown + YAML, CSV rows, PDF pages, written to `data/processed/documents.jsonl`
- [x] Print counts by doc_type; inspect the PDF table text and note its quality in the log

### 1.4 Chunking V1 / V2 / V3 (High) [Claude builds, you review and predict] (1:30)
- [x] `src/rag/chunking.py` + `tests/test_chunking.py` (caps, unique ids, overlap, V3 = 1 chunk per KPI)
- [x] Stats table per variant: count, average tokens, max tokens
- Concepts: Chunking, Overlap, Parent-child retrieval (say "I would")

### 1.5 Embeddings + Chroma (High / Medium) (0:45)
- [x] `src/rag/index.py`: 3 collections, `python -m rag.index --variant all`
- [x] Sanity queries: "how is churn calculated", "KPI-014", "who owns the customer 360 dashboard"
- Concepts: Vector store, HNSW, distance vs similarity

### 1.6 BM25 (High) [Claude builds, you review and predict] (1:15)
- [ ] `bm25_search()` with the code-preserving tokenizer and filters
- [ ] Compare against vector search on "KPI-014": which wins and why?
- Concepts: Keyword search, BM25, TF-IDF intuition

### 2.1 Golden set, part 2 (0:30, runs at the end of Day 1)
- [ ] Claude drafts 30 (traps, unanswerables, codes, typos, abbreviations); I review
- [ ] Validation script: 40 total, 8 unanswerable, 10 holdout, every expected doc_id exists

**Day 1 wrap-up:** batched CONCEPTS.md notes for the day, approved by me, then commits.

---

## Day 2: Retrieval grid, grounded answers, eval, demo, ship (about 6h20)

### 2.2 Retrieval eval (Very High) [YOU BUILD: metrics] (0:50)
- [ ] `eval/retrieval_eval.py`: recall@5, MRR@10 at document level, dev vs holdout, appended to `results/runs.csv`
- [ ] Work out MRR by hand for ranks 1, 3, missing, 2 before coding
- [ ] Baseline: V1 + vector

### 2.3 Hybrid RRF (Very High) [YOU BUILD] (1:20)
- [ ] Work one RRF example by hand (rank 1 vector + rank 4 BM25 = 1/61 + 1/64)
- [ ] `rrf()` + `hybrid_search()` + filter tests
- [ ] Grid: 3 variants x {vector, BM25, hybrid}, runs 1-9
- [ ] Error analysis of the 3 worst misses in `results/experiments.md`

### 2.4 Reranker (Very High) [YOU BUILD] (0:40)
- [ ] `rerank()` with the cross-encoder; runs 10-11 on the best 2 configs; log the added latency
- Concepts: Bi-encoder vs cross-encoder, "retrieve wide, rerank narrow"

### 2.5 Grounded generation (High) [YOU BUILD: citation check] (1:10)
- [ ] `GEMINI_API_KEY`, `LLM_MODEL`, `JUDGE_MODEL` in `.env`, `pip install google-genai`
- [ ] LLM smoke test: same question at temperature 0 and 1, print token counts
- [ ] `src/rag/llm.py`, `src/rag/generate.py`, `prompts/answer_v1.txt`
- [ ] Pydantic validation, citation check in code, one retry, refusal, `results/traces.jsonl`
- [ ] `src/rag/pipeline.py` + CLI `python -m rag.ask "..."`
- [ ] Hand test 6 questions: 2 definitions, 1 KPI code, Churn trap, 2 unanswerable (test new LLM code on 3 first)
- Concepts: Grounding, Prompt versioning, Structured output

### 3.1 Generation eval (Very High) (0:50)
- [ ] `eval/generation_eval.py` + judge prompts (correctness, faithfulness); test on 3 questions first
- [ ] Full run on 20 questions (10 holdout, 4+ unanswerable, both traps): best config vs baseline
- [ ] Run the judge in the background; I hand-grade 10 answers **before** reading the judge; compute agreement
- [ ] Cost per query (note price and date used), p50 / p95 latency

### 3.3 Streamlit demo (0:50)
- [ ] `app/streamlit_app.py`: question box, filters, config picker, **Retrieval Inspector** table (vector rank, BM25 rank, RRF score, rerank score), answer with clickable citations, tokens and latency. Calls the pipeline directly (no API).
- [ ] 60-second demo video (question that works, Churn trap, refusal). First thing cut if behind.

### 3.5 Write-up and publish (0:40)
- [ ] Final `results/experiments.md`: grid, generation table, cost and latency, 3-5 findings, failures, limits (filled as we go, real runs only)
- [ ] README (what, problem, diagram, how to run, results, trade-offs, limits, ~10-line "how this would scale" linking to my architecture doc)
- [ ] Secrets check (`git ls-files` shows only `.env.example`), then make the repo public
- [ ] Interview line filled with my own numbers (brief section 14)

**Day 2 wrap-up:** batched CONCEPTS.md notes, approved by me, then final commits.

---

## Moved out of scope
- ~~3.2 FastAPI~~ moved to the agents project (issue #15 closed).
- ~~3.4 Production architecture~~ written by me outside Claude Code (issue #17 closed).

## Cut list (if behind)
- Must: corpus, 3 chunkings, vector + BM25 + hybrid, golden set, retrieval grid, grounded answers with citations and refusal, Streamlit demo
- Should: reranker, judge eval, hand grades, cost and latency
- Could (later): query rewriting, parent-child retrieval, the bge query-prefix test, Ragas, FastAPI
