# Step 2.5 hand tests (grounded generation)

Real Gemini calls, 2026-10-16, run in the Windows `.venv` with `scripts/try_generate.py` (vector V1 top 5, prompt `answer_v1`, model `gemini-3.5-flash-lite`, temperature 0). Code at commit `2ffae85`. Nothing below was edited. No citation validation existed yet, so the checks are by hand.

## Baseline: tests 1 to 3 (before validation and the pipeline)

### Test 1. Definition, G-013: "Customer churn rate - how is that calculated?"
Retrieved: KPI-007::v1::0, KPI-007-V1::v1::0, KPI-011::v1::0, KPI-010::v1::0, KPI-012::v1::0
refused: False
answer: Customer Churn Rate (KPI-007 v2) is calculated as the percentage of customers in the start base with no purchase for 180 days by quarter end divided by the customers in the start base, multiplied by 100 [KPI-007::v1::0]. The start base consists of every identified customer with at least one completed order in the 180 days before the quarter starts [KPI-007::v1::0]. A customer who closes their account also counts as churned immediately [KPI-007::v1::0]. The older deprecated v1 formula calculated the share of loyalty members who closed their account in a month [KPI-007-V1::v1::0].
citations: KPI-007::v1::0, KPI-007-V1::v1::0
usage: in=2370 out=215 thinking=0 latency=9661 ms
Hand check: formula, 180-day window, start base and the v1 description match the chunks; every citation was retrieved. Gaps: the dashboards (Customer 360 Dashboard, Executive KPI Pack) are missing although the question asks and the chunk lists them; no explicit "v1 must not be used for reporting".

### Test 2. Unanswerable, G-036: "Who is the CEO of Kestrel Retail Group?"
Retrieved: POL-05::v1::0, POL-01::v1::0, KPI-007::v1::0, POL-04::v1::0, SOP-08::v1::0
refused: True
answer: I could not find this in the governed documents.
citations: (none)
usage: in=2373 out=24 thinking=0 latency=11238 ms
Hand check: correct refusal with the exact sentence, although 5 chunks were retrieved (the model refused, not empty retrieval).

### Test 3. Governance trap, G-018: "How many days do we use to count an Active Customer?"
Retrieved: KPI-006::v1::0, FAQ-01::v1::0, KPI-020::v1::0, CAT-08::v1::0, KPI-007::v1::0
refused: False
answer: An Active Customer is counted using a 30-day window, which is the only certified definition [KPI-006::v1::0]. Any other window, such as 90 days mentioned in informal team notes, is not certified [KPI-006::v1::0, FAQ-01::v1::0].
citations: KPI-006::v1::0, FAQ-01::v1::0
usage: in=2034 out=110 thinking=0 latency=10167 ms
Hand check: matched all five written predictions (30 days; KPI-006 wins; the 90-day figure is called informal and not certified; cites KPI-006 and FAQ-01 only as non-authoritative; refused False). POL-01 was not retrieved, so the "informal definitions have no standing" key fact cannot come from the policy. Caveat: KPI-006's own text says 90 days is not certified, so this is the easy version of the trap.

## Integrated pipeline: tests 3b, 4 to 6 (`python -m rag.ask`, validation and trace logging active)

Same date, model and prompt. Every call is one line in `results/traces.jsonl`. HF and SDK warning lines omitted; everything else verbatim.

### Test 3b. G-018 rerun through the pipeline: "How many days do we use to count an Active Customer?"
Retrieved: KPI-006::v1::0, FAQ-01::v1::0, KPI-020::v1::0, CAT-08::v1::0, KPI-007::v1::0
refused: False
answer: We use a 30-day window to count an Active Customer, which is the only certified definition [KPI-006::v1::0]. An informal team FAQ mentions 90 days, but that source is provisional and not authoritative [FAQ-01::v1::0].
citations: KPI-006::v1::0, FAQ-01::v1::0
validation: OK. usage: in=2034 out=99 thinking=0 retrieval=437 ms generation=9791 ms
Hand check: same retrieved chunks as test 3, different wording at temperature 0 (the earlier run said "informal team notes"). Now says "provisional", which can only come from the FAQ-01 certification label in the context. FAQ-01 is cited only to attribute the 90-day figure.

### Test 4. KPI-code question (ad hoc, not in the golden set): "What does KPI-010 measure and who owns it?"
Retrieved: SOP-01::v1::0, SOP-02::v1::0, SOP-03::v1::0, SOP-05::v1::0, POL-01::v1::0
refused: True
answer: I could not find this in the governed documents.
citations: (none)
validation: OK. usage: in=2312 out=24 thinking=0 retrieval=47 ms generation=7905 ms
Hand check: RETRIEVAL FAILURE, correct generation. KPI-010 was not in the top 5, so the model correctly refused instead of inventing (compare the ungrounded smoke-test answer). Vector search matched process words ("owns") to SOPs and ignored the KPI code. Validation says OK because it checks form, not retrieval. Not fixed here: noted as a limitation (exact-ID lookup is BM25's strength; no golden question is a bare KPI-code query).

### Test 5. Unanswerable value, G-034: "What was our customer churn rate last quarter?"
Retrieved: KPI-007::v1::0, KPI-007-V1::v1::0, KPI-012::v1::0, FAQ-01::v1::0, POL-05::v1::0
refused: True
answer: I could not find this in the governed documents.
citations: (none)
validation: OK. usage: in=2246 out=24 thinking=0 retrieval=45 ms generation=6755 ms
Hand check: PASS. KPI-007 (the churn definition) was retrieved, but the model did not explain the formula or state a number. The exact refusal sentence, no citations. One sample only.

### Test 6. Ownership and status, G-023: "Who owns Customer Lifetime Value and is it approved for board reporting?"
Retrieved: KPI-011::v1::0, FAQ-01::v1::0, CAT-08::v1::0, POL-01::v1::0, POL-05::v1::0
refused: False
answer: Customer Lifetime Value is owned by the Head of Customer Analytics and is not approved for board reporting [KPI-011::v1::0].
citations: KPI-011::v1::0
validation: OK. usage: in=1943 out=56 thinking=0 retrieval=40 ms generation=7540 ms
Hand check: PARTIAL PASS. Owner and "not approved for board reporting" are correct and cited. Key fact "Status: Provisional" (v0.7) is missing, and so is the Executive KPI Pack. No false claim.

## Summary of the six hand tests
- Grounding: no invented facts in any answer. Refusals: 2 of 2 correct (G-036, G-034).
- Citation validity (where validated, tests 3b to 6): all OK.
- Issues found: (1) test 4, vector retrieval missed a KPI asked for by code; (2) tests 1 and 6, accurate but incomplete answers (dashboards missing; Provisional status missing). Prompt rule 5 ("be concise") is a hypothesis for (2), untested.
- FAQ-01 appeared in the retrieved set in 4 of the 7 runs (tests 3, 3b, 5 and 6), so the certification label in the context matters.
- Not decided here: any retrieval or prompt change. Step 3.1 should measure key-fact coverage on dev before any prompt v2, and never tune on holdout.
