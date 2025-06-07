# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Launch OpenStudioLandscapes](#launch-openstudiolandscapes)
  * [up](#up)
    * [Interactive Sessions](#interactive-sessions)
      * [Dagster (`openstudiolandscapes-dagster-postgres`)](#dagster-openstudiolandscapes-dagster-postgres)
      * [Postgres (`openstudiolandscapes-postgres`)](#postgres-openstudiolandscapes-postgres)
  * [down](#down)
<!-- TOC -->

---

# Launch OpenStudioLandscapes

## up

```shell
docker compose --progress plain --file docker/docker-compose.yml --project-name openstudiolandscapes up --remove-orphans
```

### Interactive Sessions

#### Dagster (`openstudiolandscapes-dagster-postgres`)

```shell
docker exec -it openstudiolandscapes-dagster-postgres bash
```

#### Postgres (`openstudiolandscapes-postgres`)

```shell
docker exec -it openstudiolandscapes-postgres bash
```

## down

```shell
docker compose --progress plain --file docker/docker-compose.yml --project-name openstudiolandscapes down
```
