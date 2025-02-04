![logo128.png](_images/logo128.png)

---

<!-- TOC -->
* [OpenStudioLandscapes](#openstudiolandscapes)
  * [Brief](#brief)
  * [Structure](#structure)
  * [Tested on](#tested-on)
  * [About the Author](#about-the-author)
  * [Requirements](#requirements)
  * [Limitations](#limitations)
    * [Render Farms](#render-farms)
      * [Deadline](#deadline)
    * [VFX Platform](#vfx-platform)
  * [Secrets](#secrets)
    * [Personal Secrets](#personal-secrets)
    * [Internal Secrets](#internal-secrets)
      * [Workflow "encrypt"](#workflow-encrypt)
      * [Workflow "unlock"](#workflow-unlock)
      * [Remove git History of a Secrets file](#remove-git-history-of-a-secrets-file)
    * [Public](#public)
  * [Integrated Tools](#integrated-tools)
    * [Render Manager](#render-manager)
    * [3rd Party](#3rd-party)
  * [Dagster Lineage](#dagster-lineage)
  * [Docker Compose Graph](#docker-compose-graph)
    * [Deadline 10.2](#deadline-102)
    * [Repository-Installer 10.2](#repository-installer-102)
  * [Clone](#clone)
  * [Install](#install)
    * [venv](#venv)
    * [open-studio-landscapes](#open-studio-landscapes)
    * [Git Repos](#git-repos)
    * [DeadlineDatabase10](#deadlinedatabase10)
      * [Use Test DB](#use-test-db)
  * [Create Landscape](#create-landscape)
    * [Launch Dagster](#launch-dagster)
    * [Configure Landscape](#configure-landscape)
    * [Materialize Landscape](#materialize-landscape)
      * [Resulting Files and Directories (aka "Landscape")](#resulting-files-and-directories-aka-landscape)
  * [Run Repository Installer](#run-repository-installer)
  * [Run Deadline Farm](#run-deadline-farm)
  * [Client](#client)
    * [Deadline Monitor](#deadline-monitor)
  * [Docker](#docker)
    * [Clean](#clean)
  * [pre-commit](#pre-commit)
  * [nox](#nox)
  * [Pylint](#pylint)
  * [SBOM](#sbom)
    * [3.11](#311)
    * [3.12](#312)
* [Roadmap](#roadmap)
<!-- TOC -->

---

# OpenStudioLandscapes

## Brief

Setup and launch Deadline - your 3D Animation and VFX
Pipeline backbone - with ease, independence
and scalability.

A toolkit - or a declarative build system
if you will - to easily create reproducible
Render Farm environment setups:
create Landscapes for production,
testing, debugging, development,
migration, DB restore etc.

![Overview](_images/Overview.png)

No more black boxes.
No more path dependencies due to bad decisions
made in the past. Stay flexible and adaptable
with this modular system by reconfiguring
any Landscape with ease:
- Easily add, edit, replace or remove services
- Clone (or modify and clone) entire production Landscapes for testing, debugging or development
- Code as source of truth:
  - Always stay on top of things with maps and node trees of code and Landscapes
  - Limit manual documentation to a bare minimum
- `open-studio-landscapes` is (primarily) powered by [Dagster](https://github.com/dagster-io/) and [Docker](https://github.com/docker)
- Fully Python based

This platform is aimed towards small to medium-sized
studios where only limited resources for Pipeline
Engineers and Technical Directors are available.
This system allows those studios to share a common
underlying system to build arbitrary pipeline tools
on top with the ability to share them among others
without sacrificing the technical freedom to implement
highly studio specific and individual solutions if needed.

## Structure

The structure of a Landscape:

```mermaid
%% https://mermaid-js.github.io/mermaid-live-editor
mindmap
  root(landscape)
    Deadline
        RCS
        Webserver
        Pulse
        MongoDB
    Ayon
        Redis
        Postgres
    Kitsu
        Postgres
    Dagster
    LikeC4
    Filebrowser
    Landscape Map
```

The hierarchy of multiple Landscapes
in the context of `open-studio-landscapes`:

```mermaid
%% https://mermaid-js.github.io/mermaid-live-editor
mindmap
root((open-studio-landscapes))
    Landscape(Production)
      Deadline
          RCS
          Webserver
          Pulse
          MongoDB
      Ayon
          Redis
          Postgres
      Kitsu
          Postgres
      Dagster
      LikeC4
      Filebrowser
      Landscape Map
    Landscape(Development)
      Version{{v1}}
        Deadline
            RCS
            Webserver
            Pulse
            MongoDB
        Ayon
            Redis
            Postgres
        Kitsu
            Postgres
        Dagster
        LikeC4
        Filebrowser
        Landscape Map
      Version{{v2}}
        Deadline
            RCS
            Webserver
            Pulse
            MongoDB
        Ayon
            Redis
            Postgres
        Kitsu
            Postgres
        Dagster
        LikeC4
        Filebrowser
        Landscape Map
      Version{{v3}}
        Deadline
            RCS
            Webserver
            Pulse
            MongoDB
        Ayon
            Redis
            Postgres
        Kitsu
            Postgres
        Dagster
        LikeC4
        Filebrowser
        Landscape Map
    Landscape(Debugging)
      Deadline
          RCS
          Webserver
          Pulse
          MongoDB
      Ayon
          Redis
          Postgres
      Kitsu
          Postgres
      Dagster
      LikeC4
      Filebrowser
      Landscape Map
```

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

### Render Farms

The only farm management software that is
currently implemented is Deadline. Others
(as per [this table](#render-manager)) are
(potentially) on the roadmap.

#### Deadline

Currently only for Deadline version 10.2.
Versions 10.3 and 10.4 are WIP and will be
implemented as soon as 10.2 fully works as
a proof of concept.

### VFX Platform

Integration of VFX Platform compatibility
is on the roadmap.

## Secrets

There are many ways to protect sensitive data.
It is `open-studio-landscapes` does not provide a dedicated solution
to protect your secrets - it lets (and wants you to) implement
your own solution or use existing ones if you have something
implemented already. Dagster does handle secrets in
its own way. This approach might be a valid candidate for
`open-studio-landscapes` in the future. More on this here:
https://docs.dagster.io/guides/deploy/using-environment-variables-and-secrets

However, I do have sensitive data myself and I would like to
quickly present my approach to you here. I'm not a security
engineer, hence, I'm coming up with my personal (very basic)
terminology.

I'm suggesting three levels of secrecy, although I'm
only using two in practice:
- Personal
  > Secrets that only certain individuals can know
- Internal
  > Secrets that all individuals within an entity can know
    but not the outside world
- Public
  > Everything that comes with the public `michimussato/open-studio-landscapes`
    Git repository

### Personal Secrets

I'm not concerned about this level of secrecy in my environment.
Integrate/implement your own solution or make suggestions.

### Internal Secrets

I'm protecting secrets from the outside world which need to
be part of the Git repo (version controlled). I've had
very good experience using `git-crypt` which transparently
encrypts files and directories based on a `.gitattributes`
file. The contents of those files are in clear text as
long as the local clone has the key.

My `.gitattributes` file looks as follows:

```
# files starting with __SECRET__
__SECRET__* filter=git-crypt diff=git-crypt
.env filter=git-crypt diff=git-crypt

# folders starting with __SECRET__
*/__SECRET__*/** filter=git-crypt diff=git-crypt
```

You get the idea.

#### Workflow "encrypt"

1. Clone Repo
   ```
   git clone repo
   ```
2. Init `git-crypt`
   ```
   cd repo
   git-crypt init
   ```
3. Export Key
   ```
   git-crypt export-key keyfile.key
   ```
4. Create Filter (`.gitattribtes`)
5. Push Filter
6. Add secrets
7. Push

#### Workflow "unlock"

1. Clone Repo
   ```
   git clone repo
   ```
2. Unlock Repo
   ```
   cd repo
   git-crypt unlock /path/to/keyfile.key
   ```

#### Remove git History of a Secrets file

Requirements:
- `bfg` (https://rtyley.github.io/bfg-repo-cleaner/)

- backup secrets file
- remove secrets file from local repo, commit and push
- `bfg --delete-files __SECRET__* /path/to/repo/.git`
- `git reflog expire --expire=now --all && git gc --prune=now --aggressive`
- `git push --force`

Re-add secrets file with `.gitattributes` filter in place,
commit and push.

More info: https://github.com/AGWA/git-crypt

### Public

You clone (or fork-clone) the repo, make your modification and
push everything publicly.

## Integrated Tools

- [docker-compose-graph](https://github.com/michimussato/docker-compose-graph)

### Render Manager

There are a multitude of managers available
and I had to make a decision to begin with.
In general, `open-studio-landscapes` has the
capability to support arbitrary managers,
however, as of now, only Deadline is considered
integrated. The decision to go with Deadline
was based on the following specs:

- Cross Platform
- Feature rich
- Production proven
- Freely available (not necessarily OSS)
- Scalability (locally and into the cloud)
- Active Development
- Local (no exclusive cloud rendering)
- Python (Python API)
- DCC agnostic

Here's a non-exhaustive list of managers in
comparison:

| Render Manager | Integrated | Cross Platform | Freely Available | Scalability (local and cloud) | Active Development | Local | Python API | DCC agnostic |
|----------------|------------|----------------|------------------|-------------------------------|--------------------|-------|------------|--------------|
| Deadline 10.x  | ✅          | ✅              | ✅                | ✅                             | ☐                  | ✅     | ✅          | ✅            |
| OpenCue        | ❌          | ☐              | ☐                | ☐                             | ❌                  | ☐     | ☐          | ☐            |
| Tractor        | ❌          | ☐              | ❌                | ☐                             | ☐                  | ☐     | ☐          | ☐            |
| Flamenco       | ❌          | ☐              | ☐                | ☐                             | ☐                  | ☐     | ☐          | ❌            |
| RoyalRender    | ❌          | ☐              | ☐                | ☐                             | ☐                  | ☐     | ☐          | ☐            |
| Qube!          | ❌          | ☐              | ❌                | ☐                             | ☐                  | ☐     | ☐          | ☐            |
| AFANASY        | ❌          | ☐              | ☐                | ☐                             | ☐                  | ☐     | ☐          | ☐            |
| Muster         | ❌          | ☐              | ☐                | ☐                             | ☐                  | ☐     | ☐          | ☐            |


### 3rd Party

- [Dagster](https://dagster.io/)
- [LikeC4](https://likec4.dev/)
- [Kitsu](https://kitsu.cg-wire.com/)
- [Ayon](https://ayon.ynput.io/)
- [mongo-express](https://hub.docker.com/_/mongo-express)
- [filebrowser/filebrowser](https://hub.docker.com/r/filebrowser/filebrowser)

## Dagster Lineage

![Global_Asset_Lineage.svg](_images/Global_Asset_Lineage.svg)

![dagster_cascade.png](_images/dagster_cascade.png)

## Docker Compose Graph

Dynamic Docker Compose documentation:
[`docker-compose-graph`](https://github.com/michimussato/docker-compose-graph) creates a visual representation of
`docker-compose.yml` files for every individual
Landscape for quick reference and context.

### Deadline 10.2

`.landscapes/2025-02-01_00-11-08__578595276b424d1ea62550cb0b6f166f/Deadline_10_2/docker_compose/Deadline_10_2__compose_10_2/docker-compose.yml`

![Docker_Compose_Graph__docker_compose_graph_10_2.svg](_images/Docker_Compose_Graph__docker_compose_graph_10_2.svg)

Manual (via CLI):

```shell
docker-compose-graph --yaml .landscapes/2025-02-01_00-11-08__578595276b424d1ea62550cb0b6f166f/Deadline_10_2/docker_compose/Deadline_10_2__compose_10_2/docker-compose.yml --outfile Docker_Compose_Graph__docker_compose_graph_10_2.png -f png
```

### Repository-Installer 10.2

`.landscapes/2025-02-01_00-11-08__578595276b424d1ea62550cb0b6f166f/Deadline_10_2/docker_compose/Deadline_10_2__compose_repository_10_2/docker-compose.yml`

![Docker_Compose_Graph__docker_compose_graph_repository_10_2.svg](_images/Docker_Compose_Graph__docker_compose_graph_repository_10_2.svg)

Manual (via CLI):

```shell
docker-compose-graph --yaml .landscapes/2025-02-01_00-11-08__578595276b424d1ea62550cb0b6f166f/Deadline_10_2/docker_compose/Deadline_10_2__compose_repository_10_2/docker-compose.yml --outfile Docker_Compose_Graph__docker_compose_graph_repository_10_2.png -f png
```

## Clone

```shell
git clone https://github.com/michimussato/open-studio-landscapes.git
cd open-studio-landscapes
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

### open-studio-landscapes

```shell
python -m pip install git+https://github.com/michimussato/open-studio-landscapes.git@main
```

### Git Repos

Clone the

```shell
cd open-studio-landscapes
mkdir -p repos
git -C repos clone https://github.com/ynput/ayon-docker.git
```

### DeadlineDatabase10

#### Use Test DB

Make sure that the `DeadlineDatabase10` directory has
appropriate ownership:

```shell
sudo chown -R 101:65534 /path/to/DeadlineDatabase10
```

And in `OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2.assets.env` set

```python
f"DATABASE_INSTALL_DESTINATION_{KEY}": {
    "default": [...],                     # <-- Set key-value pairs as desired
    "test_db_10_2": pathlib.Path(
        "/path/to/DeadlineDatabase10"
    ).as_posix(),                         # <--
    "another_test_db": [...],  # <--
}["test_db_10_2"]                         # <--- Set to value to be used
```

## Create Landscape

### Launch Dagster

```shell
cd ~/git/repos/open-studio-landscapes
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/dagster/materializations"
dagster dev --workspace "$(pwd)/dagster/workspace.yaml" --host 0.0.0.0  # --port 3000
```

http://0.0.0.0:3000

### Configure Landscape

Edit
- `OpenStudioLandscapes.open_studio_landscapes.assets.env`
- `OpenStudioLandscapes.open_studio_landscapes.Deadline.[...].assets.env`
- `OpenStudioLandscapes.open_studio_landscapes.third_party.[...].assets.env`
according to your needs.

### Materialize Landscape

![materialize_all.png](_images/materialize_all.png)

#### Resulting Files and Directories (aka "Landscape")

```shell
$ tree .landscapes/2025-02-01_00-38-08__cd68a765e3394d41b5e20420f33970bb
.landscapes/2025-02-01_00-38-08__cd68a765e3394d41b5e20420f33970bb
├── Base__env
│   └── Base__env.json
├── configs
│   └── kitsu
│       └── init_zou.sh
├── data
│   └── kitsu
│       ├── postgresql
│       │   └── 14
│       │       └── main  [error opening dir]
│       └── previews
├── Deadline_10_2
│   ├── configs
│   │   ├── Deadline10
│   │   │   └── deadline.ini
│   │   └── DeadlineRepository10
│   │       └── settings
│   │           └── connection.ini
│   ├── data
│   │   └── opt
│   │       └── Thinkbox
│   │           └── DeadlineDatabase10
│   ├── Deadline_10_2__env_10_2.json
│   ├── docker_compose
│   │   ├── Deadline_10_2__compose_10_2
│   │   │   ├── docker-compose.yml
│   │   │   └── Viz__viz_compose_10_2
│   │   │       ├── Viz__viz_compose_10_2.dot
│   │   │       └── Viz__viz_compose_10_2.svg
│   │   └── Deadline_10_2__compose_repository_10_2
│   │       ├── docker-compose.yml
│   │       └── Viz__viz_compose_repository_10_2
│   │           ├── Viz__viz_compose_repository_10_2.dot
│   │           └── Viz__viz_compose_repository_10_2.svg
│   └── Dockerfiles
│       ├── Deadline_10_2__build_client_image_10_2
│       │   └── Dockerfile
│       └── Deadline_10_2__build_repository_image_10_2
│           └── Dockerfile
├── docker_compose
│   └── Ayon
│       └── compose_override
│           └── docker-compose.override.yml
├── Dockerfiles
│   ├── Base__build_base_image
│   │   └── Dockerfile
│   ├── Dagster
│   │   └── build
│   │       ├── Dockerfile
│   │       └── payload
│   │           ├── dagster.yaml
│   │           └── workspace.yaml
│   ├── Deadline_10_2__build_base_image_10_2
│   │   └── Dockerfile
│   ├── Kitsu
│   │   └── build
│   │       └── Dockerfile
│   └── LikeC4
│       └── build
│           ├── Dockerfile
│           └── payload
│               ├── run.sh
│               └── setup.sh
└── third_party
    ├── Ayon
    │   └── env
    │       └── Ayon__env.json
    ├── Dagster
    │   └── env
    │       └── Dagster__env.json
    ├── Grafana
    │   └── env
    │       └── Grafana__env.json
    ├── Kitsu
    │   └── env
    │       └── Kitsu__env.json
    └── LikeC4
        └── env
            └── LikeC4__env.json

52 directories, 28 files
```

## Run Repository Installer

Copy/Paste command, execute and wait for it to finish:

![installer_compose_up.png](_images/installer_compose_up.png)

![installer.png](_images/installer.png)

And `docker compose down` eventually:

![installer_compose_down.png](_images/installer_compose_down.png)

## Run Deadline Farm

Together with:
- Kitsu
- Ayon
- Dagster
- LikeC4
- ...

Copy/Paste command and execute:

![farm_compose_up.png](_images/farm_compose_up.png)

![runner.png](_images/runner.png)

## Client

### Deadline Monitor

![monitor.png](_images/monitor.png)

![monitor_2.png](_images/monitor_2.png)

## Docker

### Clean

```shell
docker stop $(docker ps -q)
docker container prune -f
docker image prune -a -f
docker volume prune -a -f
docker buildx prune -a -f
docker network prune -f
```

## pre-commit

- https://pre-commit.com/
- https://pre-commit.com/hooks.html

```shell
pre-commit install
```

```shell
pre-commit run --all-files
```

## nox

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

## Pylint

- `# pylint: disable=redefined-outer-name` ([`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html)): Due to Dagsters way of piping
  arguments into assets.

## SBOM

### 3.11

- [cyclonedx-bom](.sbom/cyclonedx-py.sbom-3.11.json)
- [pipdeptree (Dot)](.sbom/pipdeptree.sbom-3.11.dot)
- [pipdeptree (Mermaid)](.sbom/pipdeptree.sbom-3.11.mermaid)

### 3.12

- [cyclonedx-bom](.sbom/cyclonedx-py.sbom-3.12.json)
- [pipdeptree (Dot)](.sbom/pipdeptree.sbom-3.12.dot)
- [pipdeptree (Mermaid)](.sbom/pipdeptree.sbom-3.12.mermaid)

# Roadmap

- [ ] Landscape generation based on [VFX Reference Platform](https://vfxplatform.com/) spec
- [ ] Integrating [Rez](https://github.com/AcademySoftwareFoundation/rez)
- Integrating Render Managers
  - Deadline
    - [ ] 10.3
    - [ ] 10.4
  - [OpenCue](https://github.com/AcademySoftwareFoundation/OpenCue)
  - Tractor
  - [Flamenco](https://flamenco.blender.org/)
- Dynamic Documentation
  - [ ] LikeC4-Map
- Third Party Container Integration
  - [ ] [Watchtower](https://watchtower.blender.org/)
