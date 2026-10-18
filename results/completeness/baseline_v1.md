# Step 2.6B baseline: answer_v1, five dev questions

Recorded from the user's real Gemini runs (rag.ask, vector V1 top 5, model gemini-3.5-flash-lite,
prompt answer_v1, repo at commit 3b44f26). Trace lines: results/traces.jsonl (last five lines).
All five: refused=False, validation OK, attempt_count=1, no error.

Key-fact coverage is scored by hand against the key_facts in golden/golden_set.jsonl. This is my
reading, not the judge's. The same rubric must be used for the v2 run.

| ID | Key facts (golden) | Covered | Missing |
|---|---|---|---|
| G-018 | 2 | 2 | none |
| G-013 | 3 | 3 | none (deprecation note expected by decision 17 is absent, not a key fact) |
| G-002 | 3 | 2 | 2026-04-01 effective date |
| G-017 | 4 | 3 | "New customers acquired during the period are excluded" |
| G-001 | 2 | 2 | none |
| **Total** | **14** | **12** | |

Context check: the missing G-002 date is in the retrieved KPI-007 chunk text; the missing G-017
exclusion sentence is in the retrieved KPI-010 chunk text. The model omitted facts that were in context.

## Answers (verbatim)

### G-018 How many days do we use to count an Active Customer?
Retrieved: KPI-006::v1::0, FAQ-01::v1::0, KPI-020::v1::0, CAT-08::v1::0, KPI-007::v1::0
Answer: An Active Customer uses a 30-day window, which is the only certified definition [KPI-006::v1::0]. An informal team FAQ mentions a 90-day window, but that source is provisional and not authoritative [FAQ-01::v1::0].
Citations: KPI-006::v1::0, FAQ-01::v1::0

### G-013 Customer churn rate - how is that calculated? What dashboards use it?
Retrieved: KPI-007::v1::0, KPI-007-V1::v1::0, CAT-02::v1::0, CAT-05::v1::0, KPI-011::v1::0
Answer: Customer Churn Rate is calculated as the number of customers in the start base with no purchase for 180 days by quarter end divided by the customers in the start base, multiplied by 100 [KPI-007::v1::0]. It is used in the Customer 360 Dashboard and the Executive KPI Pack [KPI-007::v1::0].
Citations: KPI-007::v1::0

### G-002 What KPIs around customer churn which are enabled right now?
Retrieved: KPI-007::v1::0, KPI-007-V1::v1::0, CAT-02::v1::0, CAT-08::v1::0, CAT-03::v1::0
Answer: Customer Churn Rate (KPI-007) version 2.0 is the certified KPI enabled for tracking customer churn, defined as the share of recently active customers who stopbuying from Kestrel for 180 days [KPI-007::v1::0]. Version 1 (KPI-007-V1) is deprecated and must not be used [KPI-007-V1::v1::0].
Citations: KPI-007::v1::0, KPI-007-V1::v1::0

### G-017 What is NRR and how is it different from churn?
Retrieved: KPI-010::v1::0, KPI-007::v1::0, KPI-007-V1::v1::0, KPI-004::v1::0, KPI-012::v1::0
Answer: Net Revenue Retention (NRR) measures how much net revenue Kestrel keeps from an existing group of customers over 12 months, including growth and losses from customers who stop buying [KPI-010::v1::0]. In contrast, Customer Churn Rate measures the share of recently active customers who stop buying from Kestrel, defined as 180 days passing without a completed purchase [KPI-007::v1::0].
Citations: KPI-010::v1::0, KPI-007::v1::0

### G-001 What are key KPIs and Dashboards serving Customer Domain. Give me strcutured asnwer.
Retrieved: CAT-02::v1::0, CAT-03::v1::0, SOP-06::v1::0, CAT-06::v1::0, CAT-08::v1::0
Answer: The Customer Domain includes the following dashboards and data assets:
- Customer 360 Dashboard (CAT-02): Provides a single view of customer health including activity, churn, retention, lifetime value, repeat buying, and NPS, linked to KPIs KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, and KPI-013 [CAT-02::v1::0].
- Customers table (CAT-08): Holds customer records such as loyalty tier, account status, first order date, and acquisition channel, linked to KPIs KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, and KPI-014 [CAT-08::v1::0].
Citations: CAT-02::v1::0, CAT-08::v1::0
