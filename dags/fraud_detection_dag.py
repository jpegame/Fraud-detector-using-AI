from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import os
import sys

# =========================================================
# Ajuste de PATH para importar scripts fora da pasta dags
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# =========================================================
# Definição da DAG (Airflow 3.x)
# =========================================================
with DAG(
    dag_id="fraud_detection_pipeline",
    description="Pipeline ETL para detecção de fraudes",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",        # Airflow 3.x
    catchup=False,
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["fraud", "etl", "ml"],
) as dag:

    # =========================
    # Tasks
    # =========================

    def task_bronze():
        from scripts.bronze_processing import run_bronze
        run_bronze()

    def task_silver():
        from scripts.silver_processing import run_silver
        run_silver()

    def task_gold():
        import pandas as pd
        from scripts.gold_processing import run_gold

        silver_path = os.path.join(
            BASE_DIR, "data", "silver", "silver_data.pkl"
        )

        df = pd.read_pickle(silver_path)
        run_gold(df)

    def task_train_model():
        from scripts.train_model import train_model
        train_model()

    # =========================
    # Operators
    # =========================

    bronze_task = PythonOperator(
        task_id="bronze_layer",
        python_callable=task_bronze,
    )

    silver_task = PythonOperator(
        task_id="silver_layer",
        python_callable=task_silver,
    )

    gold_task = PythonOperator(
        task_id="gold_layer",
        python_callable=task_gold,
    )

    ml_task = PythonOperator(
        task_id="train_model",
        python_callable=task_train_model,
    )

    # =========================
    # Orquestração
    # =========================
    bronze_task >> silver_task >> gold_task >> ml_task
