with ticket_facts as (
    select * from {{ ref('int_tickets_joined_csat') }}
)

select
    received_hour_pht,
    received_hour_ust,
    cast(received_hour_pht as date) as queue_date,
    hour_of_day,
    contact_channel,
    count(ticket_id) as total_incoming_tickets,
    sum(case when is_abandoned then 1 else 0 end) as total_abandoned_tickets,
    sum(case when is_within_sla then 1 else 0 end) as total_sla_compliant_tickets,
    sum(case when not is_abandoned then 1 else 0 end) as total_handled_tickets,
    sum(queue_duration_sec) as total_queue_duration_sec,
    sum(case when not is_abandoned then handle_duration_sec else 0 end) as total_handle_duration_sec,
    sum(case when is_abandoned then 1 else 0 end)::numeric / count(ticket_id) as abandonment_rate_pct,
    sum(case when is_within_sla then 1 else 0 end)::numeric / count(ticket_id) as sla_compliance_rate,
    round(avg(queue_duration_sec), 2) as avg_queue_duration_sec,
    round(avg(case when not is_abandoned then handle_duration_sec else null end), 2) as avg_handle_duration_sec
from ticket_facts
group by 1, 2, 3, 4, 5