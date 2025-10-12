from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 28),
    'retries': 1,
}

with DAG(
    dag_id='spark_clean_dag',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['spark', 'cleaning']
) as dag:

    start = DummyOperator(task_id='start')

    spark_clean_task = SparkSubmitOperator(
        task_id='spark_clean_data',
        #application='/opt/airflow/dags/scripts/spark_clean.py',
        application='/opt/spark/scripts/spark_clean.py',
        conn_id='spark_default',
        application_args=[
            '/opt/airflow/data/raw',
            '/opt/airflow/data/clean'
        ],
        jars='/opt/airflow/dags/scripts/neo4j-spark-connector.jar'  # Optional if you need Neo4j connection
    )

    end = DummyOperator(task_id='end')

    start >> spark_clean_task >> end