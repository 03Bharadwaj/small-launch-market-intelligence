import pandas as pd
import sqlite3
import numpy as np

DB_PATH = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"

print("Running customer scoring model...")
conn = sqlite3.connect(DB_PATH)

# ── Pull operator data with satellite detail ──────────────────────────────────
ops = pd.read_sql("""
    SELECT 
        o.operator_id,
        o.operator_name,
        o.country,
        o.sector,
        o.total_satellites,
        o.total_mass_kg,
        COUNT(DISTINCT s.orbit_class) AS orbit_diversity,
        SUM(CASE WHEN s.orbit_class = 'LEO' THEN 1 ELSE 0 END) AS leo_count,
        SUM(CASE WHEN s.orbit_class = 'SSO' THEN 1 ELSE 0 END) AS sso_count,
        SUM(CASE WHEN s.mass_class IN ('under_10kg','10_50kg','50_150kg') THEN 1 ELSE 0 END) AS small_sat_count,
        SUM(CASE WHEN s.mass_class IN ('150_350kg','350_500kg') THEN 1 ELSE 0 END) AS mid_sat_count,
        COUNT(DISTINCT s.launch_vehicle) AS provider_diversity,
        MAX(s.launch_year) AS latest_launch_year
    FROM satellite_operators o
    LEFT JOIN satellites s ON o.operator_id = s.operator_id
    GROUP BY o.operator_id
""", conn)

print(f"  Operators loaded: {len(ops)}")

# ── SCORING MODEL ─────────────────────────────────────────────────────────────
# Each component scores 0-100, then weighted average gives final score

def score_orbit_fit(leo, sso, total):
    """High score if operator uses LEO or SSO — our target orbits"""
    if total == 0: return 0
    return min(100, ((leo + sso) / total) * 100)

def score_mass_fit(small, mid, total):
    """High score if operator uses mass classes a small launcher can serve"""
    if total == 0: return 0
    return min(100, ((small + mid) / total) * 100)

def score_constellation_potential(total):
    """High score for operators with many satellites — repeat business"""
    if total >= 50:  return 100
    if total >= 20:  return 80
    if total >= 10:  return 60
    if total >= 5:   return 40
    if total >= 2:   return 20
    return 5

def score_provider_diversity(diversity):
    """High score if operator has used multiple providers — not locked in"""
    if diversity >= 3: return 100
    if diversity == 2: return 60
    if diversity == 1: return 30
    return 0

def score_recency(latest_year):
    """High score if operator launched recently — still active"""
    if pd.isna(latest_year): return 0
    yr = int(latest_year)
    if yr >= 2022: return 100
    if yr >= 2020: return 70
    if yr >= 2018: return 40
    return 10

def score_sector(sector):
    """Commercial operators are more likely to shop around for launches"""
    mapping = {
        "commercial": 100,
        "academic":    60,
        "government":  40,
        "military":    20,
        "other":       30,
        "unknown":     10,
    }
    return mapping.get(str(sector).lower(), 10)

def score_geography(country):
    """India and Asia-Pacific operators get a regional access bonus"""
    if pd.isna(country): return 20
    c = str(country).lower()
    if any(x in c for x in ["india", "indian"]): return 100
    if any(x in c for x in ["singapore", "japan", "south korea", "indonesia",
                             "malaysia", "thailand", "australia", "new zealand",
                             "bangladesh", "sri lanka"]): return 70
    if any(x in c for x in ["usa", "united states", "uk", "united kingdom",
                             "germany", "france", "canada"]): return 50
    return 30

# Apply all scoring components
ops["s_orbit"]         = ops.apply(lambda r: score_orbit_fit(r.leo_count, r.sso_count, r.total_satellites), axis=1)
ops["s_mass"]          = ops.apply(lambda r: score_mass_fit(r.small_sat_count, r.mid_sat_count, r.total_satellites), axis=1)
ops["s_constellation"] = ops["total_satellites"].apply(score_constellation_potential)
ops["s_diversity"]     = ops["provider_diversity"].apply(score_provider_diversity)
ops["s_recency"]       = ops["latest_launch_year"].apply(score_recency)
ops["s_sector"]        = ops["sector"].apply(score_sector)
ops["s_geography"]     = ops["country"].apply(score_geography)

# Weighted final score
weights = {
    "s_constellation": 0.25,   # repeat business potential — highest weight
    "s_orbit":         0.20,   # orbit fit — critical
    "s_mass":          0.15,   # mass fit — critical
    "s_recency":       0.15,   # still active
    "s_sector":        0.12,   # commercial preferred
    "s_diversity":     0.08,   # not locked in
    "s_geography":     0.05,   # regional bonus
}

ops["prospect_score"] = sum(ops[col] * w for col, w in weights.items())
ops["prospect_score"] = ops["prospect_score"].round(1)

# ── Segment classification ────────────────────────────────────────────────────
def classify_segment(purpose_data):
    return "mixed"  # placeholder — refined below from satellite purposes

purpose_df = pd.read_sql("""
    SELECT operator_id, purpose, COUNT(*) as cnt
    FROM satellites
    WHERE purpose IS NOT NULL
    GROUP BY operator_id, purpose
    ORDER BY operator_id, cnt DESC
""", conn)

def get_primary_segment(op_id):
    sub = purpose_df[purpose_df.operator_id == op_id]
    if sub.empty: return "unknown"
    top = sub.iloc[0]["purpose"].lower()
    if any(x in top for x in ["earth obs", "remote", "imaging", "observation"]): return "earth_observation"
    if any(x in top for x in ["communic", "iot", "m2m", "broadband", "internet"]): return "communications"
    if any(x in top for x in ["technolog", "demo", "test", "experiment"]): return "technology_demo"
    if any(x in top for x in ["navigation", "gps", "gnss"]): return "navigation"
    if any(x in top for x in ["weather", "climate", "meteorolog"]): return "weather"
    return "other"

ops["segment"] = ops["operator_id"].apply(get_primary_segment)

# ── Priority tiers ────────────────────────────────────────────────────────────
ops["tier"] = pd.cut(
    ops["prospect_score"],
    bins=[0, 40, 60, 75, 100],
    labels=["Low", "Medium", "High", "Priority"]
)

# ── Update database ───────────────────────────────────────────────────────────
for _, row in ops.iterrows():
    conn.execute(
        "UPDATE satellite_operators SET prospect_score = ? WHERE operator_id = ?",
        (row["prospect_score"], row["operator_id"])
    )
conn.commit()

# ── Export to CSV for Power BI ────────────────────────────────────────────────
export_cols = [
    "operator_id", "operator_name", "country", "sector", "segment",
    "total_satellites", "total_mass_kg", "prospect_score", "tier",
    "s_orbit", "s_mass", "s_constellation", "s_diversity",
    "s_recency", "s_sector", "s_geography",
    "leo_count", "sso_count", "provider_diversity", "latest_launch_year"
]
ops[export_cols].to_csv(
    r"C:\Users\ASUS\Downloads\SmallLaunchMIS\data\processed\customer_scores.csv",
    index=False
)

# ── Verification ──────────────────────────────────────────────────────────────
print("\n── Score distribution ───────────────────────────────────────────────────")
print(ops["tier"].value_counts().sort_index())

print("\n── Top 20 Priority Prospects ────────────────────────────────────────────")
top20 = ops.nlargest(20, "prospect_score")[
    ["operator_name", "country", "sector", "segment",
     "total_satellites", "prospect_score", "tier"]
]
print(top20.to_string(index=False))

print("\n── Segment breakdown ────────────────────────────────────────────────────")
print(ops.groupby("segment")["operator_name"].count().sort_values(ascending=False))

conn.close()
print("\nBlock 6 complete.")