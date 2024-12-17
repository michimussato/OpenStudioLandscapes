

---


# Docker

https://depot.dev/blog/docker-clear-cache

Get disk usage:
`docker system df`

## docker compose

Build
`docker compose -f docker-compose.yaml build`

Up
`docker compose -f docker-compose.yaml up`

Down
`docker compose -f docker-compose.yaml down`

Force (Re-) Install
(maybe this only affects `build`???)
```
export FORCE_REINSTALL=true
docker compose -f docker-compose.yaml up
```
