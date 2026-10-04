---
doc_id: KPI-004
title: Average Order Value
doc_type: kpi
domain: Sales
owner: Head of Sales Analytics
certification: Certified
version: "1.2"
effective_date: "2025-05-01"
---
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
