---
doc_id: KPI-001
title: Net Revenue
doc_type: kpi
domain: Finance
owner: Head of Finance Analytics
certification: Certified
version: "2.1"
effective_date: "2025-07-01"
---
# Net Revenue (KPI-001)

## Definition
Net Revenue is the total value of sales across stores, app and web after discounts, returns and refunds, excluding sales tax. It is the base revenue figure used by every other revenue-based KPI at Kestrel.

## Formula
Net Revenue = Gross sales value - Discounts - Returns and refunds - Sales tax

## Grain and filters
- Calculated daily, reported weekly and monthly.
- Split by channel (store, app, web), region and product category.
- Staff purchases are included at the discounted price; test transactions are excluded.

## Source tables
- `sales_orders`: gross value, discount and tax per order
- `returns`: refunded value and refund date

## Dashboards
- Executive KPI Pack
- Sales Performance Dashboard

## Caveats and exclusions
- Gift card sales are not revenue when sold; they count when the card is redeemed.
- Returns are deducted in the month the refund is processed, not the month of the original sale. Return Rate (KPI-019) uses the month of sale instead.
- Delivery charges paid by customers are included.

## Change history
- v2.1 (2025-07-01): gift cards moved to recognition at redemption.
- v2.0 (2025-01-01): returns and refunds deducted.
- v1.0 (2024-04-01): first certified version.
