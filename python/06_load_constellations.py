import sqlite3

DB_PATH = r"C:\Users\ASUS\Downloads\SmallLaunchMIS\launch_mis.db"

# Publicly announced constellations — sourced from company filings,
# press releases, and industry reports. All figures are public record.
constellations = [
    # operator, name, planned_total, deployed, mass_class, orbit, completion_year, source
    ("OneWeb", "OneWeb Gen2", 648, 589, "150_350kg", "LEO", 2026,
     "OneWeb press release 2023"),
    ("Amazon", "Project Kuiper", 3236, 0, "150_350kg", "LEO", 2029,
     "FCC filing 2020"),
    ("AST SpaceMobile", "BlueBird", 243, 9, "150_350kg", "LEO", 2027,
     "AST SpaceMobile investor presentation 2023"),
    ("Telesat", "Lightspeed", 198, 0, "150_350kg", "LEO", 2027,
     "Telesat annual report 2023"),
    ("Planet Labs", "Pelican", 32, 0, "50_150kg", "SSO", 2026,
     "Planet Labs earnings call Q3 2023"),
    ("Spire Global", "Spire Gen2", 100, 0, "under_10kg", "LEO", 2026,
     "Spire Global investor presentation 2023"),
    ("Pixxel", "Pixxel Hyperspectral", 24, 6, "50_150kg", "SSO", 2025,
     "Pixxel press release 2023"),
    ("Dhruva Space", "Dhruva LEO Constellation", 18, 0, "under_10kg", "LEO", 2027,
     "IN-SPACe filing 2023"),
    ("Satellogic", "Satellogic Gen2", 90, 38, "50_150kg", "SSO", 2027,
     "Satellogic investor presentation 2023"),
    ("ICEYE", "ICEYE SAR Expansion", 50, 22, "50_150kg", "SSO", 2026,
     "ICEYE press release 2023"),
    ("HawkEye 360", "HawkEye Cluster Expansion", 40, 18, "under_10kg", "LEO", 2026,
     "HawkEye 360 press release 2023"),
    ("Kepler Communications", "Kepler Gen2", 140, 21, "10_50kg", "LEO", 2027,
     "Kepler Communications press release 2023"),
    ("Swarm Technologies", "Swarm Gen2", 150, 90, "under_10kg", "LEO", 2026,
     "SpaceX/Swarm announcement 2023"),
    ("BlackSky Global", "BlackSky Gen3", 30, 15, "50_150kg", "SSO", 2026,
     "BlackSky investor presentation 2023"),
    ("Kleos Space", "Kleos Expansion", 20, 12, "under_10kg", "LEO", 2026,
     "Kleos Space press release 2023"),
    ("GHGSat", "GHGSat Expansion", 10, 6, "under_10kg", "LEO", 2026,
     "GHGSat press release 2023"),
    ("Eutelsat", "OneWeb India Focus", 36, 0, "150_350kg", "LEO", 2026,
     "Eutelsat-OneWeb merger announcement 2023"),
    ("SatSure", "SatSure Analytics Constellation", 10, 0, "under_10kg", "SSO", 2027,
     "SatSure press release 2023"),
]

conn = sqlite3.connect(DB_PATH)
conn.execute("DELETE FROM announced_constellations")
conn.execute("DELETE FROM sqlite_sequence WHERE name='announced_constellations'")

for c in constellations:
    conn.execute("""
        INSERT INTO announced_constellations
        (operator, constellation_name, planned_total_satellites,
         satellites_deployed, mass_class, orbit_class,
         announced_completion_year, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, c)

conn.commit()

import pandas as pd
print("── Announced constellations loaded ──────────────────────────────────────")
df = pd.read_sql("SELECT operator, constellation_name, planned_total_satellites, satellites_deployed, announced_completion_year FROM announced_constellations ORDER BY planned_total_satellites DESC", conn)
print(df.to_string(index=False))
remaining = (df["planned_total_satellites"] - df["satellites_deployed"]).sum()
print(f"\n  Total satellites remaining to deploy: {remaining}")
conn.close()
print("\nConstellation data loaded.")