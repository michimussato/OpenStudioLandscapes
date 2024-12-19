<!-- TOC -->
* [Dependencies](#dependencies)
* [Docker](#docker)
  * [docker compose](#docker-compose)
<!-- TOC -->

---

# Dependencies

- https://github.com/michimussato/DeadlineWrapper

# Docker

https://depot.dev/blog/docker-clear-cache

Get disk usage:
`docker system df`

## docker compose

Build
`docker compose -f docker-compose.yaml build`
Force Rebuild
`docker compose -f docker-compose.yaml build --no-cache`

Up
`docker compose -f docker-compose.yaml up`
Force Recreate
`docker compose -f docker-compose.yaml up --force-recreate`

Down
`docker compose -f docker-compose.yaml down`

# 

```
git clone https://github.com/michimussato/deadline-docker
git clone https://github.com/ynput/ayon-docker
# kitsu
https://kitsu.cg-wire.com/installation/#cloud-hosting
https://hub.docker.com/r/cgwire/cgwire
https://gitlab.com/mathbou/docker-cgwire
```



- https://stackoverflow.com/questions/55650342/import-docker-compose-file-in-another-compose-file
- https://docs.docker.com/compose/how-tos/multiple-compose-files/include/
- https://docs.docker.com/reference/compose-file/include/
- 