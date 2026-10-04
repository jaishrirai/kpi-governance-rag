---
doc_id: KPI-006
title: Active Customer (30-day)
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: "1.1"
effective_date: "2025-11-01"
---
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
