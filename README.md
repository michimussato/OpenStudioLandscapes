![logo128.png](_images/logo128.png)

---

<!-- TOC -->
* [OpenStudioLandscapes](#openstudiolandscapes)
  * [Brief](#brief)
  * [Structure](#structure)
  * [Tested on](#tested-on)
  * [About the Author](#about-the-author)
  * [Requirements](#requirements)
    * [Harbor](#harbor)
    * [Ubuntu](#ubuntu)
      * [20.04](#2004)
        * [Python 3.11](#python-311)
      * [Manjaro](#manjaro)
        * [Official](#official)
        * [AUR](#aur)
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
    * [`python3.11`](#python311)
    * [`python3.12`](#python312)
* [Roadmap](#roadmap)
  * [SSH](#ssh)
  * [Todo](#todo)
* [PyScaffold](#pyscaffold)
  * [Create Module](#create-module)
    * [PyScaffold](#pyscaffold-1)
    * [`pyproject.toml`](#pyprojecttoml)
    * [`setup.cfg`](#setupcfg)
  * [Docker](#docker-1)
<!-- TOC -->

---

# OpenStudioLandscapes

## Brief

Setup and launch a render farm - your 3D Animation
and VFX Pipeline backbone - with ease, independence
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

The scope of this are users with some technical skills with a
desire for a somewhat pre-made solution to set up their 
service environments. OpenStudioLandscapes is therefore
a somewhat opinionated solution for working environments that
lack the fundamental skills or budget to write a solution like
OpenStudioLandscapes by themselves while being flexible enough
for everyone *with* the technical skills to make their way through
configuring a Landscape or even writing their own OpenStudioLandscapes
modules for custom or proprietary services to fully fit their needs.

I guess this is a good starting point to open the project up to
the animation and VFX community to find out where (or where else) 
exactly the needs are to make sure small studios keep growing 
in a (from a technical perspective) healthy way without ending up
in high tech dept dead end.

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

```shell
$ neofetch                                                               INT ✘ 
██████████████████  ████████   michael@lenovo 
██████████████████  ████████   -------------- 
██████████████████  ████████   OS: Manjaro Linux x86_64 
██████████████████  ████████   Host: 82K1 IdeaPad Gaming 3 15IHU6 
████████            ████████   Kernel: 6.12.12-2-MANJARO 
████████  ████████  ████████   Uptime: 2 hours, 45 mins 
████████  ████████  ████████   Packages: 1341 (pacman) 
████████  ████████  ████████   Shell: bash 5.2.37 
████████  ████████  ████████   Resolution: 2560x1080 
████████  ████████  ████████   DE: Plasma 6.2.5 
████████  ████████  ████████   WM: kwin 
████████  ████████  ████████   Theme: Breeze-Dark [GTK2], Breeze [GTK3] 
████████  ████████  ████████   Icons: breeze [GTK2/3] 
████████  ████████  ████████   Terminal: konsole 
                               CPU: 11th Gen Intel i5-11320H (8) @ 4.500GHz 
                               GPU: Intel TigerLake-LP GT2 [Iris Xe Graphics] 
                               GPU: NVIDIA GeForce GTX 1650 Mobile / Max-Q 
                               Memory: 12660MiB / 15776MiB 
```

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

- `python3.11`
- `graphviz`
- `docker`
- `git`
- `git-crypt`
- [Harbor](https://github.com/goharbor/harbor)

### Harbor

Use offline installer or online installer based
on network availability

Releases: https://github.com/goharbor/harbor/releases

```shell
cd OpenStudioLandscapes/.landscapes/.harbor

export HARBOR_RELEASE=v2.12.2

export HARBOR_INSTALLER=harbor-online-installer-${HARBOR_RELEASE}.tgz
export INSTALLER_ONLINE=https://github.com/goharbor/harbor/releases/download/${HARBOR_RELEASE}/${HARBOR_INSTALLER}
export INSTALLER_OFFLINE=https://github.com/goharbor/harbor/releases/download/${HARBOR_RELEASE}/${HARBOR_INSTALLER}

export TEMP_DIR=$(mktemp --directory)
wget -O ${TEMP_DIR}/${HARBOR_INSTALLER} ${INSTALLER_ONLINE}

tar -xvf --strip-components=1 ${TEMP_DIR}/${HARBOR_INSTALLER} -C ./bin/
```

An then, continue inside Dagster (`compose_Harbor` group) to:
- [configure `harbor.yml`](OpenStudioLandscapes/engine/compose_harbor/assets.py:write_yaml)
- generate `docker-compose.yml`
- generate `docker compose` commands

Once Harbor is running, log in and create a project that reflects the name
of the docker registry repository name that is used to prefix the docker
containers generated by OpenStudioLandscapes (see
[`enums.py`](OpenStudioLandscapes/engine/enums/DockerConfig._REPOSITORY_NAME))
Public: no Log-In is needed to push/pull
Private: Log-In is needed to push (pull?)

### Dagster

Todo
- [ ] `dagster dev` is not for production (https://docs.dagster.io/guides/deploy/deployment-options)
- [ ] Switch to postgres
  - https://docs.dagster.io/guides/deploy/deployment-options/docker
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
[SQL: INSERT INTO event_logs (run_id, event, dagster_event_type, timestamp, step_key, asset_key, partition) VALUES (?, ?, ?, ?, ?, ?, ?)]
[parameters: ('5b09c7fc-dccb-41b1-8374-7edf3866d262', '{"__class__": "EventLogEntry", "dagster_event": null, "error_info": null, "level": 10, "message": "", "pipeline_name": "__ASSET_JOB", "run_id": "5b09 ... (133 characters truncated) ... essage": "Loading file from: /home/michael/git/repos/OpenStudioLandscapes/.dagster/storage/Base/group_out using PickledObjectFilesystemIOManager..."}', None, '2025-03-28 23:30:38.580043', 'SESI_gcc_9_3_Houdini_20__build_docker_image', None, None)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/instance/__init__.py", line 260, in emit
    self._instance.handle_new_event(
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/instance/__init__.py", line 2451, in handle_new_event
    self._event_storage.store_event(events[0])
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/storage/event_log/sqlite/sqlite_event_log.py", line 258, in store_event
    conn.execute(insert_event_statement)
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1416, in execute
    return meth(
           ^^^^^
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/sql/elements.py", line 516, in _execute_on_connection
    return connection._execute_clauseelement(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1638, in _execute_clauseelement
    ret = self._execute_context(
          ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1843, in _execute_context
    return self._exec_single_context(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1983, in _exec_single_context
    self._handle_dbapi_exception(
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 2352, in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1964, in _exec_single_context
    self.dialect.do_execute(
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 942, in do_execute
    cursor.execute(statement, parameters)
The above exception was caused by the following exception:
sqlite3.OperationalError: database is locked
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/base.py", line 1964, in _exec_single_context
    self.dialect.do_execute(
  File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/sqlalchemy/engine/default.py", line 942, in do_execute
    cursor.execute(statement, parameters)
```

### Ubuntu

#### 20.04

```
sudo apt-key adv --refresh-keys
```

https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
```
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get -y install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```
sudo apt-get -y install docker.io graphviz git git-crypt
```

```
sudo systemctl enable --now docker
```

##### Python 3.11

```
sudo apt-get -y install \
    build-essential \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    iproute2

apt-get clean
```

```    
pushd $(mktemp -d)

export PYTHON_MAJ=3
export PYTHON_MIN=11
export PYTHON_PAT=11

curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
file Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz

cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} 
./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
make -j $(nproc)
make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install pip --upgrade

rm -rf $(pwd) && popd
```

#### Manjaro

##### Official

```
sudo pacman -Syyu docker docker-buildx docker-compose graphviz git git-crypt
```

```
sudo systemctl enable --now docker
```

If you get something like:

```
ERROR: permission denied while trying to connect to the Docker 
daemon socket at unix:///var/run/docker.sock: 
Head "http://%2Fvar%2Frun%2Fdocker.sock/_ping": 
dial unix /var/run/docker.sock: connect: permission denied
```

Add user `docker` to group `docker`:
- https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue

```
sudo groupadd docker
sudo usermod -aG docker $USER
```

##### AUR

```
sudo pamac install python311
```






- local
  - Manjaro: `libxcrypt-compat`
  - Deadline Client 10.2
    - `libffi6`
  - Deadline Client 10.3

```
System.TypeInitializationException: The type initializer for 'Delegates' threw an exception.
 ---> System.DllNotFoundException: Could not load libpython3.10.so with flags RTLD_NOW | RTLD_GLOBAL: libcrypt.so.1: cannot open shared object file: No such file or directory
   at Python.Runtime.Platform.PosixLoader.Load(String dllToLoad) in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\Native\LibraryLoader.cs:line 61
   at Python.Runtime.Runtime.Delegates.GetUnmanagedDll(String libraryName) in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\Runtime.Delegates.cs:line 290
   at Python.Runtime.Runtime.Delegates..cctor() in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\Runtime.Delegates.cs:line 16
   --- End of inner exception stack trace ---
   at Python.Runtime.Runtime.Delegates.get_Py_GetVersion() in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\Runtime.Delegates.cs:line 341
   at Python.Runtime.Runtime.Py_GetVersion() in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\Runtime.cs:line 826
   at Python.Runtime.PythonEngine.get_Version() in C:\thinkbox-conda\conda-bld\dotnet_pythonnet_1709944764012\work\src\runtime\PythonEngine.cs:line 143
   at FranticX.Scripting.PythonNetScriptEngine.Initialize(Boolean setUnbufferedStdioFlag, String home, String programName)
Exception on Startup: An Unexpected Error Occurred: Attempted python home: /opt/Thinkbox/Deadline10/bin/python3/../../lib/python3, The type initializer for 'Delegates' threw an exception.

Deadline Launcher will now exit.

```

Manjaro: `libxcrypt-compat`

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
| OpenCue        | ✅          | ☐              | ✅                | ☐                             | ❌                  | ✅     | ✅          | ✅            |
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
- [filebrodockerwser/filebrowser](https://hub.docker.com/r/filebrowser/filebrowser)

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
cd ~/git/repos/OpenStudioLandscapes
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/.dagster"
dagster dev
```

http://0.0.0.0:3000

### Configure Landscape

Edit
- `OpenStudioLandscapes.engine.constants`
- `OpenStudioLandscapes.<third_party_module>.constants`
according to your needs.

### Materialize Landscape

![materialize_all.png](_images/materialize_all.png)

#### Resulting Files and Directories (aka "Landscape")

```shell
$ tree .landscapes/2025-02-28_13-24-43__4ade7f1cc21d4e39bb90b1363f807e79
.landscapes/2025-02-28_13-24-43__4ade7f1cc21d4e39bb90b1363f807e79
├── Ayon__Ayon
│   ├── Ayon__clone_repository
│   │   └── repos
│   │       └── ayon-docker
│   │           └── [...]
│   ├── Ayon__compose_override
│   │   └── docker-compose.override.yml
│   └── Ayon__group_out
│       └── docker_compose
│           ├── Ayon__docker_compose_graph
│           │   ├── Ayon__docker_compose_graph.dot
│           │   ├── Ayon__docker_compose_graph.png
│           │   └── Ayon__docker_compose_graph.svg
│           └── docker-compose.yml
├── Base__Base
│   └── Base__build_docker_image
│       └── Dockerfiles
│           └── Dockerfile
├── Compose__Compose
│   └── Compose__group_out
│       └── docker_compose
│           ├── Compose__docker_compose_graph
│           │   ├── Compose__docker_compose_graph.dot
│           │   ├── Compose__docker_compose_graph.png
│           │   └── Compose__docker_compose_graph.svg
│           └── docker-compose.yml
├── Dagster__Dagster
│   ├── Dagster__build_docker_image
│   │   └── Dockerfiles
│   │       ├── Dockerfile
│   │       └── payload
│   │           ├── dagster.yaml
│   │           └── workspace.yaml
│   └── Dagster__group_out
│       └── docker_compose
│           ├── Dagster__docker_compose_graph
│           │   ├── Dagster__docker_compose_graph.dot
│           │   ├── Dagster__docker_compose_graph.png
│           │   └── Dagster__docker_compose_graph.svg
│           └── docker-compose.yml
├── Deadline_10_2__Deadline_10_2
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
│   ├── Deadline_10_2__build_docker_image
│   │   └── Dockerfiles
│   │       └── Dockerfile
│   ├── Deadline_10_2__build_docker_image_client
│   │   └── Dockerfiles
│   │       └── Dockerfile
│   ├── Deadline_10_2__build_docker_image_repository
│   │   └── Dockerfiles
│   │       └── Dockerfile
│   └── Deadline_10_2__group_out
│       └── docker_compose
│           ├── Deadline_10_2__docker_compose_graph
│           │   ├── Deadline_10_2__docker_compose_graph.dot
│           │   ├── Deadline_10_2__docker_compose_graph.png
│           │   └── Deadline_10_2__docker_compose_graph.svg
│           └── docker-compose.yml
├── filebrowser__filebrowser
│   └── filebrowser__group_out
│       └── docker_compose
│           ├── docker-compose.yml
│           └── filebrowser__docker_compose_graph
│               ├── filebrowser__docker_compose_graph.dot
│               ├── filebrowser__docker_compose_graph.png
│               └── filebrowser__docker_compose_graph.svg
├── Grafana__Grafana
│   └── Grafana__group_out
│       └── docker_compose
│           ├── docker-compose.yml
│           └── Grafana__docker_compose_graph
│               ├── Grafana__docker_compose_graph.dot
│               ├── Grafana__docker_compose_graph.png
│               └── Grafana__docker_compose_graph.svg
├── Kitsu__Kitsu
│   ├── data
│   │   └── kitsu
│   │       ├── postgresql
│   │       └── previews
│   ├── Kitsu__build_docker_image
│   │   └── Dockerfiles
│   │       ├── Dockerfile
│   │       └── scripts
│   │           ├── init_db.sh
│   │           └── postgresql.conf
│   ├── Kitsu__group_out
│   │   └── docker_compose
│   │       ├── docker-compose.yml
│   │       └── Kitsu__docker_compose_graph
│   │           ├── Kitsu__docker_compose_graph.dot
│   │           ├── Kitsu__docker_compose_graph.png
│   │           └── Kitsu__docker_compose_graph.svg
│   └── Kitsu__script_init_db
│       └── init_db.sh
├── LikeC4__LikeC4
│   ├── LikeC4__build_docker_image
│   │   └── Dockerfiles
│   │       ├── Dockerfile
│   │       └── payload
│   │           ├── run.sh
│   │           └── setup.sh
│   └── LikeC4__group_out
│       └── docker_compose
│           ├── docker-compose.yml
│           └── LikeC4__docker_compose_graph
│               ├── LikeC4__docker_compose_graph.dot
│               ├── LikeC4__docker_compose_graph.png
│               └── LikeC4__docker_compose_graph.svg
└── OpenCue__OpenCue
    ├── OpenCue__clone_repository
    │   └── repos
    │       └── OpenCue
    │           └── [...]
    ├── OpenCue__compose_override
    │   └── docker-compose.override.yml
    ├── OpenCue__group_out
    │   └── docker_compose
    │       ├── docker-compose.yml
    │       └── OpenCue__docker_compose_graph
    │           ├── OpenCue__docker_compose_graph.dot
    │           ├── OpenCue__docker_compose_graph.png
    │           └── OpenCue__docker_compose_graph.svg
    └── OpenCue__prepare_volumes
        ├── logs
        └── shots

282 directories, 1310 files
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
sudo systemctl stop openstudiolandscapes-registry.service
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

### `python3.11`

- [cyclonedx-bom](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/cyclonedx-py.sbom-3.11.json)
- [pipdeptree (Dot)](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/pipdeptree.sbom-3.11.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/pipdeptree.sbom-3.11.mermaid)

### `python3.12`

- [cyclonedx-bom](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/cyclonedx-py.sbom-3.12.json)
- [pipdeptree (Dot)](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/pipdeptree.sbom-3.12.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/open-studio-landscapes/tree/main/.sbom/pipdeptree.sbom-3.12.mermaid)

# Roadmap

- ☐ Landscape generation based on [VFX Reference Platform](https://vfxplatform.com/) spec
- ☐ Integrating [Rez](https://github.com/AcademySoftwareFoundation/rez)
- Integrating Render Managers
  - Deadline
    - ☐ 10.3
    - ☐ 10.4
  - ✅ [OpenCue](https://github.com/AcademySoftwareFoundation/OpenCue)
  - ☐ [Tractor](https://rmanwiki-26.pixar.com/space/TRA)
  - ☐ [Flamenco](https://flamenco.blender.org/)
- Dynamic Documentation
  - ☐ [LikeC4-Map](https://likec4.dev/)
- Third Party Container Integration
  - ☐ [Watchtower](https://watchtower.blender.org/)


## SSH

```shell
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519.HP_2025-02-09
```

## Todo

# PyScaffold

## Create Module

### PyScaffold

```
pip install PyScaffold
putup --package Package_1234 --force --namespace OpenStudioLandscapes --no-skeleton OpenStudioLandscapes-Package-1234
```

### `pyproject.toml`

```
[tool.dagster]
module_name = "OpenStudioLandscapes.Package_1234.definitions"
code_location_name = "OpenStudioLandscapes-Package-1234"
```

### `setup.cfg`

```
[metadata]
platforms = Linux

[options]
python_requires = >=3.11

install_requires =
    [...]
    dagster==1.9.11
    gitpython
    PyYAML
    python-on-whales
    # yaml_tags.overrides:
    docker-compose-graph @ git+https://github.com/michimussato/docker-compose-graph.git
    # Todo: Will work when released:
    # OpenStudioLandscapes @ git+https://github.com/michimussato/OpenStudioLandscapes
    [...]

[options.extras_require]
dev =
    dagster-webserver==1.9.11
    OpenStudioLandscapes-Package-1234[testing]

[tool:pytest]
norecursedirs =
    dist
    build
    .nox

[flake8]
exclude =
    .nox
    .svg
    build
    dist
    .eggs
    docs/conf.py

[pyscaffold]
package = Package_1234
extensions =
    namespace
namespace = OpenStudioLandscapes
```

## Docker

Docker caches can take up a lot of disk space. If there 
is only limited space available for Docker caches, here is some
further reading:

- https://docs.docker.com/build/cache/
- https://docs.docker.com/build/cache/backends/
- https://docs.docker.com/build/cache/backends/local/
