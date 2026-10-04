---
doc_id: KPI-003
title: Days Sales Outstanding
doc_type: kpi
domain: Finance
owner: Head of Finance Analytics
certification: Certified
version: "1.0"
effective_date: "2025-03-01"
---
# Days Sales Outstanding (KPI-003)

## Definition
Days Sales Outstanding (DSO) is the average number of days Kestrel takes to collect payment after invoicing a business customer. It only covers credit sales to wholesale partners and corporate gifting clients. Retail sales are paid at checkout and are out of scope.

## Formula
DSO = (Accounts receivable at period end / Credit sales in the period) x Number of days in the period

## Grain and filters
- Reported monthly.
- Split by customer segment (wholesale, corporate gifting).
- Intercompany invoices are excluded.

## Source tables
- `invoices`: invoice amount, invoice date, due date, paid date, status

## Dashboards
- Executive KPI Pack

## Caveats and exclusions
- Disputed invoices stay in accounts receivable until they are resolved.
- Invoices written off as bad debt leave accounts receivable on the write-off date.
- A large invoice raised on the last day of a month can push DSO up for that month only.
- Standard payment terms are 30 days, so a DSO well above 30 means late payment.

## Change history
- v1.0 (2025-03-01): first certified version.
