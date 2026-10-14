# Golden set audit

Verified against the real corpus (`data/processed/documents.jsonl`). Edit the JSONL, not this file.

| ID | Status | Reason | Correction |
|---|---|---|---|
| G-001 | Fix | 7 expected docs made recall@5 hard; individual KPI files not needed to answer | Expected [CAT-02, POL-04]; V1 churn marked conflicting; rest related |
| G-002 | Refine | Deprecated v1 is the trap | conflicting KPI-007-V1 |
| G-003 | Fix | Two questions in one; reference ignored KPI/dashboard half; cited POL-04 without listing it as expected | Added CAT-02; removed the POL-04 claim so answer and labels agree |
| G-004 | Keep | Clear, POL-04 sufficient | none (holdout shares POL-04 with G-005, G-015) |
| G-005 | Refine | Catalog half only partly answered | Question clarified; SOP-04 added as expected; reference says the corpus has no separate glossary access process |
| G-006 | Fix | Vague scope, 12 docs, CAT-10/11 owned by supply chain but omitted | Scope KPIs and dashboards, expected [POL-04, CAT-01, CAT-04], reference shortened |
| G-007 | Keep | Formula plus dashboards, 3 docs reachable | none |
| G-008 | Refine | 6 expected docs, Recall@5 ceiling is 5/6 | Standard metric kept; report Recall@5 with the ceiling plus Recall@10 for this question |
| G-009 | Refine | Weak key fact (KPI-012) | Key facts: owner, linked KPI list |
| G-010 | Refine | Question wording unclear ("in the or?") | Reworded to sales_orders table |
| G-011 | Keep | Undefined "Sales $", no data; absent term confirmed | none |
| G-012 | Keep | Clear, KPI-002 sufficient | none |
| G-013 | Refine | Deprecated v1 is the trap | conflicting KPI-007-V1 |
| G-014 | Keep | 5 docs, all needed (KPI-001, CAT-07, CAT-12 sources, CAT-01/03 dashboards) | none |
| G-015 | Refine | Ambiguous "most important" | Answer states the glossary does not rank KPIs; Executive KPI Pack is the proxy; all seven KPIs in key_facts |
| G-016 | Keep | Clear | none |
| G-017 | Refine | Compares NRR with churn; v1 trap | conflicting KPI-007-V1 |
| G-018 | Refine | FAQ-01 holds conflicting 90 days | conflicting FAQ-01 |
| G-019 | Keep | Clear | note only |
| G-020 | Keep | Clear | none |
| G-021 | Keep | V1 is the target | none |
| G-022 | Keep | Clear | none |
| G-023 | Refine | Status and owner in KPI-011, board rule in POL-04 | related KPI-007 |
| G-024 | Keep | Clear after loader fix | none |
| G-025 | Keep | Clear after loader fix | none |
| G-026 | Keep | Clear | none |
| G-027 | Keep | POL-04 lists owners; KPI files confirm | none |
| G-028 | Keep | Clear | none |
| G-029 | Keep | Clear | none |
| G-030 | Refine | Answer cites SOP-01 as a pointer | SOP-01 related, not required |
| G-031 | Keep | Clear; overlaps G-003 on SOP-04 | none |
| G-032 | Keep | Clear | none |
| G-033 | Keep | Clear | none |
| G-034 | Refine | Real value not in corpus | related KPI-007 (definition only) |
| G-035 | Refine | No SQL in corpus | related KPI-001 (formula only) |
| G-036 | Refine | Absent terms checked | none |
| G-037 | Refine | No regional data | related KPI-013 (definition only) |
| G-038 | Refine | "employee" appears in corpus; only phrases are safe absent terms | added engagement score |
| G-039 | Keep | No energy content | none |
| G-040 | Keep | No 2027 content | none |

## Schema change

Two diagnostic fields added to every row: `conflicting_doc_ids` (deprecated or conflicting traps) and `related_insufficient_doc_ids` (related but not enough alone). Never scored. Validator checks them against the manifest and against overlap with `expected_doc_ids`. No retrieval or eval code exists yet that reads them.

## Decisions taken

- G-006: scope stays KPIs and dashboards; a table-ownership question can be added later.
- G-005: question and answer clarified; access steps only for dashboards and tables (SOP-04).
- G-015: Executive KPI Pack is the documented proxy for "most important", stated explicitly.
- G-002: live churn KPI only; KPI-007-V1 stays conflicting.
- Recall: no capped recall. G-008 is scored with standard Recall@5 (ceiling 5/6, documented) and Recall@10.

## New validator rule

Any POL, SOP, CAT or FAQ document cited in a reference answer must be expected, related or conflicting, so answers and labels cannot drift apart.

## Remaining note

Holdout overlap is unchanged: G-004 with G-005 and G-015 on POL-04, G-008 with G-009 and G-013 on CAT-01 and CAT-02.

## Labels v2 (three approved changes, supersede the rows above for G-001, G-005 and G-023)

Reviewed after the V1 to V3 baselines (runs 3 to 8), using development questions only. The evidence came from the source text and from the vector ranks of the expected documents; no retrieval code, metric or holdout label was changed.

| ID | Change | Why |
|---|---|---|
| G-001 | `expected_doc_ids` is now `[CAT-02]`; POL-04 moved to `related_insufficient_doc_ids`. The reference answer was trimmed to what CAT-02 supports. | CAT-02 alone holds the dashboard name, owner, 07:00 refresh, the six linked KPI ids and the six topic names, and it ranks first in every variant. POL-04 ranked 21 to 23 and is only needed for formal KPI names, which the reference now gives as a pointer. |
| G-023 | `expected_doc_ids` is now `[KPI-011]`; POL-04 moved to related. The second key fact was rewritten as content (`Owner: Head of Customer Analytics`, `Status: Provisional`). | KPI-011 alone states the owner, status, version 0.7 and "Not approved for board reporting or the Executive KPI Pack". The old key fact only existed in POL-04's line format. KPI-011 ranks first everywhere. |
| G-005 | Question rewritten to "Which KPI owner teams are represented in the KPI glossary?". POL-04 required, SOP-04 related. | The old question had two intents. No document defines KPI categories or says where the catalog is accessed, so it was ill-posed. The reference now says the glossary lists owners but does not define formal KPI categories, and makes no claim about catalog access. The `type` field stays `catalog`. |

G-001 reference answer structure: sentences 1 and 2 hold facts supported directly by CAT-02 (dashboard, owner, refresh, linked KPI ids, topics). Sentence 3 is a pointer to POL-04 and the KPI documents for formal names and statuses, and those documents are listed as related, not required.

Not changed: G-015 and G-006 (genuine near-miss retrieval cases, kept as hybrid and reranker test cases), every holdout label, and all other questions. A mechanical "unique key fact" rule was tried as a dry run and rejected, because it wrongly flagged required dashboard documents (for example in G-007 and G-013) and missed G-023.

Scores: runs 1 to 8 use labels v1 and stay unchanged. Reruns on these labels carry "labels v2" in the `notes` field of `results/runs.csv`. Absolute dev scores shift slightly, so compare configurations only within the same label version.

