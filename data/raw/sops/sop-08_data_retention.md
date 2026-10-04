---
doc_id: SOP-08
title: Data Retention
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.1"
effective_date: "2026-02-15"
---
# Data Retention (SOP-08)

## Purpose
This procedure sets how long Kestrel keeps data and documents, and how they are deleted.

## Roles
- **Data owner:** makes sure their tables follow the retention periods.
- **Platform team:** runs the monthly deletion jobs.
- **Head of Data Governance:** approves any exception.

## Retention periods
- `sales_orders`, `returns` and `invoices`: 7 years, for finance and tax audit.
- `customers`: while the account is open, then 2 years after closure.
- `app_sessions`: 25 months.
- `nps_responses`: 3 years.
- `marketing_spend`, `inventory_snapshots` and `deliveries`: 5 years.
- Deprecated KPI definitions: 2 years after deprecation, then archived.

## Steps
1. Deletion jobs run on the first Sunday of each month.
2. The platform team sends a deletion report to each data owner.
3. A customer request to delete personal data is completed within 30 days, unless finance law requires the order record to be kept. In that case the record is anonymised.

## Related documents
- POL-01 Data Governance Policy
- POL-03 Data Classification Standard
