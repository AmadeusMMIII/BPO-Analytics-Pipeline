with agent_base as (
    select * from {{ ref('stg_bpo_agents') }}
),

agent_stats as (
    select
        agent_id,
        count(distinct shift_id) as total_shifts_worked,
        sum(overtime_hours) as total_overtime_hours,
        round(avg(utilization_rate), 2) as lifetime_avg_utilization_rate,
        round(avg(avg_daily_csat_score), 2) as lifetime_avg_csat_score
    from {{ ref('int_agent_daily_totals') }}
    group by 1
)

select
    b.agent_id,
    b.agent_name,
    b.agent_tier,
    b.preferred_shift,
    b.hire_date,
    b.is_active,
    coalesce(s.total_shifts_worked, 0) as total_shifts_worked,
    coalesce(s.total_overtime_hours, 0) as total_overtime_hours,
    coalesce(s.lifetime_avg_utilization_rate, 0) as lifetime_avg_utilization_rate,
    coalesce(s.lifetime_avg_csat_score, 0) as lifetime_avg_csat_score
from agent_base b
left join agent_stats s on b.agent_id = s.agent_id