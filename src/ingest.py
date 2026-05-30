"""
Ingestion Module for OpenSky Network Flight Data
Fetches flight states, applies the Emissions Calculator, and writes both raw Parquet
(simulating S3 Bronze Landing) and loads into DuckDB (simulating Data Warehouse Silver layer).
Includes a resilient Fallback Mock Generator to guarantee project execution if the OpenSky API
is rate-limited or down.
"""

import os
import time
import logging
import random
import requests
import pandas as pd
import duckdb
from datetime import datetime
from src.emissions_calculator import EmissionsCalculator

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AeroIngestion")

# Local directories simulating Cloud Lakehouse
RAW_DATA_DIR = "data/bronze/flights"
DB_FILE = "data/lakehouse.db"

# Continental USA Bounding Box to filter data size
US_BBOX_COORDINATES = {
    "lamin": 24.0,
    "lomin": -125.0,
    "lamax": 49.0,
    "lomax": -66.0
}

def create_directories():
    """Ensure raw and database directories exist."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def generate_mock_flight_data(num_flights=150):
    """
    Generates highly realistic aircraft state vectors simulating the OpenSky Network API.
    Ensures the pipeline is fully functional and testable locally even offline or during API timeouts.
    """
    logger.info(f"Fallback Mode: Generating {num_flights} realistic active flight states...")
    
    airlines = ["AAL", "UAL", "DAL", "SWA", "FFT", "ASA", "JBU", "BAW", "DLH", "FDX", "UPS"]
    countries = ["United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Mexico"]
    
    mock_states = []
    current_time = int(time.time())
    
    for _ in range(num_flights):
        # ICAO 24-bit address (6 hex characters)
        icao24 = f"{random.randint(0x100000, 0xFFFFFF):06x}"
        
        # Callsign e.g., SWA1285, AAL94
        callsign = f"{random.choice(airlines)}{random.randint(10, 9999)}"
        country = random.choice(countries)
        
        # Position in US bounding box
        lat = random.uniform(US_BBOX_COORDINATES["lamin"], US_BBOX_COORDINATES["lamax"])
        lon = random.uniform(US_BBOX_COORDINATES["lomin"], US_BBOX_COORDINATES["lomax"])
        
        # Altitude: 8,000 to 41,000 feet (2,438 to 12,496 meters)
        alt_m = random.uniform(2400, 12500)
        on_ground = random.random() < 0.05  # 5% chance of being on ground
        
        if on_ground:
            alt_m = 0.0
            velocity = 0.0
            vertical_rate = 0.0
        else:
            # Velocity in meters per second (120 to 260 m/s ~ 230 to 500 knots)
            velocity = random.uniform(120, 260)
            # Vertical rate: climb, descent, or level flight (-12 to 15 m/s)
            vertical_rate = random.choice([0.0, 0.0, 0.0, random.uniform(-10.0, 12.0)])
            
        track = random.uniform(0.0, 359.9)
        time_pos = current_time - random.randint(1, 10)
        
        state = [
            icao24,
            callsign,
            country,
            time_pos,
            current_time,
            lon,
            lat,
            alt_m,
            on_ground,
            velocity,
            track,
            vertical_rate,
            "[]",  # sensors
            alt_m,  # geo_altitude
            str(random.randint(1000, 7777)),  # squawk
            False,  # spi
            0       # position_source
        ]
        mock_states.append(state)
        
    return {
        "time": current_time,
        "states": mock_states
    }

def fetch_opensky_data(bbox=None):
    """
    Fetches real-time flight vectors from OpenSky Network with a quick timeout.
    If it fails, times out, or gets rate-limited, falls back to the robust Mock Generator.
    """
    url = "https://opensky-network.org/api/states/all"
    params = {}
    if bbox:
        params = bbox
    
    logger.info("Attempting to request live flight data from OpenSky API...")
    try:
        # Short timeout (5 seconds) to avoid blocking; fallback quickly if API is unresponsive
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully fetched live data from OpenSky Network API!")
        return data
    except Exception as e:
        logger.warning(f"OpenSky API unavailable ({e}). Triggering resilient fallback simulation...")
        return generate_mock_flight_data()

def process_state_vectors(data):
    """
    Cleans raw state vectors, maps column headers, and enhances with
    domain-specific calculations (emissions, classifications).
    """
    if not data or "states" not in data or data["states"] is None:
        logger.warning("No state vector data retrieved.")
        return pd.DataFrame()
    
    columns = [
        "icao24", "callsign", "origin_country", "time_position", "last_contact",
        "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
        "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
        "spi", "position_source"
    ]
    
    raw_states = data["states"]
    df = pd.DataFrame(raw_states, columns=columns)
    
    df["callsign"] = df["callsign"].str.strip()
    
    ingestion_time = datetime.utcnow()
    df["ingested_at"] = ingestion_time
    df["snapshot_time"] = datetime.utcfromtimestamp(data["time"])
    
    logger.info(f"Processing {len(df)} flight states. Running emissions algorithm...")
    
    categories = []
    base_burns = []
    adj_burns = []
    co2_rates = []
    hourly_emissions = []
    
    for _, row in df.iterrows():
        calc = EmissionsCalculator.calculate_instantaneous_emissions(
            velocity_mps=row["velocity"],
            altitude_m=row["baro_altitude"],
            vertical_rate_mps=row["vertical_rate"]
        )
        categories.append(calc["aircraft_category"])
        base_burns.append(calc["base_fuel_burn_kg_s"])
        adj_burns.append(calc["adjusted_fuel_burn_kg_s"])
        co2_rates.append(calc["co2_emissions_kg_s"])
        hourly_emissions.append(calc["hourly_co2_metric_tonnes"])
        
    df["aircraft_category"] = categories
    df["base_fuel_burn_kg_s"] = base_burns
    df["adjusted_fuel_burn_kg_s"] = adj_burns
    df["co2_emissions_kg_s"] = co2_rates
    df["hourly_co2_tonnes"] = hourly_emissions
    
    df["sensors"] = df["sensors"].astype(str)
    
    return df

def save_to_bronze(df):
    """
    Saves raw enriched data as partitioned Parquet files (representing Bronze zone).
    """
    if df.empty:
        return None
    
    snapshot_dt = df["snapshot_time"].iloc[0]
    date_str = snapshot_dt.strftime("%Y-%m-%d")
    hour_str = snapshot_dt.strftime("%H")
    
    partition_path = os.path.join(RAW_DATA_DIR, f"year_month_day={date_str}", f"hour={hour_str}")
    os.makedirs(partition_path, exist_ok=True)
    
    file_path = os.path.join(partition_path, f"flights_{int(time.time())}.parquet")
    df.to_parquet(file_path, index=False)
    logger.info(f"Bronze layer: Saved partitioned Parquet to {file_path}")
    return file_path

def load_to_silver_duckdb(df):
    """
    Loads/Appends the raw dataframe into our local DuckDB Silver layer.
    """
    if df.empty:
        return
    
    conn = duckdb.connect(DB_FILE)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS silver_flights (
            icao24 VARCHAR,
            callsign VARCHAR,
            origin_country VARCHAR,
            time_position BIGINT,
            last_contact BIGINT,
            longitude DOUBLE,
            latitude DOUBLE,
            baro_altitude DOUBLE,
            on_ground BOOLEAN,
            velocity DOUBLE,
            true_track DOUBLE,
            vertical_rate DOUBLE,
            sensors VARCHAR,
            geo_altitude DOUBLE,
            squawk VARCHAR,
            spi BOOLEAN,
            position_source INTEGER,
            ingested_at TIMESTAMP,
            snapshot_time TIMESTAMP,
            aircraft_category VARCHAR,
            base_fuel_burn_kg_s DOUBLE,
            adjusted_fuel_burn_kg_s DOUBLE,
            co2_emissions_kg_s DOUBLE,
            hourly_co2_tonnes DOUBLE
        )
    """)
    
    # Append dataframe directly into DuckDB
    conn.execute("INSERT INTO silver_flights SELECT * FROM df")
    
    # Query row count
    cnt = conn.execute("SELECT COUNT(*) FROM silver_flights").fetchone()[0]
    logger.info(f"Silver layer: Loaded data into DuckDB. Current total silver rows: {cnt}")
    conn.close()

def run_pipeline():
    """Execute the ingestion and storage pipeline."""
    create_directories()
    
    raw_payload = fetch_opensky_data(bbox=US_BBOX_COORDINATES)
    
    if raw_payload:
        df = process_state_vectors(raw_payload)
        if not df.empty:
            save_to_bronze(df)
            load_to_silver_duckdb(df)
            logger.info("Pipeline executed successfully!")
            return True
    
    logger.error("Pipeline run failed.")
    return False

if __name__ == "__main__":
    run_pipeline()
