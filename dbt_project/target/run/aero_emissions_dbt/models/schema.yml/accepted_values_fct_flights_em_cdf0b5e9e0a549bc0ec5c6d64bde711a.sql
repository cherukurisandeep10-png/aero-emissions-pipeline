
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        flight_phase as value_field,
        count(*) as n_records

    from "lakehouse"."main"."fct_flights_emissions"
    group by flight_phase

)

select *
from all_values
where value_field not in (
    'Climbing','Cruising','Descending','On Ground'
)



  
  
      
    ) dbt_internal_test