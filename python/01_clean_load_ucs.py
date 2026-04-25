import pandas as pd
import sqlite3
import numpy as np
import os

# ── PATHS ────────────────────────────────────────────────────────────────────
UCS_FILE = os.path.expanduser("~/Downloads/UCS-Satellite-Database 5-1-2023.xlsx")
DB_PATH  = os.path.join(os.path.dirname(__file__), "..", "launch_mis.db")

# ── LOAD RAW DATA ─────────────────────────────────────────────────────────────
print("Loading UCS Excel file...")
df = pd.read_excel(UCS_FILE, header=0)
print(f"  Raw rows loaded: {len(df)}")

# ── STANDARDISE COLUMN NAMES ─────────────────────────────────────────────────
df.columns = [str(c).strip() for c in df.columns]

COL_MAP = {
    "Name of Satellite, Alternate Names": "satellite_name",
    "Current Official Name of Satellite": "official_name",
    "Country of Operator/Owner":          "country_of_operator",
    "Operator/Owner":                     "operator_name",
    "Users":                              "users",
    "Purpose":                            "purpose",
    "Class of Orbit":                     "orbit_class_raw",
    "Type of Orbit":                      "orbit_type",
    "Launch Mass (kg.)":                  "mass_kg",
    "Date of Launch":                     "launch_date",
    "Launch Vehicle":                     "launch_vehicle",
    "Launch Site":                        "launch_site",
    "Perigee (km)":                       "perigee_km",
    "Apogee (km)":                        "apogee_km",
    "Inclination (degrees)":              "inclination_deg",
}

df = df.rename(columns={k: v for k, v in COL_MAP.items() if k in df.columns})
print(f"  Columns mapped. Working columns: {list(df.columns)}")

# ── EXTRACT LAUNCH YEAR ───────────────────────────────────────────────────────
df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
df["launch_year"] = df["launch_date"].dt.year

# ── CLEAN MASS ────────────────────────────────────────────────────────────────
df["mass_kg"] = pd.to_numeric(df["mass_kg"], errors="coerce")

# ── FILTER TO ADDRESSABLE MARKET: <= 500 kg ───────────────────────────────────
df_small = df[df["mass_kg"].between(0.1, 500, inclusive="both")].copy()
print(f"  Satellites <= 500 kg: {len(df_small)}")

# ── MASS CLASS CLASSIFICATION ─────────────────────────────────────────────────
def classify_mass(mass):
    if pd.isna(mass):       return "unknown"
    if mass < 10:           return "under_10kg"
    if mass < 50:           return "10_50kg"
    if mass < 150:          return "50_150kg"
    if mass < 350:          return "150_350kg"
    return                         "350_500kg"

df_small["mass_class"] = df_small["mass_kg"].apply(classify_mass)

# ── ORBIT CLASS NORMALISATION ─────────────────────────────────────────────────
def normalise_orbit(raw):
    if pd.isna(raw): return "Other"
    r = str(raw).strip().upper()
    if "GEO" in r:  return "GEO"
    if "SSO" in r:  return "SSO"
    if "LEO" in r:  return "LEO"
    if "MEO" in r:  return "MEO"
    if "HEO" in r:  return "HEO"
    return "Other"

df_small["orbit_class"] = df_small["orbit_class_raw"].apply(normalise_orbit)

# ── OPERATOR NAME NORMALISATION ───────────────────────────────────────────────
def clean_operator(name):
    if pd.isna(name): return "Unknown"
    s = str(name).strip()
    s = s.replace("  ", " ")
    # Common abbreviation fixes
    replacements = {
        "Spire Global, Inc.": "Spire Global",
        "Spire Global Inc":   "Spire Global",
        "Planet Labs, Inc.":  "Planet Labs",
        "Planet Labs PBC":    "Planet Labs",
        "SpaceX":             "SpaceX",
        "Iridium Communications": "Iridium",
        "Iridium Communications Inc": "Iridium",
    }
    return replacements.get(s, s)

df_small["operator_name"] = df_small["operator_name"].apply(clean_operator)

# ── SECTOR CLASSIFICATION ─────────────────────────────────────────────────────
def classify_sector(users, operator):
    if pd.isna(users): return "unknown"
    u = str(users).strip().lower()
    if any(w in u for w in ["military", "defence", "defense"]):
        return "military"
    if any(w in u for w in ["government", "civil"]):
        return "government"
    if any(w in u for w in ["commercial"]):
        return "commercial"
    if any(w in u for w in ["academic", "university", "research"]):
        return "academic"
    return "other"

df_small["sector"] = df_small.apply(
    lambda r: classify_sector(r.get("users", ""), r.get("operator_name", "")), axis=1
)

# ── BUILD OPERATORS TABLE ─────────────────────────────────────────────────────
print("Building operator summary...")
ops = (
    df_small.groupby("operator_name")
    .agg(
        country        = ("country_of_operator", lambda x: x.mode()[0] if not x.mode().empty else "Unknown"),
        sector         = ("sector",              lambda x: x.mode()[0] if not x.mode().empty else "unknown"),
        total_satellites = ("satellite_name",   "count"),
        total_mass_kg  = ("mass_kg",            "sum"),
    )
    .reset_index()
)
ops["funding_stage"]  = None   # populated later
ops["prospect_score"] = 0.0
print(f"  Unique operators: {len(ops)}")

# ── WRITE TO DATABASE ─────────────────────────────────────────────────────────
print("Writing to database...")
conn = sqlite3.connect(DB_PATH)

# Clear existing data (safe to re-run)
conn.execute("DELETE FROM satellites")
conn.execute("DELETE FROM satellite_operators")
conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('satellites','satellite_operators')")

# Insert operators and capture IDs
ops.to_sql("satellite_operators", conn, if_exists="append", index=False,
           method="multi",
           dtype={
               "operator_name":    "TEXT",
               "country":          "TEXT",
               "sector":           "TEXT",
               "total_satellites": "INTEGER",
               "total_mass_kg":    "REAL",
               "funding_stage":    "TEXT",
               "prospect_score":   "REAL",
           })

# Build operator_name → operator_id lookup
op_id_map = pd.read_sql("SELECT operator_id, operator_name FROM satellite_operators", conn)
op_id_map = dict(zip(op_id_map.operator_name, op_id_map.operator_id))

# Attach operator_id to satellites
df_small["operator_id"] = df_small["operator_name"].map(op_id_map)

# Select satellite columns for insert
sat_cols = {
    "satellite_name":     "satellite_name",
    "operator_id":        "operator_id",
    "launch_year":        "launch_year",
    "orbit_class":        "orbit_class",
    "orbit_type":         "orbit_type",
    "mass_class":         "mass_class",
    "mass_kg":            "mass_kg",
    "purpose":            "purpose",
    "launch_vehicle":     "launch_vehicle",
    "country_of_operator":"country_of_operator",
}

# Keep only columns that exist in df_small
insert_cols = {v: v for k, v in sat_cols.items() if v in df_small.columns or k in df_small.columns}
df_sat = df_small.rename(columns=sat_cols)[[c for c in sat_cols.values() if c in df_small.rename(columns=sat_cols).columns]].copy()

df_sat.to_sql("satellites", conn, if_exists="append", index=False, method="multi")

conn.commit()

# ── VERIFICATION ──────────────────────────────────────────────────────────────
print("\n── Verification ────────────────────────────────────────────────────────")
print(pd.read_sql("SELECT COUNT(*) AS total_operators FROM satellite_operators", conn))
print(pd.read_sql("SELECT COUNT(*) AS total_satellites FROM satellites", conn))
print(pd.read_sql("""
    SELECT mass_class, COUNT(*) AS count
    FROM satellites GROUP BY mass_class ORDER BY count DESC
""", conn))
print(pd.read_sql("""
    SELECT orbit_class, COUNT(*) AS count
    FROM satellites GROUP BY orbit_class ORDER BY count DESC
""", conn))
print(pd.read_sql("""
    SELECT sector, COUNT(*) AS count
    FROM satellite_operators GROUP BY sector ORDER BY count DESC
""", conn))

conn.close()
print("\nBlock 3 complete. Database loaded.")