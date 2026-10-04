---
doc_id: KPI-011
title: Customer Lifetime Value
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Provisional
version: "0.7"
effective_date: "2026-05-15"
---
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
