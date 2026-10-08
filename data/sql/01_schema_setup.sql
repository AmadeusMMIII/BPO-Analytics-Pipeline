-- Create an isolated raw layer schema
CREATE SCHEMA IF NOT EXISTS raw_bpo;

-- 1. Dimension: Agents
DROP TABLE IF EXISTS raw_bpo.dim_agents CASCADE;
CREATE TABLE raw_bpo.dim_agents (
    agent_id         VARCHAR(10) PRIMARY KEY,
    agent_name       VARCHAR(100) NOT NULL,
    tier             VARCHAR(10) NOT NULL,
    shift_preference VARCHAR(20) NOT NULL,
    hire_date        DATE NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE
);

-- 2. Fact: Shift Logs
DROP TABLE IF EXISTS raw_bpo.fact_shift_logs CASCADE;
CREATE TABLE raw_bpo.fact_shift_logs (
    shift_id            VARCHAR(20) PRIMARY KEY,
    agent_id            VARCHAR(10) NOT NULL REFERENCES raw_bpo.dim_agents(agent_id),
    shift_date          DATE NOT NULL,
    shift_type          VARCHAR(20) NOT NULL,
    planned_hours       NUMERIC(4, 2) NOT NULL,
    actual_worked_hours NUMERIC(4, 2) NOT NULL,
    overtime_hours      NUMERIC(4, 2) NOT NULL
);

-- 3. Fact: Ticket Logs
DROP TABLE IF EXISTS raw_bpo.fact_ticket_logs CASCADE;
CREATE TABLE raw_bpo.fact_ticket_logs (
    ticket_id              VARCHAR(20) PRIMARY KEY,
    agent_id               VARCHAR(10) REFERENCES raw_bpo.dim_agents(agent_id), -- Nullable for abandoned tickets
    channel                VARCHAR(15) NOT NULL,
    received_timestamp_utc TIMESTAMP NOT NULL,
    received_timestamp_pht TIMESTAMP NOT NULL,
    queue_duration_sec     INT NOT NULL,
    handle_duration_sec    INT NOT NULL,
    status                 VARCHAR(15) NOT NULL
);

-- 4. Fact: CSAT Surveys
DROP TABLE IF EXISTS raw_bpo.fact_csat_surveys CASCADE;
CREATE TABLE raw_bpo.fact_csat_surveys (
    survey_id            VARCHAR(20) PRIMARY KEY,
    ticket_id            VARCHAR(20) NOT NULL REFERENCES raw_bpo.fact_ticket_logs(ticket_id),
    csat_score           INT CHECK (csat_score BETWEEN 1 AND 5),
    survey_timestamp_pht TIMESTAMP NOT NULL
);

-- Create performance indexes for common joins in dbt
CREATE INDEX idx_shift_logs_agent_date ON raw_bpo.fact_shift_logs(agent_id, shift_date);
CREATE INDEX idx_ticket_logs_agent ON raw_bpo.fact_ticket_logs(agent_id);
CREATE INDEX idx_ticket_logs_ts_utc ON raw_bpo.fact_ticket_logs(received_timestamp_utc);
CREATE INDEX idx_ticket_logs_ts_pht ON raw_bpo.fact_ticket_logs(received_timestamp_pht);
CREATE INDEX idx_csat_ticket ON raw_bpo.fact_csat_surveys(ticket_id);