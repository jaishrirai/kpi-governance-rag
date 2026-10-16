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

## Remaining hand tests (4 to 6)
To be run through the integrated pipeline after citation validation: a KPI-code question, an unanswerable KPI-value question such as G-034, and a catalog or ownership question.
