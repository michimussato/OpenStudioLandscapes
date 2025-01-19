<!-- TOC -->
* [deadline-docker](#deadline-docker)
  * [Tested on](#tested-on)
  * [Requirements](#requirements)
  * [Limitations](#limitations)
  * [Integrated Tools](#integrated-tools)
    * [3rd Party](#3rd-party)
  * [Dagster Lineage](#dagster-lineage)
  * [Docker Compose Graph](#docker-compose-graph)
    * [Deadline 10.2](#deadline-102)
    * [Repository-Installer 10.2](#repository-installer-102)
  * [Clone](#clone)
  * [Install](#install)
    * [venv](#venv)
    * [deadline-docker](#deadline-docker-1)
  * [Create Generation](#create-generation)
    * [Launch Dagster](#launch-dagster)
    * [Configure Generation](#configure-generation)
    * [Materialize Generation](#materialize-generation)
      * [Resulting Files and Directories ("Generation")](#resulting-files-and-directories-generation)
  * [Run Repository Installer](#run-repository-installer)
  * [Run Deadline Farm](#run-deadline-farm)
  * [Client](#client)
    * [Deadline Monitor](#deadline-monitor)
  * [Docker](#docker)
    * [Clean](#clean)
  * [DeadlineDatabase10](#deadlinedatabase10)
    * [Use Test DB](#use-test-db)
<!-- TOC -->

---

# deadline-docker

Setup and launch Deadline - your 3D Animation and VFX
Pipeline backbone - with ease, independence
and scalability.

A toolset to easily create reproducible 
Deadline Render Farm environment setups:
create setups for production, 
testing, debugging, development, 
migration, DB restore etc.

No more black boxes.
No more path dependencies due to bad decisions
made in the past.

## Tested on

- Manjaro Linux

## Requirements

- `graphviz`
- `sshpass`
- `docker`
- `docker compose`
- `git`
- `python` (3.9 through 3.12)

## Limitations

Currently only for Deadline version 10.2. 
Versions 10.3 and 10.4 are WIP and will be
implemented as soon as 10.2 fully works as
a proof of concept.

## Integrated Tools

- [docker-graph](https://github.com/michimussato/docker-graph)

### 3rd Party

- [Dagster](https://dagster.io/)
- [LikeC4](https://likec4.dev/)
- [Kitsu](https://kitsu.cg-wire.com/)
- [Ayon](https://ayon.ynput.io/)
- Deadline
  - [Version 10.2](https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/index.html)
- [mongo-express](https://hub.docker.com/_/mongo-express)
- [filebrowser/filebrowser](https://hub.docker.com/r/filebrowser/filebrowser)

## Dagster Lineage

![Global_Asset_Lineage.svg](docs/img/Global_Asset_Lineage.svg)

![dagster_cascade.png](docs/img/dagster_cascade.png)

## Docker Compose Graph

Dynamic Docker Compose documentation with `docker-graph` visualizer.

### Deadline 10.2

`.docker/generations/1737214595.1053066/10_2/docker_compose/compose_10_2/docker-compose.yml`

![viz_compose_10_2.png](docs/img/viz_compose_10_2.png)

### Repository-Installer 10.2

`.docker/generations/1737214595.1053066/10_2/docker_compose/compose_repository_10_2/docker-compose.yml`

![viz_compose_repository_10_2.png](docs/img/viz_compose_repository_10_2.png)

## Clone

```shell
git clone https://github.com/michimussato/deadline-docker.git
cd deadline-docker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .[dev]
```

## Install

### venv

```shell
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
```

### deadline-docker

```shell
python -m pip install git+https://github.com/michimussato/deadline-docker.git@main
```

## Create Generation

### Launch Dagster

```shell
cd ~/git/repos/deadline-docker
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/dagster/materializations"
dagster dev --workspace "$(pwd)/dagster/workspace.yaml" --host 0.0.0.0 --port 3000
```

http://0.0.0.0:3000

### Configure Generation

Edit `deadline-docker.assets.env_base` and 
`deadline-docker.assets.env_10_2` according to your needs.

### Materialize Generation

![materialize_all.png](docs/img/materialize_all.png)

#### Resulting Files and Directories ("Generation")

```shell
$ tree deadline-docker/.docker/generations/1737208678.732601/
deadline-docker/.docker/generations/1737208678.732601/
├── 10_2
│   ├── configs
│   │   ├── Deadline10
│   │   │   └── deadline.ini
│   │   └── DeadlineRepository10
│   │       └── settings
│   │           └── connection.ini
│   ├── docker_compose
│   │   ├── compose_10_2
│   │   │   ├── docker-compose.yml
│   │   │   └── viz_compose_10_2
│   │   │       ├── viz_compose_10_2.dot
│   │   │       └── viz_compose_10_2.png
│   │   └── compose_repository_10_2
│   │       ├── docker-compose.yml
│   │       └── viz_compose_repository_10_2
│   │           ├── viz_compose_repository_10_2.dot
│   │           └── viz_compose_repository_10_2.png
│   ├── Dockerfiles
│   │   ├── build_base_image_10_2
│   │   │   └── Dockerfile
│   │   ├── build_client_image_10_2
│   │   │   └── Dockerfile
│   │   ├── build_generic_runner_image_10_2
│   │   │   └── Dockerfile
│   │   └── build_repository_image_10_2
│   │       └── Dockerfile
│   ├── env_10_2.json
│   └── opt
│       └── Thinkbox
│           └── DeadlineDatabase10
├── docker_compose
│   └── compose_ayon_override
│       └── docker-compose.override.yml
├── Dockerfiles
│   ├── build_base_image
│   │   └── Dockerfile
│   ├── build_dagster
│   │   ├── Dockerfile
│   │   └── payload
│   │       ├── dagster.yaml
│   │       └── workspace.yaml
│   ├── build_kitsu
│   │   └── Dockerfile
│   └── build_likec4
│       ├── Dockerfile
│       └── payload
│           ├── run.sh
│           └── setup.sh
└── env_base.json
```

## Run Repository Installer

Copy/Paste command, execute and wait for it to finish:

![installer_compose_up.png](docs/img/installer_compose_up.png)

![installer.png](docs/img/installer.png)

And `docker compose down` eventually:

![installer_compose_down.png](docs/img/installer_compose_down.png)

## Run Deadline Farm

Together with:
- Kitsu
- Ayon
- Dagster
- LikeC4
- ...

Copy/Paste command and execute:

![farm_compose_up.png](docs/img/farm_compose_up.png)

![runner.png](docs/img/runner.png)

## Client

### Deadline Monitor

![monitor.png](docs/img/monitor.png)
![monitor_2.png](docs/img/monitor_2.png)

## Docker

### Clean

```shell
docker stop $(docker ps -q)
docker container prune -f
docker image prune -a -f
docker volume prune -a -f
docker buildx prune -f
docker network prune -f
```

## DeadlineDatabase10

### Use Test DB

```shell
mkdir -p tests/fixtures/10_2/DeadlineDatabase10
tar -xzvf tests/fixtures/DeadlineDatabase10_2.tar.gz -C tests/fixtures/10_2/DeadlineDatabase10
sudo chown -R 101:65534 tests/fixtures/10_2/DeadlineDatabase10
```

And in `deadline-docker.assets.env_10_2` set

```
f"DATABASE_INSTALL_DESTINATION_{context.asset_key.path[0]}": pathlib.Path(
        f"/home/michael/git/repos/deadline-docker/tests/fixtures/{context.asset_key.path[0]}/DeadlineDatabase10",
    ).as_posix()
```
