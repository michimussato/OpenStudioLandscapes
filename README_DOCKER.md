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
