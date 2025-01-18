<!-- TOC -->
* [deadline-docker](#deadline-docker)
  * [Tested on](#tested-on)
  * [Requirements](#requirements)
  * [Limitations](#limitations)
  * [Integrated Tools](#integrated-tools)
  * [Dagster Lineage](#dagster-lineage)
  * [Dynamic Documentation with `docker-graph`](#dynamic-documentation-with-docker-graph)
    * [Deadline 10.2](#deadline-102)
    * [Repository-Installer 10.2](#repository-installer-102)
  * [Install](#install)
    * [deadline-docker](#deadline-docker-1)
    * [Docker](#docker)
      * [Verify Docker Installation](#verify-docker-installation)
  * [Create Generation](#create-generation)
    * [Launch Dagster](#launch-dagster)
    * [Configure Generation](#configure-generation)
    * [Materialize Generation](#materialize-generation)
      * [Resulting Files and Directories ("Generation")](#resulting-files-and-directories-generation)
  * [Run Repository Installer](#run-repository-installer)
  * [Run Deadline Farm](#run-deadline-farm)
<!-- TOC -->

---

# deadline-docker

A toolset to easily set up a Deadline Render Farm environment.
Easily create test setups for debugging, migration, DB restore etc.

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

- [Dagster](https://dagster.io/)
- [LikeC4](https://likec4.dev/)
- [Kitsu](https://kitsu.cg-wire.com/)
- [Ayon](https://ayon.ynput.io/)
- Deadline
  - [Version 10.2](https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/index.html)
- [docker-graph](https://github.com/michimussato/docker-graph)

## Dagster Lineage

![Global_Asset_Lineage.svg](docs/img/Global_Asset_Lineage.svg)

## Dynamic Documentation with `docker-graph`

### Deadline 10.2

![viz_compose_10_2.png](docs/img/viz_compose_10_2.png)

### Repository-Installer 10.2

![viz_compose_repository_10_2.png](docs/img/viz_compose_repository_10_2.png)
![Global_Asset_Lineage_expanded.svg](docs/img/Global_Asset_Lineage_expanded.svg)

## Install

### deadline-docker

```shell
git clone https://github.com/michimussato/deadline-docker.git
cd deadline-docker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .[dev]
```

### Docker

https://docs.docker.com/engine/install/ubuntu/

```shell
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-doc
```

```shell
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```shell
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### Verify Docker Installation

```shell
sudo docker run hello-world
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

## Run Deadline Farm

Together with:
- Kitsu
- Ayon
- Dagster
- LikeC4
- ...

Copy/Paste command and execute:

![farm_compose_up.png](docs/img/farm_compose_up.png)
