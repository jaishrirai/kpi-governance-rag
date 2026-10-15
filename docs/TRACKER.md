# Build tracker

Last updated at the end of the 2026-10-15 session, after Step 2.4 (see `git log`). Runs logged: 1 to 22 (15 to 17 and 21 carry a dirty sha and are superseded by reruns 18 to 20 and 22). Tests: 102 passed, 2 skipped in the cloud shell (the skipped ones need `rank_bm25` and `chromadb`, so run the full suite in the Windows `.venv`).

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | Done | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (40, labels v2), 2.2 retrieval eval, 2.3 hybrid RRF, 2.4 cross-encoder rerank | All done. Hybrid lost to vector on dev. Rerank: dev mixed, holdout up (n=8), FAQ-01 exposure up, latency about 50x. Decision proposed: vector default, rerank optional | RRF by hand: done. Predictions recorded at each review | About 4h |
| M3: answers with citations | 2.5 grounded answers | Plan agreed, starts next session (model IDs in `.env` to fix first) | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Progress snapshot (2026-10-15)

| Milestone | Progress | What is left |
|---|---|---|
| M1 searchable index | 100% | Nothing |
| M2 retrieval scores | 100% | Review and approve the retrieval decision (vector default, rerank optional) |
| M3 answers with citations | 0% built, plan agreed | Fix `.env` model IDs, smoke test, `llm.py`, `generate.py`, prompt, `validate_citations()` (you write it), pipeline, CLI, 6 hand tests |
| M4 shipped | 0% | 3.1 generation eval, 3.3 Streamlit demo, 3.5 README and write-up |

Pipeline status: Load, Chunk, Embed and Index, Retrieve (vector, BM25, hybrid), Rerank are done and measured. Generate and the generation Evaluate are next. Pushed: through `7395aef`. Local only, not pushed: `347e2cc`, `9866915` and the wrap-up docs commit. Push when you ask.

## Immediate next step: Step 2.5 grounded generation (plan for the next session)

Scope rules: vector V1 is the reference, rerank stays optional, no retrieval tuning, no new frameworks, no governance engine.

**Before coding (you, first thing):**
1. In AI Studio, pick a current Gemini Flash-class model ID (free tier). Set `LLM_MODEL` and `JUDGE_MODEL` in `.env`. They still hold old Anthropic IDs (`claude-haiku-4-5`, `claude-sonnet-4-5`). Never paste the key in chat.
2. Confirm `google-genai` is installed in the `.venv` (`pip install -r requirements.txt` if not).

**Build order (stop after each):**
1. Smoke test: one Gemini call at temperature 0 and 1, print token counts. Confirms key, model ID and package.
2. `src/rag/llm.py` (single `complete()` wrapper), `src/rag/generate.py`, `prompts/answer_v1.txt` (JSON `{answer, citations, refused}`, temperature 0, 400 token cap, Pydantic check). Plus the `validate_citations()` stub with failing tests.
3. You write `validate_citations()` (citations must be retrieved chunk IDs, one retry, then refusal). Then `src/rag/pipeline.py`, CLI `python -m rag.ask "..."`, and `results/traces.jsonl`.
4. Hand test 6 questions (2 definitions, 1 KPI code, churn trap G-013, 2 unanswerable). Commit. Stop before 3.1.

**Governance rule (simple, metadata based):** label every context chunk with doc ID, title, certification, version and effective date; sort Certified first; prompt says Certified and current sources govern and conflicts must be named; Deprecated and Provisional sources may only be mentioned as not authoritative; code flags answers that cite only non-Certified sources. Deprecated chunks stay in context (G-002 and G-013 expect "v1 is deprecated"). Known pairs: KPI-006 (Certified, 30 days) vs FAQ-01 (Provisional, 90 days), and KPI-007 vs KPI-007-V1 (Deprecated).

**Limits to state honestly:** a valid citation only proves the chunk was retrieved, not that it supports the claim; the rule relies on the model following labels; there is no `superseded_by` field.

**Then Step 3.1 (separate session):** automatic checks (citation validity, refusal on the 8 unanswerable, wrongly refused answerable, expected documents cited, key_facts matches), governance cases G-013, G-002, G-017, G-018, G-001, a judge for correctness and faithfulness after you hand-grade 10 answers, vector against vector+rerank, no prompt changes based on holdout.

## Next steps and their purpose

| Milestone | Step | What we do | Purpose |
|---|---|---|---|
| M2 wrap-up (done) | Push and issue #10 | Pushed through c817082 via Claude Code; issue #10 (2.2) closed with one comment | Puts the baseline, labels v2 and `rrf()` on GitHub |
| M2 (done) | 2.2 Retrieval eval | You worked MRR by hand (ranks 1, 3, missing, 2), then `eval/retrieval_eval.py` was built: recall@5 (fractional, headline), hit@5 (binary), MRR@10, dev vs holdout, `results/runs.csv`. G-008 is reported with its 5/6 recall@5 ceiling | Turns "it feels better" into numbers, and gives the baseline every later change is compared with |
| M2 (done) | Baseline review | Every dev baseline miss read by hand; golden labels v2 applied for G-001, G-005 and G-023 with written reasons; findings in `results/experiments.md` | Confirms the golden set carries information before we trust it |
| M2 (done) | 2.3a RRF by hand and `rrf()` | Three worked examples in `docs/LEARNING_NOTES.md` 7.7; `src/rag/fusion.py` and `tests/test_fusion.py`, including a test that maps fused chunk IDs back to hits and through `to_doc_ranking` | Proves the formula and the chunk-to-document contract before any retrieval runs |
| M2 (done) | 2.3b `hybrid_search()` | `fuse_hits()` (pure) and `hybrid_search()` in `src/rag/hybrid.py`, tests in `tests/test_hybrid.py`; `hybrid` retriever option in the eval runner, which requests `FETCH_DEPTH` fused chunks | Combines BM25 and vector ranks so exact IDs and meaning both count |
| M2 (done) | 2.3c Hybrid runs and error analysis | Runs 15 to 17 are logged on a dirty tree, so they are rerun on the committed code and marked as reruns. Compare with the six baseline configurations, read the misses, record the prediction against the result, write findings in `results/experiments.md`, choose the retrieval configuration on dev and confirm on holdout | Finds which chunking and retrieval combination works best, and why |
| M2 (done) | Deprecated and conflict check | Count how often KPI-007-V1 and FAQ-01 (the `conflicting_doc_ids`) appear in the top 5 for vector, BM25 and hybrid | Measures the governance risk directly; decides if a certification filter or reranker is needed |
| M3 (done) | 2.4 Reranker (runs 21 and 22, `compare_governance.py`) | Add a cross-encoder rerank over the top candidates, compare with and without | Tests whether a second, slower ranking step fixes the misses hybrid leaves, and whether it separates certified from deprecated |
| M3 | 2.5 Grounded generation | Gemini answers only from retrieved chunks, with citations, a citation check, and a refusal path; pass owner and status metadata to the model | Delivers the actual assistant behaviour: cited answers, no guessing, refusal on the 8 unanswerable questions |
| M3 | Hand grading | You ask 6 questions and grade the answers yourself | Your own judgement is the check on any automatic scoring |
| M4 | 3.1 Generation eval | Score answers against `reference_answer` and `key_facts`, citation correctness, and refusal rate on unanswerable questions | Shows whether the final answers are right, not only whether retrieval worked |
| M4 | 3.3 Streamlit demo | Small UI showing the answer, citations and retrieved chunks | Gives interviewers something to see and lets you demo failures honestly |
| M4 | 3.5 Write-up and README | Headline result in one paragraph, numbers matching `results/runs.csv`, design decisions, limits (40 questions, synthetic corpus, Claude-drafted questions) | Makes the project readable in two minutes and defensible in an interview |
| Cross-cutting | Notes and interview prep | Keep adding to `docs/LEARNING_NOTES.md`; answer the interview questions after each milestone | Turns the build into explainable knowledge |
| Cross-cutting | Housekeeping | `PLAN.md` step 2.3 still says "filter tests" and "runs 1-9"; align it with this tracker (runs now start at 15 for hybrid) | Keeps the plan and tracker from contradicting each other |
| Optional | `pyproject.toml` + `pip install -e .` | Permanent import path instead of `PYTHONPATH=src` | Removes a recurring setup error |
