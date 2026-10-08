with source as (
    select * from {{ source('raw_bpo', 'fact_csat_surveys') }}
),

renamed as (
    select
        cast(survey_id as varchar(20)) as survey_id,
        cast(ticket_id as varchar(20)) as ticket_id,
        cast(csat_score as integer) as csat_score,
        cast(survey_timestamp_pht at time zone 'UTC' at time zone 'Asia/Manila' as timestamp) as surveyed_at_pht
    from source
)

select * from renamed