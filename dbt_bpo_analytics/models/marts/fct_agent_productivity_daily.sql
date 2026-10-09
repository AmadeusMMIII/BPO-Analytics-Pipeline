with daily_totals as (
    select * from {{ ref('int_agent_daily_totals') }}
),

agents as (
    select * from {{ ref('stg_bpo_agents') }}
)

select
    d.shift_id,
    d.agent_id,
    a.agent_name,
    a.agent_tier,
    a.preferred_shift,
    d.shift_date,
    d.shift_type,
    d.planned_hours,
    d.actual_worked_hours,
    d.overtime_hours,
    d.total_tickets_handled,
    d.total_handle_sec,
    d.total_handle_hours,
    d.avg_handle_sec,
    d.utilization_rate,
    d.total_daily_csat_score,
    d.avg_daily_csat_score,
    d.total_csat_responses,
    
    -- Burnout Flag Logic: High Overtime + Utilization > 85% + Low CSAT (< 3.5)
    case 
        when d.overtime_hours >= 1.0 
         and d.utilization_rate > .85 
         and d.avg_daily_csat_score < 3.5 
        then true 
        else false 
    end as is_burnout_risk
from daily_totals d
left join agents a on d.agent_id = a.agent_id