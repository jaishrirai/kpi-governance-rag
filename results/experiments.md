# Experiments: retrieval (M2) and generation (M3 and M4)

## Summary (read this first)

Corpus: fictional Kestrel Retail Group, 52 chunks in the default chunking (V1). Golden set: 40 questions (30 dev, 10 holdout, 8 unanswerable), labels v2. Answer model and judge: `gemini-3.5-flash-lite`, free tier, temperature 0.

**Default configuration:** chunking V1, vector search, top 5 chunks, prompt `answer_v1`, certification label on every chunk, citation check with one retry.

| Result | Dev | Holdout |
|---|---|---|
| Retrieval, document level: recall@5 / hit@5 / MRR@10 | 0.815 / 1.000 / 0.938 | 0.729 / 0.875 / 0.646 |
| Key-fact coverage of answers (v1) | 75.6% (59 of 78) | 60.9% (14 of 23) |
| Faithful answers (v1) | 22 of 22 | 8 of 8 |
| Unanswerable questions refused correctly | 6 of 6 | 2 of 2 |
| Wrong refusals of answerable questions (v1) | 2 (G-006, G-015) | 0 |
| Cost per query | about $0.0008 | about $0.0008 |

Retrieval metrics use 24 dev and 8 holdout answerable questions. Details and the runs behind every number are below and in `results/runs.csv` and `results/generation/`.

### Findings

1. **Plain vector search was the best default; the extra machinery did not earn its place.** Equal-weight hybrid (RRF) lost to vector on dev in all three chunkings (recall@5 down 0.05 to 0.10). Cross-encoder reranking was mixed on dev (recall +0.010, MRR@10 -0.028) and better on an 8-question holdout, at about 50 times the latency. Both stay in the code as optional settings.
2. **Retrieval quality is not source authority, so governance lives in the generation step.** Neither hybrid nor rerank knows which source is Certified. Reranking pulled the informal, conflicting FAQ-01 into the dev top 5 on 11 questions instead of 7. The fix used is a certification label on every chunk plus prompt rules. On the trap question G-018 the answer states the certified 30-day rule and calls the 90-day figure informal.
3. **A rubric bug can pick the winner.** The first judge check missed its bar (80.6% against 85%). All six misses were one answer (G-005) whose key facts asked for role titles when the question asked for teams. It favoured v2 over v1. The fix was logged openly and agreement went to 100%; both figures are kept.
4. **The completeness prompt (v2) gained a little and cost trust, so it was not adopted.** v2 covered 3 more facts on dev and 1 more on holdout, but on holdout it produced one unsupported claim (G-028, the owner of KPI-020, inferred from an action owner). The pass rule, written before the holdout run, failed on faithfulness. v1 stays the default.
5. **Most remaining misses are retrieval misses.** Broad list questions (G-006, G-015) were refused by both prompts because only some of the needed documents were retrieved, and a bare KPI code (G-028, and an ad hoc KPI-010 test) pulled process documents instead of the KPI. Hybrid does not fix this: for the G-028 question the demo's comparison shows hybrid's top 5 holds neither the KPI-020 document nor the glossary, only the review minutes ranked higher.

### Limits (details at the end)

40 questions and 8 answerable holdout questions show direction, not proof. The corpus is synthetic and small. 30 of the 40 questions were drafted with Claude. The judge is the same model as the answer model, checked on only 10 hand-graded answers. Temperature 0 is not fully repeatable.

## Retrieval experiments (M2)

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

## Conclusions for Steps 2.3 and 2.4 (retrieval phase closed)

Status: proposed decision accepted by the project owner on 2026-10-16. No further retrieval experiments before generation.

1. **Hybrid (equal-weight RRF, k=60) did not help.** It lost to vector on dev in V1, V2 and V3 (recall down 0.05 to 0.10, MRR@10 down 0.14 to 0.18). Holdout was equal or slightly higher, on 8 questions. `rrf()` is correct (hand-worked examples and tests); the equal weighting is what does not suit this corpus.
2. **Why (supported by the counts, not proven):** BM25 is the weaker retriever (dev recall 0.59 to 0.64 against 0.81 for vector), yet RRF gives its ranks the same weight. It pulls FAQ-01 and SOP documents into the top 5 (FAQ-01 on 16 of 24 dev questions in V1 and V3, against 7 for vector). G-025 alone is 0.042 of the 0.057 V1 recall drop.
3. **Reranking is a promising experiment, not a proven improvement.** Dev is mixed (recall +0.010, hit@5 unchanged, MRR@10 -0.028). Holdout improves (recall +0.146, MRR@10 +0.271) on 8 questions. Per question: 7 improved, 4 regressed, 1 mixed, 20 unchanged; sign test p about 0.27. Cost: about 50 to 100 times the latency.
4. **Retrieval is near its ceiling on this corpus.** Vector already finds an expected document on every dev question (hit@5 1.000). Remaining misses are multi-document questions where part of the expected set is missing, and V1 and V3 have only 52 chunks, so depth 50 returns almost the whole index.
5. **Retrieval quality is not source authority.** Neither method uses certification, currentness or authority. Reranking raised FAQ-01 (Provisional, conflicting) in the dev top 5 from 7 to 11 questions.
6. **Decision.** Vector V1 is the default and the reference baseline. Hybrid and rerank stay as optional, documented code. No tuning of RRF weights, k or the reranker on 24 dev questions. Governance is handled in generation (Step 2.5) through certification labels, ordering and prompt rules. Rerank is judged on end-to-end answer quality in Step 3.1.
7. **What would change this:** a larger golden set, a weighted hybrid chosen on fresh questions, or a clear end-to-end gain from rerank in Step 3.1.
8. **Limits to state in the README:** 40 questions (24 dev, 8 answerable holdout), synthetic corpus, document-level metrics, questions drafted with Claude.

## Step 2.5 to 3.1 generation (answer prompts v1 and v2, judge `gemini-3.5-flash-lite`)

### What was run

Retrieval for every answer: V1 chunking, vector top 5. Prompts: `answer_v1` (the default) and `answer_v2` (`answer_v1` plus one completeness rule). Each answer is checked in code (every cited chunk must have been retrieved) and then judged on two things: key-fact coverage (one yes or no per key fact in the golden set) and faithfulness (is every claim supported by the retrieved chunks). Dev was run for both versions. Holdout was run once per version after the rubric, prompts and pass rule were locked (`results/generation/holdout_runs.txt`). The judge was checked first with planted failures (9 of 9) and then against 10 answers hand-graded blind (bar set before any number: 85% on key facts, 8 of 10 on faithfulness).

### Results

| | Dev v1 | Dev v2 | Holdout v1 | Holdout v2 |
|---|---|---|---|---|
| Questions (answerable / unanswerable) | 24 / 6 | 24 / 6 | 8 / 2 | 8 / 2 |
| Key-fact coverage | 75.6% (59 of 78) | 79.5% (62 of 78) | 60.9% (14 of 23) | 65.2% (15 of 23) |
| Answers with every key fact | 16 of 24 | 18 of 24 | 3 of 8 | 4 of 8 |
| Faithful answers (non-refused) | 22 of 22 | 22 of 22 | 8 of 8 | 7 of 8 |
| Unsupported claims | 0 | 0 | 0 | 1 (G-028) |
| Wrong refusals (answerable) | 2 (G-006, G-015) | 2 (G-006, G-015) | 0 | 0 |
| Correct refusals (unanswerable) | 6 of 6 | 6 of 6 | 2 of 2 | 2 of 2 |
| Retries triggered, policy refusals, errors | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 | 0, 0, 0 |
| Mean tokens per query (in / out) | 1,884 / 103 | 1,922 / 116 | 1,961 / 83 | 1,999 / 87 |
| Cost per query | $0.00082 | $0.00087 | $0.00080 | $0.00082 |
| Model-call latency p50 / p95 | 4.7 s / 8.4 s | 4.0 s / 6.4 s | not reported | not reported |

Combined key facts: v1 73 of 101, v2 77 of 101.

Cost uses $0.30 per 1M input and $2.50 per 1M output tokens from a third-party price page dated 2026-10-19 (recheck before quoting). The runs themselves used the free tier. Holdout latency is not reported: single calls took up to 282 s on the free tier, which is queueing noise, not model speed. Dev latency is the model call only (retrieval adds a median of about 0.2 s, range 15 to 900 ms).

### Pass rule and decision

Written on 2026-10-21 before the holdout run: v2 generalizes if its holdout coverage is at least v1's, faithfulness is not lower, there are no new wrong refusals and no unsupported claims.

| Condition | v2 against v1 | Result |
|---|---|---|
| Coverage at least v1 | 65.2% against 60.9% | pass |
| Faithfulness not lower | 87.5% against 100% | fail |
| No new wrong refusals | 0 and 0 | pass |
| No unsupported claims | 1 against 0 | fail |

Outcome: `answer_v1` stays the default (`docs/decisions.md` rows 21 and 22).

### Verified findings

1. **Judge validation changed one number openly.** First agreement with the hand grades: 80.6% on 31 key facts (bar 85%). All six misses were G-005 on v1. The key facts said "Head of Finance Analytics" and similar, the question asked for teams, v1 answered with team names (judge 0 of 6) and v2 repeated "Head of" (6 of 6). G-005's key facts were changed to team names and G-005 was rejudged for both versions only. Second agreement: 100%, kappa 1.0, faithfulness 10 of 10. The bar and the human grades were not changed. Only 2 of the 31 human grades were "no", so a lenient judge is weakly tested.
2. **The v2 gain on dev is small and mostly one question.** Only G-017 and G-027 differ between the versions and v2 wins both. G-017 was one of the questions v2 was designed around, so G-027 is the independent evidence. Four single-fact misses (a date, "loyalty tier", "Do not use for reporting", "Status: Provisional") were not fixed by the completeness rule in either version.
3. **The holdout unsupported claim is real, not a judge error.** The retrieved chunks for G-028 never stated the owner of KPI-020 (the glossary chunk was missed). The only "Owner: Head of Digital Product" in context belonged to an action. v1 said the owner is not stated. v2 answered "owned by the Head of Digital Product" with a citation. That is true in the real glossary, but not supported by what the model was shown. A completeness rule can push a model to fill a gap by inference, which is the wrong trade in a governance setting.
4. **Hybrid does not fix G-028.** In the demo comparison for "Who owns KPI-020 and what has to be fixed before it can be certified?", the vector top 5 holds the review minutes at rank 3 and hybrid moves them to rank 1, but neither the vector top 5 nor hybrid's top 5 holds the KPI-020 document or the glossary (one question, one screenshot, not a full run). This matches the earlier retrieval result, where hybrid improved G-028's document-level rank (reciprocal rank 0.33 to 1.00) because the minutes moved up, not because the owner source was found.
5. **The trap question works, with run-to-run variation.** G-018 (Active Customer days) was answered with the certified 30-day rule in every run seen. In the dev run the answer cited KPI-006 and the informal FAQ-01; in two later live demo runs it cited only KPI-006. Same question, same model, temperature 0, different citations. The retry was never triggered by a real answer in these 80 records or in the hand tests, so it is unit-tested only.

### Not done on purpose

- No v3 prompt (for example "if the owner is not stated, say so"). The holdout has been seen, so a new prompt needs fresh questions. Future work.
- No separate diagnostic of vector retrieval on bare KPI codes. G-028 and the ad hoc KPI-010 test (`results/step2_5_hand_tests.md`, test 4) are the evidence.
- Certified-first ordering of context chunks. No evidence called for it.
- No tuning of RRF weights, rerank settings or prompts against the holdout.

## Limits to state in the README

- 40 questions: 30 dev and 10 holdout, with 8 answerable holdout questions. One question moves a holdout score by 0.125 (retrieval) or about 4 percentage points (key facts). Results show direction, not proof.
- Synthetic corpus of 52 chunks. Depth 50 returns almost the whole index, so retrieval depth results will not transfer to a large corpus.
- 30 of the 40 golden questions were drafted with Claude and reviewed by the project owner.
- Document-level retrieval metrics, not chunk-level.
- The judge and the answer model are the same model. Checked against 10 hand-graded answers (31 key facts), where only 2 human grades were "no".
- Three holdout questions have soft key facts, listed before the run and not fixed: G-004 (terse facts), G-028 (compound facts that go beyond the question), G-032 (the second fact does not check the warning-banner action).
- Temperature 0 is not fully repeatable. The same question can give different wording and different citations on different days.
- Holdout latency is unusable (free-tier queueing). Cost is a calculation from a third-party price page, not a bill.
- The demo's BM25 and hybrid view is a read-only comparison. The answer always comes from vector V1.
