# Step 2.6B: completeness experiment, summary

Question: does a prompt with one added completeness rule (answer_v2) cover more key facts than answer_v1
on the five dev questions? Retrieval (vector V1 top 5), context order, model (gemini-3.5-flash-lite),
temperature 0 and everything else are unchanged. answer_v2 = answer_v1 plus rule 6 only. Holdout not used.

Rubric: 14 key facts from golden/golden_set.jsonl (G-018: 2, G-013: 3, G-002: 3, G-017: 4, G-001: 2).
Rule fixed before the repeat runs: adopt v2 only if its mean coverage over three runs beats v1's mean by at
least one fact and v2 does not lose a key fact that v1 covered in two or more paired runs.

## Scores (14 facts)

| Run | G-018 | G-013 | G-002 | G-017 | G-001 | Total |
|---|---|---|---|---|---|---|
| v1 run 1 | 2 | 3 | 2 | 3 | 2 | 12 |
| v1 run 2 | 2 | 3 | 1 | 3 | 2 | 11 |
| v1 run 3 | 2 | 3 | 1 | 4 | 2 | 12 |
| v2 run 1 | 2 | 3 | 2 | 4 | 2 | 13 |
| v2 run 2 | 2 | 3 | 2 | 4 | 2 | 13 |
| v2 run 3 | 2 | 3 | 2 | 4 | 2 | 13 |

v1 mean 11.7 (range 11 to 12). v2 mean 13.0 (13 in every run). Mean answer length: v1 about 342 characters,
v2 about 422 (+24%). All 30 answers valid, attempt_count 1, no refusals, no errors.

## Blind re-score

A fresh scorer saw only shuffled run codes (A to F), the questions and the answers, with the rubric. Its
per-question scores matched the first (unblinded) scoring in all 30 of 30 cases. Files: blind/blind_sheet.txt
and blind/blind_mapping_revealed.json (A=v2 run 2, B=v2 run 1, C=v2 run 3, D=v1 run 1, E=v1 run 3, F=v1 run 2).

## Reading

- Main gain: v2 states the NRR exclusion of new customers in 3 of 3 runs; v1 in 1 of 3.
- G-002 shifts rather than improves: v1 often drops "180 days"; v2 keeps it but usually drops 2026-04-01.
- v2 adds details beyond the key facts (owner, refresh time, start-base definition). All checked against the
  corpus; none unsupported.
- Decision rule passes (mean gain 1.3 facts; v2 loses a v1-covered fact in 1 of 3 paired runs).
- Limits: five questions, three runs per version, one-fact margin, single rubric. Not evidence of
  generalisation.

## Status

answer_v1 remains the default (PROMPT_VERSION in src/rag/generate.py). answer_v2 is committed as an
experimental prompt only. The default decision waits for Step 3.1 (dev plus holdout).
Trace files in this folder carry prompt_version=answer_v1 for both versions (pipeline records the default);
use the results files to tell versions apart.
