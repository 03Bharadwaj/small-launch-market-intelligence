# Commercial Small Launch Market Intelligence System

A business development analyst's operating toolkit for the small satellite launch market — built with Python, SQLite, and Power BI.

## What This Project Does

This system answers the three questions every BD team at a small launch vehicle company needs answered daily:

- Who do we sell to? 447 satellite operators scored and ranked by prospect quality
- How do we price? Competitive positioning across 19 launch vehicles with price-to-win ranges by mass class
- How large is the market? Monte Carlo demand forecast across 10,000 simulations through 2030

## Data Sources

- UCS Satellite Database (May 2023) — 6,189 satellites, 447 operators
- Company websites and press releases — launch vehicle specs and pricing
- Announced constellation filings — pipeline demand, 4,249 satellites remaining to deploy

## Tech Stack

- Python: pandas, numpy, scipy, matplotlib
- SQLite: relational database with 5 tables
- Power BI: 4-page interactive dashboard

## The Three Modules

Module 1 — Customer Intelligence Engine
Scores every satellite operator across 7 dimensions: orbit fit, mass fit, constellation potential, provider diversity, recency, sector, and geography. Outputs a ranked prospect table filterable by segment and tier.

Module 2 — Competitive Pricing Model
Benchmarks 11 operational launch vehicles on price per kg, payload capacity, and reliability. Produces a price-to-win range for each satellite mass class.

Module 3 — Launch Demand Forecast
Fits a trend model to 9 years of historical data, layers announced constellation pipeline, and runs 10,000 Monte Carlo simulations. Outputs P10, P50, P90 annual demand through 2030.

## Key Numbers

- 39 Priority-tier prospects from 447 operators scored
- Market median price for dedicated small launchers: $53,892 per kg
- 4,249 satellites remaining to deploy across 18 announced constellations
- 2030 base case forecast: 6,518 small satellites globally
- India and Asia-Pacific addressable share: 12.3 percent of global demand

## How to Run

1. Download UCS Satellite Database from https://www.ucsusa.org/resources/satellite-database
2. Place the Excel file in your Downloads folder
3. Run Python scripts in order from 01 through 07
4. Open the Power BI dashboard from the powerbi folder