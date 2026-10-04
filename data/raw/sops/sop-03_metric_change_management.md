---
doc_id: SOP-03
title: Metric Change Management
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.2"
effective_date: "2025-06-15"
---
# Metric Change Management (SOP-03)

## Purpose
This procedure controls changes to Certified KPIs, so that reports stay comparable and users know which version they are looking at.

## Roles
- **KPI owner:** proposes the change.
- **KPI Council:** approves major changes.
- **Dashboard owners:** update dashboards and labels.

## Change types
- **Minor change:** wording, clarifications or new filters that do not change the number. The version goes up by 0.1 (for example 1.3 to 1.4). The KPI owner approves it.
- **Major change:** a new formula, window or population that changes the number. The version goes up to the next whole number (for example 1.0 to 2.0). The KPI Council must approve it.

## Steps for a major change
1. The KPI owner submits the new definition and an impact estimate.
2. The KPI Council approves or rejects it at its monthly meeting.
3. Dashboard owners get at least 30 days of notice before the effective date.
4. On the effective date, the new version becomes Certified and the old version is marked Deprecated with a pointer to the new one.
5. Deprecated definitions are kept for 2 years for audit, then archived (see SOP-08).

## Example
Customer Churn Rate moved from v1 (account closures) to v2 (180 days without a purchase) on 2026-04-01. v1 is now KPI-007-V1 and is Deprecated.

## Related documents
- SOP-01 KPI Certification Process
- SOP-06 Dashboard Publishing Standard
