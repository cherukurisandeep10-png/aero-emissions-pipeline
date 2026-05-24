
  
    
    

    create  table
      "lakehouse"."main"."fct_flights_emissions__dbt_tmp"
  
    as (
      WITH flights_staging AS (
    SELECT * FROM "lakehouse"."main"."stg_flights"
)

SELECT
    snapshot_timestamp,
    aircraft_icao24,
    flight_callsign,
    country_of_origin,
    altitude_feet,
    velocity_knots,
    is_on_ground,
    aircraft_category,
    adjusted_fuel_burn_kg_s,
    co2_emissions_kg_s,
    hourly_co2_tonnes,
    -- Label flight phase based on vertical rate in feet-per-minute
    CASE
        WHEN is_on_ground THEN 'On Ground'
        WHEN vertical_rate_fpm > 300 THEN 'Climbing'
        WHEN vertical_rate_fpm < -300 THEN 'Descending'
        ELSE 'Cruising'
    END AS flight_phase,
    longitude,
    latitude
FROM flights_staging
    );
  
  