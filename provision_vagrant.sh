#!/usr/bin/env bash

echo "Running apt update ..."
apt update

echo "Installing required Python and other packages ..."
apt install -y build-essential python3-pip python3-dev python3-venv python-psycopg2 software-properties-common libssl-dev libjpeg8-dev libjpeg62 libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libaio1 g++ git wget curl vim zip unzip libpq-dev postgresql-client postgresql-client-common openssl

echo "Upgrading pip ..."
pip3 install pip --upgrade

echo "Upgrading setuptools ..."
pip3 install setuptools --upgrade

echo "Installing project-specific Python packages with pip3 ..."
cd /vagrant
pip3 install -r requirements.txt

echo "Provisioning complete."
