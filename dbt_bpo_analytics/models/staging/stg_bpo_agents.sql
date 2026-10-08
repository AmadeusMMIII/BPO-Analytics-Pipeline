with source as (
    select * from {{ source('raw_bpo', 'dim_agents') }}
),

renamed as (
    select
        cast(agent_id as varchar(10)) as agent_id,
        cast(agent_name as varchar(100)) as agent_name,
        cast(tier as varchar(10)) as agent_tier,
        cast(shift_preference as varchar(20)) as preferred_shift,
        cast(hire_date as date) as hire_date,
        cast(is_active as boolean) as is_active
    from source
)

select * from renamed