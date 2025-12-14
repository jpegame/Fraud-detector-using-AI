from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
sys.path.insert(0, "/app/scripts")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "fraud_detection_pipeline",
    default_args=default_args,
    description="Pipeline ETL para detecção de fraudes",
    schedule_interval="@daily",
    catchup=False,
)

def task_bronze():
    from bronze_processing import run_bronze
    run_bronze()

def task_silver():
    from silver_processing import run_silver
    run_silver()

def task_gold():
    import pandas as pd
    from gold_processing import run_gold
    df = pd.read_pickle("data/silver/silver_data.pkl")
    run_gold(df)

def task_train_model():
    from train_model import train_model
    train_model()

bronze_task = PythonOperator(
    task_id="bronze_layer",
    python_callable=task_bronze,
    dag=dag,
)

silver_task = PythonOperator(
    task_id="silver_layer",
    python_callable=task_silver,
    dag=dag,
)

gold_task = PythonOperator(
    task_id="gold_layer",
    python_callable=task_gold,
    dag=dag,
)

ml_task = PythonOperator(
    task_id="train_model",
    python_callable=task_train_model,
    dag=dag,
)

bronze_task >> silver_task >> gold_task >> ml_task
