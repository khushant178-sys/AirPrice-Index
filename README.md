# SIH Problem Statement 56 — India Airfare Price Index

## What this prototype does
This project converts the supplied Yatra airfare snapshots into a working dashboard for an **Airfare Price Index**.

### Included
- `app.py` — Streamlit dashboard
- `data_clean.csv` — standardized main dataset from the 15 Yatra route/date files
- `bang_mum_supplement.csv` — standardized supplemental Bangalore–Mumbai files
- `requirements.txt` — Python dependencies

## Current data
The main dataset contains 2,216 valid airfare observations across:
- Bangalore–Mumbai (`BM`)
- Delhi–Bangalore (`DB`)
- Delhi–Navi Mumbai (`DM`)
- snapshot dates: 10, 13, 15, 19 and 21 September 2026
- airlines: IndiGo, Air India, Air India Express, Akasa Air, and SpiceJet where available

The Bangalore–Mumbai supplemental files are kept separately because they overlap the BM route and should not be blindly combined with the Yatra BM files.

## Index methodology
This is a prototype, not an official CPI series:
1. Clean fare values (including commas).
2. Calculate route × snapshot-date median fare.
3. Use the earliest snapshot as base = 100.
4. Calculate each route's relative price.
5. Aggregate route indices using equal weights.

For a production system, use official passenger/expenditure weights, a defined fare basket, tax/fee treatment, seasonal adjustment, missing-data handling and revision rules.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## How this becomes a real SIH solution
Add scheduled data collectors for airline/OTA sources where permitted, a database (PostgreSQL), an API (FastAPI), automated validation, a daily index job, anomaly detection, forecasting, and role-based dashboards for policymakers.

## Suggested architecture
Sources -> Collector/API -> Raw Store -> Cleaning/Validation -> Fare Normalization -> Index Engine -> Database -> API -> Dashboard

## Important
The supplied data is used as a prototype dataset. Live scraping/API integration must comply with each source's terms, robots rules, licensing and applicable law.
