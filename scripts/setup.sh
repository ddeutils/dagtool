#!/bin/bash

echo "Start setup all necessary files before build Airflow ..."
STANDALONE_PASSWORD_FILE="./standalone_admin_password.txt";
if [[ -e "${STANDALONE_PASSWORD_FILE}" ]];
then
  echo "Standalone file already exists.";
else
  echo "Create standalone password file that will mount to Docket container.";
  touch ${STANDALONE_PASSWORD_FILE};
fi

ENV_FILE="./.env";
if [[ -e "${ENV_FILE}" ]];
then
  echo "Dotenv file already exists.";
else
  echo "Create dotenv file.";
  echo "AIRFLOW_PROJ_DIR=$(pwd)" > ${ENV_FILE};
  echo "AIRFLOW_ENV=dev" >> ${ENV_FILE};
fi
