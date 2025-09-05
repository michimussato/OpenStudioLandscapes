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


- clone_features -> `git clone` all listed (REPOS_FEATURE) Features into .features.
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
- dagster_mysql_clear -> Clear Dagster-Postgres with `sudo`. WARNING: DATA LOSS!
- dagster_mysql -> Start Dagster with MySQL as backend (not recommended).
* sbom-3.11(OpenStudioLandscapes) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-NukeRLM-8) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Deadline-10-2) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Syncthing) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-filebrowser) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Dagster) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Kitsu) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-OpenCue) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Grafana) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-LikeC4) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Ayon) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Template) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Watchtower) -> Runs Software Bill of Materials (SBOM).
* sbom-3.11(OpenStudioLandscapes-Deadline-10-2-Worker) -> Runs Software Bill of Materials (SBOM).
* coverage-3.11(OpenStudioLandscapes) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-NukeRLM-8) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Deadline-10-2) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Syncthing) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-filebrowser) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Dagster) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Kitsu) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-OpenCue) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Grafana) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-LikeC4) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Ayon) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Template) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Watchtower) -> Runs coverage (not implemented).
* coverage-3.11(OpenStudioLandscapes-Deadline-10-2-Worker) -> Runs coverage (not implemented).
* lint-3.11(OpenStudioLandscapes) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-NukeRLM-8) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Deadline-10-2) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Syncthing) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-filebrowser) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Dagster) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Kitsu) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-OpenCue) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Grafana) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-LikeC4) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Ayon) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Template) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Watchtower) -> Runs linters and fixers
* lint-3.11(OpenStudioLandscapes-Deadline-10-2-Worker) -> Runs linters and fixers
* testing-3.11(OpenStudioLandscapes) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-NukeRLM-8) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Deadline-10-2) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Syncthing) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-filebrowser) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Dagster) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Kitsu) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-OpenCue) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Grafana) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-LikeC4) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Ayon) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Template) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Watchtower) -> Runs pytests (not implemented).
* testing-3.11(OpenStudioLandscapes-Deadline-10-2-Worker) -> Runs pytests (not implemented).
* readme(OpenStudioLandscapes-NukeRLM-8) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Deadline-10-2) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Syncthing) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-filebrowser) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Dagster) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Kitsu) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-OpenCue) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Grafana) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-LikeC4) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Ayon) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Template) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Watchtower) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* readme(OpenStudioLandscapes-Deadline-10-2-Worker) -> Generate dynamic README.md file for OpenStudioLandscapes modules.
* release-3.11(OpenStudioLandscapes) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-NukeRLM-8) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Deadline-10-2) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Syncthing) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-filebrowser) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Dagster) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Kitsu) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-OpenCue) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Grafana) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-LikeC4) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Ayon) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Template) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Watchtower) -> Build and release to a repository (not implemented).
* release-3.11(OpenStudioLandscapes-Deadline-10-2-Worker) -> Build and release to a repository (not implemented).
- tag(OpenStudioLandscapes) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-NukeRLM-8) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Deadline-10-2) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Syncthing) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-filebrowser) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Dagster) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Kitsu) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-OpenCue) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Grafana) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-LikeC4) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Ayon) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Template) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Watchtower) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag(OpenStudioLandscapes-Deadline-10-2-Worker) -> Git tag OpenStudioLandscapes modules (RELEASE_TYPE=`rc`|`main`, FORCE=`0`|`1`). Needs exactly one argument (i.e. `nox --session tag -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-NukeRLM-8) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Deadline-10-2) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Syncthing) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-filebrowser) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Dagster) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Kitsu) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-OpenCue) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Grafana) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-LikeC4) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Ayon) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Template) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Watchtower) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- tag_delete(OpenStudioLandscapes-Deadline-10-2-Worker) -> Git tag delete OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session tag_delete -- 1.2.0[-rc1]`).
- gh_login -> GitHub CLI Login.
- gh_pr_create(OpenStudioLandscapes) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-NukeRLM-8) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Deadline-10-2) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Syncthing) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-filebrowser) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Dagster) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Kitsu) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-OpenCue) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Grafana) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-LikeC4) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Ayon) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Template) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Watchtower) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_create(OpenStudioLandscapes-Deadline-10-2-Worker) -> Create PR for OpenStudioLandscapes modules. Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-NukeRLM-8) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Deadline-10-2) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Syncthing) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-filebrowser) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Dagster) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Kitsu) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-OpenCue) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Grafana) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-LikeC4) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Ayon) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Template) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Watchtower) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).
- gh_pr_set_mode(OpenStudioLandscapes-Deadline-10-2-Worker) -> Set mode for OpenStudioLandscapes PRs (MODE=`draft`|`ready`). Needs exactly one argument (i.e. `nox --session gh_pr_create -- <branch>`).

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
