# Retrieval experiments (M2)

Metrics at document level, answerable questions only (dev n=24, holdout n=8). recall@5 is the share of expected documents in the top 5 (headline), hit@5 is 1 if any expected document is in the top 5, MRR@10 uses the first expected document. All runs are in `results/runs.csv`. Fetch depth 50 chunks, collapsed to documents before scoring.

## Step 2.2 baseline (single retrievers, no fusion, no rerank)

Labels v1 are runs 3 to 8 (code `3258ca8`). Labels v2 are runs 9 to 14 (code `5458fcd`). Runs 1 and 2 are the first V1 runs, tagged `+dirty`, kept for the record. Compare configurations only within one label version.

| Variant | Retriever | dev recall@5 v1 / v2 | dev hit@5 v1 / v2 | dev MRR@10 v1 / v2 | holdout recall@5 | holdout hit@5 | holdout MRR@10 |
|---|---|---|---|---|---|---|---|
| V1 | vector | 0.732 / 0.815 | 0.958 / 1.000 | 0.896 / 0.938 | 0.729 | 0.875 | 0.646 |
| V2 | vector | 0.722 / 0.805 | 0.958 / 1.000 | 0.906 / 0.927 | 0.646 | 0.750 | 0.650 |
| V3 | vector | 0.728 / 0.812 | 0.958 / 1.000 | 0.896 / 0.917 | 0.708 | 0.875 | 0.649 |
| V1 | BM25 | 0.550 / 0.592 | 0.833 / 0.833 | 0.543 / 0.564 | 0.417 | 0.500 | 0.492 |
| V2 | BM25 | 0.557 / 0.640 | 0.833 / 0.875 | 0.590 / 0.599 | 0.667 | 0.750 | 0.428 |
| V3 | BM25 | 0.550 / 0.592 | 0.833 / 0.833 | 0.543 / 0.564 | 0.417 | 0.500 | 0.492 |

Holdout is identical across label versions because no holdout label changed.

### Verified findings

1. On the development set, vector outperforms BM25 in all three variants on all three metrics (recall@5 by about 0.17 to 0.22, MRR@10 by about 0.33 to 0.37). Holdout results are mixed: V1 and V3 favour vector on every metric, but for V2 BM25 has higher recall@5 than vector (0.667 vs 0.646), equal hit@5 (0.750 each) and lower MRR@10 (0.428 vs 0.650). With 8 holdout questions, one question moves a score by 0.125, so the holdout gap should not be over-read.
2. Chunking barely matters here. V1 and V3 are effectively the same chunking (52 chunks each, most documents are shorter than the chunk size), and their BM25 results are identical. V2 differs from them by about 0.01 on dev recall@5 for vector, which 24 questions cannot resolve.
3. With labels v2 the vector retriever finds at least one expected document in the top 5 for every dev question (hit@5 1.000). Remaining dev misses are about coverage: a second or third expected document is missing (for example G-003, G-006, G-013, G-014, G-015, G-027). So hit@5 no longer separates configurations on dev; recall@5 and MRR@10 do.
4. Part of the jump from labels v1 to v2 comes from the label changes, not retrieval. Dev recall@5 rose by about 0.083 for V1 vector: G-001 and G-023 each +0.5 and the rewritten G-005 +1.0, divided by 24.
5. Vector similarity scores are compressed: the document at rank 5 and the one at rank 20 differ by only 0.03 to 0.05 cosine similarity.
6. The deprecated KPI-007-V1 and the conflicting FAQ-01 appear in top 5 lists, for example KPI-007-V1 at rank 2 for G-013 (vector) and FAQ-01 for G-018, G-031.

### Dev miss review (2.2e)

Verified from source text and vector ranks (`scripts/inspect_misses.py`):

- G-015: POL-04 sits at vector rank 7 (V1, V3) or 17 (V2), only 0.008 cosine below the cut for V1. BM25 ranks it 6. Genuine near-miss, kept as a hybrid and reranker test case.
- G-006: CAT-01 at rank 13 to 16; POL-04 is found in V1 and V3 but at rank 6 in V2. The typo "finnance" appears nowhere in the corpus. Genuine partial miss, kept.
- G-001, G-023: the key document ranks first everywhere; POL-04 (rank 14 to 28) was an overstrict label. Changed in labels v2, see `docs/GOLDEN_SET_AUDIT.md`.
- G-005: ill-posed (no document defines KPI categories or says where the catalog is). Rewritten in labels v2.

### Hypotheses, not yet tested

- Hybrid RRF should lift G-015 and G-006 because BM25 and vector both rank POL-04 near the cut (G-015: BM25 6, vector 7).
- The V2 holdout dip (recall@5 0.646 vs 0.729) is probably noise (one holdout question moves a score by 0.125).
- Holdout questions G-004 and G-028 are POL-04 cases like G-015; they were not read or tuned against.

### Rules kept

No tuning against holdout. Holdout is run once per final configuration.

## Next: Step 2.3 hybrid RRF

Work the example by hand first (rank 1 in vector + rank 4 in BM25 = 1/61 + 1/64), then build `rrf()` and `hybrid_search()`, run V1, V2, V3 with hybrid on labels v2, and compare with the table above.
