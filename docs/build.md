# Build

This is an Airflow building document for local provisioning when we want to develop or
testing.

Support Versions:

| Package | Version | Component |
|---------|---------|-----------|

## Prerequisite

```shell
./script/setup.sh
```

> [!WARNING]
> For the Airflow3, you should set `AIRFLOW__API_AUTH__JWT_SECRET` in the dotenv
> file before start because it needs this value.

## Docker Image (Optional)

Build only Docker image (Optional):

```shell
docker build --rm \
  --build-arg AIRFLOW_VERSION="2.7.1" \
  --build-arg PYTHON_VERSION="3.10" \
  -f ./.container/base.Dockerfile \
  -t airflow-local \
  .
```

## Docker Compose

Start provision Airflow application via Docker Compose file.

### Standalone

1. Create receive password file for standalone mode.

    ```shell
    touch ./standalone_admin_password.txt
    ```

2. Start provision Airflow Standalone:

    ```shell
    docker compose -f ./.container/docker-compose-local-standalone.base.yml --env-file .env up -d
    ```

3. User & Password will show on the Docker Container console.

4. After finish, Down Airflow Standalone:

    ```shell
    docker compose -f ./.container/docker-compose-local-standalone.base.yml --env-file .env down --rmi all
    ```

### LocalExecutor

> Does not set yet.

### CeleryExecutor

> Does not set yet.
