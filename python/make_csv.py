import os

data = """vehicle_name,company,country,status,payload_leo_kg,payload_sso_kg,price_per_launch_usd,price_per_kg_usd,fairing_diameter_m,first_launch_year,total_launches,successful_launches,success_rate,rideshare_capable,lead_time_months,data_confidence
Rocket Lab Electron,Rocket Lab,New Zealand / USA,operational,300,200,7500000,25000,1.2,2017,52,49,0.94,1,6,confirmed
SpaceX Falcon 9 Rideshare,SpaceX,USA,operational,200,200,6000,6000,1.0,2021,10,10,1.00,1,12,confirmed
ISRO PSLV,ISRO,India,operational,3800,1750,25000000,6579,3.2,1993,57,55,0.96,1,18,confirmed
ISRO SSLV,ISRO,India,operational,500,300,30000000,60000,0.75,2022,3,2,0.67,1,12,estimated
Arianespace Vega-C Rideshare,Arianespace,Europe,operational,700,700,8000,11429,2.6,2022,2,1,0.50,1,18,confirmed
Rocket Lab Neutron,Rocket Lab,USA,in_development,13000,1500,,,, 2026,0,0,,1,,confirmed
Relativity Space Terran R,Relativity Space,USA,in_development,20000,,,,,2026,0,0,,0,,confirmed
Firefly Alpha,Firefly Aerospace,USA,operational,1030,630,15000000,14563,1.8,2022,4,2,0.50,0,12,confirmed
ABL Space RS1,ABL Space Systems,USA,in_development,1350,,12000000,8889,1.5,2023,1,0,0.00,0,12,reported
Exolaunch Rideshare,Exolaunch,Germany,operational,,200,,8500,,2020,30,30,1.00,1,12,reported
Mitsubishi H-IIA,Mitsubishi,Japan,operational,10000,4000,90000000,9000,4.0,2001,47,46,0.98,1,24,confirmed
JAXA Epsilon,JAXA,Japan,operational,590,450,55000000,93220,1.2,2013,6,5,0.83,0,24,confirmed
Kuaizhou-1A,CASIC,China,operational,300,200,30000000,100000,1.0,2017,20,19,0.95,1,6,reported
Long March 2D Rideshare,CASC,China,operational,1200,1000,30000000,25000,2.9,1992,60,59,0.98,1,18,reported
Launcher One,Virgin Orbit,USA,retired,500,,12000000,24000,,2021,5,4,0.80,0,,confirmed
Astra Rocket 3,Astra,USA,retired,50,,,,,2020,7,2,0.29,0,,confirmed
Agnikul Agnibaan,Agnikul Cosmos,India,in_development,100,50,,,0.7,2024,1,0,0.00,0,,reported
PLD Space Miura 5,PLD Space,Spain,in_development,300,200,,,1.0,2025,0,0,,0,,reported
Isar Aerospace Spectrum,Isar Aerospace,Germany,in_development,1000,700,,,1.5,2025,0,0,,0,,reported
"""

out_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "launch_vehicles.csv")
os.makedirs(os.path.dirname(out_path), exist_ok=True)

with open(out_path, "w", newline="", encoding="utf-8") as f:
    f.write(data.strip())

print("CSV written successfully")
print("Path:", os.path.abspath(out_path))