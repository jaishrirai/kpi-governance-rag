# Build tracker

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | Done | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (40, audited, committed), 2.2 metrics, 2.3 RRF | 2.1 and 2.2 done (runs 1 to 14, labels v2 baseline), 2.3 next | Calculate one RRF score by hand on paper | About 2.5h |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | To do | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Next steps and their purpose

| Milestone | Step | What we do | Purpose |
|---|---|---|---|
| M2 wrap-up | Push | Push commits 497edd3 to the latest via Claude Code, close issue #10 (2.2) once `results/runs.csv` and `results/experiments.md` are committed | Puts the baseline and labels v2 on GitHub |
| M2 (done) | 2.2 Retrieval eval | You work MRR by hand (ranks 1, 3, missing, 2), then build `eval/retrieval_eval.py`: Recall@5, MRR@10, dev vs holdout, `results/runs.csv`, baseline V1 + vector. G-008 reported with its 5/6 Recall@5 ceiling plus Recall@10 | Turns "it feels better" into numbers, and gives the baseline every later change is compared with |
| M2 | Baseline review | Read every baseline miss by hand, check whether the golden labels or the retriever were wrong | Confirms the golden set carries information before we trust it; fix labels only with a written reason |
| M2 | 2.3 Hybrid RRF | You do RRF by hand (rank 1 vector + rank 4 BM25 = 1/61 + 1/64), then build `rrf()` and `hybrid_search()`, run the grid of 3 variants x {vector, BM25, hybrid}, write error analysis in `results/experiments.md` | Finds which chunking and retrieval combination works best, and why, with holdout kept for the final check |
| M2 | Deprecated and conflict check | Count how often KPI-007-V1 and FAQ-01 (the `conflicting_doc_ids`) appear in the top 5 | Measures the governance risk directly; decides if a certification filter or reranker is needed |
| M3 | 2.4 Reranker | Add a cross-encoder rerank over the top candidates, compare with and without | Tests whether a second, slower ranking step fixes the misses hybrid leaves, and whether it separates certified from deprecated |
| M3 | 2.5 Grounded generation | Gemini answers only from retrieved chunks, with citations, a citation check, and a refusal path; pass owner and status metadata to the model | Delivers the actual assistant behaviour: cited answers, no guessing, refusal on the 8 unanswerable questions |
| M3 | Hand grading | You ask 6 questions and grade the answers yourself | Your own judgement is the check on any automatic scoring |
| M4 | 3.1 Generation eval | Score answers against `reference_answer` and `key_facts`, citation correctness, and refusal rate on unanswerable questions | Shows whether the final answers are right, not only whether retrieval worked |
| M4 | 3.3 Streamlit demo | Small UI showing the answer, citations and retrieved chunks | Gives interviewers something to see and lets you demo failures honestly |
| M4 | 3.5 Write-up and README | Headline result in one paragraph, numbers matching `results/runs.csv`, design decisions, limits (40 questions, synthetic corpus, Claude-drafted questions) | Makes the project readable in two minutes and defensible in an interview |
| Cross-cutting | Notes and interview prep | Keep adding to `docs/LEARNING_NOTES.md`; answer the interview questions after each milestone | Turns the build into explainable knowledge |
| Optional | `pyproject.toml` + `pip install -e .` | Permanent import path instead of `PYTHONPATH=src` | Removes a recurring setup error |
