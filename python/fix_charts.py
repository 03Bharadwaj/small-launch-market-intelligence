import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import os

CHART_DIR  = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\charts"
DB_PATH    = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"

conn = sqlite3.connect(DB_PATH)

# ── Fix Chart 1: Pipeline by mass class ──────────────────────────────────────
cons = pd.read_sql("SELECT mass_class, planned_total_satellites, satellites_deployed FROM announced_constellations", conn)
cons["remaining"] = cons["planned_total_satellites"] - cons["satellites_deployed"]
mass_pip = cons.groupby("mass_class")["remaining"].sum().sort_values()

fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#3498DB", "#2ECC71", "#E74C3C", "#F39C12", "#9B59B6"]
bars = ax.barh(mass_pip.index, mass_pip.values,
               color=colors[:len(mass_pip)], edgecolor="white")

# Fix: manually add labels instead of using bar_label fmt
for bar, val in zip(bars, mass_pip.values):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
            f"{int(val):,}", va="center", ha="left", fontsize=10)

ax.set_xlabel("Satellites Remaining to Deploy", fontsize=11)
ax.set_title("Constellation Pipeline by Mass Class\n(Announced, not yet deployed)", fontsize=12)
ax.grid(axis="x", alpha=0.3)
ax.set_xlim(0, mass_pip.max() * 1.12)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "pipeline_mass_class.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Fixed: pipeline_mass_class.png")

# ── Fix Chart 3: Historical growth with y-floor at 0 ─────────────────────────
hist = pd.read_sql("""
    SELECT year, SUM(launch_count) AS total
    FROM annual_launch_history
    WHERE year BETWEEN 2014 AND 2022
    GROUP BY year ORDER BY year
""", conn)

x = hist["year"].values
y = hist["total"].values
coeffs = np.polyfit(x, y, 1)

# Clip trend line at zero
trend_y = [max(0, int(np.polyval(coeffs, yr))) for yr in x]

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(hist["year"], hist["total"], color="#2C3E50", alpha=0.8, edgecolor="white")
ax.plot(hist["year"], trend_y, color="#E74C3C", lw=2, ls="--", label="Linear trend")
ax.set_ylim(bottom=0)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Small Satellites Launched", fontsize=11)
ax.set_title("Historical Small Satellite Launch Volume 2014–2022\n(LEO/SSO, <500kg)", fontsize=12)
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "historical_growth.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Fixed: historical_growth.png")

conn.close()
print("\nChart fixes complete.")