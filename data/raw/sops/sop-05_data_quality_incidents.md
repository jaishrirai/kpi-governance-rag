---
doc_id: SOP-05
title: Data Quality Incidents
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.3"
effective_date: "2025-09-01"
---
# Data Quality Incidents (SOP-05)

## Purpose
This procedure explains what to do when a KPI or dashboard shows wrong or missing data.

## Roles
- **Reporter:** anyone who spots the problem.
- **Data steward:** triages the incident and sets the severity.
- **KPI owner:** communicates with users and signs off the fix.

## Severity levels
- **P1:** a Certified KPI in the Executive KPI Pack is wrong or missing.
- **P2:** any other Certified KPI or Certified dashboard is wrong or missing.
- **P3:** a Provisional KPI, a single report or a cosmetic issue.

## Steps
1. The reporter logs a "Data incident" in the data service portal with a screenshot and the KPI id.
2. The data steward sets the severity within 1 hour for P1 and within 1 working day for P2 and P3.
3. For P1 and P2, a warning banner is added to every affected dashboard within 2 hours.
4. The KPI owner tells key users what is affected and when a fix is expected.
5. The fix is tested and the banner is removed once the KPI owner signs off.
6. For P1 incidents, a root cause note is written within 5 working days and shared at the next KPI Council.

## Related documents
- SOP-06 Dashboard Publishing Standard
- POL-01 Data Governance Policy
