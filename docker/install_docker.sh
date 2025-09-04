#!/bin/bash

# update linux instance
sudo yum update -y
# install httpd to see airflow content in browser
sudo yum install httpd -y
sudo systemctl enable httpd
sudo systemctl start httpd

# install docker to setup docker application in linux
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user
sudo yum install git -y

# install docker-compose  to create container from images
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# install airflow code repo from git
sudo git clone https://github.com/ankitnandwani1313/airflow.git
# create directories for
# sudo mkdir /home/ec2-user/airflow-docker
# chmod 777 /home/ec2-user/airflow-docker
# download docker-compose.yaml file to create airflow container from various images
#sudo curl -L 'https://airflow.apache.org/docs/apache-airflow/2.8.3/docker-compose.yaml' -o /home/ec2-user/airflow-docker/docker-compose.yaml
#chmod 777 /home/ec2-user/airflow-docker/docker-compose.yaml

# create directories in airflow-docker folder and also create .env file to store AIRFLOW_UID from linux instance
# sudo mkdir -p /home/ec2-user/airflow-docker/dags /home/ec2-user/airflow-docker/logs /home/ec2-user/airflow-docker/plugins /home/ec2-user/airflow-docker/config
# chmod 777 /home/ec2-user/airflow-docker/dags
# chmod 777 /home/ec2-user/airflow-docker/logs
# chmod 777 /home/ec2-user/airflow-docker/plugins
# chmod 777 /home/ec2-user/airflow-docker/config
sudo mkdir -p /home/ec2-user/airflow/logs /home/ec2-user/airflow/plugins /home/ec2-user/airflow/config
chmod 777 /home/ec2-user/airflow
chmod 777 /home/ec2-user/airflow/logs
chmod 777 /home/ec2-user/airflow/plugins
chmod 777 /home/ec2-user/airflow/config
sudo cp -r /airflow/* /home/ec2-user/airflow/
chmod 777 /home/ec2-user/airflow/dags
chmod 777 /home/ec2-user/airflow/docker-compose.yaml
chmod 777 /home/ec2-user/airflow/requirements.txt
chmod 777 /home/ec2-user/airflow/Dockerfile

# sudo echo -e "AIRFLOW_UID=$(id -u)" > /home/ec2-user/airflow-docker/.env
sudo echo -e "AIRFLOW_UID=$(id -u)" > /home/ec2-user/airflow/.env

# build image to install libraries

sudo docker-compose -f /home/ec2-user/airflow/docker-compose.yaml build

#run airflow-init to initialize airflow
# sudo docker-compose -f /home/ec2-user/airflow-docker/docker-compose.yaml up airflow-init
sudo docker-compose -f /home/ec2-user/airflow/docker-compose.yaml up airflow-init

# run all other applications in docker to kick start airflow
# sudo docker-compose -f /home/ec2-user/airflow-docker/docker-compose.yaml up
sudo docker-compose -f /home/ec2-user/airflow/docker-compose.yaml up