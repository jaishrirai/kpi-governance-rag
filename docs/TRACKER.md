# Build tracker

Last updated with the hybrid commit (see `git log`). Runs logged: 1 to 17 (15 to 17 are hybrid, tagged `+dirty`; clean reruns pending). Tests: 86 passed, 2 skipped in the cloud shell (the skipped ones need `rank_bm25` and `chromadb`, so run the full suite in the Windows `.venv`).

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | Done | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (40, audited, labels v2), 2.2 retrieval eval (runs 1 to 14), 2.3 hybrid RRF | 2.1 and 2.2 done and pushed. 2.3 in progress: `rrf()`, `fuse_hits()`, `hybrid_search()` and the `hybrid` runner option are built and tested. Hybrid runs 15 to 17 are logged on a dirty tree. Clean reruns, two diagnostics and the retrieval decision are next | RRF by hand: done. Prediction against result: recorded at review | About 2.5h |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | To do | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Immediate next step: close 2.3 and decide the retrieval configuration

1. Commit the hybrid code (this commit).
2. Rerun V1, V2 and V3 hybrid on the committed code so the run records carry a clean git sha, with notes marking them as reruns of 15 to 17. Runs 15 to 17 stay in `results/runs.csv` unchanged: they carry `c817082+dirty`, so they do not identify the code that produced them.
3. Run a read-only diagnostic script (committed after review): distinct documents in the fused top 50, and how often KPI-007-V1 and FAQ-01 appear in the top 5, by retriever, variant and split.
4. Review the results against the written prediction, record the findings in `results/experiments.md`, and choose the retrieval configuration with a stated reason. No tuning of labels or retrieval in this step.

## Next steps and their purpose

| Milestone | Step | What we do | Purpose |
|---|---|---|---|
| M2 wrap-up (done) | Push and issue #10 | Pushed through c817082 via Claude Code; issue #10 (2.2) closed with one comment | Puts the baseline, labels v2 and `rrf()` on GitHub |
| M2 (done) | 2.2 Retrieval eval | You worked MRR by hand (ranks 1, 3, missing, 2), then `eval/retrieval_eval.py` was built: recall@5 (fractional, headline), hit@5 (binary), MRR@10, dev vs holdout, `results/runs.csv`. G-008 is reported with its 5/6 recall@5 ceiling | Turns "it feels better" into numbers, and gives the baseline every later change is compared with |
| M2 (done) | Baseline review | Every dev baseline miss read by hand; golden labels v2 applied for G-001, G-005 and G-023 with written reasons; findings in `results/experiments.md` | Confirms the golden set carries information before we trust it |
| M2 (done) | 2.3a RRF by hand and `rrf()` | Three worked examples in `docs/LEARNING_NOTES.md` 7.7; `src/rag/fusion.py` and `tests/test_fusion.py`, including a test that maps fused chunk IDs back to hits and through `to_doc_ranking` | Proves the formula and the chunk-to-document contract before any retrieval runs |
| M2 (done) | 2.3b `hybrid_search()` | `fuse_hits()` (pure) and `hybrid_search()` in `src/rag/hybrid.py`, tests in `tests/test_hybrid.py`; `hybrid` retriever option in the eval runner, which requests `FETCH_DEPTH` fused chunks | Combines BM25 and vector ranks so exact IDs and meaning both count |
| M2 (next) | 2.3c Hybrid runs and error analysis | Runs 15 to 17 are logged on a dirty tree, so they are rerun on the committed code and marked as reruns. Compare with the six baseline configurations, read the misses, record the prediction against the result, write findings in `results/experiments.md`, choose the retrieval configuration on dev and confirm on holdout | Finds which chunking and retrieval combination works best, and why |
| M2 | Deprecated and conflict check | Count how often KPI-007-V1 and FAQ-01 (the `conflicting_doc_ids`) appear in the top 5 for vector, BM25 and hybrid | Measures the governance risk directly; decides if a certification filter or reranker is needed |
| M3 | 2.4 Reranker | Add a cross-encoder rerank over the top candidates, compare with and without | Tests whether a second, slower ranking step fixes the misses hybrid leaves, and whether it separates certified from deprecated |
| M3 | 2.5 Grounded generation | Gemini answers only from retrieved chunks, with citations, a citation check, and a refusal path; pass owner and status metadata to the model | Delivers the actual assistant behaviour: cited answers, no guessing, refusal on the 8 unanswerable questions |
| M3 | Hand grading | You ask 6 questions and grade the answers yourself | Your own judgement is the check on any automatic scoring |
| M4 | 3.1 Generation eval | Score answers against `reference_answer` and `key_facts`, citation correctness, and refusal rate on unanswerable questions | Shows whether the final answers are right, not only whether retrieval worked |
| M4 | 3.3 Streamlit demo | Small UI showing the answer, citations and retrieved chunks | Gives interviewers something to see and lets you demo failures honestly |
| M4 | 3.5 Write-up and README | Headline result in one paragraph, numbers matching `results/runs.csv`, design decisions, limits (40 questions, synthetic corpus, Claude-drafted questions) | Makes the project readable in two minutes and defensible in an interview |
| Cross-cutting | Notes and interview prep | Keep adding to `docs/LEARNING_NOTES.md`; answer the interview questions after each milestone | Turns the build into explainable knowledge |
| Cross-cutting | Housekeeping | `PLAN.md` step 2.3 still says "filter tests" and "runs 1-9"; align it with this tracker (runs now start at 15 for hybrid) | Keeps the plan and tracker from contradicting each other |
| Optional | `pyproject.toml` + `pip install -e .` | Permanent import path instead of `PYTHONPATH=src` | Removes a recurring setup error |
