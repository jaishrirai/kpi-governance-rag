---
doc_id: KPI-016
title: Inventory Turnover
doc_type: kpi
domain: Operations
owner: Head of Supply Chain Analytics
certification: Certified
version: "1.0"
effective_date: "2025-04-01"
---
# Inventory Turnover (KPI-016)

## Definition
Inventory Turnover is the number of times Kestrel sells and replaces its average stock in a year. A higher number means stock moves faster and less cash is tied up in inventory.

## Formula
Inventory Turnover = Cost of goods sold over the last 12 months / Average inventory value at cost

Average inventory is the mean of the 13 month-end stock values covering the same 12 months. Cost of goods sold follows the definition in KPI-002.

## Grain and filters
- Reported monthly on a rolling 12-month basis.
- Split by product category and distribution centre.
- Concession stock is excluded because Kestrel does not own it.

## Source tables
- `inventory_snapshots`: SKU, location, units on hand, unit cost, snapshot date
- `sales_orders`: landed cost of items sold

## Dashboards
- Supply Chain Control Tower

## Caveats and exclusions
- Stock in transit between a supplier and a distribution centre is included once it is invoiced.
- Seasonal categories show large swings within the year, so compare the same month year on year.
- Days of inventory can be derived as 365 / Inventory Turnover.

## Change history
- v1.0 (2025-04-01): first certified version.
