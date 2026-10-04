---
doc_id: KPI-008
title: Basket Size
doc_type: kpi
domain: Sales
owner: Head of Sales Analytics
certification: Provisional
version: "0.9"
effective_date: "2026-02-01"
---
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
