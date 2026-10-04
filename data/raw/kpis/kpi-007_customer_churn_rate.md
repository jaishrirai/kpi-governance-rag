---
doc_id: KPI-007
title: Customer Churn Rate
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: "2.0"
effective_date: "2026-04-01"
---
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
