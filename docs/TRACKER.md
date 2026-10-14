# Build tracker

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | 1.3 to 1.6 done; M1 wrap-up and push pending | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (11 of about 40), 2.2 metrics, 2.3 RRF | To do | Calculate one RRF score by hand on paper | About 2.5h |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | To do | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Next steps

1. Rebuild the vector index after the loader change: `python -m rag.index --variant all`, then `python -m rag.index --sanity`. Paste the output; results go into `docs/walkthroughs/M1.md`.
2. Review and approve the golden set (`docs/GOLDEN_SET_REVIEW.md`, 40 questions with reference answers), then commit it.
3. Step 2.2: work out MRR by hand, then build `eval/retrieval_eval.py` (decide the recall rule for list-style questions).
4. Step 2.3: hybrid search with RRF, the grid of 3 variants x {vector, BM25, hybrid}, error analysis.
5. Push the new commits with Claude Code.
