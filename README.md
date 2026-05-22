# Village Economic Growth Intelligence

### Identifying Top 100 High-Growth Villages Using Satellite Data · 2019–2023

## What This Is
A data pipeline that scores 588,760 Indian villages on economic 
growth using satellite nighttime lights and public datasets, 
producing a ranked list of the top 100 fastest-growing villages.

## Data Sources
| Source | What I Used It For |
|--------|-------------------|
| SHRUG VIIRS (DDL) | Village-level nighttime light brightness 2019 & 2023 |
| SHRUG Census VD 2011 | Infrastructure indicators — roads, electricity, banks |
| Antyodaya 2020 | Housing quality, PMAY scheme penetration |
| Google Earth Engine | District-level NTL validation (my own GEE script) |

## Scoring Formula: Score = 0.40 × NTL Growth
+ 0.25 × Infrastructure
+ 0.20 × Housing Quality
+ 0.15 × Market Access

NTL growth uses log ratio to handle scale differences fairly.
Outliers capped at 99th percentile.

## How To Run
```bash
pip install pandas numpy
python pipeline.py
# Opens dashboard: india_village_dashboard_REAL.html
```

## Key Findings
- Kerala leads with 37 of top 100 villages
- Rank 1: Haryana District 75 — NCR peri-urban corridor
- Villages near highways show strongest NTL growth
- Higher PMAY density correlates with economic growth score

## Limitations
- Infrastructure data from Census 2011 (14 years old)
- No village names — SHRUG uses numeric IDs
- Data window 2019–2023, not full 5 years

## What I'd Do Next
- Add Sentinel-2 land cover change detection
- Match scores against income survey data for validation
- Build live monthly refresh using VIIRS 15-day composites
