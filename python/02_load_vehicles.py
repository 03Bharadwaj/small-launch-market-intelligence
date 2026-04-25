import pandas as pd
import sqlite3
import os
import numpy as np

DB_PATH  = os.path.join(os.path.dirname(__file__), "..", "launch_mis.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "launch_vehicles.csv")

print("Loading launch vehicle data...")
df = pd.read_csv(CSV_PATH)

# Convert NULL strings to actual NaN
df = df.replace("NULL", np.nan)

# Ensure numeric columns are correct type
numeric_cols = [
    "payload_leo_kg", "payload_sso_kg", "price_per_launch_usd",
    "price_per_kg_usd", "fairing_diameter_m", "first_launch_year",
    "total_launches", "successful_launches", "success_rate",
    "rideshare_capable", "lead_time_months"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print(f"  Vehicles loaded: {len(df)}")
print(df[["vehicle_name", "status", "data_confidence"]].to_string(index=False))

conn = sqlite3.connect(DB_PATH)
conn.execute("DELETE FROM launch_vehicles")
conn.execute("DELETE FROM sqlite_sequence WHERE name='launch_vehicles'")

df.to_sql("launch_vehicles", conn, if_exists="append", index=False, method="multi")
conn.commit()

# Verification
print("\n── Verification ────────────────────────────────────────────────────────")
print(pd.read_sql("SELECT COUNT(*) AS total_vehicles FROM launch_vehicles", conn))
print(pd.read_sql("""
    SELECT status, COUNT(*) AS count 
    FROM launch_vehicles GROUP BY status
""", conn))
print(pd.read_sql("""
    SELECT vehicle_name, country, payload_sso_kg, price_per_kg_usd, data_confidence
    FROM launch_vehicles
    WHERE status = 'operational'
    ORDER BY price_per_kg_usd ASC
""", conn))

conn.close()
print("\nBlock 4 complete.")