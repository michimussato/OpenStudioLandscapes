# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Nox](#nox)
  * [Current Sessions](#current-sessions)
  * [Python Versions](#python-versions)
  * [SBOM](#sbom)
    * [Python 3.11](#python-311)
    * [Python 3.12](#python-312)
<!-- TOC -->

---

# Nox

`OpenStudioLandscapes` comes with several convenience shortcuts for 
repetitive tasks unsing `nox` as its task runner.

```shell
nox --help
```

## Current Sessions

```shell
nox --list-sessions
Sessions defined in OpenStudioLandscapes/noxfile.py:

- clone_features -> `git clone` all listed (REPOS_FEATURE) Features into .features. Performs `git pull` if repos already exist.
- readme_features -> Create README.md for all listed (REPOS_FEATURE) Features.
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
- dagster_mysql -> Start Dagster with MySQL as backend (not recommended).
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
- docs_features -> Create README.md for all listed (REPOS_FEATURE) Features.

sessions marked with * are selected, sessions marked with - are skipped.
```

## Python Versions

- `python3.11`
- `python3.12`

## SBOM

### Python 3.11

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.11.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.mermaid)

### Python 3.12

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.12.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.mermaid)
