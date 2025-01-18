<!-- TOC -->
* [deadline-docker](#deadline-docker)
  * [Tested on](#tested-on)
  * [Requirements](#requirements)
  * [Integrated Tools](#integrated-tools)
  * [Dagster Lineage](#dagster-lineage)
  * [docker-graph (Visualizer)](#docker-graph-visualizer)
    * [Deadline 10.2](#deadline-102)
    * [Repository-Installer 10.2](#repository-installer-102)
  * [Install](#install)
    * [deadline-docker](#deadline-docker-1)
    * [Docker](#docker)
      * [Verify Docker Installation](#verify-docker-installation)
  * [Run](#run)
    * [Dagster](#dagster)
<!-- TOC -->

---

# deadline-docker

A toolset to easily set up a Deadline Render Farm environment.
Easily create test setups for debugging, migration, DB restore etc.

## Tested on

- Manjaro

## Requirements

- `graphviz`
- `sshpass`
- `docker`
- `docker compose`
- `git`
- `python` (3.9 through 3.12)

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

## docker-graph (Visualizer)

### Deadline 10.2

![viz_compose_10_2.png](docs/img/viz_compose_10_2.png)

### Repository-Installer 10.2

![viz_compose_repository_10_2.png](docs/img/viz_compose_repository_10_2.png)

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

## Run

### Dagster

```shell
cd ~/git/repos/deadline-docker
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/dagster/materializations"
dagster dev --workspace "$(pwd)/dagster/workspace.yaml" --host 0.0.0.0 --port 3000
```

http://0.0.0.0:3000
