---
doc_id: KPI-019
title: Return Rate
doc_type: kpi
domain: Operations
owner: Head of Supply Chain Analytics
certification: Certified
version: "1.2"
effective_date: "2025-10-15"
---
# Return Rate (KPI-019)

## Definition
Return Rate is the share of sales value that customers send or bring back for a refund. It covers returns from all channels.

## Formula
Return Rate % = Value of items returned / Gross sales value x 100

Both values are assigned to the month of the original sale. A unit-based rate (units returned / units sold) is available as a secondary view.

## Grain and filters
- Reported monthly by month of original sale.
- Split by product category and sales channel.
- Exchanges count as a return plus a new sale.

## Source tables
- `returns`: order id, returned value, units, return reason, return date
- `sales_orders`: order id, gross value, units, sale date

## Dashboards
- Supply Chain Control Tower
- Sales Performance Dashboard

## Caveats and exclusions
- Customers can return items for up to 60 days, so the latest two months keep rising.
- Net Revenue (KPI-001) deducts returns in the month of refund, so the two KPIs will not line up month by month.
- Items returned as faulty are also tracked in data quality reports for suppliers.

## Change history
- v1.2 (2025-10-15): switched to month of original sale.
- v1.0 (2024-11-01): first certified version.
