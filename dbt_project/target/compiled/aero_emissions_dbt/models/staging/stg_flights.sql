WITH raw_data AS (
    SELECT * FROM main.silver_flights
),

renamed_and_cleaned AS (
    SELECT
        UPPER(TRIM(icao24)) AS aircraft_icao24,
        UPPER(TRIM(callsign)) AS flight_callsign,
        TRIM(origin_country) AS country_of_origin,
        epoch_ms(time_position * 1000) AS position_timestamp,
        epoch_ms(last_contact * 1000) AS last_contact_timestamp,
        longitude,
        latitude,
        baro_altitude AS altitude_meters,
        altitude_meters * 3.28084 AS altitude_feet,
        on_ground AS is_on_ground,
        velocity AS velocity_mps,
        velocity_mps * 1.94384 AS velocity_knots,
        true_track,
        vertical_rate AS vertical_rate_mps,
        vertical_rate_mps * 196.85 AS vertical_rate_fpm, -- convert to feet per minute
        CAST(snapshot_time AS TIMESTAMP) AS snapshot_timestamp,
        aircraft_category,
        base_fuel_burn_kg_s,
        adjusted_fuel_burn_kg_s,
        co2_emissions_kg_s,
        hourly_co2_tonnes,
        ingested_at AS ingestion_timestamp
    FROM raw_data
),

deduplicated AS (
    -- Deduplicate observations of the same flight in the exact same snapshot
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY aircraft_icao24, snapshot_timestamp 
            ORDER BY last_contact_timestamp DESC
        ) AS row_num
    FROM renamed_and_cleaned
)

SELECT 
    aircraft_icao24,
    flight_callsign,
    country_of_origin,
    position_timestamp,
    last_contact_timestamp,
    longitude,
    latitude,
    altitude_meters,
    altitude_feet,
    is_on_ground,
    velocity_mps,
    velocity_knots,
    true_track,
    vertical_rate_mps,
    vertical_rate_fpm,
    snapshot_timestamp,
    aircraft_category,
    base_fuel_burn_kg_s,
    adjusted_fuel_burn_kg_s,
    co2_emissions_kg_s,
    hourly_co2_tonnes,
    ingestion_timestamp
FROM deduplicated
WHERE row_num = 1