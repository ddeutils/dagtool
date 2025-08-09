# Build

## Docker Image

```shell
echo -e "AIRFLOW_UID=50000" > .env
```

```shell
docker build --rm --build-arg AIRFLOW_VERSION="2.7.1" \
  --build-arg PYTHON_VERSION="3.10" \
  -f ./.container/Dockerfile \
  -t airflow-local \
  .
```

## Docker Compose

### Standalone

```shell
docker compose -f ./.container/docker-compose-local.yml --env-file .env up -d
```

```shell
docker compose -f ./.container/docker-compose-local.yml --env-file .env down --rmi all
```
