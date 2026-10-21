# Hand-grading sheet

How to grade (the same rubric the judge uses):
- Key fact: y only if the answer clearly states it. A paraphrase counts if the meaning is the same. Do not give credit for a hint. Ignore extra facts, style and typos.
- Faithfulness: y only if every claim in the answer is supported by the context chunks shown below. A fact, number, date, name or relationship that no chunk states makes it n.

Fill in handgrade_template.csv, column 'answer': y or n. One row per key fact, plus one faithfulness row per answer.


---

## H01

**Question:** Can I put Basket Size on the Executive KPI Pack?

**Answer:** No, you cannot put Basket Size on the Executive KPI Pack because provisional KPIs must not appear in the Executive KPI Pack [KPI-008::v1::0], and only certified KPIs may appear there [CAT-01::v1::0]. Basket Size is currently status Provisional [KPI-008::v1::0].

**Key facts to check:**
1. The Executive KPI Pack may only contain Certified KPIs
2. Provisional KPIs must not appear in the Executive KPI Pack

**Context chunks the answer was given:**

- `KPI-008::v1::0` (Provisional): Basket Size (KPI-008) | part 1
# Basket Size (KPI-008)

## Definition
Basket Size is the average number of units in a completed order. It shows whether customers add more items each time they buy.

## Formula
Basket Size = Total units sold / Number of completed orders

Units come from the item count on each order. An order is one transaction id.

## Grain and filters
- Calculated daily, reported weekly.
- Split by channel, store and product category.
- Cancelled and zero-value orders are excluded, as in KPI-004.

## Source tables
- `sales_orders`: order id, status, item count, channel, store

## Dashboards
- Sales Performance Dashboard

## Caveats and exclusions
- Provisional: multi-packs count as one unit in the app but as the pack size in some store tills. This must be fixed before the KPI can be certified under SOP-01.
- A bundle sold under one product code counts as one unit.
- Basket Size measures units per order. For value per order, use Average Order Value (KPI-004).
- Provisional KPIs must not appear in the Executive KPI Pack.

## Change history
- v0.9 (2026-02-01): draft submitted for certification.

## Ownership and status
Owner: Head of Sales Analytics
Status: Provisional
Version: 0.9
Effective date: 2026-02-01
Domain: Sales

- `CAT-01::v1::0` (Certified): Executive KPI Pack (CAT-01) | part 1
Executive KPI Pack (dashboard)
Description: Board-level pack of headline KPIs. Only Certified KPIs may appear here, as set out in SOP-06. Used for monthly board and leadership reporting.
Refresh: monthly (working day 3)
Linked KPIs: KPI-001, KPI-002, KPI-003, KPI-006, KPI-007, KPI-010, KPI-013
Owner: Head of Finance Analytics
Status: Certified
Version: 3.0
Effective date: 2026-04-01
Domain: Finance

- `POL-05::v1::0` (Certified): Quarterly KPI Review Minutes (Q2 2026) (POL-05) | part 1
# Kestrel Retail Group: Quarterly KPI Review Minutes (Q2 2026)

POL-05 | Version 1.0 | Effective 2026-07-10 | Owner: Head of Data Governance

Meeting date: 2026-07-10. Chair: Head of Data Governance. Attendees: Heads of Finance, Sales, Customer, Marketing and Supply Chain Analytics; Head of Digital Product.

## Decisions

1. Customer Churn Rate v2 (KPI-007) is confirmed as live since 2026-04-01. v1 has been removed from all dashboards.

2. Active User (app 30-day) (KPI-020) is approved as Provisional, version 0.8. The Council asked for duplicate user ids to be fixed before certification.

3. Basket Size (KPI-008) certification is postponed to Q4 2026 because of the multi-pack unit counting issue.

4. Marketing ROI (ROAS) (KPI-015) stays Provisional until the attribution review closes.

## Actions

Action: Fix multi-pack unit counts in store tills | Owner: Head of Sales Analytics | Due: 2026-09-30
Action: Remove duplicate app user ids | Owner: Head of Digital Product | Due: 2026-10-31
Action: Close attribution review for ROAS | Owner: Head of Marketing Analytics | Due: 2026-11-30

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2026-07-10
Domain: Governance

- `SOP-03::v1::0` (Certified): Metric Change Management (SOP-03) | part 1
# Metric Change Management (SOP-03)

## Purpose
This procedure controls changes to Certified KPIs, so that reports stay comparable and users know which version they are looking at.

## Roles
- **KPI owner:** proposes the change.
- **KPI Council:** approves major changes.
- **Dashboard owners:** update dashboards and labels.

## Change types
- **Minor change:** wording, clarifications or new filters that do not change the number. The version goes up by 0.1 (for example 1.3 to 1.4). The KPI owner approves it.
- **Major change:** a new formula, window or population that changes the number. The version goes up to the next whole number (for example 1.0 to 2.0). The KPI Council must approve it.

## Steps for a major change
1. The KPI owner submits the new definition and an impact estimate.
2. The KPI Council approves or rejects it at its monthly meeting.
3. Dashboard owners get at least 30 days of notice before the effective date.
4. On the effective date, the new version becomes Certified and the old version is marked Deprecated with a pointer to the new one.
5. Deprecated definitions are kept for 2 years for audit, then archived (see SOP-08).

## Example
Customer Churn Rate moved from v1 (account closures) to v2 (180 days without a purchase) on 2026-04-01. v1 is now KPI-007-V1 and is Deprecated.

## Related documents
- SOP-01 KPI Certification Process
- SOP-06 Dashboard Publishing Standard

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.2
Effective date: 2025-06-15
Domain: Governance

- `POL-02::v1::0` (Certified): Acceptable Use of AI Tools (POL-02) | part 1
# Kestrel Retail Group: Acceptable Use of AI Tools

POL-02 | Version 1.0 | Effective 2026-01-01 | Owner: Head of Data Governance

## 1. Purpose

This policy sets safe use of AI tools, including chat assistants and internal RAG assistants, at Kestrel.

## 2. Approved tools

Only tools on the approved list published by the Head of Data Governance may be used with company data.

## 3. Data rules

Public and Internal data may be used with approved tools. Confidential and Restricted data (see POL-03) must never be entered into public AI tools. Customer-level data must not leave approved systems.

## 4. Answers about KPIs

An AI assistant that answers KPI questions must cite the governed source document for every answer, must state the certification level of the KPI, and must say it does not know when the answer is not in the governed documents.

## 5. Human review

AI output used in board packs or external communication must be checked by a person, who stays accountable for it.

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2026-01-01
Domain: Governance


---

## H02

**Question:** How does a KPI go from Provisional to Certified?

**Answer:** To move a KPI from Provisional to Certified, the KPI owner submits the definition using the standard KPI template [SOP-01::v1::0]. The data steward then confirms that every source table and dashboard named in the definition is listed in the data catalog, and runs a two-month parallel test where the KPI must reconcile within 1% against an independent calculation [SOP-01::v1::0]. Next, the KPI owner presents the definition at the monthly KPI Council [SOP-01::v1::0]. If approved by the Council, the version becomes 1.0, the status becomes Certified, the change history is updated, and the data steward updates the KPI Glossary Summary (POL-04) within 5 working days [SOP-01::v1::0].

**Key facts to check:**
1. two-month parallel test
2. within 1%
3. KPI Council

**Context chunks the answer was given:**

- `SOP-01::v1::0` (Certified): KPI Certification Process (SOP-01) | part 1
# KPI Certification Process (SOP-01)

## Purpose
This procedure explains how a KPI moves from Provisional to Certified. Only Certified KPIs may be used in the Executive KPI Pack and in board packs.

## Roles
- **KPI owner:** the domain head who is accountable for the definition (for example Head of Customer Analytics).
- **Data steward:** checks the formula, source tables and data quality.
- **KPI Council:** chaired by the Head of Data Governance; approves or rejects certification.

## Steps
1. The KPI owner submits the definition using the standard KPI template. The KPI starts as Provisional with a version below 1.0.
2. The data steward confirms that every source table and dashboard named in the definition is listed in the data catalog.
3. The data steward runs a two-month parallel test. The KPI must reconcile within 1% against an independent calculation.
4. The KPI owner presents the definition at the monthly KPI Council.
5. If approved, the version becomes 1.0, the status becomes Certified, and the change history is updated.
6. The data steward updates the KPI Glossary Summary (POL-04) within 5 working days.
7. Certified KPIs are reviewed every 12 months. A KPI that misses its review drops back to Provisional.

## Related documents
- SOP-02 Requesting a New KPI
- SOP-03 Metric Change Management
- POL-01 Data Governance Policy

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 2.0
Effective date: 2025-02-01
Domain: Governance

- `SOP-02::v1::0` (Certified): Requesting a New KPI (SOP-02) | part 1
# Requesting a New KPI (SOP-02)

## Purpose
This procedure explains how anyone at Kestrel can request a new KPI, and how duplicates are avoided.

## Roles
- **Requester:** any employee with a business question that no existing KPI answers.
- **Data steward:** checks for duplicates and assigns an owner.
- **KPI owner:** the domain head who will be accountable for the new KPI.

## Steps
1. The requester raises a "New KPI" request in the data service portal, giving the business question, a proposed definition and the intended audience.
2. The data steward searches the KPI Glossary Summary (POL-04) for an existing KPI with the same meaning. Similar names are checked with care; for example Active Customer (KPI-006) and Active User (KPI-020) measure different things.
3. If a matching KPI exists, the request is closed and the requester is pointed to it.
4. If not, the data steward assigns the KPI owner from the relevant domain and a new id in the form KPI-NNN (see SOP-07).
5. The KPI owner writes the definition using the KPI template. It is published as Provisional with version 0.1.
6. Certification then follows SOP-01.

## Service level
The data steward responds to a new request within 10 working days.

## Related documents
- SOP-01 KPI Certification Process
- SOP-07 Naming Conventions

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.1
Effective date: 2025-02-01
Domain: Governance

- `SOP-03::v1::0` (Certified): Metric Change Management (SOP-03) | part 1
# Metric Change Management (SOP-03)

## Purpose
This procedure controls changes to Certified KPIs, so that reports stay comparable and users know which version they are looking at.

## Roles
- **KPI owner:** proposes the change.
- **KPI Council:** approves major changes.
- **Dashboard owners:** update dashboards and labels.

## Change types
- **Minor change:** wording, clarifications or new filters that do not change the number. The version goes up by 0.1 (for example 1.3 to 1.4). The KPI owner approves it.
- **Major change:** a new formula, window or population that changes the number. The version goes up to the next whole number (for example 1.0 to 2.0). The KPI Council must approve it.

## Steps for a major change
1. The KPI owner submits the new definition and an impact estimate.
2. The KPI Council approves or rejects it at its monthly meeting.
3. Dashboard owners get at least 30 days of notice before the effective date.
4. On the effective date, the new version becomes Certified and the old version is marked Deprecated with a pointer to the new one.
5. Deprecated definitions are kept for 2 years for audit, then archived (see SOP-08).

## Example
Customer Churn Rate moved from v1 (account closures) to v2 (180 days without a purchase) on 2026-04-01. v1 is now KPI-007-V1 and is Deprecated.

## Related documents
- SOP-01 KPI Certification Process
- SOP-06 Dashboard Publishing Standard

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.2
Effective date: 2025-06-15
Domain: Governance

- `POL-04::v1::1` (Certified): KPI Glossary Summary (POL-04) | part 2
ID: KPI-008 | KPI: Basket Size | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Units sold / completed orders.
ID: KPI-009 | KPI: Store Footfall Conversion | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Store transactions / door-counter footfall.
ID: KPI-010 | KPI: Net Revenue Retention | Owner: Head of Customer Analytics | Status: Certified | Short definition: 12-month net revenue kept from an existing customer cohort.
ID: KPI-011 | KPI: Customer Lifetime Value | Owner: Head of Customer Analytics | Status: Provisional | Short definition: Annual gross margin per customer x expected lifetime.
ID: KPI-012 | KPI: Repeat Purchase Rate | Owner: Head of Customer Analytics | Status: Certified | Short definition: New customers buying again within 90 days.
ID: KPI-013 | KPI: Net Promoter Score | Owner: Head of Customer Analytics | Status: Certified | Short definition: % promoters (9-10) minus % detractors (0-6).
ID: KPI-014 | KPI: Customer Acquisition Cost | Owner: Head of Marketing Analytics | Status: Certified | Short definition: Acquisition spend / new customers.
ID: KPI-015 | KPI: Marketing ROI (ROAS) | Owner: Head of Marketing Analytics | Status: Provisional | Short definition: Attributed net revenue / paid media spend.
ID: KPI-016 | KPI: Inventory Turnover | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: 12-month COGS / average inventory at cost.

- `POL-05::v1::0` (Certified): Quarterly KPI Review Minutes (Q2 2026) (POL-05) | part 1
# Kestrel Retail Group: Quarterly KPI Review Minutes (Q2 2026)

POL-05 | Version 1.0 | Effective 2026-07-10 | Owner: Head of Data Governance

Meeting date: 2026-07-10. Chair: Head of Data Governance. Attendees: Heads of Finance, Sales, Customer, Marketing and Supply Chain Analytics; Head of Digital Product.

## Decisions

1. Customer Churn Rate v2 (KPI-007) is confirmed as live since 2026-04-01. v1 has been removed from all dashboards.

2. Active User (app 30-day) (KPI-020) is approved as Provisional, version 0.8. The Council asked for duplicate user ids to be fixed before certification.

3. Basket Size (KPI-008) certification is postponed to Q4 2026 because of the multi-pack unit counting issue.

4. Marketing ROI (ROAS) (KPI-015) stays Provisional until the attribution review closes.

## Actions

Action: Fix multi-pack unit counts in store tills | Owner: Head of Sales Analytics | Due: 2026-09-30
Action: Remove duplicate app user ids | Owner: Head of Digital Product | Due: 2026-10-31
Action: Close attribution review for ROAS | Owner: Head of Marketing Analytics | Due: 2026-11-30

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2026-07-10
Domain: Governance


---

## H03

**Question:** What approvals do I need to get access to the customers table?

**Answer:** To get access to the customers table, which is classified as Confidential, you must raise an access request in the data service portal [SOP-04::v1::0, FAQ-01::v1::0, CAT-08::v1::0]. This requires approval of your business need from your line manager and the data owner [SOP-04::v1::0, FAQ-01::v1::0].

**Key facts to check:**
1. the data owner must also approve
2. Line manager
3. Data owner approval

**Context chunks the answer was given:**

- `SOP-04::v1::0` (Certified): Data Access Requests (SOP-04) | part 1
# Data Access Requests (SOP-04)

## Purpose
This procedure explains how to get access to a dashboard or a source table. Access depends on the data classification in POL-03.

## Roles
- **Requester:** the employee who needs access.
- **Line manager:** confirms the business need.
- **Data owner:** the owner listed in the data catalog for that asset.
- **Head of Data Governance:** approves access to Restricted data.

## Steps
1. The requester raises an "Access request" in the data service portal, naming the asset from the data catalog and the reason.
2. The line manager approves the business need.
3. For Internal data, access is granted after step 2.
4. For Confidential data (for example the `customers` table), the data owner must also approve.
5. For Restricted data, the Head of Data Governance must also approve, and access is time-limited to 90 days.
6. The platform team grants access within 5 working days of the final approval.

## Reviews
Data owners review the access list for their assets every 6 months and remove anyone who no longer needs it. Leavers lose all access on their last working day.

## Related documents
- POL-03 Data Classification Standard
- POL-01 Data Governance Policy

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2025-03-01
Domain: Governance

- `FAQ-01::v1::0` (Provisional): Customer Team FAQ (informal) (FAQ-01) | part 1
# Customer Team FAQ (informal)

Quick answers we get asked a lot. Informal team notes, not reviewed by Data Governance.

## What counts as an active customer?
Anyone who bought something from us in the last 90 days. We use 90 days because it smooths out seasonal shoppers.

## Where can I see customer numbers?
Most of what you need is on the Customer 360 Dashboard. Ask the Customer Insights Team if a number looks odd.

## How do I get access to customer-level data?
Raise an access request in the data service portal. The customers table is Confidential, so the data owner has to approve as well as your manager.

## Is there an official KPI list?
Yes, the KPI Glossary Summary has the official list. It is kept by the Data Governance team.

## Who do I ask about loyalty tiers?
The Customer Insights Team. Tiers are reviewed every January.

## Ownership and status
Owner: Customer Insights Team
Status: Provisional
Version: 0.1
Effective date: 2024-11-20
Domain: Customer

- `CAT-08::v1::0` (Certified): customers (CAT-08) | part 1
customers (table)
Description: One row per identified customer (loyalty member or account holder). Holds loyalty tier, account status, first order date, acquisition channel, and staff and test flags. Classified as Confidential.
Refresh: daily 05:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-014
Owner: Head of Customer Analytics
Status: Certified
Version: 3.2
Effective date: 2025-06-01
Domain: Customer

- `CAT-09::v1::0` (Certified): invoices (CAT-09) | part 1
invoices (table)
Description: One row per invoice to wholesale and corporate gifting customers. Holds amount, invoice date, due date, paid date and status.
Refresh: daily 05:00
Linked KPIs: KPI-003
Owner: Head of Finance Analytics
Status: Certified
Version: 2.0
Effective date: 2025-03-01
Domain: Finance

- `KPI-006::v1::0` (Certified): Active Customer (30-day) (KPI-006) | part 1
# Active Customer (30-day) (KPI-006)

## Definition
An Active Customer is an identified customer (loyalty member or account holder) who completed at least one purchase in any channel (store, app or web) in the last 30 days. Anonymous buyers cannot be counted.

## Formula
Active Customers = Count of distinct customer ids with at least one completed order where the order date is between (run date - 29 days) and the run date

## Grain and filters
- Daily snapshot, reported weekly and monthly (month-end snapshot).
- Split by channel, region and loyalty tier.
- Staff and test accounts are excluded.

## Source tables
- `sales_orders`: customer id, order date, status
- `customers`: loyalty tier, staff and test flags

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- Orders that are fully returned within the 30 days do not make a customer active.
- This KPI requires a purchase. It is not the same as Active User (KPI-020), which counts app logins without a purchase.
- The 30-day window is the only certified definition. Any other window (for example 90 days) is not certified.

## Change history
- v1.1 (2025-11-01): fully returned orders excluded.
- v1.0 (2025-02-01): first certified version, replacing informal team definitions.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 1.1
Effective date: 2025-11-01
Domain: Customer


---

## H04

**Question:** Which KPIs does the Head of Marketing Analytics own?

**Answer:** The Head of Marketing Analytics owns Customer Acquisition Cost (KPI-014), which is Certified, and Marketing ROI (ROAS) (KPI-015), which is Provisional [POL-04::v1::1].

**Key facts to check:**
1. KPI: Customer Acquisition Cost | Owner: Head of Marketing Analytics | Status: Certified
2. KPI: Marketing ROI (ROAS) | Owner: Head of Marketing Analytics | Status: Provisional

**Context chunks the answer was given:**

- `POL-05::v1::0` (Certified): Quarterly KPI Review Minutes (Q2 2026) (POL-05) | part 1
# Kestrel Retail Group: Quarterly KPI Review Minutes (Q2 2026)

POL-05 | Version 1.0 | Effective 2026-07-10 | Owner: Head of Data Governance

Meeting date: 2026-07-10. Chair: Head of Data Governance. Attendees: Heads of Finance, Sales, Customer, Marketing and Supply Chain Analytics; Head of Digital Product.

## Decisions

1. Customer Churn Rate v2 (KPI-007) is confirmed as live since 2026-04-01. v1 has been removed from all dashboards.

2. Active User (app 30-day) (KPI-020) is approved as Provisional, version 0.8. The Council asked for duplicate user ids to be fixed before certification.

3. Basket Size (KPI-008) certification is postponed to Q4 2026 because of the multi-pack unit counting issue.

4. Marketing ROI (ROAS) (KPI-015) stays Provisional until the attribution review closes.

## Actions

Action: Fix multi-pack unit counts in store tills | Owner: Head of Sales Analytics | Due: 2026-09-30
Action: Remove duplicate app user ids | Owner: Head of Digital Product | Due: 2026-10-31
Action: Close attribution review for ROAS | Owner: Head of Marketing Analytics | Due: 2026-11-30

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2026-07-10
Domain: Governance

- `POL-04::v1::0` (Certified): KPI Glossary Summary (POL-04) | part 1
# Kestrel Retail Group: KPI Glossary Summary

POL-04 | Version 2.0 | Effective 2026-04-15 | Owner: Head of Data Governance

Official list of KPIs. The full definition of each KPI is in its own KPI document. Deprecated versions are not listed; Customer Churn Rate v1 (KPI-007-V1) was replaced by KPI-007 on 2026-04-01.

ID: KPI-001 | KPI: Net Revenue | Owner: Head of Finance Analytics | Status: Certified | Short definition: Sales after discounts, returns and refunds, excluding sales tax.
ID: KPI-002 | KPI: Gross Margin % | Owner: Head of Finance Analytics | Status: Certified | Short definition: (Net Revenue - COGS) / Net Revenue.
ID: KPI-003 | KPI: Days Sales Outstanding | Owner: Head of Finance Analytics | Status: Certified | Short definition: Average days to collect payment on B2B invoices.
ID: KPI-004 | KPI: Average Order Value | Owner: Head of Sales Analytics | Status: Certified | Short definition: Net Revenue / completed orders.
ID: KPI-005 | KPI: Conversion Rate | Owner: Head of Sales Analytics | Status: Certified | Short definition: App and web sessions with an order / qualifying sessions.
ID: KPI-006 | KPI: Active Customer (30-day) | Owner: Head of Customer Analytics | Status: Certified | Short definition: Identified customers with a purchase in the last 30 days.
ID: KPI-007 | KPI: Customer Churn Rate | Owner: Head of Customer Analytics | Status: Certified | Short definition: Start-base customers with no purchase for 180 days.
ID: KPI-008 | KPI: Basket Size | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Units sold / completed orders.

- `SOP-01::v1::0` (Certified): KPI Certification Process (SOP-01) | part 1
# KPI Certification Process (SOP-01)

## Purpose
This procedure explains how a KPI moves from Provisional to Certified. Only Certified KPIs may be used in the Executive KPI Pack and in board packs.

## Roles
- **KPI owner:** the domain head who is accountable for the definition (for example Head of Customer Analytics).
- **Data steward:** checks the formula, source tables and data quality.
- **KPI Council:** chaired by the Head of Data Governance; approves or rejects certification.

## Steps
1. The KPI owner submits the definition using the standard KPI template. The KPI starts as Provisional with a version below 1.0.
2. The data steward confirms that every source table and dashboard named in the definition is listed in the data catalog.
3. The data steward runs a two-month parallel test. The KPI must reconcile within 1% against an independent calculation.
4. The KPI owner presents the definition at the monthly KPI Council.
5. If approved, the version becomes 1.0, the status becomes Certified, and the change history is updated.
6. The data steward updates the KPI Glossary Summary (POL-04) within 5 working days.
7. Certified KPIs are reviewed every 12 months. A KPI that misses its review drops back to Provisional.

## Related documents
- SOP-02 Requesting a New KPI
- SOP-03 Metric Change Management
- POL-01 Data Governance Policy

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 2.0
Effective date: 2025-02-01
Domain: Governance

- `POL-04::v1::1` (Certified): KPI Glossary Summary (POL-04) | part 2
ID: KPI-008 | KPI: Basket Size | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Units sold / completed orders.
ID: KPI-009 | KPI: Store Footfall Conversion | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Store transactions / door-counter footfall.
ID: KPI-010 | KPI: Net Revenue Retention | Owner: Head of Customer Analytics | Status: Certified | Short definition: 12-month net revenue kept from an existing customer cohort.
ID: KPI-011 | KPI: Customer Lifetime Value | Owner: Head of Customer Analytics | Status: Provisional | Short definition: Annual gross margin per customer x expected lifetime.
ID: KPI-012 | KPI: Repeat Purchase Rate | Owner: Head of Customer Analytics | Status: Certified | Short definition: New customers buying again within 90 days.
ID: KPI-013 | KPI: Net Promoter Score | Owner: Head of Customer Analytics | Status: Certified | Short definition: % promoters (9-10) minus % detractors (0-6).
ID: KPI-014 | KPI: Customer Acquisition Cost | Owner: Head of Marketing Analytics | Status: Certified | Short definition: Acquisition spend / new customers.
ID: KPI-015 | KPI: Marketing ROI (ROAS) | Owner: Head of Marketing Analytics | Status: Provisional | Short definition: Attributed net revenue / paid media spend.
ID: KPI-016 | KPI: Inventory Turnover | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: 12-month COGS / average inventory at cost.

- `POL-04::v1::2` (Certified): KPI Glossary Summary (POL-04) | part 3
ID: KPI-016 | KPI: Inventory Turnover | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: 12-month COGS / average inventory at cost.
ID: KPI-017 | KPI: Stockout Rate | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Active SKU-locations with zero sellable stock at 06:00.
ID: KPI-018 | KPI: On-Time Delivery % | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Orders delivered or ready by the promised date.
ID: KPI-019 | KPI: Return Rate | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Returned value / gross sales, by month of sale.

ID: KPI-020 | KPI: Active User (app 30-day) | Owner: Head of Digital Product | Status: Provisional | Short definition: App users with a session in the last 30 days (no purchase needed).

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 2.0
Effective date: 2026-04-15
Domain: Governance


---

## H05

**Question:** What did the old churn rate (v1) measure and why was it replaced?

**Answer:** Customer Churn Rate v1 measured the share of loyalty members who closed their loyalty account in a month [KPI-007-V1::v1::0]. It was replaced because most customers who stop buying never close their account (causing the method to understate churn), customers who bought without a loyalty account were invisible to the metric, and the KPI Council replaced it with the inactivity-based v2 [KPI-007-V1::v1::0].

**Key facts to check:**
1. close their loyalty account
2. understated churn
3. Do not use for reporting

**Context chunks the answer was given:**

- `KPI-007-V1::v1::0` (Deprecated): Customer Churn Rate (v1) (KPI-007-V1) | part 1
# Customer Churn Rate (v1) (KPI-007-V1)

## Definition
DEPRECATED. Replaced by Customer Churn Rate v2 (KPI-007) from 2026-04-01. Do not use for reporting.

Customer Churn Rate v1 is the share of loyalty members who close their loyalty account in a month.

## Formula
Churn Rate % = Loyalty accounts closed in the month / Loyalty accounts open at the start of the month x 100

## Grain and filters
- Reported monthly.
- Loyalty members only; customers without an account are not included.

## Source tables
- `customers`: account status, account open date, account closed date

## Dashboards
- None. Removed from all dashboards on 2026-04-01.

## Caveats and exclusions
- Most customers who stop buying never close their account, so this method understated churn.
- Customers who buy without a loyalty account were invisible to this KPI.
- These weaknesses are why the KPI Council replaced it with the inactivity-based v2.

## Change history
- 2026-04-01: Deprecated, replaced by KPI-007 v2.0.
- v1.0 (2025-01-01): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Deprecated
Version: 1.0
Effective date: 2025-01-01
Domain: Customer

- `KPI-007::v1::0` (Certified): Customer Churn Rate (KPI-007) | part 1
# Customer Churn Rate (KPI-007)

## Definition
Customer Churn Rate is the share of recently active customers who stop buying from Kestrel. A customer has churned when 180 days pass without a completed purchase in any channel.

## Formula
Churn Rate % = Customers in the start base with no purchase for 180 days by quarter end / Customers in the start base x 100

The start base is every identified customer with at least one completed order in the 180 days before the quarter starts.

## Grain and filters
- Reported quarterly, with a monthly rolling view.
- Split by loyalty tier, region and first purchase channel.
- Staff and test accounts are excluded.

## Source tables
- `customers`: customer id, loyalty tier, account status
- `sales_orders`: customer id, order date, status

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- A customer who closes their account counts as churned immediately.
- This v2 replaces v1 (KPI-007-V1), which counted account closures only. v1 is Deprecated and its figures must not be compared with v2.
- Churn is reported one quarter after the fact, because the 180-day window must pass first.

## Change history
- v2.0 (2026-04-01): 180-day inactivity definition approved by the KPI Council under SOP-03.
- v1.0 (2025-01-01): account-closure definition, now Deprecated.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 2.0
Effective date: 2026-04-01
Domain: Customer

- `KPI-011::v1::0` (Provisional): Customer Lifetime Value (KPI-011) | part 1
# Customer Lifetime Value (KPI-011)

## Definition
Customer Lifetime Value (CLV) estimates the total gross margin an identified customer will generate for Kestrel over their whole relationship. It is used to decide how much to spend on acquiring and keeping customers.

## Formula
CLV = Average annual gross margin per active customer x Expected customer lifetime in years

Expected lifetime = 1 / Annual churn rate, where the annual churn rate comes from KPI-007 v2. The lifetime is capped at 5 years.

## Grain and filters
- Reported monthly.
- Split by loyalty tier and acquisition channel.
- Staff and test accounts are excluded.

## Source tables
- `sales_orders`: margin per order, customer id
- `returns`: refunded value
- `customers`: loyalty tier, acquisition channel

## Dashboards
- Customer 360 Dashboard

## Caveats and exclusions
- Provisional: the model is still being validated against actual customer histories.
- Uses gross margin, not revenue. Older team estimates based on revenue are much higher and are not valid.
- Not approved for board reporting or the Executive KPI Pack.

## Change history
- v0.7 (2026-05-15): changed from revenue basis to gross margin basis.
- v0.5 (2026-01-10): first draft.

## Ownership and status
Owner: Head of Customer Analytics
Status: Provisional
Version: 0.7
Effective date: 2026-05-15
Domain: Customer

- `KPI-010::v1::0` (Certified): Net Revenue Retention (KPI-010) | part 1
# Net Revenue Retention (KPI-010)

## Definition
Net Revenue Retention (NRR) measures how much net revenue Kestrel keeps from an existing group of customers over 12 months. It includes growth from those customers and losses from customers who stop buying. New customers acquired during the period are excluded.

## Formula
NRR % = (Net revenue in the current 12 months from the base cohort / Net revenue in the prior 12 months from the same cohort) x 100

The base cohort is every identified customer with at least one order in the prior 12-month window. Net revenue follows KPI-001 (after discounts and returns, excluding sales tax).

## Grain and filters
- Reported monthly on a rolling 12-month basis.
- Split by channel (store, app, web) and by loyalty tier.
- Staff purchases and test accounts are excluded.

## Source tables
- `sales_orders`: order value, discounts, order date
- `returns`: refunded value per order
- `customers`: customer id, loyalty tier, staff and test flags

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- A value above 100% means the cohort spent more than in the prior year, even after churn.
- Merged customer records keep the earliest customer id.
- Not comparable with figures before v1.4, which did not deduct returns.

## Change history
- v1.4 (2025-10-01): returns now deducted, aligned with KPI-001.
- v1.0 (2025-01-15): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 1.4
Effective date: 2025-10-01
Domain: Customer

- `KPI-012::v1::0` (Certified): Repeat Purchase Rate (KPI-012) | part 1
# Repeat Purchase Rate (KPI-012)

## Definition
Repeat Purchase Rate is the share of new customers who come back and buy a second time within 90 days of their first purchase. It measures how well Kestrel turns first-time buyers into regular customers.

## Formula
Repeat Purchase Rate % = New customers with a second completed order within 90 days of their first order / New customers in the cohort month x 100

A new customer is an identified customer whose first ever completed order falls in the cohort month.

## Grain and filters
- Reported monthly by cohort (month of first purchase).
- Split by first purchase channel and region.
- Staff and test accounts are excluded.

## Source tables
- `sales_orders`: customer id, order id, order date, status
- `customers`: first order date, staff and test flags

## Dashboards
- Customer 360 Dashboard

## Caveats and exclusions
- Each cohort is reported 90 days after the cohort month closes, so the latest three months are always blank.
- A second order on the same day counts only if it is a separate transaction.
- The 90-day window here is about repeat buying. It is not related to the Active Customer definition (KPI-006).

## Change history
- v1.0 (2025-06-01): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 1.0
Effective date: 2025-06-01
Domain: Customer


---

## H06

**Question:** Customer churn rate - how is that calculated? What dashboards use it?

**Answer:** Customer Churn Rate is calculated as the share of recently active customers who stop buying from Kestrel, specifically measured as customers in the start base with no purchase for 180 days by quarter end divided by customers in the start base, multiplied by 100 [KPI-007::v1::0]. It is used on the Customer 360 Dashboard and the Executive KPI Pack [KPI-007::v1::0].

**Key facts to check:**
1. no purchase for 180 days
2. Customer 360 Dashboard
3. Executive KPI Pack

**Context chunks the answer was given:**

- `KPI-007::v1::0` (Certified): Customer Churn Rate (KPI-007) | part 1
# Customer Churn Rate (KPI-007)

## Definition
Customer Churn Rate is the share of recently active customers who stop buying from Kestrel. A customer has churned when 180 days pass without a completed purchase in any channel.

## Formula
Churn Rate % = Customers in the start base with no purchase for 180 days by quarter end / Customers in the start base x 100

The start base is every identified customer with at least one completed order in the 180 days before the quarter starts.

## Grain and filters
- Reported quarterly, with a monthly rolling view.
- Split by loyalty tier, region and first purchase channel.
- Staff and test accounts are excluded.

## Source tables
- `customers`: customer id, loyalty tier, account status
- `sales_orders`: customer id, order date, status

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- A customer who closes their account counts as churned immediately.
- This v2 replaces v1 (KPI-007-V1), which counted account closures only. v1 is Deprecated and its figures must not be compared with v2.
- Churn is reported one quarter after the fact, because the 180-day window must pass first.

## Change history
- v2.0 (2026-04-01): 180-day inactivity definition approved by the KPI Council under SOP-03.
- v1.0 (2025-01-01): account-closure definition, now Deprecated.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 2.0
Effective date: 2026-04-01
Domain: Customer

- `KPI-007-V1::v1::0` (Deprecated): Customer Churn Rate (v1) (KPI-007-V1) | part 1
# Customer Churn Rate (v1) (KPI-007-V1)

## Definition
DEPRECATED. Replaced by Customer Churn Rate v2 (KPI-007) from 2026-04-01. Do not use for reporting.

Customer Churn Rate v1 is the share of loyalty members who close their loyalty account in a month.

## Formula
Churn Rate % = Loyalty accounts closed in the month / Loyalty accounts open at the start of the month x 100

## Grain and filters
- Reported monthly.
- Loyalty members only; customers without an account are not included.

## Source tables
- `customers`: account status, account open date, account closed date

## Dashboards
- None. Removed from all dashboards on 2026-04-01.

## Caveats and exclusions
- Most customers who stop buying never close their account, so this method understated churn.
- Customers who buy without a loyalty account were invisible to this KPI.
- These weaknesses are why the KPI Council replaced it with the inactivity-based v2.

## Change history
- 2026-04-01: Deprecated, replaced by KPI-007 v2.0.
- v1.0 (2025-01-01): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Deprecated
Version: 1.0
Effective date: 2025-01-01
Domain: Customer

- `CAT-02::v1::0` (Certified): Customer 360 Dashboard (CAT-02) | part 1
Customer 360 Dashboard (dashboard)
Description: Single view of customer health: activity, churn, retention, lifetime value, repeat buying and NPS. Provisional KPIs are labelled on their tiles.
Refresh: daily 07:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-013
Owner: Head of Customer Analytics
Status: Certified
Version: 2.2
Effective date: 2026-04-01
Domain: Customer

- `CAT-05::v1::0` (Provisional): Marketing Effectiveness Dashboard (CAT-05) | part 1
Marketing Effectiveness Dashboard (dashboard)
Description: Paid media performance: acquisition cost and return on ad spend by channel and campaign. Provisional until the attribution review closes.
Refresh: daily 09:00
Linked KPIs: KPI-014, KPI-015
Owner: Head of Marketing Analytics
Status: Provisional
Version: 0.9
Effective date: 2026-03-01
Domain: Marketing

- `KPI-011::v1::0` (Provisional): Customer Lifetime Value (KPI-011) | part 1
# Customer Lifetime Value (KPI-011)

## Definition
Customer Lifetime Value (CLV) estimates the total gross margin an identified customer will generate for Kestrel over their whole relationship. It is used to decide how much to spend on acquiring and keeping customers.

## Formula
CLV = Average annual gross margin per active customer x Expected customer lifetime in years

Expected lifetime = 1 / Annual churn rate, where the annual churn rate comes from KPI-007 v2. The lifetime is capped at 5 years.

## Grain and filters
- Reported monthly.
- Split by loyalty tier and acquisition channel.
- Staff and test accounts are excluded.

## Source tables
- `sales_orders`: margin per order, customer id
- `returns`: refunded value
- `customers`: loyalty tier, acquisition channel

## Dashboards
- Customer 360 Dashboard

## Caveats and exclusions
- Provisional: the model is still being validated against actual customer histories.
- Uses gross margin, not revenue. Older team estimates based on revenue are much higher and are not valid.
- Not approved for board reporting or the Executive KPI Pack.

## Change history
- v0.7 (2026-05-15): changed from revenue basis to gross margin basis.
- v0.5 (2026-01-10): first draft.

## Ownership and status
Owner: Head of Customer Analytics
Status: Provisional
Version: 0.7
Effective date: 2026-05-15
Domain: Customer


---

## H07

**Question:** Which KPI owner teams are represented in the KPI glossary?

**Answer:** The KPI owner teams represented in the KPI glossary are Finance Analytics, Sales Analytics, Customer Analytics, Marketing Analytics, Supply Chain Analytics, and Digital Product [POL-04::v1::0], [POL-04::v1::1], [POL-04::v1::2].

**Key facts to check:**
1. Head of Finance Analytics
2. Head of Sales Analytics
3. Head of Customer Analytics
4. Head of Marketing Analytics
5. Head of Supply Chain Analytics
6. Head of Digital Product

**Context chunks the answer was given:**

- `POL-04::v1::0` (Certified): KPI Glossary Summary (POL-04) | part 1
# Kestrel Retail Group: KPI Glossary Summary

POL-04 | Version 2.0 | Effective 2026-04-15 | Owner: Head of Data Governance

Official list of KPIs. The full definition of each KPI is in its own KPI document. Deprecated versions are not listed; Customer Churn Rate v1 (KPI-007-V1) was replaced by KPI-007 on 2026-04-01.

ID: KPI-001 | KPI: Net Revenue | Owner: Head of Finance Analytics | Status: Certified | Short definition: Sales after discounts, returns and refunds, excluding sales tax.
ID: KPI-002 | KPI: Gross Margin % | Owner: Head of Finance Analytics | Status: Certified | Short definition: (Net Revenue - COGS) / Net Revenue.
ID: KPI-003 | KPI: Days Sales Outstanding | Owner: Head of Finance Analytics | Status: Certified | Short definition: Average days to collect payment on B2B invoices.
ID: KPI-004 | KPI: Average Order Value | Owner: Head of Sales Analytics | Status: Certified | Short definition: Net Revenue / completed orders.
ID: KPI-005 | KPI: Conversion Rate | Owner: Head of Sales Analytics | Status: Certified | Short definition: App and web sessions with an order / qualifying sessions.
ID: KPI-006 | KPI: Active Customer (30-day) | Owner: Head of Customer Analytics | Status: Certified | Short definition: Identified customers with a purchase in the last 30 days.
ID: KPI-007 | KPI: Customer Churn Rate | Owner: Head of Customer Analytics | Status: Certified | Short definition: Start-base customers with no purchase for 180 days.
ID: KPI-008 | KPI: Basket Size | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Units sold / completed orders.

- `SOP-07::v1::0` (Certified): Naming Conventions (SOP-07) | part 1
# Naming Conventions (SOP-07)

## Purpose
Consistent names make KPIs, tables and dashboards easy to find and hard to confuse.

## Roles
- **Data steward:** assigns ids and checks names before publishing.

## Rules
1. **KPI ids:** KPI- followed by three digits, for example KPI-014. Ids are never reused.
2. **Deprecated versions:** keep the original id with a version suffix, for example KPI-007-V1.
3. **KPI names:** plain English in Title Case. Use "Rate" or "%" for ratios (for example Return Rate, Gross Margin %). Include the time window in the name when it is part of the definition, for example "Active Customer (30-day)".
4. **Catalog ids:** CAT- followed by two digits, for example CAT-02.
5. **Tables:** lower case snake_case plural nouns, for example `sales_orders`, `nps_responses`.
6. **Dashboards:** Title Case ending in "Dashboard", except the Executive KPI Pack and the Supply Chain Control Tower, which keep their established names.
7. **Documents:** SOP-NN for procedures, POL-NN for policies and standards.
8. **Similar names:** a new KPI name must not differ from an existing one by a single word unless both definitions explain the difference (see KPI-006 and KPI-020).

## Related documents
- SOP-02 Requesting a New KPI

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2025-01-15
Domain: Governance

- `POL-04::v1::1` (Certified): KPI Glossary Summary (POL-04) | part 2
ID: KPI-008 | KPI: Basket Size | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Units sold / completed orders.
ID: KPI-009 | KPI: Store Footfall Conversion | Owner: Head of Sales Analytics | Status: Provisional | Short definition: Store transactions / door-counter footfall.
ID: KPI-010 | KPI: Net Revenue Retention | Owner: Head of Customer Analytics | Status: Certified | Short definition: 12-month net revenue kept from an existing customer cohort.
ID: KPI-011 | KPI: Customer Lifetime Value | Owner: Head of Customer Analytics | Status: Provisional | Short definition: Annual gross margin per customer x expected lifetime.
ID: KPI-012 | KPI: Repeat Purchase Rate | Owner: Head of Customer Analytics | Status: Certified | Short definition: New customers buying again within 90 days.
ID: KPI-013 | KPI: Net Promoter Score | Owner: Head of Customer Analytics | Status: Certified | Short definition: % promoters (9-10) minus % detractors (0-6).
ID: KPI-014 | KPI: Customer Acquisition Cost | Owner: Head of Marketing Analytics | Status: Certified | Short definition: Acquisition spend / new customers.
ID: KPI-015 | KPI: Marketing ROI (ROAS) | Owner: Head of Marketing Analytics | Status: Provisional | Short definition: Attributed net revenue / paid media spend.
ID: KPI-016 | KPI: Inventory Turnover | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: 12-month COGS / average inventory at cost.

- `POL-04::v1::2` (Certified): KPI Glossary Summary (POL-04) | part 3
ID: KPI-016 | KPI: Inventory Turnover | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: 12-month COGS / average inventory at cost.
ID: KPI-017 | KPI: Stockout Rate | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Active SKU-locations with zero sellable stock at 06:00.
ID: KPI-018 | KPI: On-Time Delivery % | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Orders delivered or ready by the promised date.
ID: KPI-019 | KPI: Return Rate | Owner: Head of Supply Chain Analytics | Status: Certified | Short definition: Returned value / gross sales, by month of sale.

ID: KPI-020 | KPI: Active User (app 30-day) | Owner: Head of Digital Product | Status: Provisional | Short definition: App users with a session in the last 30 days (no purchase needed).

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 2.0
Effective date: 2026-04-15
Domain: Governance

- `CAT-08::v1::0` (Certified): customers (CAT-08) | part 1
customers (table)
Description: One row per identified customer (loyalty member or account holder). Holds loyalty tier, account status, first order date, acquisition channel, and staff and test flags. Classified as Confidential.
Refresh: daily 05:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-014
Owner: Head of Customer Analytics
Status: Certified
Version: 3.2
Effective date: 2025-06-01
Domain: Customer


---

## H08

**Question:** Which team owns the customers table, how often is it refreshed and how sensitive is the data?

**Answer:** The customers table is owned by the Head of Customer Analytics, refreshed daily at 05:00, and classified as Confidential [CAT-08::v1::0].

**Key facts to check:**
1. Head of Customer Analytics
2. daily 05:00
3. Confidential

**Context chunks the answer was given:**

- `FAQ-01::v1::0` (Provisional): Customer Team FAQ (informal) (FAQ-01) | part 1
# Customer Team FAQ (informal)

Quick answers we get asked a lot. Informal team notes, not reviewed by Data Governance.

## What counts as an active customer?
Anyone who bought something from us in the last 90 days. We use 90 days because it smooths out seasonal shoppers.

## Where can I see customer numbers?
Most of what you need is on the Customer 360 Dashboard. Ask the Customer Insights Team if a number looks odd.

## How do I get access to customer-level data?
Raise an access request in the data service portal. The customers table is Confidential, so the data owner has to approve as well as your manager.

## Is there an official KPI list?
Yes, the KPI Glossary Summary has the official list. It is kept by the Data Governance team.

## Who do I ask about loyalty tiers?
The Customer Insights Team. Tiers are reviewed every January.

## Ownership and status
Owner: Customer Insights Team
Status: Provisional
Version: 0.1
Effective date: 2024-11-20
Domain: Customer

- `CAT-08::v1::0` (Certified): customers (CAT-08) | part 1
customers (table)
Description: One row per identified customer (loyalty member or account holder). Holds loyalty tier, account status, first order date, acquisition channel, and staff and test flags. Classified as Confidential.
Refresh: daily 05:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-014
Owner: Head of Customer Analytics
Status: Certified
Version: 3.2
Effective date: 2025-06-01
Domain: Customer

- `CAT-12::v1::0` (Certified): returns (CAT-12) | part 1
returns (table)
Description: One row per returned item, with original order id, refunded value, units, return reason and refund date.
Refresh: daily 05:00
Linked KPIs: KPI-001, KPI-002, KPI-010, KPI-011, KPI-019
Owner: Head of Supply Chain Analytics
Status: Certified
Version: 1.3
Effective date: 2025-10-15
Domain: Operations

- `CAT-13::v1::0` (Provisional): app_sessions (CAT-13) | part 1
app_sessions (table)
Description: One row per app or web session, with user id, platform, app version, duration and bot flag. Provisional because of duplicate user ids after app reinstalls.
Refresh: hourly
Linked KPIs: KPI-005, KPI-020
Owner: Head of Digital Product
Status: Provisional
Version: 0.6
Effective date: 2026-07-01
Domain: Digital

- `SOP-04::v1::0` (Certified): Data Access Requests (SOP-04) | part 1
# Data Access Requests (SOP-04)

## Purpose
This procedure explains how to get access to a dashboard or a source table. Access depends on the data classification in POL-03.

## Roles
- **Requester:** the employee who needs access.
- **Line manager:** confirms the business need.
- **Data owner:** the owner listed in the data catalog for that asset.
- **Head of Data Governance:** approves access to Restricted data.

## Steps
1. The requester raises an "Access request" in the data service portal, naming the asset from the data catalog and the reason.
2. The line manager approves the business need.
3. For Internal data, access is granted after step 2.
4. For Confidential data (for example the `customers` table), the data owner must also approve.
5. For Restricted data, the Head of Data Governance must also approve, and access is time-limited to 90 days.
6. The platform team grants access within 5 working days of the final approval.

## Reviews
Data owners review the access list for their assets every 6 months and remove anyone who no longer needs it. Leavers lose all access on their last working day.

## Related documents
- POL-03 Data Classification Standard
- POL-01 Data Governance Policy

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2025-03-01
Domain: Governance


---

## H09

**Question:** What is NRR and how is it different from churn?

**Answer:** Net Revenue Retention (NRR) measures how much net revenue Kestrel keeps from an existing group of customers over 12 months, including growth and losses from customers who stop buying [KPI-010::v1::0]. In contrast, Customer Churn Rate measures the share of recently active customers who stop buying from Kestrel, defined as 180 days passing without a completed purchase [KPI-007::v1::0].

**Key facts to check:**
1. Net Revenue Retention
2. 12 months
3. 180 days
4. New customers acquired during the period are excluded

**Context chunks the answer was given:**

- `KPI-010::v1::0` (Certified): Net Revenue Retention (KPI-010) | part 1
# Net Revenue Retention (KPI-010)

## Definition
Net Revenue Retention (NRR) measures how much net revenue Kestrel keeps from an existing group of customers over 12 months. It includes growth from those customers and losses from customers who stop buying. New customers acquired during the period are excluded.

## Formula
NRR % = (Net revenue in the current 12 months from the base cohort / Net revenue in the prior 12 months from the same cohort) x 100

The base cohort is every identified customer with at least one order in the prior 12-month window. Net revenue follows KPI-001 (after discounts and returns, excluding sales tax).

## Grain and filters
- Reported monthly on a rolling 12-month basis.
- Split by channel (store, app, web) and by loyalty tier.
- Staff purchases and test accounts are excluded.

## Source tables
- `sales_orders`: order value, discounts, order date
- `returns`: refunded value per order
- `customers`: customer id, loyalty tier, staff and test flags

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- A value above 100% means the cohort spent more than in the prior year, even after churn.
- Merged customer records keep the earliest customer id.
- Not comparable with figures before v1.4, which did not deduct returns.

## Change history
- v1.4 (2025-10-01): returns now deducted, aligned with KPI-001.
- v1.0 (2025-01-15): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 1.4
Effective date: 2025-10-01
Domain: Customer

- `KPI-007::v1::0` (Certified): Customer Churn Rate (KPI-007) | part 1
# Customer Churn Rate (KPI-007)

## Definition
Customer Churn Rate is the share of recently active customers who stop buying from Kestrel. A customer has churned when 180 days pass without a completed purchase in any channel.

## Formula
Churn Rate % = Customers in the start base with no purchase for 180 days by quarter end / Customers in the start base x 100

The start base is every identified customer with at least one completed order in the 180 days before the quarter starts.

## Grain and filters
- Reported quarterly, with a monthly rolling view.
- Split by loyalty tier, region and first purchase channel.
- Staff and test accounts are excluded.

## Source tables
- `customers`: customer id, loyalty tier, account status
- `sales_orders`: customer id, order date, status

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- A customer who closes their account counts as churned immediately.
- This v2 replaces v1 (KPI-007-V1), which counted account closures only. v1 is Deprecated and its figures must not be compared with v2.
- Churn is reported one quarter after the fact, because the 180-day window must pass first.

## Change history
- v2.0 (2026-04-01): 180-day inactivity definition approved by the KPI Council under SOP-03.
- v1.0 (2025-01-01): account-closure definition, now Deprecated.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 2.0
Effective date: 2026-04-01
Domain: Customer

- `KPI-007-V1::v1::0` (Deprecated): Customer Churn Rate (v1) (KPI-007-V1) | part 1
# Customer Churn Rate (v1) (KPI-007-V1)

## Definition
DEPRECATED. Replaced by Customer Churn Rate v2 (KPI-007) from 2026-04-01. Do not use for reporting.

Customer Churn Rate v1 is the share of loyalty members who close their loyalty account in a month.

## Formula
Churn Rate % = Loyalty accounts closed in the month / Loyalty accounts open at the start of the month x 100

## Grain and filters
- Reported monthly.
- Loyalty members only; customers without an account are not included.

## Source tables
- `customers`: account status, account open date, account closed date

## Dashboards
- None. Removed from all dashboards on 2026-04-01.

## Caveats and exclusions
- Most customers who stop buying never close their account, so this method understated churn.
- Customers who buy without a loyalty account were invisible to this KPI.
- These weaknesses are why the KPI Council replaced it with the inactivity-based v2.

## Change history
- 2026-04-01: Deprecated, replaced by KPI-007 v2.0.
- v1.0 (2025-01-01): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Deprecated
Version: 1.0
Effective date: 2025-01-01
Domain: Customer

- `KPI-004::v1::0` (Certified): Average Order Value (KPI-004) | part 1
# Average Order Value (KPI-004)

## Definition
Average Order Value (AOV) is the average net value of a completed order across all channels. It shows how much a customer spends each time they buy.

## Formula
AOV = Net Revenue / Number of completed orders

Net Revenue follows KPI-001. An order is one transaction id; an online order shipped in several parcels still counts as one order.

## Grain and filters
- Calculated daily, reported weekly and monthly.
- Split by channel, region and store.
- Cancelled orders are excluded.

## Source tables
- `sales_orders`: order id, status, net value, channel, store

## Dashboards
- Sales Performance Dashboard

## Caveats and exclusions
- Zero-value orders (for example free replacements) are excluded.
- Because returns reduce Net Revenue in the month they are refunded, AOV for a closed month can change slightly.
- AOV measures value per order. For units per order, use Basket Size (KPI-008).

## Change history
- v1.2 (2025-05-01): zero-value orders excluded.
- v1.0 (2024-06-01): first certified version.

## Ownership and status
Owner: Head of Sales Analytics
Status: Certified
Version: 1.2
Effective date: 2025-05-01
Domain: Sales

- `KPI-012::v1::0` (Certified): Repeat Purchase Rate (KPI-012) | part 1
# Repeat Purchase Rate (KPI-012)

## Definition
Repeat Purchase Rate is the share of new customers who come back and buy a second time within 90 days of their first purchase. It measures how well Kestrel turns first-time buyers into regular customers.

## Formula
Repeat Purchase Rate % = New customers with a second completed order within 90 days of their first order / New customers in the cohort month x 100

A new customer is an identified customer whose first ever completed order falls in the cohort month.

## Grain and filters
- Reported monthly by cohort (month of first purchase).
- Split by first purchase channel and region.
- Staff and test accounts are excluded.

## Source tables
- `sales_orders`: customer id, order id, order date, status
- `customers`: first order date, staff and test flags

## Dashboards
- Customer 360 Dashboard

## Caveats and exclusions
- Each cohort is reported 90 days after the cohort month closes, so the latest three months are always blank.
- A second order on the same day counts only if it is a separate transaction.
- The 90-day window here is about repeat buying. It is not related to the Active Customer definition (KPI-006).

## Change history
- v1.0 (2025-06-01): first certified version.

## Ownership and status
Owner: Head of Customer Analytics
Status: Certified
Version: 1.0
Effective date: 2025-06-01
Domain: Customer


---

## H10

**Question:** What are key KPIs and Dashboards serving Customer Domain. Give me strcutured asnwer.

**Answer:** The Customer Domain includes the following dashboards and tables: 1. Customer 360 Dashboard (CAT-02), which provides a single view of customer health including activity, churn, retention, lifetime value, repeat buying, and NPS, refreshed daily at 07:00 and linked to KPIs KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, and KPI-013 [CAT-02::v1::0]. 2. Customers table (CAT-08), which holds one row per identified customer including loyalty tier, account status, first order date, acquisition channel, and staff and test flags, refreshed daily at 05:00 and linked to KPIs KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, and KPI-014 [CAT-08::v1::0].

**Key facts to check:**
1. Customer 360 Dashboard
2. Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-013

**Context chunks the answer was given:**

- `CAT-02::v1::0` (Certified): Customer 360 Dashboard (CAT-02) | part 1
Customer 360 Dashboard (dashboard)
Description: Single view of customer health: activity, churn, retention, lifetime value, repeat buying and NPS. Provisional KPIs are labelled on their tiles.
Refresh: daily 07:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-013
Owner: Head of Customer Analytics
Status: Certified
Version: 2.2
Effective date: 2026-04-01
Domain: Customer

- `CAT-03::v1::0` (Certified): Sales Performance Dashboard (CAT-03) | part 1
Sales Performance Dashboard (dashboard)
Description: Trading view for store, app and web sales: revenue, order value, conversion, basket size, footfall conversion and returns. Provisional KPIs are labelled on their tiles.
Refresh: daily 07:00
Linked KPIs: KPI-001, KPI-004, KPI-005, KPI-008, KPI-009, KPI-019
Owner: Head of Sales Analytics
Status: Certified
Version: 2.0
Effective date: 2026-01-15
Domain: Sales

- `SOP-06::v1::0` (Certified): Dashboard Publishing Standard (SOP-06) | part 1
# Dashboard Publishing Standard (SOP-06)

## Purpose
This standard sets the rules every dashboard must meet before it is shared outside its own team.

## Roles
- **Dashboard owner:** builds and maintains the dashboard; listed in the data catalog.
- **Data steward:** checks the dashboard against this standard before publishing.

## Rules
1. Every published dashboard must have an entry in the data catalog with an owner, a refresh schedule and its linked KPIs.
2. Every KPI tile must show the KPI id and version, for example "KPI-007 v2.0".
3. Provisional KPIs must carry a visible "Provisional" label on their tile.
4. Deprecated KPIs must be removed from all dashboards on their deprecation date.
5. The Executive KPI Pack may only contain Certified KPIs. No exceptions.
6. Each dashboard shows the time of the last data refresh.
7. A dashboard can only be Certified if all its tiles use Certified KPIs or carry the Provisional label.

## Steps to publish
1. The dashboard owner requests a review in the data service portal.
2. The data steward checks rules 1 to 7 and records the result.
3. If all rules pass, the dashboard is published and its catalog entry is updated.

## Related documents
- SOP-01 KPI Certification Process
- SOP-03 Metric Change Management
- SOP-05 Data Quality Incidents

## Ownership and status
Owner: Head of Data Governance
Status: Certified
Version: 1.0
Effective date: 2025-11-15
Domain: Governance

- `CAT-06::v1::0` (Provisional): Digital Engagement Dashboard (CAT-06) | part 1
Digital Engagement Dashboard (dashboard)
Description: App and web engagement: active app users, sessions and digital conversion by platform and app version.
Refresh: daily 08:00
Linked KPIs: KPI-005, KPI-020
Owner: Head of Digital Product
Status: Provisional
Version: 0.8
Effective date: 2026-07-01
Domain: Digital

- `CAT-08::v1::0` (Certified): customers (CAT-08) | part 1
customers (table)
Description: One row per identified customer (loyalty member or account holder). Holds loyalty tier, account status, first order date, acquisition channel, and staff and test flags. Classified as Confidential.
Refresh: daily 05:00
Linked KPIs: KPI-006, KPI-007, KPI-010, KPI-011, KPI-012, KPI-014
Owner: Head of Customer Analytics
Status: Certified
Version: 3.2
Effective date: 2025-06-01
Domain: Customer

