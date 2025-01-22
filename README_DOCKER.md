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

```
# docker container prune -f
docker stop $(docker ps -q)
docker container prune -f
docker image prune -a -f
docker volume prune -a -f
docker buildx prune -f
docker network prune -f
```

```
# Remove images
docker rmi $(docker image ls)
```

Get disk usage:
`docker system df`

## docker compose

Build
`docker compose -f docker-compose.yaml build`
Force Rebuild
`docker compose -f docker-compose.yaml build --no-cache`

Up
`docker compose -f docker-compose.yaml up`

Down
`docker compose -f docker-compose.yaml down`





```
git -C repos clone https://github.com/michimussato/studio-landscapes
git -C repos clone https://github.com/ynput/ayon-docker
git -C repos clone https://github.com/cgwire/kitsu-docker
git -C repos clone https://gitlab.com/mathbou/docker-cgwire.git
git -C repos clone https://github.com/mathbou/docker-cgwire
# kitsu
https://kitsu.cg-wire.com/installation/#cloud-hosting
https://hub.docker.com/r/cgwire/cgwire
https://gitlab.com/mathbou/docker-cgwire
```



- https://stackoverflow.com/questions/55650342/import-docker-compose-file-in-another-compose-file
- https://docs.docker.com/compose/how-tos/multiple-compose-files/include/
- https://docs.docker.com/reference/compose-file/include/



Errors

```
$ docker network rm 68b241dbc9c2
Error response from daemon: error while removing network: network 102_default id 68b241dbc9c20535d7ad069e1b69ae0a3c223643ff4fe15d89cae5ee4dfc8191 has active endpoint
```
- https://stackoverflow.com/a/70404916/2207196
```
$ docker network inspect \
  --format '{{range $cid,$v := .Containers}}{{printf "%s: %s\n" $cid $v.Name}}{{end}}' \
  68b241dbc9c2
4b8dfb9978f87b9b15d259d6b6d4b8e6a2631032b01fd035a3806a1dcba7e7dd: ayon-10-2

$ docker container stop ayon-10-2
ayon-10-2

$ docker network rm 68b241dbc9c2
68b241dbc9c2
```