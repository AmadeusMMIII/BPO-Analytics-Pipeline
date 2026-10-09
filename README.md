# BPO Operations & Workforce Productivity Analytics Pipeline

An end-to-end, production-grade data engineering and analytics pipeline built to diagnose operational bottlenecks, evaluate SLA compliance, and monitor agent burnout across global BPO support queues.

---

## Dashboard Previews

### 1. Executive Operations Overview
![Executive Operations Overview](docs/images/executive_operations_overview.png)
*Tracks global ticket volume, SLA compliance, abandonment rates, average wait times, hourly volume heatmaps, and channel performance against operational benchmarks.*

### 2. Workforce Productivity & Burnout Monitor
![Workforce Productivity & Burnout Monitor](docs/images/workforce_productivity_&_burnout_monitor.png)
*Monitors agent utilization vs. CSAT to flag burnout risks, analyzes shift-level overtime trends, and identifies capacity allocation deficits.*

---

## System Architecture

```text
               +-----------------------+
               |   Raw CSV Datasets    |
               |      (data/raw/)      |
               +-----------+-----------+
                           |
                           v
               +-----------------------+
               |  Python ETL Loader    |  (psycopg / SQLAlchemy COPY Stream)
               | (scripts/02_load.py)  |
               +-----------+-----------+
                           |
                           v
               +-----------------------+
               | PostgreSQL Data Mart  |  (Schema: raw_bpo)
               |     (bpo_analytics)   |
               +-----------+-----------+
                           |
                           v
               +-----------------------+
               |      dbt Core         |  (Data Transformations, UTC/PHT Timezone
               | (dbt_bpo_analytics)   |   Standardization, Staging & Mart Models)
               +-----------+-----------+
                           |
                           v
               +-----------------------+
               |   Tableau Dashboard   |  (Weighted SUM/SUM KPI Aggregations,
               |   (Visualization)     |   Interactive Filter Actions)
               +-----------------------+
```

---

## Key Metric & Modeling Logic

To avoid the mathematical inaccuracies of averaging pre-calculated row-level percentages, all aggregate KPIs in dbt and Tableau strictly enforce **weighted ratio logic (`SUM/SUM`)**:

* **SLA Compliance Rate:**

$$\text{SLA Compliance Rate} = \frac{\sum \text{Total SLA Compliant Tickets}}{\sum \text{Total Incoming Tickets}}$$


* **Abandonment Rate:**

$$\text{Abandonment Rate} = \frac{\sum \text{Total Abandoned Tickets}}{\sum \text{Total Incoming Tickets}}$$


* **Utilization Rate:**

$$\text{Utilization Rate} = \frac{\sum \text{Total Ticket Handling Time}}{\sum \text{Total Logged Shift Time}}$$



---

## Executive Insights & Strategic Recommendations

### 1. The Core Issue: Timezone Misalignment

* **Macro Performance:** Overall SLA Compliance sits at **35.28%** (against an **80% target**), and the Abandonment Rate averages **9.60%** (exceeding the **5% maximum threshold**).
* **Graveyard Surge:** Over 55% of incoming ticket volume arrives during Manila graveyard hours (**21:00 to 05:00 PHT**) to align with US peak operating hours, creating severe queue bottlenecks.

### 2. Shift Dynamics & Capacity Allocation

* **Night Shift Strain:** High ticket arrivals during the Night Shift force excessive overtime (**0.78 hrs/agent**) and drive the shift abandonment rate up to **14.10%**.
* **Off-Peak Stability:** Day and Mid Shifts handle off-peak volume where abandonment stays low (**4.04%**), yet SLA compliance remains depressed across all shifts (**~33%–38%**), pointing to schedule misalignment rather than individual agent underperformance.

### 3. Strategic Action Plan

* **Workforce Management (WFM) Realignment:** Reallocate roster headcount from off-peak Day/Mid shifts into Night Shift to cover peak US operating volume without relying on chronic overtime.
* **Schedule & Break Optimization:** Adjust interval scheduling and break rotations during Day/Mid shifts to match mini-volume spikes and improve SLA compliance.
* **Burnout Prevention:** Immediate managerial intervention and workload rebalancing for agents flagged at high utilization thresholds (**>85%**) and declining CSAT scores to prevent turnover.

---

## Tech Stack & Prerequisites

* **Language:** Python 3.10+
* **Database:** PostgreSQL
* **Transformation:** dbt-core / dbt-postgres
* **Libraries:** `pandas`, `SQLAlchemy`, `psycopg`, `python-dotenv`
* **Visualization:** Tableau Desktop

---

## Local Setup & Execution

### 1. Repository Setup

```bash
git clone https://github.com/AmadeusMMIII/BPO-Analytics-Pipeline.git
cd BPO-Analytics-Pipeline
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database & Environment Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/bpo_analytics
```

### 3. Data Ingestion

Execute the Python ETL script to build the schema and load raw data via PostgreSQL native `COPY`:

```bash
python scripts/02_load_data.py
```

### 4. dbt Transformation Models

Navigate to the dbt directory and run full refresh transformations:

```bash
cd dbt_bpo_analytics
dbt deps
dbt run --full-refresh
dbt test
```

---

## 📁 Repository Structure

```text
├── data/
│   ├── raw/                        # Raw CSV datasets
│   └── sql/
│       └── 01_schema_setup.sql     # Database DDL schema definitions
├── dbt_bpo_analytics/              # dbt project root
│   ├── models/                     # Staging & Mart SQL transformation models
│   ├── dbt_project.yml
│   └── profiles.yml.example
├── docs/
│   └── images/                     # Readme visual assets
├── scripts/
│   └── 02_load_data.py             # Bulk ingestion Python ETL script
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```"# BPO-Analytics-Pipeline" 
