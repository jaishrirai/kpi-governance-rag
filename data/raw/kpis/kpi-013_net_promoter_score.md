---
doc_id: KPI-013
title: Net Promoter Score
doc_type: kpi
domain: Customer
owner: Head of Customer Analytics
certification: Certified
version: "1.2"
effective_date: "2025-08-01"
---
# Net Promoter Score (KPI-013)

## Definition
Net Promoter Score (NPS) measures how likely customers are to recommend Kestrel to a friend. It comes from a survey question scored 0 to 10, sent after a purchase.

## Formula
NPS = % Promoters - % Detractors

Promoters score 9 or 10. Detractors score 0 to 6. Passives (7 or 8) count in the total but in neither group. NPS ranges from -100 to +100.

## Grain and filters
- Reported monthly.
- Split by channel and region.
- A cut is only shown when it has at least 100 responses.

## Source tables
- `nps_responses`: response id, score, channel, region, response date

## Dashboards
- Customer 360 Dashboard
- Executive KPI Pack

## Caveats and exclusions
- The survey is sent 7 days after a purchase. A customer is surveyed at most once every 90 days.
- The `nps_responses` table is Provisional in the catalog while the survey platform migration finishes. The KPI keeps Certified status by an exception approved by the KPI Council.
- Free-text comments are not part of the score.

## Change history
- v1.2 (2025-08-01): minimum of 100 responses per cut.
- v1.0 (2024-08-01): first certified version.
