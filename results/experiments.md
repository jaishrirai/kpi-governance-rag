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

## Step 2.3 hybrid RRF (chunk-level fusion, RRF k=60, 50 candidates per retriever, labels v2)

### Which runs to trust

Runs 15 to 17 were logged on a dirty tree (`c817082+dirty`) before the hybrid code was committed, so their sha does not identify the code used. Runs 18 to 20 repeat them on the clean commit `ab028be`; every metric matches runs 15 to 17 exactly to four decimals (only latency differs). Use runs 18 to 20 as the record. Runs 15 to 17 stay in `results/runs.csv` unchanged. A vector V1 rerun without logging reproduced the baseline (dev 0.815 / 1.000 / 0.938), so the runner change did not affect it.

### Results (recall@5 / hit@5 / MRR@10)

| Variant | Split | Vector | BM25 | Hybrid |
|---|---|---|---|---|
| V1 | dev | 0.815 / 1.000 / 0.938 | 0.592 / 0.833 / 0.564 | 0.758 / 0.958 / 0.758 |
| V1 | holdout | 0.729 / 0.875 / 0.646 | 0.417 / 0.500 / 0.492 | 0.708 / 0.875 / 0.708 |
| V2 | dev | 0.805 / 1.000 / 0.927 | 0.640 / 0.875 / 0.599 | 0.706 / 0.917 / 0.783 |
| V2 | holdout | 0.646 / 0.750 / 0.650 | 0.667 / 0.750 / 0.428 | 0.708 / 0.875 / 0.729 |
| V3 | dev | 0.812 / 1.000 / 0.917 | 0.592 / 0.833 / 0.564 | 0.758 / 0.958 / 0.753 |
| V3 | holdout | 0.708 / 0.875 / 0.649 | 0.417 / 0.500 / 0.492 | 0.708 / 0.875 / 0.708 |

### Prediction against result

Stated before the runs: hybrid may improve recall, MRR is uncertain, and it may help G-015 and G-006. The pass-or-fail version proposed before the runs (V2 dev recall above 0.805, hit@5 stays 1.000, MRR@10 within 0.05 of 0.927, G-015 gains an expected document) failed on every test: recall 0.706, hit@5 0.917, MRR@10 0.783. G-015 in V1 and V3: POL-04 does enter the top 5, as hypothesised, but CAT-01 leaves, so recall stays 0.50 and the reciprocal rank falls from 1.00 to 0.25. G-006 does not improve (V1 recall 0.67 before and after).

### Verified findings

1. Dev: hybrid is below vector on all three metrics in all three variants (recall down 0.05 to 0.10, MRR@10 down 0.14 to 0.18). Holdout: equal or slightly higher, but n=8 and the V2 gain (hit@5 0.750 to 0.875) is one question.
2. V1, vector against hybrid, per question (dev): G-007, G-013, G-014 and G-025 lose recall; G-003, G-013, G-015, G-018 and G-025 lose reciprocal rank; G-031 gains (0.50 to 1.00). G-025 alone is 0.042 of the 0.057 recall drop: CAT-08 is in the vector top 5 and falls to hybrid rank 9. Holdout: G-028 improves in rank (reciprocal rank 0.33 to 1.00), G-008 recall falls 0.50 to 0.33.
3. Depth: the fused top 50 holds at least 20 distinct documents in V2 and at least 48 in V1 and V3, on all 40 questions. None is below 10. V1 and V3 have only 52 chunks, so depth 50 returns almost the whole index.
4. Governance documents in the top 5, dev questions (24), V1 / V2 / V3:
   - FAQ-01: vector 7 / 7 / 8, BM25 16 / 11 / 16, hybrid 16 / 7 / 15. Only one dev question declares FAQ-01 (expected, conflicting or related).
   - KPI-007-V1: vector 4 / 7 / 5, BM25 10 / 8 / 10, hybrid 6 / 8 / 7. Four dev questions declare it (five for V2 hybrid).
   - Holdout (8): FAQ-01 vector 0 / 2 / 0, hybrid 3 / 1 / 3; KPI-007-V1 at most 1 for any retriever.
   - G-013 (V1): hybrid ranks the deprecated KPI-007-V1 first, above the current KPI-007; vector ranks KPI-007 first.

### Interpretation (supported by the counts, not proven)

BM25 puts FAQ-01 in the top 5 on 16 of 24 dev questions in V1 and V3. RRF weights BM25 ranks like vector ranks, even though BM25 is the weaker retriever here (dev recall 0.59 to 0.64 against 0.81), so FAQ-01 and SOP documents displace correct vector hits (G-025, G-007, G-014). V2 is affected less by FAQ-01 (hybrid 7, same as vector) and loses recall for a different reason: its G-006 top 5 is mostly KPI-016 to KPI-019 chunks, consistent with the earlier suspicion that repeated "Ownership and status" chunks add noise. That V2 explanation is untested.

Hypothesis status: "hybrid lifts G-015 and G-006" is not supported; "the V2 holdout dip is noise" is consistent with the data (one question).

### Proposed decision (pending review)

- Use vector retrieval as the application default. V1 and V3 are tied on dev (recall 0.815 and 0.812, MRR@10 0.938 and 0.917); choose between them on non-retrieval grounds.
- Keep the hybrid code and runner option and report equal-weight RRF as a negative result on this corpus. Do not tune k or weights on 24 dev questions after seeing the results.
- The governance exposure exists with vector too: FAQ-01 is in the top 5 on 7 to 8 of 24 dev questions and only one of them declares it. Step 2.5 must handle conflicting and deprecated sources through metadata and the prompt, not rely on retrieval alone.
- Proceed to the reranker (2.4) on vector candidates.

### Rules kept

No tuning against holdout. Holdout is run once per final configuration. Golden labels, metric definitions and baseline runs 1 to 14 were not changed in this step.

## Step 2.4 cross-encoder rerank (V1 vector candidates, labels v2)

Config: V1, vector top 50 chunks, all 50 rescored by `cross-encoder/ms-marco-MiniLM-L-6-v2` (max_length 512), reordered, same document-level evaluation (fetch depth 50, cutoff top 5). No tuning. Holdout run once.

### Which runs to trust

Run 22 is the record: clean git sha 347e2cc, metrics identical to run 21. Run 21 was logged on `7395aef+dirty` (the code was not yet committed) and is kept unchanged. The V1 vector baseline reproduced exactly in the same session.

### Results (recall@5 / hit@5 / MRR@10)

| Config | Dev (n=24) | Holdout (n=8) |
|---|---|---|
| V1 vector baseline | 0.815 / 1.000 / 0.938 | 0.729 / 0.875 / 0.646 |
| V1 vector + rerank (run 22) | 0.826 / 1.000 / 0.910 | 0.875 / 1.000 / 0.917 |
| V1 hybrid (runs 18 to 20) | 0.758 / 0.958 / 0.758 | 0.708 / 0.875 / 0.708 |

Latency: about 3.4 to 3.9 s per query with rerank in run 22 (2.4 to 2.5 s in run 21) against about 40 to 50 ms for vector. Latency varies between runs; the order of magnitude (about 50 to 100 times) is the finding.

### Verified findings

1. Dev is mixed: recall@5 +0.010 (about a quarter of one question), hit@5 unchanged, MRR@10 down 0.028. Holdout improves a lot (recall +0.146, MRR +0.271) but has only 8 answerable questions.
2. Per question, vector to rerank, 32 answerable: 7 improved, 4 regressed, 1 mixed, 20 unchanged.
   - Dev improved: G-015 (recall 0.50 to 1.00, POL-04 from vector rank 7 to rank 1), G-031 (recall 0.50 to 1.00), G-022 (reciprocal rank 0.50 to 1.00).
   - Dev regressed: G-006 (recall 0.67 to 0.33, POL-04 lost), G-007 (0.67 to 0.33, CAT-03 lost), G-027 (0.67 to 0.33, reciprocal rank 0.50 to 0.33), G-026 (reciprocal rank 1.00 to 0.50). Mixed: G-003 (recall 0.50 to 0.75, reciprocal rank 1.00 to 0.50).
   - Holdout improved: G-004 (recall 0 to 1.00), G-008 (reciprocal rank 0.33 to 1.00), G-028 and G-032 (reciprocal rank up to 1.00).
3. POL-04 appears in both gains (G-015, G-004) and losses (G-006, G-027), so no simple document-type explanation holds.
4. Sign test on the 11 decided questions (7 up, 4 down): one-sided p about 0.27, two-sided about 0.55. This is not evidence of a win.

### Governance comparison (`scripts/compare_governance.py`, top 5, answerable questions)

Counts of questions with the document in the top 5, declared count in brackets.

| Config | Split | KPI-007-V1 | FAQ-01 | Deprecated above current KPI-007 |
|---|---|---|---|---|
| vector | dev | 4 [4] | 7 [1] | 2 of 6 |
| vector | holdout | 0 [0] | 0 [0] | 1 of 1 |
| rerank | dev | 4 [4] | 11 [1] | 1 of 4 |
| rerank | holdout | 0 [0] | 1 [0] | 0 of 0 |

- The vector rows match `diagnose_hybrid.py` (shared counting code), a consistency check.
- Undeclared FAQ-01 appearances on dev rise from 6 to 10 with rerank. G-003 and G-004 now put FAQ-01 at rank 1.
- KPI-007-V1 appears only on questions that declare it, in both configs. G-013 keeps KPI-007 first and KPI-007-V1 second.
- The "deprecated above current" counts rest on very few questions (1 to 6). Do not read a trend into them.

### Interpretation (hypotheses, not proven)

The cross-encoder reads only text. It has no access to certification, currentness or source authority, so it can promote a conflicting document (FAQ-01) just as readily as a certified one. Reranking does not enforce source authority. It also cannot recover chunks missing from the vector top 50 (little limit here, since V1 has 52 chunks). The holdout gain may be noise at n=8; the dev result is neutral.

### Proposed decision (pending review)

- Keep vector-only as the default. Keep reranking as an optional configuration (`--rerank cross-encoder`), reported as a promising experiment, not a proven improvement.
- Reasons: neutral dev result, 8-question holdout, much higher latency, higher FAQ-01 exposure.
- Settle the question by end-to-end answer quality in Step 3.1. Handle conflicting and deprecated sources in Step 2.5 through metadata and the prompt, not through retrieval.
- Not done on purpose: reranker tuning, other models, governance filters.

### Rules kept

No tuning against holdout; holdout run once for this configuration. Golden labels, metrics, retrieval logic and runs 1 to 20 unchanged. Run 21 kept as logged.
