---
doc_id: KPI-005
title: Conversion Rate
doc_type: kpi
domain: Sales
owner: Head of Sales Analytics
certification: Certified
version: "2.0"
effective_date: "2026-01-15"
---
# Conversion Rate (KPI-005)

## Definition
Conversion Rate is the share of app and web sessions that end in at least one completed order. It covers digital channels only. Store conversion is measured separately by Store Footfall Conversion (KPI-009).

## Formula
Conversion Rate % = Qualifying sessions with a completed order / Total qualifying sessions x 100

A qualifying session has at least one page or screen view, lasts more than 5 seconds and is not flagged as a bot.

## Grain and filters
- Calculated daily.
- Split by platform (iOS, Android, web) and traffic source.
- Internal staff traffic is excluded.

## Source tables
- `app_sessions`: session id, platform, duration, bot flag
- `sales_orders`: order id, session id, status

## Dashboards
- Sales Performance Dashboard
- Digital Engagement Dashboard

## Caveats and exclusions
- A session ends after 30 minutes without activity.
- Orders are linked to sessions by session id. If a customer browses on one device and buys on another, only the buying session converts.
- v2.0 figures are not comparable with v1.x because bot traffic was counted before.

## Change history
- v2.0 (2026-01-15): bot filter and 5-second rule added.
- v1.0 (2024-10-01): first certified version.
