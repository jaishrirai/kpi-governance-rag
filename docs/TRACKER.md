# Build tracker

| Milestone | Steps | Status | Hands-on check | Time |
|---|---|---|---|---|
| M1: searchable index | 1.4 chunking (done), 1.5 embeddings and Chroma (done), 1.6 BM25 (done) | 1.3 to 1.6 done; M1 wrap-up and push pending | Change the overlap in `chunking.py` and predict how the chunk count changes | About 3.5h |
| M2: retrieval scores | 2.1 golden set (11 of about 40), 2.2 metrics, 2.3 RRF | To do | Calculate one RRF score by hand on paper | About 2.5h |
| M3: answers with citations | 2.4 reranker, 2.5 grounded answers | To do | Ask 6 questions and grade the answers yourself | About 2h |
| M4: shipped | 3.1 eval, 3.3 demo, 3.5 README | To do | Write the headline result in one paragraph and check the numbers match the runs | Remaining |

## Next steps

1. Rebuild the vector index with the new chunk header: `python -m rag.index --variant all`, then `python -m rag.index --sanity`. Paste the output; results go into `docs/walkthroughs/M1.md`.
2. M1 hands-on check: change the overlap number in `chunking.py` (OVERLAP_TOKENS), predict how the V1 chunk count changes, run `python -m rag.chunking`, then restore it.
3. M1 interview questions (3) answered by you.
4. Push all M1 commits together with Claude Code, then close the issue for 1.4 (#5) and any other finished step issues.
5. Step 1.7: write about 4 more golden questions to reach 15 (your 4 drafted questions can become G-012 to G-015).
6. M2: Step 2.1 (draft the remaining golden questions), 2.2 (retrieval metrics), 2.3 (RRF hybrid search).
