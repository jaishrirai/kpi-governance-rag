# Build tracker

Last updated at the end of the 2026-10-21 session, after Step 3.1 (see `git log`; latest commit `4792b75`). Retrieval runs logged: 1 to 22 (15 to 17 and 21 carry a dirty sha and are superseded by reruns 18 to 20 and 22). Generation runs (dev and holdout) are in `results/generation/`. Tests: 205 passed, 2 skipped (the skipped ones need `rank_bm25` and `chromadb`, so run the full suite in the Windows `.venv`).

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | Done | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (40, labels v2), 2.2 retrieval eval, 2.3 hybrid RRF, 2.4 cross-encoder rerank | All done. Hybrid lost to vector on dev. Rerank: dev mixed, holdout up (n=8), FAQ-01 exposure up, latency about 50x. Decision proposed: vector default, rerank optional | RRF by hand: done. Predictions recorded at each review | About 4h |
| M3: answers with citations | 2.5 grounded answers, 2.6A one citation retry, 2.6B completeness experiment | Done. 2.5 hand tests recorded; retry is unit-tested only (no real failure triggered it); `answer_v2` (one completeness rule) tested and not adopted, `answer_v1` stays the default | Ask 6 questions and grade the answers yourself | About 2h for 2.5, plus 2.6 |
| M4: shipped | 3.1 eval (done), 3.3 demo, 3.5 README | 3.1 done on 2026-10-21. 3.3 and 3.5 to do | Write the headline result in one paragraph and check the numbers match the runs | Remaining: 3.3 and 3.5 |

## Progress snapshot (2026-10-21)

| Milestone | Progress | What is left |
|---|---|---|
| M1 searchable index | 100% | Nothing |
| M2 retrieval scores | 100% | Nothing. Decision accepted 2026-10-16; conclusions are in `results/experiments.md` and `docs/LEARNING_NOTES.md` Section 11 |
| M3 answers with citations | 100% | Nothing. Retry (2.6A) and completeness experiment (2.6B) done. Certified-first ordering is deferred and not planned (no evidence called for it) |
| M4 shipped | 3.1 done; 3.3 and 3.5 left | 3.1 generation eval is done. 3.3 Streamlit demo and 3.5 README and write-up are left, then the secrets check, push and public repo |

Pipeline status: Load, Chunk, Embed and Index, Retrieve (vector, BM25, hybrid), Rerank, Generate with citation validation and one retry, and the generation Evaluate are done and measured. The demo and the write-up are next. Git: 13 local commits are not yet pushed to GitHub. Push only on explicit approval, after the secrets check.

## Step 3.1 results (done 2026-10-21)

- **Judge:** `gemini-3.5-flash-lite` (free tier). Sanity check 9 of 9. Hand-graded 10 answers blind: agreement 80.6% on first check (bar 85%, missed because of one over-specific G-005 rubric), 100% after a logged fix, faithfulness 10 of 10.
- **Dev (30 questions):** key-fact coverage v1 75.6%, v2 79.5%; faithfulness 100% for both.
- **Holdout (10 questions, run once per version):** coverage v1 60.9%, v2 65.2%; faithfulness v1 100%, v2 87.5% with one unsupported claim (G-028, KPI owner inferred from an action owner).
- **Decision:** pass rule failed, so `answer_v2` is not adopted and `answer_v1` stays the default (`docs/decisions.md` rows 19 to 22).
- **Cost and latency:** about $0.0008 per query (price page dated 2026-10-19, recheck before quoting; the runs were free tier). Dev p50 and p95: v1 4.6 s and 8.4 s, v2 4.0 s and 6.4 s. Holdout latency is free-tier noise and is not reported.
- **Known limits to write up:** retrieval misses on broad list questions (G-006, G-015, both wrongly refused) and on bare KPI codes (G-028); the bare-code diagnostic was not run separately; the holdout has 8 answerable questions, so it shows direction, not proof; G-004, G-028 and G-032 have soft key facts.

## Immediate next step: 3.3 Streamlit demo, then 3.5 write-up and ship

1. **3.3 Streamlit demo (about 50 min):** question box, answer with citations, retrieved chunks table (ranks and scores), tokens and latency. Calls the pipeline directly. No video; screenshots in the README are enough.
2. **3.5 Write-up (about 40 to 60 min):** final `results/experiments.md` (grid, generation table, 3 to 5 findings, limits), README (what, problem, diagram, how to run, results, trade-offs, limits), the G-028 case as a headline finding, and the interview line filled with your own numbers.
3. **Ship (about 15 min):** secrets check (`git ls-files` shows only `.env.example`), push, make the repo public, close the GitHub issues for steps 2.3 to 2.5 and 3.1.
4. **Future work, not now:** a v3 prompt ("if the KPI's owner is not stated, say so") needs fresh questions because the holdout has been seen; Certified-first ordering; retrieval fixes for bare KPI codes and broad list questions.

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
| M3 (done) | 2.5 Grounded generation | Gemini answers only from retrieved chunks, with citations, a citation check, and a refusal path; pass owner and status metadata to the model | Delivers the actual assistant behaviour: cited answers, no guessing, refusal on the unanswerable questions |
| M3 (done) | 2.6A Citation retry | One retry when citation validation fails, then refuse; unit-tested with forced failures | Fixes form errors cheaply without retrying support or retrieval problems |
| M3 (done) | 2.6B Completeness experiment | `answer_v2` is `answer_v1` plus one completeness rule, run 3 times each and re-scored blind | Tests one prompt change at a time, with evidence |
| M3 (done) | Hand grading | You asked 6 questions and graded the answers yourself (2.5) | Your own judgement is the check on any automatic scoring |
| M4 (done) | 3.1 Generation eval | Key-fact coverage and faithfulness judge validated against 10 blind hand grades, dev runs, holdout once per version, cost and latency. v2 not adopted, v1 kept | Shows whether the final answers are right, not only whether retrieval worked |
| M4 | 3.3 Streamlit demo | Small UI showing the answer, citations and retrieved chunks | Gives interviewers something to see and lets you demo failures honestly |
| M4 | 3.5 Write-up and README | Headline result in one paragraph, numbers matching `results/runs.csv`, design decisions, limits (40 questions, synthetic corpus, Claude-drafted questions) | Makes the project readable in two minutes and defensible in an interview |
| Cross-cutting | Notes and interview prep | `docs/LEARNING_NOTES.md` is up to date through Section 15 (Steps 2.6 and 3.1); answer the interview questions after the write-up | Turns the build into explainable knowledge |
| Cross-cutting | Housekeeping | `PLAN.md` is aligned with this tracker. Left: secrets check, push on explicit approval, close GitHub issues for 2.3 to 2.5 and 3.1 with a short result comment | Keeps GitHub in step with the local work |
| Optional | `pyproject.toml` + `pip install -e .` | Permanent import path instead of `PYTHONPATH=src` | Removes a recurring setup error |
