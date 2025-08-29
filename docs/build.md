# Build

This is a building document for local testing when I want to develop features.

**Set `.env` file**:

1. Create project dir value:

    ```shell
    echo -e "AIRFLOW_PROJ_DIR=$(pwd)" > .env
    ```

2. Add other values:

    ```dotenv
    AIRFLOW_UID=50000
    AIRFLOW__CORE__UNIT_TEST_MODE=true
    AIRFLOW_ENV=dev
    ```

> [!WARNING]
> For Airflow3, you should set `AIRFLOW__API_AUTH__JWT_SECRET` in dotenv file.

## Docker Image

Build only Docker image (Optional):

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

1. Start provision Airflow Standalone:

    ```shell
    docker compose -f ./.container/docker-compose-local-standalone.yml --env-file .env up -d
    ```

2. User & Password will show on the Docker Container console.

3. After finish, Down Airflow Standalone:

    ```shell
    docker compose -f ./.container/docker-compose-local-standalone.yml --env-file .env down --rmi all
    ```

### LocalExecutor

> Does not set yet.

### CeleryExecutor

> Does not set yet.
