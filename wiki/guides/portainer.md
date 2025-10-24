<!-- TOC -->
* [Portainer](#portainer)
  * [Up](#up)
  * [Down](#down)
<!-- TOC -->

---

# Portainer

A `docker-compose.yml` to spin up a Portainer instance is available at
`.portainer/docker-compose.yml`

## Up

```shell
cd ../../.portainer

docker compose --progress plain --file ./docker-compose.yml --project-name openstudiolandscapes-portainer up --remove-orphans
```

## Down



```shell
cd ../../.portainer

docker compose --progress plain --file ./docker-compose.yml --project-name openstudiolandscapes-portainer down
```
