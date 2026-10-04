---
doc_id: KPI-014
title: Customer Acquisition Cost
doc_type: kpi
domain: Marketing
owner: Head of Marketing Analytics
certification: Certified
version: "1.1"
effective_date: "2025-12-01"
---
# Customer Acquisition Cost (KPI-014)

## Definition
Customer Acquisition Cost (CAC) is the average marketing spend needed to win one new identified customer. A new customer is someone whose first ever completed order falls in the period.

## Formula
CAC = Acquisition marketing spend in the period / New customers acquired in the period

## Grain and filters
- Reported monthly and quarterly.
- Split by marketing channel (paid search, paid social, affiliates, print).
- Only campaigns tagged as acquisition are included.

## Source tables
- `marketing_spend`: campaign, channel, objective tag, spend, agency fees
- `customers`: customer id, first order date, acquisition channel

## Dashboards
- Marketing Effectiveness Dashboard

## Caveats and exclusions
- Brand and retention campaigns are excluded from spend.
- Agency fees are included in spend from v1.1.
- Channel-level CAC uses the acquisition channel recorded on the customer. Customers with no recorded channel only count in the total.
- Compare with Customer Lifetime Value (KPI-011) to judge payback, but note CLV is still Provisional.

## Change history
- v1.1 (2025-12-01): agency fees added to spend.
- v1.0 (2025-03-15): first certified version.
