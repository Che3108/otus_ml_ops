#!/usr/bin/python3

# -*- coding:utf-8 -*-

# задача DAGа - Создать виртуальную машину


from airflow.operators.bash import BashOperator 
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.sftp.operators.sftp import SFTPOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow import DAG
from airflow.utils.dates import days_ago
import os


YC_PATH = "$HOME/yc"
INSTANCE_NAME = "my-instance-1"
home_dir = os.environ["HOME"]
out_ip = "51.250.91.188"

def find_out_ip(out_ip, **kwargs):
    home_dir = os.environ["HOME"]
    with open(os.path.join(home_dir, "vm_params.txt"), 'r', encoding="utf-8") as f_param:
        l = f_param.readlines()
        l = [i.replace("\n", "") for i in l]
        l = [i.replace(" ", "") for i in l]
        if "one_to_one_nat:" not in l:
            raise ValueError("not out ip")
        out_ip_index = l.index("one_to_one_nat:") + 1
        out_ip = l[out_ip_index].replace("address:", "")


create_vm = DAG(
    dag_id="create_vm",
    start_date=days_ago(0),
    schedule="@daily",
)


#genegate_ssh = BashOperator(
#    task_id="genegate_ssh",
#    dag=create_vm,
#    bash_command='mkdir $HOME/.ssh && \
#                  ssh-keygen -t ed25519 -q -N "" -f $HOME/.ssh/id_ed25519 -C yc-user@$HOSTNAME && \
#                  echo -n "yc-user:" > $HOME/sshkeys.txt && \
#                  cat $HOME/.ssh/id_ed25519.pub >> $HOME/sshkeys.txt'
#)


create_vm_1 = BashOperator(
    task_id="create_vm_1",
    dag=create_vm,
    bash_command=f'{YC_PATH}/bin/yc compute instance create --name {INSTANCE_NAME} \
                    --hostname {INSTANCE_NAME} \
                    --zone ru-central1-a \
                    --create-boot-disk image-family=ubuntu-2004-lts,size=30,type=network-nvme \
                    --image-folder-id standard-images \
                    --memory 8 --cores 2 --core-fraction 100 \
                    --network-interface subnet-name=cherepanov-net-ru-central1-a,nat-ip-version=ipv4 \
                    --ssh-key $HOME/.ssh/id_ed25519.pub > $HOME/vm_params.txt'
                    
)

# --metadata-from-file ssh-keys=$HOME/sshkeys.txt > $HOME/vm_params.txt'

pars_vm_params = PythonOperator(
    task_id="pars_vm_params",
    dag=create_vm,
    python_callable=find_out_ip,
    op_args=[out_ip]
)

update_system = SSHOperator(
    task_id="update_system",
    ssh_hook=SSHHook(remote_host=out_ip, username='yc-user', key_file=f'{home_dir}/.ssh/id_ed25519.key', conn_timeout=99999999),
    command="apt-get -y update && \
             apt -y full-upgrade && \
             apt -y install git && \
             apt -y install docker && \
             apt -y install awscli && \
             git clone https://github.com/Che3108/otus_ml_ops.git ml_ops_engineer/application && \
             git clone https://github.com/Che3108/otus_ml_ops.git ml_ops_engineer/application",
    dag=create_vm,
    do_xcom_push=True,
    cmd_timeout=99999999
)

pars_vm_params >> update_system
