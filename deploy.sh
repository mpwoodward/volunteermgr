#!/bin/bash

SRC_DIR=""
TARGET_DIR=""
SERVICE_NAME=""
VENV_DIR=""
SETTINGS_FILE="volunteermgr.settings.production"
USER=""

echo "Clearing out ${TARGET_DIR} ..."
su ${USER} -c "rm -rf ${TARGET_DIR}/*"

echo "Copying code to ${TARGET_DIR} ..."
su ${USER} -c "cp -R ${SRC_DIR}/* ${TARGET_DIR}"
su ${USER} -c "rm -rf ${TARGET_DIR}/.git"

cd ${TARGET_DIR}

echo "Installing requirements ..."
su ${USER} -c "${VENV_DIR}/bin/pip install -r requirements.txt"

echo "Running migrations ..."
su ${USER} -c "${VENV_DIR}/bin/python manage.py migrate --settings=${SETTINGS_FILE}"

echo "Running collectstatic ..."
su ${USER} -c "${VENV_DIR}/bin/python manage.py collectstatic --settings=${SETTINGS_FILE}"

echo "Reloading systemd process ..."
systemctl reload ${SERVICE_NAME}

echo "Reloading nginx ..."
systemctl reload nginx

echo "Done."
