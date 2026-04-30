# Commercial Small Launch Market Intelligence System

A business development analyst's operating toolkit for the small satellite launch market — built with Python, SQLite, and Power BI.

---

## Dashboard Preview

![Market Intelligence Summary](screenshots/Market%20Intelligence%20-%20Summary.png)

---

## What This Project Does

This system answers the three questions every BD team at a small launch vehicle company needs answered:

- **Who do we sell to?** — 447 satellite operators scored and ranked by prospect quality
- **How do we price?** — Competitive positioning across 19 launch vehicles with price-to-win ranges by satellite mass class
- **How large is the market?** — Monte Carlo demand forecast (10,000 simulations) through 2030 with conservative, base, and optimistic scenarios

---

## Dashboard Pages

### Customer Intelligence — Prospect Scoring Engine
![Customer Intelligence](screenshots/Customer%20Intelligence%20-%20Prospective%20Scoring.png)

### Competitive Pricing & Market Positioning
![Competitive Pricing](screenshots/Competitive%20Pricing%20%26%20Market%20Positioning%20.png)

### Launch Demand Forecast — Monte Carlo Simulation
![Launch Demand Forecast](screenshots/Launch%20Demand%20Forecast.png)

### Market Intelligence Summary
![Market Intelligence Summary](screenshots/Market%20Intelligence%20-%20Summary.png)

> **To interact with the full dashboard:** Download Power BI Desktop (free) from microsoft.com, then open `powerbi/SmallLaunchMIS_Dashboard.pbix`

---

## Data Sources

| Source | Used For |
|--------|----------|
| UCS Satellite Database (May 2023) | 6,189 satellites, 447 operators |
| Company websites and press releases | Launch vehicle specs and pricing (manually compiled) |
| Announced constellation filings | Pipeline demand — 4,249 satellites remaining to deploy |

All data is publicly available. Pricing gaps are explicitly labelled by confidence level: confirmed, estimated, or reported.

---

## Tech Stack

- **Python** — pandas, numpy, scipy, matplotlib
- **SQLite** — relational database with 5 tables
- **Power BI** — 4-page interactive dashboard
- **GitHub** — full documented pipeline

---

## Project Structure

```
SmallLaunchMIS/
├── data/
│   ├── raw/                  # Source data files
│   └── processed/            # Cleaned outputs and charts
├── python/                   # All analysis scripts (run in order 01–07)
├── sql/                      # Database schema
├── powerbi/                  # Dashboard (.pbix)
├── screenshots/              # Dashboard page previews
└── README.md
```

---

## Key Outputs

- 39 Priority-tier prospects identified from 447 operators scored
- Market median price for dedicated small launchers: $53,892/kg
- Lowest market price: $6,000/kg (SpaceX Falcon 9 rideshare)
- 4,249 satellites remaining to deploy across 18 announced constellations
- 2030 demand forecast: 4,808 (conservative) — 6,518 (base) — 8,854 (optimistic)
- India and Asia-Pacific addressable share: ~12.3% of global demand

---

## How to Run

1. Download the UCS Satellite Database from [ucsusa.org](https://www.ucsusa.org/resources/satellite-database) and place the Excel file in your Downloads folder
2. Run Python scripts in order from `01` through `07` inside the `python/` folder
3. Open `powerbi/SmallLaunchMIS_Dashboard.pbix` in Power BI Desktop

---

## Known Limitations & Next Iteration

The historical data powering this model runs through May 2023. When validated against 2024 and 2025 actuals, the model's demand figures showed variance — partly because the historical trend was fitted to a period heavily influenced by SpaceX Starlink deployments, which inflated growth rates. Since Starlink is vertically integrated and not a viable customer for any third-party launch provider, including them distorts both the customer scoring and the demand baseline.

In the next iteration, the model will be recalibrated to exclude vertically integrated operators like SpaceX from the scoring and demand pipeline, and the historical baseline will be refitted on the addressable market only. This is expected to produce more conservative and commercially accurate forecasts that better reflect the real opportunity for an independent small launch vehicle operator.
