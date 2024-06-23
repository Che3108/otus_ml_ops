#!/usr/bin/python3

# -*- coding:utf-8 -*-

# задача DAGа - Создать виртуальную машину


from airflow.operators.bash import BashOperator 
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.utils.dates import days_ago
import os


YC_PATH = "$HOME/yc"

install_application = DAG(
    dag_id="install_application",
    start_date=days_ago(0),
    schedule="@daily",
)

get_info = BashOperator(
    task_id="get_info",
    dag=install_application,
    bash_command=f'{YC_PATH}/bin/yc compute instance get --full my-instance-1'
)

get_info
