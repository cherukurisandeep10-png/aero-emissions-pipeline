
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select aircraft_icao24
from "lakehouse"."main"."fct_flights_emissions"
where aircraft_icao24 is null



  
  
      
    ) dbt_internal_test