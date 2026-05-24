
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select co2_emissions_kg_s
from "lakehouse"."main"."stg_flights"
where co2_emissions_kg_s is null



  
  
      
    ) dbt_internal_test