<!-- TOC -->
* [Docker](#docker)
  * [Create Docker `config.json`](#create-docker-configjson)
  * [Cleanup](#cleanup)
    * [Prune All](#prune-all)
    * [`hosts` file in Container](#hosts-file-in-container)
<!-- TOC -->

---

# Docker

## Create Docker `config.json`

```shell
export OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME=
export OPENSTUDIOLANDSCAPES__HARBOR_PORT=
```

```shell
sudo --preserve-env=OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME,OPENSTUDIOLANDSCAPES__HARBOR_PORT bash -c 'cat << EOF > /etc/docker/daemon.json
{
  "features": {
    "buildkit": true
  },
  "max-concurrent-uploads": 1
}
EOF'
```

## Cleanup

- [Pruning](https://docs.docker.com/engine/manage-resources/pruning/)

### Prune All

```shell
docker system prune --volumes
docker image prune -a
docker container prune
```

### `hosts` file in Container

If the `hosts` file in the container needs
extra entries, the `extra_hosts` key in `docker-compose.yaml`
is here to help:
[https://docs.docker.com/reference/compose-file/services/#extra_hosts]()

## Issues

```
[...]
Error Error response from daemon: all predefined address pools have been fully subnetted
[...]
```

Solution:

```shell
docker network prune
```

```
[...]
unable to get image 'docker.io/postgres:17': permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.51/images/docker.io/postgres:17/json": dial unix /var/run/docker.sock: connect: permission denied
[...]
```

or

```
permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.51/containers/json?all=1&filters=%7B%22label%22%3A%7B%22com.docker.compose.config-hash%22%3Atrue%2C%22com.docker.compose.oneoff%3DFalse%22%3Atrue%2C%22com.docker.compose.project%3Dopenstudiolandscapes-dagster-postgres%22%3Atrue%7D%7D": dial unix /var/run/docker.sock: connect: permission denied
```

Solution:

```shell
sudo groupadd --force --gid 959 docker
sudo usermod --append --groups docker ${USER}
sudo reboot
```
