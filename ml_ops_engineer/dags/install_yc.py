#!/usr/bin/python3

# -*- coding:utf-8 -*-

# задача DAGа - установка и конфигурирование yc cli

from airflow.operators.bash import BashOperator 
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow import DAG
from airflow.utils.dates import days_ago
import os

env_var = (
    ("YANDEX_OAUTH_KEY",   os.environ["YANDEX_OAUTH_KEY"]),
    ("YANDEX_CLOUD_ID", os.environ["YANDEX_CLOUD_ID"]),
    ("YANDEX_FOLDER_ID",   os.environ["YANDEX_FOLDER_ID"]),
)

YC_PATH = "$HOME/yc"

def check_yc_config(**kwargs):
    check_cmd = f'{YC_PATH}/bin/yc config list'
    res = os.system(check_cmd)
    if res != 0:
        return 'install_yc'
    else:
        return 'skpi_install_config_yc'

install_config_yc = DAG(
    dag_id="install_config_yc",
    start_date=days_ago(0),
    schedule="@daily",
)

check_yc = BranchPythonOperator(
    task_id="check_yc",
    dag=install_config_yc,
    python_callable=check_yc_config
)

skpi_install_config_yc = EmptyOperator(
    task_id="skpi_install_config_yc",
    dag=install_config_yc,
)

install_yc = BashOperator(
    task_id="install_yc",
    dag=install_config_yc,
    bash_command=f'curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash -s -- -i {YC_PATH} -n && \
                     {YC_PATH}/bin/yc config profile create $YANDEX_SERVICE_ACCOUNT_NAME && \
                     {YC_PATH}/bin/yc config set token $YANDEX_OAUTH_KEY && \
                     {YC_PATH}/bin/yc config set cloud-id $YANDEX_CLOUD_ID && \
                     {YC_PATH}/bin/yc config set folder-id $YANDEX_FOLDER_ID && \
                     {YC_PATH}/bin/yc iam key create --service-account-name $YANDEX_SERVICE_ACCOUNT_NAME --output $HOME/key.json --folder-id $YANDEX_FOLDER_ID && \
                     {YC_PATH}/bin/yc config set service-account-key $HOME/key.json'
)

check_yc >> [install_yc, skpi_install_config_yc]
