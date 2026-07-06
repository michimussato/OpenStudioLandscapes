<!-- TOC -->
* [Docker](#docker)
  * [Create Docker `config.json`](#create-docker-configjson)
  * [Cleanup](#cleanup)
    * [List all with `Tag`](#list-all-with-tag)
    * [Prune All](#prune-all)
    * [`/var/lib/docker` and `/var/lib/containerd`](#varlibdocker-and-varlibcontainerd)
      * [docker](#docker-1)
      * [containerd](#containerd)
  * [`hosts` file in Container](#hosts-file-in-container)
  * [Issues](#issues)
<!-- TOC -->

---

# Docker

## Create Docker `config.json`

```shell
export VAR1=
export VAR2=
```

```shell
sudo --preserve-env=VAR1,VAR2 bash -c 'cat << EOF > /etc/docker/daemon.json
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

### List all with `Tag`

```shell
TAG=<TAG>
docker images --filter=reference="*:${TAG}" --format "{{.ID}}"
```

Delete all by `Tag`

```shell
TAG=<TAG>
docker image rm --force $(docker images --filter=reference="*:${TAG}" --format "{{.ID}}")
```

### Prune All

```shell
docker system prune --all --volumes --force
docker image prune --all --force
docker container prune --force
```

### `/var/lib/docker` and `/var/lib/containerd`

```shell
sudo du -sh /*
```

#### docker

```shell
sudo du -sh /var/lib/docker/*
```

```shell
sudo systemctl disable --now docker.service docker.socket
sudo mv /var/lib/docker /var/lib/docker.bak
sudo systemctl enable --now  docker.service docker.socket

sudo rm -rf /var/lib/docker.bak
```

#### containerd

```shell
sudo du -sh /var/lib/containerd/*
```

```shell
sudo systemctl disable --now docker.service docker.socket containerd
sudo mv /var/lib/containerd /var/lib/containerd.bak
sudo systemctl enable --now docker.service docker.socket containerd

sudo rm -rf /var/lib/containerd.bak
```

## `hosts` file in Container

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

```
    ~/gi/r/Farm-Setup/konsole_setups    main ?1  sshpass -p user /usr/bin/ssh -t user@minion03 -o StrictHostKeyChecking=no "echo user | sudo -S -k systemctl enable --now openstudiolandscapes-worker.service;     journalctl --follow --unit openstudiolandscapes-worker.service --output cat;     bash -l" 
[sudo] password for user:  Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Error failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://registry.openstudiolandscapes.lan:5000/v2/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client/manifests/sha256:3f2175fb94a9d27fcdff3ca62cbcbcad82c6878b396c3fc6a53a9940af599824": dial tcp: lookup registry.openstudiolandscapes.lan on 127.0.0.53:53: no such host
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Interrupted
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_grafana_build_docker_image_alloy:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Interrupted
Error response from daemon: failed to copy: httpReadSeeker: failed open: failed to do request: Get "https://registry.openstudiolandscapes.lan:5000/v2/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client/manifests/sha256:3f2175fb94a9d27fcdff3ca62cbcbcad82c6878b396c3fc6a53a9940af599824": dial tcp: lookup registry.openstudiolandscapes.lan on 127.0.0.53:53: no such host
/
/data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose /
Working Directory: /data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose
/
openstudiolandscapes-worker.seremoved default_username, default_password from config.ymlrvice: Deactivated successfully.
Started OpenStudioLandscapes Compose Scope "worker" Systemd Unit (openstudiolandscapes-worker.service) - 2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer.
/data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose /
Working Directory: /data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Pulling
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_grafana_build_docker_image_alloy:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Pulling
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Pulling
 Image docker.io/fosrl/newt Pulling
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Error failed to resolve reference "registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer": failed to do request: Head "https://registry.openstudiolandscapes.lan:5000/v2/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client/manifests/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer": dial tcp: lookup registry.openstudiolandscapes.lan on 127.0.0.53:53: no such host
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_grafana_build_docker_image_alloy:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Interrupted
 Image docker.io/fosrl/newt Interrupted
 Image registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer Interrupted
Error response from daemon: failed to resolve reference "registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client:2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer": failed to do request: Head "https://registry.openstudiolandscapes.lan:5000/v2/openstudiolandscapes/openstudiolandscapes_deadline_10_2_build_docker_image_client/manifests/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer": dial tcp: lookup registry.openstudiolandscapes.lan on 127.0.0.53:53: no such host
/
/data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose /
Working Directory: /data/local/.openstudiolandscapes/.landscapes/2026-01-21_17-22-54__seasoned-jelly-wholesale-mixer/ComposeScope_worker/docker_compose
/
openstudiolandscapes-worker.service: Deactivated successfully.
```

Todo: schedule cleanup?
