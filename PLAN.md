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
- [x] After the skim and BEFORE any search or retrieval run, I write 10 questions in `golden/golden_set.jsonl` (done: 15 written, G-001 to G-015; Claude drafts 25 more in Step 2.1)

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
- [x] `bm25_search()` with the code-preserving tokenizer and filters
- [x] Compare against vector search on "KPI-014": which wins and why?
- Concepts: Keyword search, BM25, TF-IDF intuition

### 2.1 Golden set, part 2 (0:30, runs at the end of Day 1)
- [x] Claude drafts 30 (traps, unanswerables, codes, typos, abbreviations); I review (40 questions, labels v2 after the audit)
- [x] Validation script: 40 total, 8 unanswerable, 10 holdout, every expected doc_id exists (`scripts/validate_golden.py`)

**Day 1 wrap-up:** batched CONCEPTS.md notes for the day, approved by me, then commits.

---

## Day 2: Retrieval grid, grounded answers, eval, demo, ship (about 6h20)

### 2.2 Retrieval eval (Very High) [YOU BUILD: metrics] (0:50)
- [x] `eval/retrieval_eval.py`: recall@5 (fractional, headline), hit@5 (binary), MRR@10 at document level, dev vs holdout, appended to `results/runs.csv`
- [x] Work out MRR by hand for ranks 1, 3, missing, 2 before coding
- [x] Baseline: V1 + vector (baseline grid is runs 1 to 14 in `results/runs.csv`; runs 1 and 2 were logged on a dirty tree, runs 3 and 4 repeat them on a clean commit, 3258ca8)

### 2.3 Hybrid RRF (Very High) [YOU BUILD] (1:20)
- [x] Work one RRF example by hand (rank 1 vector + rank 4 BM25 = 1/61 + 1/64); three worked examples in `docs/LEARNING_NOTES.md` 7.7
- [x] `rrf()` + `hybrid_search()` with tests (the `where` filter is passed through and tested with fakes; no filtered queries are in the evaluation)
- [x] Grid: 3 variants x {vector, BM25, hybrid}: baseline runs 1 to 14 (runs 1 and 2 dirty, repeated clean as runs 3 and 4), hybrid runs 15 to 20 (15 to 17 logged on a dirty tree, kept; reruns are 18 to 20). Result: equal-weight RRF lost to vector on dev
- [x] Error analysis in `results/experiments.md` (Step 2.2 miss review, Step 2.3 hybrid diagnostics, conclusions)

### 2.4 Reranker (Very High) [YOU BUILD] (0:40)
- [x] `rerank()` with the cross-encoder; run on V1 + vector only (the best config), runs 21 and 22 (21 dirty, 22 clean rerun); added latency logged (about 50x). Result: dev mixed, holdout up on 8 questions, optional
- Concepts: Bi-encoder vs cross-encoder, "retrieve wide, rerank narrow"

### 2.5 Grounded generation (High) [YOU BUILD: citation check] (1:10)
- [x] `GEMINI_API_KEY`, `LLM_MODEL`, `JUDGE_MODEL` in `.env`, `pip install google-genai` (models: gemini-3.5-flash-lite for answers, gemini-3.8-flash for the judge; judge gave a 503 once, retest in 3.1)
- [x] LLM smoke test: same question at temperature 0 and 1, print token counts (run ad hoc; `scripts/smoke_test.py` Part B was left as a placeholder)
- [x] `src/rag/llm.py`, `src/rag/generate.py`, `prompts/answer_v1.txt`
- [x] JSON shape check (stdlib, not Pydantic), citation check in code (`src/rag/validate.py`), refusal, `results/traces.jsonl`
- [x] One retry on a failed citation check, then refuse: built in 2.6A (see 2.6)
- [x] `src/rag/pipeline.py` + CLI `python -m rag.ask "..."`
- [x] Hand test 6 questions, recorded in `results/step2_5_hand_tests.md` (churn definition, active-customer trap, ownership, KPI code, 2 unanswerable). Found: vector missed a KPI asked by code; answers sometimes incomplete
- Concepts: Grounding, Prompt versioning, Structured output

### 2.6 Governance in generation + housekeeping (added after Step 2.5, small)
- [x] 2.6A: one retry on a failed citation check, then refuse (`ask()`, `generate(correction=...)`, `build_correction()`). Implemented and unit-tested with forced failures only. No real Gemini validation failure has triggered the retry yet (7 real runs, none failed validation); do not treat it as proven on real output
- [ ] Sort Certified chunks first and add version and effective date (from the manifest) to the context labels; optional flag when an answer cites only non-Certified sources. Simple explicit rules, no governance engine
- [ ] Housekeeping: push on explicit approval; close the GitHub issues for steps 2.3 to 2.5 (comment with the result)

### 3.1 Generation eval (Very High) (0:50)
- [x] `eval/generation_eval.py` + judge prompts (key-fact coverage, faithfulness); tested on 3 questions first, then judge sanity check (9 of 9)
- [x] Full run on all 40 questions (30 dev, 10 holdout once per version): `answer_v1` vs `answer_v2`. Result: v2 is not adopted, v1 stays the default (`docs/decisions.md` rows 20 to 22)
- [x] Judge run with `gemini-3.5-flash-lite` (free tier); I hand-graded 10 answers blind before reading the judge; agreement 80.6% then 100% after a logged G-005 rubric fix, faithfulness 10 of 10
- [x] Cost per query about $0.0008 (input $0.30 and output $2.50 per 1M tokens, third-party price page updated 2026-10-19, recheck before quoting; the runs themselves were free tier). Latency p50 / p95 from dev: v1 4.6 s / 8.4 s, v2 4.0 s / 6.4 s; holdout latency is unusable (free-tier outliers up to 282 s)
- [ ] Key-fact coverage of answers is measured (2.6B and 3.1). Vector retrieval of bare KPI codes is NOT run as a separate diagnostic; it stays a documented limit (G-028 is one real example: the KPI-020 owner chunk was not retrieved)

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
