
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select aircraft_category
from "lakehouse"."main"."dim_aircraft_types"
where aircraft_category is null



  
  
      
    ) dbt_internal_test