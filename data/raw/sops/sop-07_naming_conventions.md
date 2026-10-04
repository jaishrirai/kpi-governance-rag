---
doc_id: SOP-07
title: Naming Conventions
doc_type: sop
domain: Governance
owner: Head of Data Governance
certification: Certified
version: "1.0"
effective_date: "2025-01-15"
---
# Naming Conventions (SOP-07)

## Purpose
Consistent names make KPIs, tables and dashboards easy to find and hard to confuse.

## Roles
- **Data steward:** assigns ids and checks names before publishing.

## Rules
1. **KPI ids:** KPI- followed by three digits, for example KPI-014. Ids are never reused.
2. **Deprecated versions:** keep the original id with a version suffix, for example KPI-007-V1.
3. **KPI names:** plain English in Title Case. Use "Rate" or "%" for ratios (for example Return Rate, Gross Margin %). Include the time window in the name when it is part of the definition, for example "Active Customer (30-day)".
4. **Catalog ids:** CAT- followed by two digits, for example CAT-02.
5. **Tables:** lower case snake_case plural nouns, for example `sales_orders`, `nps_responses`.
6. **Dashboards:** Title Case ending in "Dashboard", except the Executive KPI Pack and the Supply Chain Control Tower, which keep their established names.
7. **Documents:** SOP-NN for procedures, POL-NN for policies and standards.
8. **Similar names:** a new KPI name must not differ from an existing one by a single word unless both definitions explain the difference (see KPI-006 and KPI-020).

## Related documents
- SOP-02 Requesting a New KPI
