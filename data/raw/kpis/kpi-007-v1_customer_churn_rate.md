---
doc_id: KPI-007-V1
title: Customer Churn Rate (v1)
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Deprecated
version: "1.0"
effective_date: "2025-01-01"
---
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
