
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    aircraft_category as unique_field,
    count(*) as n_records

from "lakehouse"."main"."dim_aircraft_types"
where aircraft_category is not null
group by aircraft_category
having count(*) > 1



  
  
      
    ) dbt_internal_test