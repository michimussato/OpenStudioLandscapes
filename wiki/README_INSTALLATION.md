<!-- TOC -->
* [Installation](#installation)
  * [System](#system)
  * [Environment](#environment)
  * [Docker](#docker)
    * [Add `${USER}` to Group `docker`](#add-user-to-group-docker)
  * [After the Reboot](#after-the-reboot)
    * [Clone the OpenStudioLandscapes Engine Repository](#clone-the-openstudiolandscapes-engine-repository)
    * [Base Setup - Install OpenStudioLandscapes Engine](#base-setup---install-openstudiolandscapes-engine)
    * [Install Features](#install-features)
  * [Run OpenStudioLandscapes Engine](#run-openstudiolandscapes-engine)
<!-- TOC -->

---

# Installation

## System

Starting off with an Ubuntu 22.04
(Desktop or Server).

```shell
cat /etc/issue
```

```
Ubuntu 22.04.1 LTS \n \l
```

```shell
sudo apt-get -y update \
    && sudo apt-get -y upgrade \
    && sudo apt-get -y install git make
```

## Environment

The *most basic* environment

Open `~/.bashrc` and append the following entries 
at the bottom of the file:

```shell
nano ~/.bashrc
```

```
# OpenStudioLandscapes
## Basics

export OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT=~/git/repos/OpenStudioLandscapes

## Defaults
### Domains
#### LAN

export OPENSTUDIOLANDSCAPES__DOMAIN_LAN=openstudiolandscapes.lan

### su method
# Choices:
# - `su`
# - `sudo`
# - `pkexec`
export SU_METHOD=pkexec

### Passwords
# This is only relevant if `SU_METHOD` is
# anything other than `pkexec`
export SUDO_PASS=

### Make
export PYTHON_MAJ=3
export PYTHON_MIN=11
export PYTHON_PAT=11

### Features
# export OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_AYON=True
# export OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DAGSTER=True
# export OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_KITSU=True
```

## Docker

Here are the preliminary Docker setup steps.

### Add `${USER}` to Group `docker`

```shell
sudo groupadd --force --gid 959 docker  
sudo usermod --append --groups docker ${USER}
sudo reboot
```

---

## After the Reboot

### Clone the OpenStudioLandscapes Engine Repository

```shell
mkdir -p $(dirname ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT})
git -C $(dirname ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}) clone https://github.com/michimussato/OpenStudioLandscapes.git
```

### Base Setup - Install OpenStudioLandscapes Engine

> [!IMPORTANT]
>
> All `make` commands have to be executed inside the
> `${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}` directory.
> 
> ```shell
> cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}
> ```

| Step | Routine                             | Command                             |
|------|-------------------------------------|-------------------------------------|
| 1    | Prepare `/etc/hosts` File           | `make edit_hosts_file`              |
| 2    | Install package dependencies        | `make install_deps`                 |
| 3    | Install Docker Engine               | `make install_docker`               |
| 4    | Install Python 3.11.11              | `make install_python`               |
| 5    | Install OpenStudioLandscapes Engine | `make openstudiolandscapes_install` |

### Install Features

> [!IMPORTANT]
> 
> Features have to be installed into the correct `venv` - the one that was 
> setup in the previous step (5).
> 
> Activate the `venv` with the following command before running any of those
> in the table:
> 
> ```shell
> source ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.venv/bin/activate
> ```

| Feature                                                                                      | Command                                                                                                                                                                                                                                   |
|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)       | `git -C ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features clone https://github.com/michimussato/OpenStudioLandscapes-Ayon.git && pip install -e ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features/OpenStudioLandscapes-Ayon[dev]`       |
| [OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster) | `git -C ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features clone https://github.com/michimussato/OpenStudioLandscapes-Dagster.git && pip install -e ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features/OpenStudioLandscapes-Dagster[dev]` |
| [OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)     | `git -C ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features clone https://github.com/michimussato/OpenStudioLandscapes-Kitsu.git && pip install -e ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.features/OpenStudioLandscapes-Kitsu[dev]`     |

After the installation, the `venv` can be deactivated

```shell
deactivate
```

## Run OpenStudioLandscapes Engine

> [!IMPORTANT]
> 
> Again, for `make` commands, see [important note](#base-setup---install-openstudiolandscapes-engine)

```
make up && make down
```

> [!TIP]
> 
> If you are getting errors here, make sure your user is member or the `docker` group.

The Dagster Web UI - following the terminal 
output - will be accessible here:

```
[...]
2025-11-16 13:06:28 +0100 - dagster-webserver - INFO - Serving dagster-webserver on http://openstudiolandscapes-dagster.openstudiolandscapes.lan:3000 in process 18442
```