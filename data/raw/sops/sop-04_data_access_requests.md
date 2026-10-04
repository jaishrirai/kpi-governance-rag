---
doc_id: SOP-04
title: Data Access Requests
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.0"
effective_date: "2025-03-01"
---
# Data Access Requests (SOP-04)

## Purpose
This procedure explains how to get access to a dashboard or a source table. Access depends on the data classification in POL-03.

## Roles
- **Requester:** the employee who needs access.
- **Line manager:** confirms the business need.
- **Data owner:** the owner listed in the data catalog for that asset.
- **Head of Data Governance:** approves access to Restricted data.

## Steps
1. The requester raises an "Access request" in the data service portal, naming the asset from the data catalog and the reason.
2. The line manager approves the business need.
3. For Internal data, access is granted after step 2.
4. For Confidential data (for example the `customers` table), the data owner must also approve.
5. For Restricted data, the Head of Data Governance must also approve, and access is time-limited to 90 days.
6. The platform team grants access within 5 working days of the final approval.

## Reviews
Data owners review the access list for their assets every 6 months and remove anyone who no longer needs it. Leavers lose all access on their last working day.

## Related documents
- POL-03 Data Classification Standard
- POL-01 Data Governance Policy
