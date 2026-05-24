WITH flights_staging AS (
    SELECT * FROM {{ ref('stg_flights') }}
)

SELECT
    aircraft_category,
    COUNT(DISTINCT aircraft_icao24) AS unique_aircraft_count,
    COUNT(DISTINCT flight_callsign) AS unique_flights_count,
    ROUND(AVG(altitude_feet), 2) AS average_altitude_feet,
    ROUND(AVG(velocity_knots), 2) AS average_velocity_knots,
    ROUND(AVG(adjusted_fuel_burn_kg_s), 4) AS average_fuel_burn_kg_s,
    ROUND(AVG(co2_emissions_kg_s), 4) AS average_co2_kg_s,
    ROUND(SUM(co2_emissions_kg_s * 10) / 1000.0, 4) AS estimated_snapshot_co2_tonnes -- Assuming a 10-second sampling window per state
FROM flights_staging
GROUP BY 1
ORDER BY unique_aircraft_count DESC
