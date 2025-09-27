<!-- TOC -->
* [Docker](#docker)
  * [Cleanup](#cleanup)
    * [Prune All](#prune-all)
    * [`hosts` file in Container](#hosts-file-in-container)
<!-- TOC -->

---

# Docker

## Cleanup

- [Pruning](https://docs.docker.com/engine/manage-resources/pruning/)

### Prune All

```shell
docker system prune --volumes
```

### `hosts` file in Container

If the `hosts` file in the container needs
extra entries, the `extra_hosts` key in `docker-compose.yaml`
is here to help:
[https://docs.docker.com/reference/compose-file/services/#extra_hosts]()
