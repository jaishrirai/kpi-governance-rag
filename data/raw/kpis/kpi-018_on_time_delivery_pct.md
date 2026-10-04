---
doc_id: KPI-018
title: On-Time Delivery %
doc_type: kpi
domain: Operations
owner: Head of Supply Chain Analytics
certification: Certified
version: "1.0"
effective_date: "2026-01-01"
---
# On-Time Delivery % (KPI-018)

## Definition
On-Time Delivery % is the share of customer orders delivered, or ready for collection, on or before the date promised at checkout. It covers home delivery and click-and-collect.

## Formula
On-Time Delivery % = Orders delivered or ready on or before the promised date / Total delivered or collected orders x 100

## Grain and filters
- Calculated daily, reported weekly and monthly.
- Split by delivery method (home delivery, click-and-collect), carrier and region.
- Orders cancelled before dispatch are excluded.

## Source tables
- `deliveries`: order id, promised date, delivered date, ready-for-collection date, carrier, method

## Dashboards
- Supply Chain Control Tower

## Caveats and exclusions
- If the customer asks to change the delivery date, the new date becomes the promised date.
- A failed delivery because the customer was not at home still counts as on time if the first attempt was on time.
- For click-and-collect, on time means the order was ready in store by the promised time, not when the customer collected it.

## Change history
- v1.0 (2026-01-01): first certified version.
