---
doc_id: KPI-009
title: Store Footfall Conversion
doc_type: kpi
domain: Sales
owner: Head of Sales Analytics
certification: Provisional
version: "0.8"
effective_date: "2026-06-01"
---
# Store Footfall Conversion (KPI-009)

## Definition
Store Footfall Conversion is the share of people entering a store who make a purchase. It covers physical stores only. Digital conversion is measured by Conversion Rate (KPI-005).

## Formula
Store Footfall Conversion % = Store transactions / Store footfall x 100

Footfall is the number of entries counted by door counters during opening hours.

## Grain and filters
- Calculated daily per store, reported weekly.
- Split by store and region.
- Stores without a working door counter are excluded.

## Source tables
- `sales_orders`: store transactions, plus a daily store footfall field loaded from door counters

## Dashboards
- Sales Performance Dashboard

## Caveats and exclusions
- Provisional: door-counter files are loaded manually, and 12 stores have no counter yet.
- Staff entries are not filtered out in every store, which lowers the rate.
- A group shopping together counts as several visitors but usually one transaction.
- Provisional KPIs must not appear in the Executive KPI Pack.

## Change history
- v0.8 (2026-06-01): pilot definition used in 40 stores.
