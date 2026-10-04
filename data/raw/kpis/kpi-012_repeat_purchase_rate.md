---
doc_id: KPI-012
title: Repeat Purchase Rate
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: "1.0"
effective_date: "2025-06-01"
---
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
