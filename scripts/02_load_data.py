import io
import os
import sys
import csv
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
DB_URI = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/bpo_analytics"
)

# Dynamic path resolution relative to project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

SCHEMA_SQL_PATH = PROJECT_ROOT / "data" / "sql" / "01_schema_setup.sql"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

TABLES_TO_LOAD = [
    "dim_agents",
    "fact_shift_logs",
    "fact_ticket_logs",
    "fact_csat_surveys",
]


def load_raw_data():
    """Builds database schema and performs high-speed bulk ingestion into PostgreSQL."""
    print("Connecting to PostgreSQL database...")
    engine = create_engine(DB_URI)

    # 1. Execute DDL Schema Setup (data/sql/01_schema_setup.sql)
    if SCHEMA_SQL_PATH.exists():
        print(f"Executing schema setup from {SCHEMA_SQL_PATH.relative_to(PROJECT_ROOT)}...")
        with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        with engine.begin() as conn:
            conn.execute(text(schema_sql))
        print("Schema setup complete.")
    else:
        print(f"Warning: Schema file not found at {SCHEMA_SQL_PATH}")

    # High-speed bulk stream using PostgreSQL native COPY protocol
    def psql_insert_copy(table, conn, keys, data_iter):
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = io.StringIO()
            writer = csv.writer(s_buf)
            writer.writerow(keys)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ", ".join([f'"{k}"' for k in keys])
            table_name = f'"{table.schema}"."{table.name}"' if table.schema else f'"{table.name}"'
            sql = f"COPY {table_name} ({columns}) FROM STDIN WITH CSV HEADER"
            cur.copy_expert(sql=sql, file=s_buf)

    # 2. Ingest CSV Data (data/raw/*.csv)
    with engine.begin() as connection:
        print("Clearing existing staging data...")
        connection.execute(
            text("""
            TRUNCATE TABLE 
                raw_bpo.fact_csat_surveys,
                raw_bpo.fact_ticket_logs,
                raw_bpo.fact_shift_logs,
                raw_bpo.dim_agents
            CASCADE;
        """)
        )

        for table in TABLES_TO_LOAD:
            csv_file = RAW_DATA_DIR / f"{table}.csv"

            if not csv_file.exists():
                print(f"Error: Required file missing at {csv_file}")
                sys.exit(1)

            print(f"Loading {csv_file.name} into raw_bpo.{table}...")
            df = pd.read_csv(csv_file)

            df.to_sql(
                name=table,
                schema="raw_bpo",
                con=connection,
                if_exists="append",
                index=False,
                method=psql_insert_copy,
            )
            print(f"Successfully loaded {len(df):,} rows into raw_bpo.{table}.")

    print("\nPipeline execution complete! Tables built and raw data ingested successfully.")


if __name__ == "__main__":
    load_raw_data()