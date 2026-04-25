-- Commercial Small Launch Market Intelligence System
-- Database Schema

CREATE TABLE IF NOT EXISTS satellite_operators (
    operator_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator_name TEXT NOT NULL,
    country TEXT,
    sector TEXT,          -- 'commercial', 'government', 'academic', 'military'
    total_satellites INTEGER DEFAULT 0,
    total_mass_kg REAL DEFAULT 0,
    funding_stage TEXT,   -- populated later for commercial operators
    prospect_score REAL DEFAULT 0  -- populated by scoring model
);

CREATE TABLE IF NOT EXISTS satellites (
    satellite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    satellite_name TEXT,
    operator_id INTEGER REFERENCES satellite_operators(operator_id),
    launch_year INTEGER,
    orbit_class TEXT,     -- 'LEO', 'SSO', 'MEO', 'GEO', 'Other'
    orbit_type TEXT,
    mass_class TEXT,      -- 'under_10kg', '10_50kg', '50_150kg', '150_350kg', '350_500kg'
    mass_kg REAL,
    purpose TEXT,
    launch_provider TEXT,
    launch_vehicle TEXT,
    country_of_operator TEXT
);

CREATE TABLE IF NOT EXISTS launch_vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_name TEXT NOT NULL,
    company TEXT,
    country TEXT,
    status TEXT,          -- 'operational', 'in_development', 'retired'
    payload_leo_kg REAL,
    payload_sso_kg REAL,
    price_per_launch_usd REAL,
    price_per_kg_usd REAL,
    fairing_diameter_m REAL,
    first_launch_year INTEGER,
    total_launches INTEGER,
    successful_launches INTEGER,
    success_rate REAL,
    rideshare_capable INTEGER DEFAULT 0,  -- 0=no, 1=yes
    lead_time_months INTEGER,
    data_confidence TEXT  -- 'confirmed', 'estimated', 'reported'
);

CREATE TABLE IF NOT EXISTS annual_launch_history (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    mass_class TEXT,
    orbit_class TEXT,
    launch_count INTEGER
);

CREATE TABLE IF NOT EXISTS announced_constellations (
    constellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operator TEXT,
    constellation_name TEXT,
    planned_total_satellites INTEGER,
    satellites_deployed INTEGER DEFAULT 0,
    mass_class TEXT,
    orbit_class TEXT,
    announced_completion_year INTEGER,
    source TEXT
);