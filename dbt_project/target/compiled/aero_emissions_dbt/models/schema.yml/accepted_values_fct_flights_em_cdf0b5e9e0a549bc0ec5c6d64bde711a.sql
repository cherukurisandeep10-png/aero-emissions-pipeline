
    
    

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


