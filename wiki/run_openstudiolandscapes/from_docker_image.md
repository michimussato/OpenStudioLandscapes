# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Launch OpenStudioLandscapes via Docker Image](#launch-openstudiolandscapes-via-docker-image)
  * [Requirements](#requirements)
  * [Launch OpenStudioLandscapes](#launch-openstudiolandscapes)
    * [up](#up)
      * [Interactive Sessions](#interactive-sessions)
        * [Dagster (`openstudiolandscapes-dagster-postgres`)](#dagster-openstudiolandscapes-dagster-postgres)
        * [Postgres (`openstudiolandscapes-postgres`)](#postgres-openstudiolandscapes-postgres)
    * [down](#down)
  * [Web Interface](#web-interface)
<!-- TOC -->

---

# Launch OpenStudioLandscapes via Docker Image

> [!NOTE]
> Reference: [https://hub.docker.com/repository/docker/michimussato/openstudiolandscapes/general]()

> [!NOTE]
> I tried `include` Harbor into the OpenStudioLandscapes
> `docker-compose.yml` but Harbor needs `sudo` whereas OpenStudioLandscapes does not. 
> This lead to problems, hence, launch them separately.
> ```shell
> include:  
>   - path:  
>     - ../.landscapes/.harbor/bin/docker-compose.yml
> ```

## Requirements

Harbor must be running:
- [Run Harbor](../run/run_harbor.md#up)

## Launch OpenStudioLandscapes

> [!TIP]
> Running the OpenStudioLandscapes Docker image does not
> actually require an activated `virtualenv` or `nox` (yet),
> so these pure bash commands work as long as the 
> `docker-compose.yml` is available on your local drive.
> Hence, cloning the Git repository is still advisable.

> [!WARNING]
> **Todo**
> Create nox commands for these.

### up

```shell
docker compose --progress plain --file docker/docker-compose.yml --project-name openstudiolandscapes up --remove-orphans
```

#### Interactive Sessions

##### Dagster (`openstudiolandscapes-dagster-postgres`)

```shell
docker exec -it openstudiolandscapes-dagster-postgres bash
```

##### Postgres (`openstudiolandscapes-postgres`)

```shell
docker exec -it openstudiolandscapes-postgres bash
```

### down

```shell
docker compose --progress plain --file docker/docker-compose.yml --project-name openstudiolandscapes down
```

## Web Interface

[http://localhost:3000]()
