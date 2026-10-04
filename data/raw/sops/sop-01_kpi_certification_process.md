---
doc_id: SOP-01
title: KPI Certification Process
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "2.0"
effective_date: "2025-02-01"
---
# KPI Certification Process (SOP-01)

## Purpose
This procedure explains how a KPI moves from Provisional to Certified. Only Certified KPIs may be used in the Executive KPI Pack and in board packs.

## Roles
- **KPI owner:** the domain head who is accountable for the definition (for example Head of Customer Analytics).
- **Data steward:** checks the formula, source tables and data quality.
- **KPI Council:** chaired by the Head of Data Governance; approves or rejects certification.

## Steps
1. The KPI owner submits the definition using the standard KPI template. The KPI starts as Provisional with a version below 1.0.
2. The data steward confirms that every source table and dashboard named in the definition is listed in the data catalog.
3. The data steward runs a two-month parallel test. The KPI must reconcile within 1% against an independent calculation.
4. The KPI owner presents the definition at the monthly KPI Council.
5. If approved, the version becomes 1.0, the status becomes Certified, and the change history is updated.
6. The data steward updates the KPI Glossary Summary (POL-04) within 5 working days.
7. Certified KPIs are reviewed every 12 months. A KPI that misses its review drops back to Provisional.

## Related documents
- SOP-02 Requesting a New KPI
- SOP-03 Metric Change Management
- POL-01 Data Governance Policy
