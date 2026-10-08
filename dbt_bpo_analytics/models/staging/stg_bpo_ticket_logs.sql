with source as (
    select * from {{ source('raw_bpo', 'fact_ticket_logs') }}
),

renamed as (
    select
        cast(ticket_id as varchar(20)) as ticket_id,
        cast(agent_id as varchar(10)) as agent_id,
        cast(channel as varchar(15)) as contact_channel,
        
        -- Explicitly parse both explicit columns
        cast(received_timestamp_utc as timestamp) as received_at_utc,
        cast(received_timestamp_pht as timestamp) as received_at_pht,
        
        cast(queue_duration_sec as integer) as queue_duration_sec,
        cast(handle_duration_sec as integer) as handle_duration_sec,
        cast(status as varchar(15)) as ticket_status,
        case 
            when status = 'Abandoned' then true 
            else false 
        end as is_abandoned,
        case 
            when queue_duration_sec <= 20 and status != 'Abandoned' then true 
            else false 
        end as is_within_sla
    from source
)

select * from renamed