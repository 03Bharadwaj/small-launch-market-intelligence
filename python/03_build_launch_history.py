import pandas as pd
import sqlite3

DB_PATH = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"

print("Building annual launch history from satellites table...")
conn = sqlite3.connect(DB_PATH)

# Verify tables and columns
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("  Tables found:", [t[0] for t in tables])

cols = conn.execute("PRAGMA table_info(annual_launch_history)").fetchall()
print("  annual_launch_history columns:", [c[1] for c in cols])

# Pull all satellites with valid launch year and mass class
df = pd.read_sql("""
    SELECT launch_year, mass_class, orbit_class, COUNT(*) as launch_count
    FROM satellites
    WHERE launch_year IS NOT NULL
      AND launch_year BETWEEN 2014 AND 2023
      AND mass_class != 'unknown'
      AND orbit_class != 'Other'
    GROUP BY launch_year, mass_class, orbit_class
    ORDER BY launch_year, mass_class, orbit_class
""", conn)

print(f"  Records to insert: {len(df)}")
print(df.head())

# Clear and reload
conn.execute("DELETE FROM annual_launch_history")
conn.execute("DELETE FROM sqlite_sequence WHERE name='annual_launch_history'")

# Insert row by row to avoid column mismatch
for _, row in df.iterrows():
    conn.execute(
        "INSERT INTO annual_launch_history (year, mass_class, orbit_class, launch_count) VALUES (?, ?, ?, ?)",
        (int(row["launch_year"]), row["mass_class"], row["orbit_class"], int(row["launch_count"]))
    )
conn.commit()

# Verification
print("\n── Annual totals by year ────────────────────────────────────────────────")
print(pd.read_sql("""
    SELECT year, SUM(launch_count) AS total_satellites
    FROM annual_launch_history
    GROUP BY year ORDER BY year
""", conn))

print("\n── Mass class totals (2014-2023) ────────────────────────────────────────")
print(pd.read_sql("""
    SELECT mass_class, SUM(launch_count) AS total
    FROM annual_launch_history
    GROUP BY mass_class ORDER BY total DESC
""", conn))

print("\n── Orbit class totals (2014-2023) ───────────────────────────────────────")
print(pd.read_sql("""
    SELECT orbit_class, SUM(launch_count) AS total
    FROM annual_launch_history
    GROUP BY orbit_class ORDER BY total DESC
""", conn))

print("\n── Growth check: LEO under_10kg by year ─────────────────────────────────")
print(pd.read_sql("""
    SELECT year, launch_count
    FROM annual_launch_history
    WHERE mass_class = 'under_10kg' AND orbit_class = 'LEO'
    ORDER BY year
""", conn))

conn.close()
print("\nBlock 5 complete.")