with ticket_summary as (
    select
        agent_id,
        ticket_date_pht as performance_date,
        count(ticket_id) as total_tickets_handled,
        sum(handle_duration_sec) as total_handle_sec,
        avg(handle_duration_sec) as avg_handle_sec,
        avg(csat_score) as avg_daily_csat,
        count(csat_score) as total_csat_responses
    from {{ ref('int_tickets_joined_csat') }}
    where agent_id is not null
    group by 1, 2
),

shifts as (
    select * from {{ ref('stg_bpo_shift_logs') }}
)

select
    s.shift_id,
    s.agent_id,
    s.shift_date,
    s.shift_type,
    s.planned_hours,
    s.actual_worked_hours,
    s.overtime_hours,
    coalesce(t.total_tickets_handled, 0) as total_tickets_handled,
    coalesce(t.total_handle_sec, 0) as total_handle_sec,
    round(coalesce(t.total_handle_sec, 0) / 3600.0, 2) as total_handle_hours,
    round(coalesce(t.avg_handle_sec, 0), 2) as avg_handle_sec,
    round(t.avg_daily_csat, 2) as avg_daily_csat,
    coalesce(t.total_csat_responses, 0) as total_csat_responses,
    -- Utilization % = (Total Handle Hours / Actual Worked Hours) * 100
    case 
        when s.actual_worked_hours > 0 
        then round(( (coalesce(t.total_handle_sec, 0) / 3600.0) / s.actual_worked_hours ) * 100, 2)
        else 0 
    end as utilization_pct
from shifts s
left join ticket_summary t 
    on s.agent_id = t.agent_id 
   and s.shift_date = t.performance_date