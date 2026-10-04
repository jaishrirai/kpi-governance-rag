---
doc_id: KPI-002
title: Gross Margin %
doc_type: kpi
domain: Finance
owner: Head of Finance Analytics
certification: Certified
version: "1.3"
effective_date: "2025-09-15"
---
# Gross Margin % (KPI-002)

## Definition
Gross Margin % is the share of Net Revenue left after paying for the goods that were sold. It shows how profitable the product mix is before store, logistics and head office costs.

## Formula
Gross Margin % = (Net Revenue - Cost of goods sold) / Net Revenue x 100

Net Revenue follows KPI-001. Cost of goods sold (COGS) is the landed cost of items sold, including freight from suppliers to distribution centres.

## Grain and filters
- Reported monthly and year to date.
- Split by product category and channel.
- Concession sales are excluded because Kestrel only earns a commission on them.

## Source tables
- `sales_orders`: net value and landed cost per order line
- `returns`: refunded value and restocked cost

## Dashboards
- Executive KPI Pack

## Caveats and exclusions
- Items that are returned and restocked reverse their COGS.
- Damaged returns that are written off stay in COGS.
- Stock shrinkage (theft, damage in store) is not included here; Finance reports it separately.
- Store labour and delivery to customers are not part of COGS.

## Change history
- v1.3 (2025-09-15): inbound freight added to COGS.
- v1.0 (2024-09-01): first certified version.
