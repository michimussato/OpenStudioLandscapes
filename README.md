<!-- TOC -->
* [studio-landscapes](#studio-landscapes)
  * [Tested on](#tested-on)
  * [About the Author](#about-the-author)
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
    * [deadline-docker](#deadline-docker)
  * [Create Generation](#create-generation)
    * [Launch Dagster](#launch-dagster)
    * [Configure Generation](#configure-generation)
    * [Materialize Generation](#materialize-generation)
      * [Resulting Files and Directories (aka "Generation")](#resulting-files-and-directories-aka-generation)
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

# studio-landscapes

Setup and launch Deadline - your 3D Animation and VFX
Pipeline backbone - with ease, independence
and scalability.

A toolkit to easily create reproducible 
Deadline Render Farm environment setups:
create setups for production, 
testing, debugging, development, 
migration, DB restore etc.

No more black boxes.
No more path dependencies due to bad decisions
made in the past. Stay flexible and adaptable 
with this modular system by reconfiguring
your production landscape with ease:
- Easily add, replace or remove services
- Clone (or modify and clone) entire production landscapes for testing, debugging or development
- Always stay on top of things with maps and node trees of code and landscapes
- `deadline-docker` is powered by Dagster

This platform is aimed towards small to medium-sized
studios where only limited resources for Pipeline 
Engineers and Technical Directors are available.
This system allows those studios to share a common
underlying system to build arbitrary pipeline tools
on top of with the ability to share them among others 
without sacrificing the technical freedom  
to implement highly studio specific and individual solutions if 
needed.

## Tested on

- Manjaro Linux

## About the Author

Michael Mussato
- [LinkedIn](https://www.linkedin.com/in/michael-mussato-815902190/)
- [IMDb](https://www.imdb.com/name/nm5961264/)

Former employers, among others:
- [Netflix Animation Studios](https://www.netflixanimation.com/)
- [Animal Logic](https://animallogic.com/)
- [Trixter](https://www.trixter.de/)
- Axis Animation
- [Elefant Studios](http://www.elefantstudios.ch/)

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

Todo:
- [ ] Deadline 10.3
- [ ] Deadline 10.4

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

Dynamic Docker Compose documentation: 
`docker-graph` creates a visual representation of
`docker-compose.yml` files for every individual
Landscape for quick reference and context.

Todo:
- [ ] LikeC4-Map

### Deadline 10.2

`.docker/landscapes/1737214595.1053066/10_2/docker_compose/compose_10_2/docker-compose.yml`

![viz_compose_10_2.png](docs/img/viz_compose_10_2.png)

### Repository-Installer 10.2

`.docker/landscapes/1737214595.1053066/10_2/docker_compose/compose_repository_10_2/docker-compose.yml`

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

## Create Landscape

### Launch Dagster

```shell
cd ~/git/repos/deadline-docker
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/dagster/materializations"
dagster dev --workspace "$(pwd)/dagster/workspace.yaml" --host 0.0.0.0 --port 3000
```

http://0.0.0.0:3000

### Configure Landscape

Edit `deadline-docker.assets.env_base` and 
`deadline-docker.assets.env_10_2` according to your needs.

### Materialize Landscape

![materialize_all.png](docs/img/materialize_all.png)

#### Resulting Files and Directories (aka "Landscape")

```shell
$ tree deadline-docker/.docker/landscapes/1737208678.732601/
deadline-docker/.docker/landscapes/1737208678.732601/
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

Todo
- [ ] rename project `compose_10_2` to `<landscape_id>`

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
