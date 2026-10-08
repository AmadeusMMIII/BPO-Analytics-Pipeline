import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from faker import Faker
import zoneinfo

# Set up timezone references
PHT = zoneinfo.ZoneInfo("Asia/Manila")
UTC = zoneinfo.ZoneInfo("UTC")

fake = Faker("en_PH")
np.random.seed(42)
random.seed(42)

# --- CONFIGURATION ---
NUM_AGENTS = 50
START_DATE = datetime(2026, 1, 1, tzinfo=PHT)
DAYS_TO_GENERATE = 30


def generate_dim_agents(num_agents):
    """Generates agent roster with assigned shifts and baseline performance metrics."""
    shifts = ["Day Shift", "Mid Shift", "Night Shift"]
    tiers = ["Tier 1", "Tier 2"]

    agents = []
    for i in range(1, num_agents + 1):
        agent_id = f"AGT{i:04d}"
        agents.append(
            {
                "agent_id": agent_id,
                "agent_name": fake.name(),
                "tier": np.random.choice(tiers, p=[0.7, 0.3]),
                "shift_preference": np.random.choice(shifts, p=[0.25, 0.25, 0.50]), # Weighted towards Night Shift
                "hire_date": fake.date_between(
                    start_date="-3y", end_date="-1m"
                ),
                "is_active": True,
            }
        )
    return pd.DataFrame(agents)


def generate_fact_shift_logs(df_agents, start_date, days):
    """Generates daily shift logs including planned vs actual worked hours and overtime."""
    shift_logs = []
    shift_id_counter = 1

    for day_idx in range(days):
        current_date = (start_date + timedelta(days=day_idx)).date()

        for _, agent in df_agents.iterrows():
            # 5-day work week simulation (skip 20% of random agent days as Rest Days)
            if random.random() < 0.2:
                continue

            planned_hours = 9.0  # 8 hours work + 1 hour break

            if agent["shift_preference"] == "Night Shift":
                actual_worked_hours = planned_hours + np.random.choice(
                    [0, 0.5, 1.0, 1.5, 2.0], p=[0.3, 0.2, 0.2, 0.15, 0.15]
                )
            else:
                actual_worked_hours = planned_hours + np.random.choice(
                    [0, 0.5, 1.0], p=[0.7, 0.2, 0.1]
                )

            overtime_hours = max(0.0, actual_worked_hours - planned_hours)

            shift_logs.append(
                {
                    "shift_id": f"SFT{shift_id_counter:07d}",
                    "agent_id": agent["agent_id"],
                    "shift_date": current_date,
                    "shift_type": agent["shift_preference"],
                    "planned_hours": planned_hours,
                    "actual_worked_hours": round(actual_worked_hours, 2),
                    "overtime_hours": round(overtime_hours, 2),
                }
            )
            shift_id_counter += 1

    return pd.DataFrame(shift_logs)


def generate_fact_ticket_logs(df_agents, df_shifts, start_date, days):
    """Generates ticket logs with dual timezone timestamps (UTC & PHT) and higher volume density."""
    ticket_logs = []
    ticket_id_counter = 1
    channels = ["Voice", "Chat", "Email"]

    for day_idx in range(days):
        current_date = start_date + timedelta(days=day_idx)
        active_shifts_today = df_shifts[
            df_shifts["shift_date"] == current_date.date()
        ]

        for hour in range(24):
            # Volume pattern: Graveyard / US business hours (21:00 - 05:00 PHT) see heavy volume
            if 21 <= hour or hour <= 5:
                hourly_ticket_count = random.randint(90, 140)  # Increased density for higher utilization
                current_shift = "Night Shift"
            elif 6 <= hour < 14:
                hourly_ticket_count = random.randint(35, 60)
                current_shift = "Day Shift"
            else:
                hourly_ticket_count = random.randint(50, 80)
                current_shift = "Mid Shift"

            available_agents = active_shifts_today[
                active_shifts_today["shift_type"] == current_shift
            ]["agent_id"].tolist()

            for _ in range(hourly_ticket_count):
                minute = random.randint(0, 59)
                second = random.randint(0, 59)

                # Local PHT Timestamp
                pht_timestamp = current_date.replace(
                    hour=hour, minute=minute, second=second, tzinfo=PHT
                )
                # Corresponding UTC Timestamp (Subtracts 8 hours)
                utc_timestamp = pht_timestamp.astimezone(UTC)

                channel = np.random.choice(channels, p=[0.55, 0.35, 0.10])

                # Determine if ticket is abandoned
                is_abandoned = random.random() < (
                    0.14 if current_shift == "Night Shift" else 0.04
                )

                if is_abandoned or not available_agents:
                    assigned_agent = None
                    queue_duration = random.randint(45, 300)
                    handle_duration = 0
                    status = "Abandoned"
                else:
                    assigned_agent = random.choice(available_agents)
                    queue_duration = random.randint(5, 45)
                    status = np.random.choice(
                        ["Resolved", "Escalated"], p=[0.88, 0.12]
                    )

                    # Duration per channel (Voice/Chat tuned to drive 70-85% utilization)
                    if channel == "Voice":
                        handle_duration = random.randint(300, 720)   # 5–12 mins
                    elif channel == "Chat":
                        handle_duration = random.randint(240, 540)   # 4–9 mins
                    else:
                        handle_duration = random.randint(120, 360)   # 2–6 mins

                ticket_logs.append(
                    {
                        "ticket_id": f"TCK{ticket_id_counter:08d}",
                        "agent_id": assigned_agent,
                        "channel": channel,
                        "received_timestamp_utc": utc_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "received_timestamp_pht": pht_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "queue_duration_sec": queue_duration,
                        "handle_duration_sec": handle_duration,
                        "status": status,
                    }
                )
                ticket_id_counter += 1

    return pd.DataFrame(ticket_logs)


def generate_fact_csat_surveys(df_tickets):
    """Generates CSAT feedback ratings mapped to timestamp instances."""
    handled_tickets = df_tickets[df_tickets["status"] != "Abandoned"].copy()
    survey_tickets = handled_tickets.sample(frac=0.35, random_state=42)

    surveys = []
    survey_id_counter = 1

    for _, ticket in survey_tickets.iterrows():
        # High queue duration or extended handle time depresses customer satisfaction
        if (
            ticket["queue_duration_sec"] > 35
            or ticket["handle_duration_sec"] > 600
        ):
            csat = np.random.choice([1, 2, 3, 4, 5], p=[0.25, 0.25, 0.25, 0.15, 0.10])
        else:
            csat = np.random.choice([1, 2, 3, 4, 5], p=[0.02, 0.04, 0.09, 0.35, 0.50])

        pht_time = datetime.strptime(ticket["received_timestamp_pht"], "%Y-%m-%d %H:%M:%S")
        survey_pht = pht_time + timedelta(minutes=random.randint(10, 60))

        surveys.append(
            {
                "survey_id": f"SRV{survey_id_counter:08d}",
                "ticket_id": ticket["ticket_id"],
                "csat_score": int(csat),
                "survey_timestamp_pht": survey_pht.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        survey_id_counter += 1

    return pd.DataFrame(surveys)


if __name__ == "__main__":
    print("Generating Updated BPO Data with explicit Dual Timezones...")
    df_agents = generate_dim_agents(NUM_AGENTS)
    df_shifts = generate_fact_shift_logs(df_agents, START_DATE, DAYS_TO_GENERATE)
    df_tickets = generate_fact_ticket_logs(df_agents, df_shifts, START_DATE, DAYS_TO_GENERATE)
    df_csat = generate_fact_csat_surveys(df_tickets)

    df_agents.to_csv("data/raw/dim_agents.csv", index=False)
    df_shifts.to_csv("data/raw/fact_shift_logs.csv", index=False)
    df_tickets.to_csv("data/raw/fact_ticket_logs.csv", index=False)
    df_csat.to_csv("data/raw/fact_csat_surveys.csv", index=False)

    print("Generation complete! Tickets generated:", len(df_tickets))