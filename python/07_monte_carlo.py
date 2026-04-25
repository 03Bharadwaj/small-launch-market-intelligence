import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import os

DB_PATH    = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"
OUTPUT_DIR = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed"
CHART_DIR  = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\charts"
os.makedirs(CHART_DIR, exist_ok=True)

np.random.seed(42)
N_SIMS = 10000
YEARS  = list(range(2024, 2031))

conn = sqlite3.connect(DB_PATH)

# ── Historical data ───────────────────────────────────────────────────────────
hist = pd.read_sql("""
    SELECT year, SUM(launch_count) AS total
    FROM annual_launch_history
    WHERE year BETWEEN 2014 AND 2022
    GROUP BY year ORDER BY year
""", conn)

x = hist["year"].values
y = hist["total"].values
coeffs = np.polyfit(x, y, 1)
slope, intercept = coeffs
print(f"Historical trend: {slope:.1f} satellites/year growth")

# ── Constellation pipeline ────────────────────────────────────────────────────
cons = pd.read_sql("""
    SELECT planned_total_satellites, satellites_deployed,
           announced_completion_year, orbit_class, mass_class
    FROM announced_constellations
""", conn)
cons["remaining"]    = cons["planned_total_satellites"] - cons["satellites_deployed"]
cons["deploy_window"] = (cons["announced_completion_year"] - 2023).clip(lower=1)
cons["annual_rate"]   = cons["remaining"] / cons["deploy_window"]

total_pipeline = cons["remaining"].sum()
print(f"Total pipeline satellites remaining: {total_pipeline:,}")
print(f"Average annual pipeline rate (no slippage): {cons['annual_rate'].sum():.0f}/year")

# ── MONTE CARLO ───────────────────────────────────────────────────────────────
print(f"\nRunning {N_SIMS:,} simulations...")
annual_results = {yr: [] for yr in YEARS}

for sim in range(N_SIMS):
    # Draw parameters once per simulation
    trend_mult    = np.random.normal(1.0, 0.15)       # trend uncertainty ±15%
    market_growth = np.random.uniform(0.03, 0.12)     # 3-12% organic growth pa
    slippage_yrs  = np.random.uniform(0.5, 2.5)       # deployment delays
    new_op_sats   = np.random.randint(20, 80)         # new operator satellites per year

    for yr in YEARS:
        # Baseline: trend extrapolation with growth adjustment
        base_trend = max(200, np.polyval(coeffs, yr) * trend_mult)
        baseline   = base_trend * (1 + market_growth) ** (yr - 2022)

        # Pipeline: each constellation contributes proportionally each year
        pipeline = 0.0
        for _, row in cons.iterrows():
            if row["remaining"] <= 0:
                continue
            # Effective completion year after slippage
            eff_completion = row["announced_completion_year"] + slippage_yrs
            # Only contribute if deployment is still ongoing
            if yr > eff_completion:
                continue
            # Contribution: annual rate with small ±10% jitter
            rate   = row["annual_rate"]
            jitter = rate * np.random.uniform(-0.10, 0.10)
            pipeline += max(0.0, rate + jitter)

        total = baseline + pipeline + new_op_sats
        annual_results[yr].append(total)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n── Demand Forecast (small satellites, LEO/SSO, <500kg) ──────────────────")
print(f"{'Year':<6} {'P10':>8} {'P50':>8} {'P90':>8}")
print("-" * 36)

forecast_records = []
p10_vals, p50_vals, p90_vals = [], [], []

for yr in YEARS:
    sims = np.array(annual_results[yr])
    p10  = int(np.percentile(sims, 10))
    p50  = int(np.percentile(sims, 50))
    p90  = int(np.percentile(sims, 90))
    p10_vals.append(p10)
    p50_vals.append(p50)
    p90_vals.append(p90)
    print(f"{yr:<6} {p10:>8,} {p50:>8,} {p90:>8,}")
    forecast_records.append({
        "year": yr, "p10": p10, "p50": p50, "p90": p90,
        "mean": int(np.mean(sims)), "std": int(np.std(sims))
    })

forecast_df = pd.DataFrame(forecast_records)

# ── India / Asia-Pacific share ────────────────────────────────────────────────
apac_count = pd.read_sql("""
    SELECT COUNT(*) as cnt FROM satellite_operators
    WHERE LOWER(country) LIKE '%india%'
       OR LOWER(country) LIKE '%singapore%'
       OR LOWER(country) LIKE '%japan%'
       OR LOWER(country) LIKE '%south korea%'
       OR LOWER(country) LIKE '%australia%'
""", conn)["cnt"].values[0]

apac_share = apac_count / 447
print(f"\n── India/APAC addressable share: {apac_count} operators ({apac_share:.1%}) ──")
for rec in forecast_records:
    print(f"  {rec['year']}: ~{int(rec['p50'] * apac_share):,} satellites (P50)")

# ── Chart 1: Forecast with uncertainty band ───────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(hist["year"], hist["total"], color="#2C3E50", lw=2.5,
        marker="o", ms=5, label="Historical (UCS data)", zorder=5)
ax.fill_between(YEARS, p10_vals, p90_vals, alpha=0.20,
                color="#2980B9", label="P10–P90 range")
ax.plot(YEARS, p50_vals, color="#2980B9", lw=2.5, ls="--",
        marker="s", ms=5, label="P50 base case", zorder=5)
ax.plot(YEARS, p10_vals, color="#E74C3C", lw=1.2, ls=":", label="P10 pessimistic")
ax.plot(YEARS, p90_vals, color="#27AE60", lw=1.2, ls=":", label="P90 optimistic")
ax.axvline(x=2023.5, color="grey", ls="--", lw=1, alpha=0.6)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Small Satellites Launched (<500kg, LEO/SSO)", fontsize=11)
ax.set_title(f"Global Small Satellite Demand Forecast 2024–2030\n"
             f"Monte Carlo | n={N_SIMS:,} simulations", fontsize=13)
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
ax.set_xticks(list(hist["year"]) + YEARS)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "demand_forecast.png"), dpi=150, bbox_inches="tight")
plt.close()

# ── Chart 2: Pipeline by mass class ──────────────────────────────────────────
mass_pip = cons.groupby("mass_class")["remaining"].sum().sort_values()
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(mass_pip.index, mass_pip.values,
               color=["#3498DB","#2ECC71","#E74C3C","#F39C12","#9B59B6"],
               edgecolor="white")
ax.bar_label(bars, fmt="%,.0f", padding=4, fontsize=10)
ax.set_xlabel("Satellites Remaining to Deploy", fontsize=11)
ax.set_title("Constellation Pipeline by Mass Class", fontsize=12)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "pipeline_mass_class.png"), dpi=150, bbox_inches="tight")
plt.close()

# ── Chart 3: Historical growth ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(hist["year"], hist["total"], color="#2C3E50", alpha=0.8, edgecolor="white")
ax.plot(hist["year"], [int(np.polyval(coeffs, yr)) for yr in hist["year"]],
        color="#E74C3C", lw=2, ls="--", label="Linear trend")
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Small Satellites Launched", fontsize=11)
ax.set_title("Historical Small Satellite Launch Volume 2014–2022", fontsize=12)
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "historical_growth.png"), dpi=150, bbox_inches="tight")
plt.close()

# ── Export ────────────────────────────────────────────────────────────────────
forecast_df.to_csv(os.path.join(OUTPUT_DIR, "demand_forecast.csv"), index=False)
print("\n  Charts and CSV saved.")
conn.close()
print("\nBlock 8 complete.")