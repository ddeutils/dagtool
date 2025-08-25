# Build

This is a building document for local testing when I want to develop features.

## Docker Image

Build only Docker image.

Set `.env` file:

```shell
echo -e "AIRFLOW_PROJ_DIR=$(pwd)" > .env
```

```dotenv
AIRFLOW_UID=50000
AIRFLOW__CORE__UNIT_TEST_MODE=true
AIRFLOW_ENV=dev
```

Start build Docker image:

```shell
docker build --rm \
  --build-arg AIRFLOW_VERSION="2.7.1" \
  --build-arg PYTHON_VERSION="3.10" \
  -f ./.container/Dockerfile \
  -t airflow-local \
  .
```

## Docker Compose

Start provision Airflow application via Docker Compose file.

### Standalone

```shell
docker compose -f ./.container/docker-compose-local-standalone.yml --env-file .env up -d
```

```shell
docker compose -f ./.container/docker-compose-local-standalone.yml --env-file .env down --rmi all
```

### LocalExecutor

### CeleryExecutor
