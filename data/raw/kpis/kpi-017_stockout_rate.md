---
doc_id: KPI-017
title: Stockout Rate
doc_type: kpi
domain: Operations
owner: Head of Supply Chain Analytics
certification: Certified
version: "1.1"
effective_date: "2025-09-01"
---
# Stockout Rate (KPI-017)

## Definition
Stockout Rate is the share of products that should be available in a location but have no sellable stock. It shows how often customers find an empty shelf or an out-of-stock product page.

## Formula
Stockout Rate % = Active SKU-location pairs with zero sellable units at the 06:00 snapshot / Total active SKU-location pairs x 100

An active SKU-location pair is a product that is in the current range for that store or for online.

## Grain and filters
- Calculated daily, reported weekly.
- Split by location, region and product category.
- Online availability uses distribution centre stock.

## Source tables
- `inventory_snapshots`: SKU, location, sellable units, range status, snapshot time

## Dashboards
- Supply Chain Control Tower

## Caveats and exclusions
- Discontinued products and seasonal products outside their season are excluded.
- Damaged or reserved units are not sellable and count as zero.
- A product that sells out at noon and is refilled before the next 06:00 snapshot is not counted.

## Change history
- v1.1 (2025-09-01): snapshot time moved from midnight to 06:00.
- v1.0 (2025-02-01): first certified version.
