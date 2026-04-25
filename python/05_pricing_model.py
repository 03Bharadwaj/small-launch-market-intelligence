import pandas as pd
import sqlite3
import numpy as np

DB_PATH = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"

print("Running competitive pricing model...")
conn = sqlite3.connect(DB_PATH)

# ── Load vehicle data ─────────────────────────────────────────────────────────
vehicles = pd.read_sql("SELECT * FROM launch_vehicles", conn)
print(f"  Vehicles loaded: {len(vehicles)}")

# ── Fill missing price_per_kg where we have launch price and payload ──────────
mask = vehicles["price_per_kg_usd"].isna() & vehicles["price_per_launch_usd"].notna() & vehicles["payload_sso_kg"].notna()
vehicles.loc[mask, "price_per_kg_usd"] = (
    vehicles.loc[mask, "price_per_launch_usd"] / vehicles.loc[mask, "payload_sso_kg"]
)

# ── Market rate analysis by orbit ─────────────────────────────────────────────
operational = vehicles[vehicles["status"] == "operational"].copy()

print("\n── Operational vehicles with pricing data ───────────────────────────────")
priced = operational[operational["price_per_kg_usd"].notna()].sort_values("price_per_kg_usd")
print(priced[["vehicle_name", "country", "payload_sso_kg", "price_per_kg_usd",
              "success_rate", "rideshare_capable", "data_confidence"]].to_string(index=False))

# ── Price-to-win model ────────────────────────────────────────────────────────
# For a new entrant in the small launch market, what price range is competitive?
# Logic: new entrant needs to undercut established providers by 10-20%
#        but can charge premium over pure rideshare for dedicated orbit access

dedicated = priced[priced["rideshare_capable"] == 0]
rideshare  = priced[priced["rideshare_capable"] == 1]

if len(dedicated) > 0:
    dedicated_median = dedicated["price_per_kg_usd"].median()
    dedicated_min    = dedicated["price_per_kg_usd"].min()
    dedicated_max    = dedicated["price_per_kg_usd"].max()
else:
    dedicated_median = dedicated_min = dedicated_max = np.nan

if len(rideshare) > 0:
    rideshare_median = rideshare["price_per_kg_usd"].median()
    rideshare_min    = rideshare["price_per_kg_usd"].min()
    rideshare_max    = rideshare["price_per_kg_usd"].max()
else:
    rideshare_median = rideshare_min = rideshare_max = np.nan

print("\n── Market rate summary ──────────────────────────────────────────────────")
print(f"  Dedicated launchers  — median: ${dedicated_median:,.0f}/kg  "
      f"range: ${dedicated_min:,.0f}–${dedicated_max:,.0f}/kg")
print(f"  Rideshare providers  — median: ${rideshare_median:,.0f}/kg  "
      f"range: ${rideshare_min:,.0f}–${rideshare_max:,.0f}/kg")

# ── Price-to-win ranges by mass class ────────────────────────────────────────
# Small satellites have different price sensitivity by mass class
mass_classes = {
    "under_10kg":  {"label": "CubeSat (<10kg)",      "sensitivity": "high",   "discount": 0.15},
    "10_50kg":     {"label": "Small sat (10-50kg)",   "sensitivity": "medium", "discount": 0.12},
    "50_150kg":    {"label": "Mini sat (50-150kg)",   "sensitivity": "medium", "discount": 0.10},
    "150_350kg":   {"label": "Medium sat (150-350kg)","sensitivity": "low",    "discount": 0.08},
    "350_500kg":   {"label": "Large small (350-500kg)","sensitivity": "low",   "discount": 0.05},
}

print("\n── Price-to-win ranges by mass class ────────────────────────────────────")
ptw_records = []
for mc, info in mass_classes.items():
    # Benchmark: use dedicated launcher median as reference
    # New entrant discounts this by sensitivity factor
    if not np.isnan(dedicated_median):
        ptw_low  = dedicated_median * (1 - info["discount"] - 0.05)
        ptw_high = dedicated_median * (1 - info["discount"] + 0.05)
    else:
        ptw_low = ptw_high = np.nan

    print(f"  {info['label']:28s} → ${ptw_low:,.0f}–${ptw_high:,.0f}/kg  "
          f"(sensitivity: {info['sensitivity']})")

    ptw_records.append({
        "mass_class":        mc,
        "label":             info["label"],
        "price_sensitivity": info["sensitivity"],
        "ptw_low_usd_kg":    round(ptw_low, 0) if not np.isnan(ptw_low) else None,
        "ptw_high_usd_kg":   round(ptw_high, 0) if not np.isnan(ptw_high) else None,
        "dedicated_median":  round(dedicated_median, 0) if not np.isnan(dedicated_median) else None,
        "rideshare_median":  round(rideshare_median, 0) if not np.isnan(rideshare_median) else None,
    })

ptw_df = pd.DataFrame(ptw_records)

# ── Positioning matrix export ─────────────────────────────────────────────────
# Full vehicle dataset enriched for Power BI scatter plot
positioning = vehicles.copy()
positioning["reliability_pct"] = (positioning["success_rate"] * 100).round(1)
positioning["is_operational"]  = (positioning["status"] == "operational").astype(int)
positioning["bubble_size"]     = positioning["reliability_pct"].fillna(50)

# ── Export CSVs ───────────────────────────────────────────────────────────────
vehicles.to_csv(
    r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\vehicles_enriched.csv",
    index=False
)
ptw_df.to_csv(
    r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\price_to_win.csv",
    index=False
)
positioning.to_csv(
    r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\positioning_matrix.csv",
    index=False
)

print("\n── Exports ──────────────────────────────────────────────────────────────")
print("  vehicles_enriched.csv")
print("  price_to_win.csv")
print("  positioning_matrix.csv")

conn.close()
print("\nBlock 7 complete.")