### Docker

Running out of disk space?

Docker (not only caches) can take up a lot of disk space. If there 
is only limited space available for Docker caches, here is some
further reading:

- https://docs.docker.com/build/cache/
- https://docs.docker.com/build/cache/backends/
- https://docs.docker.com/build/cache/backends/local/

#### Remove unused Data

```shell
docker system prune --all --volumes
```

```
docker system prune --help
Usage:  docker system prune [OPTIONS]

Remove unused data

Options:
  -a, --all             Remove all unused images not just dangling ones
      --filter filter   Provide filter values (e.g. "label=<key>=<value>")
  -f, --force           Do not prompt for confirmation
      --volumes         Prune anonymous volumes
```

#### Clean All

Clean filesystem from Docker items (quick and dirty)

```shell
# Todo
#  - [ ] move to `nox`
# sudo systemctl stop openstudiolandscapes-registry.service
docker stop $(docker ps -q)
docker container prune -f
docker image prune -a -f
docker volume prune -a -f
docker buildx prune -a -f
docker network prune -f
```
