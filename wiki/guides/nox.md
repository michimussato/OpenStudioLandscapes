## nox

```shell
nox --help
```

### Issues

```
ERROR: Failed to build installable wheels for some pyproject.toml based projects (...)
nox > Session readme_all failed.
```
-> Probably jus delete `.nox/readme_all` and re-run
-> Disable re-use venv?

### OpenStudioLandscapes Quick Start

#### Up

```shell
# nox --sessions harbor_up_detach pi_hole_up_detach dagster_postgres_up_detach dagster_postgres
nox --sessions harbor_up_detach dagster_postgres_up_detach dagster_postgres
```

#### Down

```shell
nox --sessions dagster_postgres_down pi_hole_down harbor_down
```

### Current Sessions

```shell
OpenStudioLandscapes git:[main]
nox --list-sessions
Sessions defined in OpenStudioLandscapes/noxfile.py:

- clone_features -> `git clone` all listed (REPOS_FEATURE) Features into .features.
- pull_features -> `git pull` all listed (REPOS_FEATURE) Features.
- readme_all -> Create README.md for all listed (REPOS_FEATURE) Features.
- stash_features -> `git stash` all listed (REPOS_FEATURE) Features.
- stash_apply_features -> `git stash apply` all listed (REPOS_FEATURE) Features.
- pull_engine -> `git pull` engine.
- stash_engine -> `git stash` engine.
- stash_apply_engine -> `git stash apply` engine.
- create_venv_features -> Create a `venv`s in .features/<Feature> after `nox --session clone_features` and installing the Feature into its own `.venv`.
- install_features_into_engine -> Installs the Features after `nox --session clone_features` into the engine `.venv`.
- fix_hardlinks_in_features -> See https://github.com/michimussato/OpenStudioLandscapes?tab=readme-ov-file#hard-links-sync-files-and-directories-across-repositories-de-duplication
- pi_hole_up -> Start Pi-hole in attached mode.
- pi_hole_prepare -> Prepare Pi-hole in attached mode.
- pi_hole_clear -> Clear Pi-hole with `sudo`. WARNING: DATA LOSS!
- pi_hole_up_detach -> Start Pi-hole in detached mode.
- pi_hole_down -> Shut down Pi-hole.
- harbor_prepare -> Prepare Harbor with `sudo`.
- harbor_clear -> Clear Harbor with `sudo`.
- harbor_up -> Start Harbor with `sudo` in attached mode.
- harbor_up_detach -> Start Harbor with `sudo` in detached mode.
- harbor_down -> Stop Harbor with `sudo`.
- dagster_postgres_up -> Start Postgres backend for Dagster in attached mode.
- dagster_postgres_clear -> Clear Dagster-Postgres with `sudo`. WARNING: DATA LOSS!
- dagster_postgres_up_detach -> Start Postgres backend for Dagster in detached mode.
- dagster_postgres_down -> Shut down Postgres backend for Dagster.
- dagster_postgres -> Start Dagster with Postgres as backend after `nox --session dagster_postgres_up_detach`.
* sbom-3.11 -> Runs Software Bill of Materials (SBOM).
* sbom-3.12 -> Runs Software Bill of Materials (SBOM).
* coverage-3.11 -> Runs coverage
* coverage-3.12 -> Runs coverage
* lint-3.11 -> Runs linters and fixers
* lint-3.12 -> Runs linters and fixers
* testing-3.11 -> Runs pytests.
* testing-3.12 -> Runs pytests.
* readme -> Generate dynamically created README.md file for OpenStudioLandscapes modules.
- release-3.11 -> Build and release to a repository
- release-3.12 -> Build and release to a repository
* docs -> Creates Sphinx documentation.

sessions marked with * are selected, sessions marked with - are skipped.
```

### Generate Report

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

Scope:
- [x] Engine
- [x] Features

### Python Versions

- `python3.11`
- `python3.12`

### Engine

#### Harbor

##### harbor_up

```shell
nox --session harbor_up
```

Scope:
- [x] Engine
- [ ] Features

##### harbor_up_detach

```shell
nox --session harbor_up_detach
```

Scope:
- [x] Engine
- [ ] Features

##### harbor_prepare

```shell
nox --session harbor_prepare
```

Scope:
- [x] Engine
- [ ] Features

##### harbor_clear

```shell
nox --session harbor_clear
```

Scope:
- [x] Engine
- [ ] Features

##### harbor_down

```shell
nox --session harbor_down
```
    
Scope:
- [x] Engine
- [ ] Features

#### Pi Hole

##### pi_hole_up

```shell
nox --session pi_hole_up
```

Scope:
- [x] Engine
- [ ] Features

##### pi_hole_up_detach

```shell
nox --session pi_hole_up_detach
```

Scope:
- [x] Engine
- [ ] Features

##### pi_hole_prepare

```shell
nox --session pi_hole_prepare
```

Scope:
- [x] Engine
- [ ] Features

##### pi_hole_clear

```shell
nox --session pi_hole_clear
```

Scope:
- [x] Engine
- [ ] Features

##### pi_hole_down

```shell
nox --session pi_hole_down
```
    
Scope:
- [x] Engine
- [ ] Features

#### Dagster

##### MySQL

```shell
nox --session dagster_mysql
```
    
Scope:
- [x] Engine
- [ ] Features

##### Postgres

```shell
nox --session dagster_postgres
```
    
Scope:
- [x] Engine
- [ ] Features

#### SBOM

```shell
nox --session sbom
```
    
Scope:
- [x] Engine
- [x] Features

##### Python 3.11

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.11.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.mermaid)

##### Python 3.12

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.12.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.mermaid)

#### Coverage

```shell
nox --session coverage
```
    
Scope:
- [x] Engine
- [x] Features

#### Lint (pylint)

```shell
nox --session lint
```
    
Scope:
- [x] Engine
- [x] Features

- `# pylint: disable=redefined-outer-name` ([`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html)): Due to Dagsters way of piping
  arguments into assets.

#### Testing (pytest)

```shell
nox --session testing
```
    
Scope:
- [x] Engine
- [x] Features

#### Readme

```shell
nox --session readme
```
    
Scope:
- [ ] Engine
- [x] Features

#### Readme All

```shell
nox --session readme_all
```
    
Scope:
- [x] Engine
- [ ] Features

#### Release

Not implemented.

```shell
nox --session release
```
    
Scope:
- [x] Engine
- [x] Features

#### Docs

```shell
nox --session docs
```
    
Scope:
- [x] Engine
- [x] Features

### Batch Jobs (for Features)

#### Clone Features

```shell
nox --session clone_features
```

#### Setup Feature-`venv` (`[dev]`)

Create `.feature/<Feature>/.venv` and 
`pip install --editable .feature/<Feature>`
into it:

```shell
nox --session create_venv_features
```

#### Generate README.md for Features

The Feature-README.md's all follow the same basic
structure, hence, they are created programmatically.

Every Feature has a nox `readme` session.
To create a `README.md` for a single Feature, run:

```shell
cd .features/OpenStudioLandscape-Feature

nox --session readme
```

To create a batch job for all Features, run:

```shell
# Todo
#  - [ ] move to `nox`
pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit
    
    if [ ! -d .venv ]; then
        python3.11 -m venv .venv
    fi;
    
    source .venv/bin/activate
    echo "venv activated."
    
    echo "Generating README.md in ${dir}..."
    nox --session readme
    echo "nox (readme) done."
    
    deactivate
    echo "deactivated."

    popd || exit
done;

popd || exit
```

#### nox Documentation

```shell
# Todo
#  - [ ] move to `nox`
pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit
    
    if [ ! -d .venv ]; then
        python3.11 -m venv .venv
    fi;
    
    source .venv/bin/activate
    echo "venv activated."
    
    echo "Running nox in ${dir}..."
    nox --session docs
    echo "nox (docs) done."
    
    deactivate
    echo "deactivated."

    popd || exit
done;

popd || exit
```

#### Clear .nox Directories

```shell
# Todo
#  - [ ] move to `nox`
pushd .features || exit

for dir in */; do
    echo "${dir}"
    sudo rm -rf "${dir}".nox/*/ || exit
done;

popd || exit
```

#### nox Report

To update the `nox-report.json`, run

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

on each Feature:

```shell
# Todo
#  - [ ] move to `nox`
pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit
    
    if [ ! -d .venv ]; then
        python3.11 -m venv .venv
    fi;
    
    source .venv/bin/activate
    echo "venv activated."
    
    echo "Running nox in ${dir}..."
    nox --no-error-on-missing-interpreters --report .nox/nox-report.json
    echo "nox done."
    
    deactivate
    echo "deactivated."

    popd || exit
done;

popd || exit
```

#### Issues

##### Fix: `pip install -e "../OpenStudioLandscapes/[dev]"`

```
Traceback (most recent call last):
  File "/home/michael/git/repos/OpenStudioLandscapes-Deadline-10-2/readme_generator.py", line 1, in <module>
    from OpenStudioLandscapes.engine.utils import markdown
  File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/utils/markdown.py", line 3, in <module>
    import snakemd
ModuleNotFoundError: No module named 'snakemd'
```

```
Traceback (most recent call last):
  File "/home/michael/git/repos/OpenStudioLandscapes-NukeRLM-8/readme_generator.py", line 1, in <module>
    from OpenStudioLandscapes.engine.utils import markdown
ModuleNotFoundError: No module named 'OpenStudioLandscapes.engine'
```

##### Fix: Enable in `OpenStudioLandscapes.engine.constants`

```
Traceback (most recent call last):
  File "/home/michael/git/repos/OpenStudioLandscapes-OpenCue/readme_generator.py", line 5, in <module>
    from OpenStudioLandscapes.OpenCue import constants
  File "/home/michael/git/repos/OpenStudioLandscapes-OpenCue/src/OpenStudioLandscapes/OpenCue/constants.py", line 63, in <module>
    raise Exception("No compose_scope found for module '%s'" % _module)
Exception: No compose_scope found for module 'OpenStudioLandscapes.OpenCue.constants'
```
