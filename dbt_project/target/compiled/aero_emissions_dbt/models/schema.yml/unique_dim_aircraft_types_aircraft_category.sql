
    
    

select
    aircraft_category as unique_field,
    count(*) as n_records

from "lakehouse"."main"."dim_aircraft_types"
where aircraft_category is not null
group by aircraft_category
having count(*) > 1


