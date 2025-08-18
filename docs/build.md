# Build

This is a building document for local testing when I want to develop features.

## Docker Image

```shell
echo -e "AIRFLOW_UID=50000" > .env
```

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
