# Build tracker

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (next), 1.6 BM25 | 1.3 and 1.4 done, 1.5 and 1.6 to do | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (11 of about 40), 2.2 metrics, 2.3 RRF | To do | Calculate one RRF score by hand on paper | About 2.5h |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | To do | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Next steps

1. Push 1.3 and 1.4 (committed locally as 66ff746; push pending). Close issues for 1.3 and 1.4 on GitHub.
2. V2 and BM25 labels changed to "Claude builds, you review and predict" (decided).
3. Step 1.5: predict the sanity-query results, then build `src/rag/index.py`.
4. Step 1.6: BM25, compare with vector on "KPI-014".
5. Step 1.7: write about 4 more golden questions to reach 15.
6. Delete the stale `docs/notes/` folder on the laptop.
