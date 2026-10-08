with source as (
    select * from {{ source('raw_bpo', 'fact_shift_logs') }}
),

renamed as (
    select
        cast(shift_id as varchar(20)) as shift_id,
        cast(agent_id as varchar(10)) as agent_id,
        cast(shift_date as date) as shift_date,
        cast(shift_type as varchar(20)) as shift_type,
        cast(planned_hours as numeric(4,2)) as planned_hours,
        cast(actual_worked_hours as numeric(4,2)) as actual_worked_hours,
        cast(overtime_hours as numeric(4,2)) as overtime_hours
    from source
)

select * from renamed