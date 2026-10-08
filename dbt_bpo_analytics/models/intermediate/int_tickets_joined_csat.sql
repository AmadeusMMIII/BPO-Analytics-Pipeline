with tickets as (
    select * from {{ ref('stg_bpo_ticket_logs') }}
),

csat as (
    select * from {{ ref('stg_bpo_csat_surveys') }}
)

select
    t.ticket_id,
    t.agent_id,
    t.contact_channel,
    t.received_at_utc,
    date_trunc('hour', t.received_at_utc) as received_hour_ust,
    t.received_at_pht,
    date_trunc('hour', t.received_at_pht) as received_hour_pht,
    cast(t.received_at_pht as date) as ticket_date_pht,
    extract(hour from t.received_at_pht) as hour_of_day,
    t.queue_duration_sec,
    t.handle_duration_sec,
    t.ticket_status,
    t.is_abandoned,
    t.is_within_sla,
    c.survey_id,
    c.csat_score,
    case when c.csat_score is not null then true else false end as has_csat_response
from tickets t
left join csat c on t.ticket_id = c.ticket_id