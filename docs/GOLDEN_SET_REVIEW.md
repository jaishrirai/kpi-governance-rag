# Golden set review

Generated from `golden/golden_set.jsonl` by `scripts/golden_to_markdown.py`. Edit the JSONL, not this file.

Each question has two kinds of ground truth:

- **Expected documents**: used to score retrieval (recall@5, MRR@10). Document level, so it works for V1, V2 and V3.
- **Reference answer**: used to score the generated answer in Step 3.1. Every key fact in it is checked by `scripts/validate_golden.py` against the expected documents.

H = holdout (never tuned against). Author `human` = your question, `claude` = drafted by Claude.

## G-001 | catalog | author: human

**Question:** What are key KPIs and Dashboards serving Customer Domain. Give me strcutured asnwer.

**Expected documents:** CAT-02, POL-04

**Conflicting (trap) documents:** KPI-007-V1

**Related but not sufficient:** KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-013

**Reference answer:** Customer-domain KPIs: Active Customer (30-day) KPI-006, Customer Churn Rate KPI-007, Net Revenue Retention KPI-010, Customer Lifetime Value KPI-011 (Provisional), Repeat Purchase Rate KPI-012 and Net Promoter Score KPI-013. The dashboard is the Customer 360 Dashboard (CAT-02), owned by the Head of Customer Analytics and refreshed daily at 07:00.

**Notes:** draft ids by Claude, owner to confirm; list-style question | AUDIT: expected cut from 7 to 2 sufficient docs: CAT-02 lists the dashboard and its six linked KPIs, POL-04 gives the KPI names. Individual KPI files are related but not required. KPI-007-V1 is a deprecated trap. Recall@5 is now reachable.

## G-002 | definition | author: human

**Question:** What KPIs around customer churn which are enabled right now?

**Expected documents:** KPI-007

**Conflicting (trap) documents:** KPI-007-V1

**Related but not sufficient:** none

**Reference answer:** Customer Churn Rate v2 (KPI-007) is the live, Certified churn KPI: a customer has churned after 180 days without a purchase, in force since 2026-04-01. Churn v1 (KPI-007-V1, account closures only) is Deprecated and must not be used.

**Notes:** trap: KPI-007-V1 is Deprecated and must not be the answer | AUDIT: KPI-007-V1 (deprecated) marked conflicting. Scope is only the live churn KPI; kept. | DECISION: confirmed scope: live churn KPI only; KPI-007-V1 stays conflicting.

## G-003 | process | author: human

**Question:** Customer level data - What data I can access. I am working on a use case, I need to see what KPIs and dashboards already exist?

**Expected documents:** CAT-08, SOP-04, POL-03, CAT-02

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The customers table (CAT-08) has one row per identified customer: loyalty tier, account status, first order date, acquisition channel and staff and test flags. It is owned by the Head of Customer Analytics and classified Confidential. Access needs a request in the data service portal, line manager approval and data owner approval (SOP-04), and Confidential data must not be entered into public AI tools (POL-03). For existing KPIs and dashboards on customer data, the Customer 360 Dashboard (CAT-02) is the live dashboard; it shows KPI-006, KPI-007, KPI-010, KPI-011, KPI-012 and KPI-013.

**Notes:** draft ids by Claude, owner to confirm; two questions in one | AUDIT: original reference ignored the second half (which KPIs and dashboards exist). Added CAT-02 as expected; POL-04 is related but not required. | DECISION: reference no longer cites POL-04, so expected docs and answer agree.

## G-004 (H) | catalog | author: human

**Question:** Is there a KPI list which you can share with me so that I can plan for a business meeting?

**Expected documents:** POL-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Yes. The KPI Glossary Summary (POL-04) is the official list: 20 KPIs (KPI-001 to KPI-020), each with owner, status (15 Certified, 5 Provisional) and a short definition. Deprecated versions are not listed.

**Notes:** POL-04 is the official KPI glossary

## G-005 | catalog | author: human

**Question:** Can you tell me what are main areas/subject matter in which KPIs could be categorised? Is there a catalog which I can access? (KPI categories, and where the KPI list or catalog is found)

**Expected documents:** POL-04, SOP-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The official KPI list is the KPI Glossary Summary (POL-04). It groups KPIs by owner area: Finance (KPI-001 to 003), Sales (KPI-004, 005, 008, 009), Customer (KPI-006, 007, 010 to 013), Marketing (KPI-014, 015), Supply Chain (KPI-016 to 019) and Digital (KPI-020). Dashboards and source tables are listed in the data catalog, and access to them is requested through the data service portal (SOP-04). The corpus does not describe a separate access process for the KPI glossary itself.

**Notes:** confirmed: key is POL-04 only. The answer is the KPI domains (Finance, Sales, Customer, Marketing, Supply Chain, Digital); CAT rows also help but are not required, so recall@5 stays reachable | AUDIT: second half ("is there a catalog I can access") is only partly answered; the data catalog is the CAT documents and SOP-04 explains access. Kept POL-04 as the only required doc so recall@5 stays reachable. Human decision: add the catalog part to the reference? | DECISION: question clarified, SOP-04 added as expected because the reference describes catalog access; no invented access steps for the glossary.

## G-006 | ownership | author: human

**Question:** What are key areas being handled by head of finnance and head of supply chain? (KPIs and dashboards)

**Expected documents:** POL-04, CAT-01, CAT-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** KPI-001, KPI-002, KPI-003, KPI-016, KPI-017, KPI-018, KPI-019

**Reference answer:** Head of Finance Analytics owns Net Revenue (KPI-001), Gross Margin % (KPI-002), Days Sales Outstanding (KPI-003) and the Executive KPI Pack dashboard (CAT-01). Head of Supply Chain Analytics owns Inventory Turnover (KPI-016), Stockout Rate (KPI-017), On-Time Delivery % (KPI-018), Return Rate (KPI-019) and the Supply Chain Control Tower dashboard (CAT-04). Each also owns source tables in the data catalog (not listed here).

**Notes:** draft ids by Claude, owner to confirm; multi-document list question | AUDIT: expected cut from 12 to 3: POL-04 holds every KPI owner, CAT-01 and CAT-04 the dashboards. The question is vague, so scope fixed to KPIs and dashboards; table ownership (CAT-09, 10, 11, 12) dropped from the reference. Human decision: confirm this scope or split into two questions. | DECISION: confirmed: keep KPIs and dashboards scope; a table-ownership question may be added later.

## G-007 | definition | author: human

**Question:** What is the formula of Net Revenue and which dashboard have that KPIs?

**Expected documents:** KPI-001, CAT-01, CAT-03

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Net Revenue = Gross sales value - Discounts - Returns and refunds - Sales tax. It appears on the Executive KPI Pack and the Sales Performance Dashboard.

**Notes:** KPI-001 is linked to CAT-01 and CAT-03 in the catalog

## G-008 (H) | catalog | author: human

**Question:** Can you enlist all key dashboards along with their description?

**Expected documents:** CAT-01, CAT-02, CAT-03, CAT-04, CAT-05, CAT-06

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Six dashboards: Executive KPI Pack (board-level pack of headline Certified KPIs, monthly); Customer 360 Dashboard (customer health: activity, churn, retention, lifetime value, repeat buying, NPS; daily 07:00); Sales Performance Dashboard (revenue, order value, conversion, basket size, footfall conversion, returns; daily 07:00); Supply Chain Control Tower (stock and fulfilment; hourly); Marketing Effectiveness Dashboard (paid media acquisition cost and ROAS; Provisional; daily 09:00); Digital Engagement Dashboard (app and web engagement; Provisional; daily 08:00).

**Notes:** list-style question, 6 dashboards | AUDIT: six expected docs, so plain recall@5 is capped at 5/6. Needs the capped-recall rule in Step 2.2. Holdout: shares CAT-01/CAT-02 with dev questions G-009 and G-013. | DECISION: metric stays standard. Report Recall@5 with its documented 5/6 ceiling, plus Recall@10 for this question. No capped recall rule.

## G-009 | catalog | author: human

**Question:** Customer 360 Dashboards - give me all details about it.

**Expected documents:** CAT-02

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The Customer 360 Dashboard (CAT-02) is a Certified Customer-domain dashboard owned by the Head of Customer Analytics, refreshed daily at 07:00. It is a single view of customer health: activity, churn, retention, lifetime value, repeat buying and NPS, and Provisional KPIs are labelled on their tiles. Linked KPIs: KPI-006, 007, 010, 011, 012, 013.

**Notes:** AUDIT: key fact KPI-012 alone was weak; replaced with owner and the full linked KPI list.

## G-010 | catalog | author: human

**Question:** Sales orders - give me all details available for the sales_orders table.

**Expected documents:** CAT-07

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The sales_orders table (CAT-07) has one row per order line across store, app and web. It holds order id, customer id, channel, store, values, discounts, tax, landed cost, item count, session id, last paid click and daily store footfall. It is owned by the Head of Sales Analytics, Certified and refreshed hourly.

**Notes:** typo at the end is kept on purpose; sales_orders table | AUDIT: wording fixed ("in the or?" was unclear; the intent is the sales_orders table CAT-07). Human question reworded.

## G-011 | unanswerable | author: human

**Question:** What is Sales $ in value happened in last month?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** the corpus has definitions only, no actual figures; correct behaviour is to refuse | AUDIT: absent term "last month" confirmed absent. "Sales $" is not a defined metric, which makes refusal the right behaviour.

## G-012 (H) | definition | author: human

**Question:** How are gross margins calculated in the org? At what granularity level is the information available?

**Expected documents:** KPI-002

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Gross Margin % = (Net Revenue - Cost of goods sold) / Net Revenue x 100, where COGS is the landed cost of items sold including inbound freight. It is reported monthly and year to date, split by product category and channel; concession sales are excluded.

**Notes:** ids drafted by Claude from the KPI file, owner to confirm; two-part question (formula + grain: monthly and YTD by category and channel)

## G-013 | definition | author: human

**Question:** Customer churn rate - how is that calculated? What dashboards use it?

**Expected documents:** KPI-007, CAT-02, CAT-01

**Conflicting (trap) documents:** KPI-007-V1

**Related but not sufficient:** none

**Reference answer:** Churn Rate % = customers in the start base with no purchase for 180 days by quarter end / customers in the start base x 100. The start base is every identified customer with at least one completed order in the 180 days before the quarter starts. It is used on the Customer 360 Dashboard and the Executive KPI Pack. The v1 version is Deprecated.

**Notes:** ids drafted by Claude, owner to confirm; trap: KPI-007-V1 is Deprecated and must not be the answer; overlaps with G-002

## G-014 | catalog | author: human

**Question:** Net Revenue - where does this KPI get populated from? In which dashboards is it used?

**Expected documents:** KPI-001, CAT-01, CAT-03, CAT-07, CAT-12

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Net Revenue (KPI-001) is calculated from the sales_orders table (gross value, discount and tax per order) and the returns table (refunded value and refund date). It appears on the Executive KPI Pack and the Sales Performance Dashboard.

**Notes:** ids drafted by Claude, owner to confirm; source tables sales_orders (CAT-07) and returns (CAT-12), dashboards CAT-01 and CAT-03; overlaps with G-007

## G-015 | catalog | author: human

**Question:** From the KPI glossary, pull the most important KPIs and tell me.

**Expected documents:** POL-04, CAT-01

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The glossary (POL-04) does not rank KPIs by importance, so "most important" is not defined in the corpus. The closest documented proxy is the set of headline KPIs in the Executive KPI Pack (CAT-01), which is used for board reporting: Net Revenue, Gross Margin %, Days Sales Outstanding, Active Customer, Customer Churn Rate, Net Revenue Retention and Net Promoter Score.

**Notes:** ids drafted by Claude, owner to confirm; ambiguous: 'most important' is not defined in the corpus, best evidence is the Executive KPI Pack headline set (7 KPIs) plus the glossary; overlaps with G-004 | AUDIT: ambiguous: "most important" is undefined. Kept the Executive KPI Pack headline set as best evidence. Overlaps with G-004 (holdout) and G-005 (dev) on POL-04. Human decision. | DECISION: Executive KPI Pack accepted as proxy with explicit qualification; all seven KPIs in key_facts.

## G-016 (H) | definition | author: claude

**Question:** whats the formula for CAC and does it include agency fees?

**Expected documents:** KPI-014

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** CAC = acquisition marketing spend in the period / new customers acquired in the period. Yes, agency fees are included in spend from v1.1 (2025-12-01); brand and retention campaigns are excluded.

**Notes:** drafted by Claude, owner to review; abbreviation + typo style; agency fees included from v1.1

## G-017 | definition | author: claude

**Question:** What is NRR and how is it different from churn?

**Expected documents:** KPI-010, KPI-007

**Conflicting (trap) documents:** KPI-007-V1

**Related but not sufficient:** none

**Reference answer:** NRR (KPI-010) measures how much net revenue is kept from an existing customer cohort over 12 months: current 12-month net revenue from the base cohort / prior 12-month net revenue from the same cohort x 100, excluding new customers. Churn Rate (KPI-007) counts the share of start-base customers with no purchase for 180 days. NRR is revenue-based and can exceed 100%; churn is a customer count.

**Notes:** drafted by Claude, owner to review; two KPIs; NRR is revenue-based, churn counts customers

## G-018 | definition | author: claude

**Question:** How many days do we use to count an Active Customer?

**Expected documents:** KPI-006, POL-01

**Conflicting (trap) documents:** FAQ-01

**Related but not sufficient:** none

**Reference answer:** 30 days. Active Customer (KPI-006) is an identified customer with at least one completed purchase in the last 30 days, and the 30-day window is the only certified definition. The 90-day figure in the Customer Team FAQ is informal and has no standing; informal definitions that conflict with a Certified KPI do not apply (POL-01).

**Notes:** drafted by Claude, owner to review; TRAP: FAQ-01 says 90 days (informal, Provisional); certified answer is 30 days (KPI-006); POL-01 says informal definitions have no standing | AUDIT: FAQ-01 has the conflicting 90-day figure and is intentionally not required; a good answer must prefer KPI-006.

## G-019 | definition | author: claude

**Question:** What is the difference between Active User and Active Customer?

**Expected documents:** KPI-020, KPI-006

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Active Customer (KPI-006, Certified) needs at least one completed purchase in any channel in the last 30 days. Active User (KPI-020, Provisional) is a logged-in app user with at least one session in the last 30 days; no purchase is needed. They are different KPIs and must not be mixed.

**Notes:** drafted by Claude, owner to review; near-duplicate names: KPI-020 counts app logins, KPI-006 needs a purchase | AUDIT: shares KPI-020 with holdout G-028 (leakage risk is low, different intent).

## G-020 (H) | definition | author: claude

**Question:** How is DSO calculated and which customers does it cover?

**Expected documents:** KPI-003

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** DSO = (accounts receivable at period end / credit sales in the period) x number of days in the period. It covers credit sales to wholesale partners and corporate gifting clients; retail sales paid at checkout are out of scope.

**Notes:** drafted by Claude, owner to review; abbreviation; B2B credit sales only

## G-021 | definition | author: claude

**Question:** What did the old churn rate (v1) measure and why was it replaced?

**Expected documents:** KPI-007-V1, KPI-007

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Churn v1 (KPI-007-V1) was the share of loyalty members who close their loyalty account in a month. It was replaced because most customers who stop buying never close their account, so it understated churn, and customers without a loyalty account were invisible. It is Deprecated and replaced by KPI-007 v2 (180 days without a purchase) from 2026-04-01; it must not be used for reporting.

**Notes:** drafted by Claude, owner to review; asks about the Deprecated KPI on purpose; a good answer says it is Deprecated and points to KPI-007 | AUDIT: KPI-007-V1 is the target here, not a trap.

## G-022 | definition | author: claude

**Question:** How do we calculate NPS and who counts as a detractor?

**Expected documents:** KPI-013

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** NPS = % promoters - % detractors. Detractors score 0 to 6; promoters score 9 or 10 and passives (7 or 8) are in neither group. It comes from a 0 to 10 survey question and ranges from -100 to +100.

**Notes:** drafted by Claude, owner to review; abbreviation; detractors score 0 to 6

## G-023 | ownership | author: claude

**Question:** Who owns Customer Lifetime Value and is it approved for board reporting?

**Expected documents:** KPI-011, POL-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** KPI-007

**Reference answer:** Customer Lifetime Value (KPI-011) is owned by the Head of Customer Analytics. It is Provisional (v0.7) and not approved for board reporting or the Executive KPI Pack.

**Notes:** drafted by Claude, owner to review; Head of Customer Analytics; Provisional, not for the Executive KPI Pack

## G-024 (H) | ownership | author: claude

**Question:** Who is accountable for the marketing effectivness dashboard and how often does it refresh?

**Expected documents:** CAT-05

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The Marketing Effectiveness Dashboard (CAT-05) is owned by the Head of Marketing Analytics and refreshes daily at 09:00. It is Provisional until the attribution review closes.

**Notes:** drafted by Claude, owner to review; typo; Head of Marketing Analytics, daily 09:00, Provisional | AUDIT: shares CAT-05 with nothing else; clean holdout.

## G-025 | ownership | author: claude

**Question:** Which team owns the customers table, how often is it refreshed and how sensitive is the data?

**Expected documents:** CAT-08

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The customers table (CAT-08) is owned by the Head of Customer Analytics, refreshed daily at 05:00 and classified Confidential.

**Notes:** drafted by Claude, owner to review; Head of Customer Analytics, daily 05:00, Confidential

## G-026 | ownership | author: claude

**Question:** Who chairs the KPI Council?

**Expected documents:** SOP-01, POL-01

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The KPI Council is chaired by the Head of Data Governance.

**Notes:** drafted by Claude, owner to review; Head of Data Governance

## G-027 | ownership | author: claude

**Question:** Which KPIs does the Head of Marketing Analytics own?

**Expected documents:** KPI-014, KPI-015, POL-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The Head of Marketing Analytics owns Customer Acquisition Cost (KPI-014, Certified) and Marketing ROI (ROAS) (KPI-015, Provisional).

**Notes:** drafted by Claude, owner to review; list-style; KPI-014 Certified, KPI-015 Provisional | AUDIT: overlaps G-024 only through owner naming; fine.

## G-028 (H) | ownership | author: claude

**Question:** Who owns KPI-020 and what has to be fixed before it can be certified?

**Expected documents:** KPI-020, POL-05, POL-04

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** KPI-020 Active User (app 30-day) is owned by the Head of Digital Product. Before it can be certified, the duplicate app user ids (reinstalling the app creates a second id for the same person) must be fixed; that action is due 2026-10-31.

**Notes:** drafted by Claude, owner to review; code lookup; Head of Digital Product; duplicate user ids, action due 2026-10-31

## G-029 | process | author: claude

**Question:** How does a KPI go from Provisional to Certified?

**Expected documents:** SOP-01

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The KPI owner submits the definition (it starts as Provisional, version below 1.0). The data steward checks that sources and dashboards are in the data catalog and runs a two-month parallel test that must reconcile within 1% against an independent calculation. The owner presents to the monthly KPI Council; if approved the version becomes 1.0 and the status Certified, and the glossary is updated within 5 working days. Certified KPIs are reviewed every 12 months.

**Notes:** drafted by Claude, owner to review; two-month parallel test, KPI Council approval

## G-030 | process | author: claude

**Question:** I want a new KPI added. What are the steps and how long does the data steward take to respond?

**Expected documents:** SOP-02

**Conflicting (trap) documents:** none

**Related but not sufficient:** SOP-01

**Reference answer:** Raise a New KPI request in the data service portal with the business question, proposed definition and audience. The data steward checks the glossary for a duplicate; if one exists the request is closed. If not, an owner and a new KPI id are assigned, the owner writes the definition (Provisional, version 0.1) and certification follows SOP-01. The data steward responds within 10 working days.

**Notes:** drafted by Claude, owner to review; 10 working days | DECISION: SOP-01 is only a pointer in the answer, so it is related, not required.

## G-031 | process | author: claude

**Question:** What approvals do I need to get access to the customers table?

**Expected documents:** SOP-04, POL-03

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** The customers table is Confidential. Raise an access request in the data service portal naming the asset; your line manager approves the business need and the data owner must also approve (SOP-04, POL-03). The platform team grants access within 5 working days of the final approval.

**Notes:** drafted by Claude, owner to review; Confidential: line manager plus data owner; FAQ-01 gives an informal version

## G-032 (H) | process | author: claude

**Question:** A Certified KPI in the Executive KPI Pack is wrong. What severity is that and what must happen within 2 hours?

**Expected documents:** SOP-05

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** That is a P1 incident (a Certified KPI in the Executive KPI Pack is wrong or missing). The data steward sets the severity within 1 hour, and a warning banner must be added to every affected dashboard within 2 hours.

**Notes:** drafted by Claude, owner to review; P1; warning banner on affected dashboards within 2 hours

## G-033 | process | author: claude

**Question:** Can I put Basket Size on the Executive KPI Pack?

**Expected documents:** SOP-06, KPI-008

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** No. Basket Size (KPI-008) is Provisional, and the Executive KPI Pack may only contain Certified KPIs (SOP-06, no exceptions).

**Notes:** drafted by Claude, owner to review; TRAP: no, Basket Size is Provisional and the Executive KPI Pack only allows Certified KPIs

## G-034 | unanswerable | author: claude

**Question:** What was our customer churn rate last quarter?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** KPI-007

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; the documents define churn but hold no actual values; should refuse | DECISION: KPI-007 gives the definition or formula but not the requested value or query.

## G-035 | unanswerable | author: claude

**Question:** Can you share the SQL query used to calculate Net Revenue?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** KPI-001

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; formula exists, SQL does not; should refuse | DECISION: KPI-001 gives the definition or formula but not the requested value or query.

## G-036 (H) | unanswerable | author: claude

**Question:** Who is the CEO of Kestrel Retail Group?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; not in the governed documents; should refuse | AUDIT: also check that "employee" is not used as an absent term: it appears 3 times in the corpus.

## G-037 | unanswerable | author: claude

**Question:** What is our NPS for the north region this month?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** KPI-013

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; NPS is defined but no values; should refuse | DECISION: KPI-013 gives the definition or formula but not the requested value or query.

## G-038 | unanswerable | author: claude

**Question:** Which KPI measures employee satisfaction?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; no such KPI exists; should refuse | AUDIT: absent terms must be specific phrases; plain "employee" appears in the corpus.

## G-039 | unanswerable | author: claude

**Question:** Which dashboard shows store energy costs?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; no such dashboard; should refuse

## G-040 (H) | unanswerable | author: claude

**Question:** What is the marketing budget for 2027?

**Expected documents:** none (should refuse)

**Conflicting (trap) documents:** none

**Related but not sufficient:** none

**Reference answer:** Not in the governed documents. The assistant should say it does not know and must not guess.

**Notes:** drafted by Claude, owner to review; not in the governed documents; should refuse
