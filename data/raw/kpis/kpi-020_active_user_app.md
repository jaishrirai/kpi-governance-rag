---
doc_id: KPI-020
title: Active User (app 30-day)
doc_type: kpi
domain: Digital
owner: Head of Digital Product
certification: Provisional
version: "0.8"
effective_date: "2026-07-01"
---
# Active User (app 30-day) (KPI-020)

## Definition
An Active User is a logged-in user of the Kestrel mobile app who had at least one session in the last 30 days. No purchase is needed. It measures app engagement, not buying.

## Formula
Active Users = Count of distinct app user ids with at least one qualifying session where the session date is between (run date - 29 days) and the run date

A qualifying session follows the rules in KPI-005: longer than 5 seconds and not a bot.

## Grain and filters
- Daily snapshot, reported weekly and monthly.
- Split by platform (iOS, Android) and app version.
- Web sessions are excluded; this KPI is for the app only.

## Source tables
- `app_sessions`: user id, session id, platform, app version, duration, bot flag

## Dashboards
- Digital Engagement Dashboard

## Caveats and exclusions
- This is not Active Customer (KPI-006). Active Customer requires a purchase in any channel; Active User only requires an app session.
- Provisional: reinstalling the app can create a second user id for the same person, which inflates the count.
- Not approved for the Executive KPI Pack.

## Change history
- v0.8 (2026-07-01): approved as Provisional at the Q2 2026 KPI review.
