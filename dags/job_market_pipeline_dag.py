"""
Job Market Intelligence pipeline DAG.

Chains: ingest Kaggle data -> dbt seed -> dbt run -> dbt test -> retrain
salary model. Training is included in the scheduled run (not just a
one-off script) so the model stays current as new data flows in --
though note the Kaggle dataset itself is a static download, not a live
feed, so in practice this mostly demonstrates the pattern rather than
being triggered by genuinely new data each run.
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

default_args = {
    "owner": "shiva",
    "retries": 1,
}

with DAG(
    dag_id="job_market_pipeline",
    description="Ingest LinkedIn postings, transform with dbt, retrain salary model",
    default_args=default_args,
    start_date=datetime(2026, 9, 1),
    schedule="@weekly",
    catchup=False,
    tags=["job-market", "portfolio"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_kaggle_data",
        bash_command=f"cd {PROJECT_DIR}/scripts && python ingest_kaggle_to_gcs_bigquery.py",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {PROJECT_DIR} && dbt seed --no-partial-parse",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT_DIR} && dbt run --no-partial-parse",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT_DIR} && dbt test --no-partial-parse",
    )

    train_model = BashOperator(
        task_id="train_salary_model",
        bash_command=f"cd {PROJECT_DIR}/scripts && python train_salary_model.py",
    )

    ingest >> dbt_seed >> dbt_run >> dbt_test >> train_model
