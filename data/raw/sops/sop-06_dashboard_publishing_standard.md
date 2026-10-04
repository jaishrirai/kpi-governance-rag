---
doc_id: SOP-06
title: Dashboard Publishing Standard
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.0"
effective_date: "2025-11-15"
---
# Dashboard Publishing Standard (SOP-06)

## Purpose
This standard sets the rules every dashboard must meet before it is shared outside its own team.

## Roles
- **Dashboard owner:** builds and maintains the dashboard; listed in the data catalog.
- **Data steward:** checks the dashboard against this standard before publishing.

## Rules
1. Every published dashboard must have an entry in the data catalog with an owner, a refresh schedule and its linked KPIs.
2. Every KPI tile must show the KPI id and version, for example "KPI-007 v2.0".
3. Provisional KPIs must carry a visible "Provisional" label on their tile.
4. Deprecated KPIs must be removed from all dashboards on their deprecation date.
5. The Executive KPI Pack may only contain Certified KPIs. No exceptions.
6. Each dashboard shows the time of the last data refresh.
7. A dashboard can only be Certified if all its tiles use Certified KPIs or carry the Provisional label.

## Steps to publish
1. The dashboard owner requests a review in the data service portal.
2. The data steward checks rules 1 to 7 and records the result.
3. If all rules pass, the dashboard is published and its catalog entry is updated.

## Related documents
- SOP-01 KPI Certification Process
- SOP-03 Metric Change Management
- SOP-05 Data Quality Incidents
