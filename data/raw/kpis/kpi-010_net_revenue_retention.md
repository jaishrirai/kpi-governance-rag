---
doc_id: KPI-010
title: Net Revenue Retention
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: "1.4"
effective_date: "2025-10-01"
---
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
