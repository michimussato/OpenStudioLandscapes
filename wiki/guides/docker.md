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
  "max-concurrent-uploads": 1,
  "insecure-registries": [
    "http://${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME}:{OPENSTUDIOLANDSCAPES__HARBOR_PORT}"
  ]
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
