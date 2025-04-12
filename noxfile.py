import json
import shutil
import os
import nox
import pathlib
import requests
import logging

import yaml

logging.basicConfig(level=logging.DEBUG)


def download(
    url: str,
    dest_folder: pathlib.Path,
) -> pathlib.Path:
    if not dest_folder.exists():
        dest_folder.mkdir(
            parents=True, exist_ok=True
        )  # create folder if it does not exist

    filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
    file_path = dest_folder / filename

    r = requests.get(url, stream=True)
    if r.ok:
        logging.info("Saving to %s" % file_path.absolute().as_posix())
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return file_path
    else:  # HTTP status code 4XX/5XX
        raise Exception(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )


import tarfile


# nox Configuration & API
# https://nox.thea.codes/en/stable/config.html
# # nox.sessions.Session.run
# https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run


# https://www.youtube.com/watch?v=ImBvrDvK-1U&ab_channel=HynekSchlawack
# https://codewitholi.com/_posts/python-nox-automation/


# reuse_existing_virtualenvs:
# local: @nox.session(reuse_venv=True)
# global: nox.options.reuse_existing_virtualenvs = True
nox.options.reuse_existing_virtualenvs = True

# default sessions when none is specified
# nox --session [SESSION] [SESSION] [...]
# or
# nox --tag [TAG] [TAG] [...]
nox.options.sessions = [
    "readme",
    "sbom",
    "coverage",
    "lint",
    "testing",
    "docs",
    # "docs_live",
    # "release",
]

# Python versions to test against
# dagster==1.9.11 needs >=3.9 but 3.13 does not seem to be working
VERSIONS = [
    "3.11",
    "3.12",
    # "3.13",
]

VERSIONS_README = VERSIONS[0]

ENV = {}


#######################################################################################################################
# Pi-hole

# Todo
#  - [ ] Maybe we can create the docker-compose.yml in here directly taking into consideration
#        all the variables

compose_pi_hole = (
    pathlib.Path.cwd()
    / ".landscapes"
    / ".pi-hole"
    / "docker_compose"
    / "docker-compose.yml"
)

cmd_pi_hole = [
    shutil.which("docker"),
    "compose",
    "--file",
    compose_pi_hole.as_posix(),
    "--project-name",
    "openstudiolandscapes-pi-hole",
]

# # pi_hole_up
@nox.session(python=None, tags=["pi_hole_up"])
def pi_hole_up(session):
    """
    Start Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session pi_hole_up
    # nox --tags pi_hole_up

    # /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.pi-hole/docker_compose/docker-compose.yml \
    #     --project-name openstudiolandscapes-pi-hole up --remove-orphans

    if not compose_pi_hole.exists():
        raise FileNotFoundError(
            f"Compose file not found: {compose_pi_hole}. "
            f"Execute `Compose_pi_hole / compose` in "
            f"Dagster to create it."
        )

    session.run(
        *cmd_pi_hole,
        "up",
        "--remove-orphans",
        env=ENV,
        external=True,
    )


# # pi_hole_up_detach
@nox.session(python=None, tags=["pi_hole_up_detach"])
def pi_hole_up_detach(session):
    """
    Start Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session pi_hole_up_detach
    # nox --tags pi_hole_up_detach

    # /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.pi-hole/docker_compose/docker-compose.yml \
    #     --project-name openstudiolandscapes-pi-hole up --remove-orphans --detach

    if not compose_pi_hole.exists():
        raise FileNotFoundError(
            f"Compose file not found: {compose_pi_hole}. "
            f"Execute `Compose_pi_hole / compose` in "
            f"Dagster to create it."
        )

    session.run(
        *cmd_pi_hole,
        "up",
        "--remove-orphans",
        "--detach",
        env=ENV,
        external=True,
    )


# # pi_hole_down
@nox.session(python=None, tags=["pi_hole_down"])
def pi_hole_down(session):
    """
    Start Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session pi_hole_down
    # nox --tags pi_hole_down

    # /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.pi-hole/docker_compose/docker-compose.yml \
    #     --project-name openstudiolandscapes-pi-holw down

    if not compose_pi_hole.exists():
        raise FileNotFoundError(
            f"Compose file not found: {compose_pi_hole}. "
            f"Execute `Compose_pi_hole / compose` in "
            f"Dagster to create it."
        )

    session.run(
        *cmd_pi_hole,
        "down",
        env=ENV,
        external=True,
    )


#######################################################################################################################


#######################################################################################################################
# Harbor

# # ENVIRONMENT
ENVIRONMENT_HARBOR = {
    "HARBOR_HOSTNAME": "harbor.farm.evil",
    "HARBOR_ADMIN": "admin",
    "HARBOR_PASSWORD": "Harbor12345",
    "HARBOR_PORT": 80,
    "HARBOR_RELEASE": [
        "v2.12.2",
        "v2.13.0",
    ][0],
    "HARBOR_INSTALLER": {
        "online": "https://github.com/goharbor/harbor/releases/download/{HARBOR_RELEASE}/harbor-online-installer-{HARBOR_RELEASE}.tgz",
        "offline": "https://github.com/goharbor/harbor/releases/download/{HARBOR_RELEASE}/harbor-offline-installer-{HARBOR_RELEASE}.tgz",
    }["online"],
    "HARBOR_ROOT_DIR": pathlib.Path.cwd() / ".landscapes" / ".harbor",
    "HARBOR_BIN_DIR": "bin",
    "HARBOR_DOWNLOAD_DIR": "download",
    "HARBOR_DATA_DIR": "data",
}


def setup_harbor(
    harbor_download_dir: pathlib.Path,
) -> pathlib.Path:

    file_path: pathlib.Path = download(
        url=f"{ENVIRONMENT_HARBOR['HARBOR_INSTALLER']}".format(
            **ENVIRONMENT_HARBOR,
        ),
        dest_folder=harbor_download_dir,
    )

    logging.info("File successfully downloaded to %s" % file_path.as_posix())

    return file_path


def write_harbor_yml(
    yaml_out: pathlib.Path,
) -> pathlib.Path:

    harbor_root_dir: pathlib.Path = ENVIRONMENT_HARBOR["HARBOR_ROOT_DIR"]
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    harbor_data_dir = harbor_root_dir / ENVIRONMENT_HARBOR["HARBOR_DATA_DIR"]
    harbor_data_dir.mkdir(parents=True, exist_ok=True)

    harbor_dict = {
        "hostname": ENVIRONMENT_HARBOR["HARBOR_HOSTNAME"],
        "http": {"port": ENVIRONMENT_HARBOR["HARBOR_PORT"]},
        "harbor_admin_password": ENVIRONMENT_HARBOR["HARBOR_PASSWORD"],
        "database": {
            "password": "root123",
            "max_idle_conns": 100,
            "max_open_conns": 900,
            "conn_max_idle_time": 0,
        },
        "data_volume": harbor_data_dir.as_posix(),
        "trivy": {
            "ignore_unfixed": False,
            "skip_update": False,
            "skip_java_db_update": False,
            "offline_scan": False,
            "security_check": "vuln",
            "insecure": False,
            "timeout": "5m0s",
        },
        "jobservice": {
            "max_job_workers": 10,
            "job_loggers": ["STD_OUTPUT", "FILE"],
            "logger_sweeper_duration": 1,
        },
        "notification": {
            "webhook_job_max_retry": 3,
            "webhook_job_http_client_timeout": 3,
        },
        "log": {
            "level": "info",
            "local": {
                "rotate_count": 50,
                "rotate_size": "200M",
                "location": "/var/log/harbor",
            },
        },
        "_version": "2.12.0",
        "proxy": {
            "http_proxy": None,
            "https_proxy": None,
            "no_proxy": None,
            "components": ["core", "jobservice", "trivy"],
        },
        "upload_purging": {
            "enabled": True,
            "age": "168h",
            "interval": "24h",
            "dryrun": False,
        },
        "cache": {"enabled": False, "expire_hours": 24},
    }

    logging.debug(
        "Harbor Configuration = %s"
        % json.dumps(
            obj=harbor_dict,
            sort_keys=True,
            indent=2,
        )
    )

    harbor_yml: str = yaml.dump(
        harbor_dict,
        indent=2,
    )

    with open(yaml_out, "w") as fw:
        fw.write(harbor_yml)

    logging.debug("Contents harbor.yml: \n%s" % harbor_yml)

    return yaml_out


# Todo
#  - [x] Maybe we can run prepare in here directly taking into consideration
#        all the variables
#  - [x] Maybe we can create the docker-compose.yml in here directly taking into consideration
#        all the variables

compose_harbor = (
    ENVIRONMENT_HARBOR["HARBOR_ROOT_DIR"]
    / ENVIRONMENT_HARBOR["HARBOR_BIN_DIR"]
    / "docker-compose.yml"
)

cmd_harbor = [
    shutil.which("sudo"),
    shutil.which("docker"),
    "compose",
    "--file",
    compose_harbor.as_posix(),
    "--project-name",
    "openstudiolandscapes-harbor",
]

# # harbor_prepare
@nox.session(python=None, tags=["harbor_prepare"])
def harbor_prepare(session):
    """
    Prepare Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session harbor_prepare
    # nox --tags harbor_prepare

    # /usr/bin/sudo \
    #     /usr/bin/bash
    #     /data/share/nfs/git/repos/OpenStudioLandscapes/OpenStudioLandscapes/.landscapes/.harbor/bin/prepare

    harbor_root_dir: pathlib.Path = ENVIRONMENT_HARBOR["HARBOR_ROOT_DIR"]
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    harbor_bin_dir: pathlib.Path = (
        harbor_root_dir / ENVIRONMENT_HARBOR["HARBOR_BIN_DIR"]
    )
    harbor_bin_dir.mkdir(parents=True, exist_ok=True)

    prepare: pathlib.Path = harbor_bin_dir / "prepare"

    if prepare.exists():
        logging.info(
            "`prepare` already present in. Use that or start fresh by "
            "issuing `nox --session harbor_clear` first."
        )
        return

    harbor_download_dir = harbor_root_dir / ENVIRONMENT_HARBOR["HARBOR_DOWNLOAD_DIR"]
    harbor_download_dir.mkdir(parents=True, exist_ok=True)

    tar_file = setup_harbor(
        harbor_download_dir=harbor_download_dir,
    )

    # equivalent to tar --strip-components=1
    # Credits: https://stackoverflow.com/a/78461535
    strip1 = lambda member, path: member.replace(
        name=pathlib.Path(*pathlib.Path(member.path).parts[1:])
    )

    logging.debug("Extracting tar file...")
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(
            path=harbor_bin_dir,
            filter=strip1,
        )
    logging.debug("All files extracted to %s" % harbor_bin_dir.as_posix())

    harbor_yml: pathlib.Path = write_harbor_yml(
        yaml_out=harbor_bin_dir / "harbor.yml",
    )

    if not harbor_yml.exists():
        raise FileNotFoundError("`harbor.yml` file not found. " "Not able to continue.")

    prepare: pathlib.Path = harbor_bin_dir / "prepare"

    if not prepare.exists():
        raise FileNotFoundError("`prepare` file not found. " "Not able to continue.")

    logging.debug("Preparing Harbor...")
    session.run(
        shutil.which("sudo"),
        shutil.which("bash"),
        prepare.as_posix(),
        env=ENV,
        external=True,
    )


# # harbor_clear
@nox.session(python=None, tags=["harbor_clear"])
def harbor_clear(session):
    """
    Clear Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session harbor_clear
    # nox --tags harbor_clear

    harbor_root_dir: pathlib.Path = ENVIRONMENT_HARBOR["HARBOR_ROOT_DIR"]

    logging.debug("Clearing Harbor...")

    if harbor_root_dir.exists():
        logging.warning("Clearing out Harbor...\n" "Continue? Type `yes` to confirm.")
        answer = input()
        if answer.lower() == "yes":
            session.run(
                shutil.which("sudo"),
                shutil.which("rm"),
                "-rf",
                harbor_root_dir.as_posix(),
                env=ENV,
                external=True,
            )
        else:
            logging.info("Clearing Harbor was aborted.")
            return

    logging.debug("%s removed" % harbor_root_dir.as_posix())


# # Harbor up
@nox.session(python=None, tags=["harbor_up"])
def harbor_up(session):
    """
    Start Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session harbor_up
    # nox --tags harbor_up

    # /usr/bin/sudo \
    #     /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/docker-compose.yml \
    #     --project-name openstudiolandscapes-harbor up --remove-orphans

    session.run(
        *cmd_harbor,
        "up",
        "--remove-orphans",
        env=ENV,
        external=True,
    )


# # Harbor detach
@nox.session(python=None, tags=["harbor_up_detach"])
def harbor_up_detach(session):
    """
    Start Harbor with `sudo` and detach.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session harbor_up_detach
    # nox --tags harbor_up_detach

    # /usr/bin/sudo \
    #     /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/docker-compose.yml \
    #     --project-name openstudiolandscapes-harbor up --remove-orphans --detach

    session.run(
        *cmd_harbor,
        "up",
        "--remove-orphans",
        "--detach",
        env=ENV,
        external=True,
    )


# # Harbor Down
@nox.session(python=None, tags=["harbor_down"])
def harbor_down(session):
    """
    Stop Harbor with `sudo`.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session harbor_down
    # nox --tags harbor_down

    # /usr/bin/sudo \
    #     /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/docker-compose.yml \
    #     --project-name openstudiolandscapes-harbor down

    session.run(
        *cmd_harbor,
        "down",
        env=ENV,
        external=True,
    )


#######################################################################################################################


#######################################################################################################################
# Dagster
# # Dagster MySQL
@nox.session(python=None, tags=["dagster_mysql"])
def dagster_mysql(session):
    """
    Start Dagster with MySQL (default) as backend.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session dagster_mysql
    # nox --tags dagster_mysql

    # cd ~/git/repos/OpenStudioLandscapes
    # source .venv/bin/activate
    # export DAGSTER_HOME="$(pwd)/.dagster"
    # dagster dev --host 0.0.0.0
    session.run(
        shutil.which("dagster"),
        "dev",
        "--host",
        "0.0.0.0",
        env={"DAGSTER_HOME": f"{pathlib.Path.cwd()}/.dagster"},
        external=True,
    )


# # Dagster Postgres
@nox.session(python=None, tags=["dagster_postgres"])
def dagster_postgres(session):
    """
    Start Dagster with Postgres as backend.

    Scope:
    - [x] Engine
    - [ ] Modules
    """
    # Ex:
    # nox --session dagster_postgres
    # nox --tags dagster_postgres

    # docker run \
    #     --name postgres-dagster \
    #     --domainname farm.evil \
    #     --hostname postgres-dagster.farm.evil \
    #     --env POSTGRES_USER=postgres \
    #     --env POSTGRES_PASSWORD=mysecretpassword \
    #     --env POSTGRES_DB=postgres \
    # 	--env PGDATA=/var/lib/postgresql/data/pgdata \
    # 	--volume ./.postgres:/var/lib/postgresql/data \
    # 	--publish 5432:5432 \
    # 	--rm \
    #     docker.io/postgres
    try:
        with session.chdir(".dagster-postgres"):
            session.run(
                shutil.which("docker"),
                "run",
                "--detach",
                "--name",
                "postgres-dagster",
                "--domainname",
                "farm.evil",
                "--hostname",
                "postgres-dagster.farm.evil",
                "--env",
                "POSTGRES_USER=postgres",
                "--env",
                "POSTGRES_PASSWORD=mysecretpassword",
                "--env",
                "POSTGRES_DB=postgres",
                "--env",
                "PGDATA=/var/lib/postgresql/data/pgdata",
                "--volume",
                "./.postgres:/var/lib/postgresql/data",
                "--publish",
                "5432:5432",
                "--rm",
                "docker.io/postgres",
                # env={
                #
                # },
                external=True,
            )
    except Exception as e:
        print(f"PostgreSQL is already running, skipping ({e})")

    # cd ~/git/repos/OpenStudioLandscapes
    # source .venv/bin/activate
    # export DAGSTER_HOME="$(pwd)/.dagster-postgres"
    # dagster dev --host 0.0.0.0
    # with session.chdir(".dagster-postgres"):
    session.run(
        shutil.which("dagster"),
        "dev",
        "--host",
        "0.0.0.0",
        env={"DAGSTER_HOME": f"{pathlib.Path.cwd()}/.dagster-postgres"},
        external=True,
    )


#######################################################################################################################


#######################################################################################################################
# SBOM
@nox.session(python=VERSIONS, tags=["sbom"])
def sbom(session):
    """
    Runs Software Bill of Materials (SBOM).

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session sbom
    # nox --tags sbom

    # https://pypi.org/project/pipdeptree/

    session.install("-e", ".[sbom]")

    target_dir = pathlib.Path(__file__).parent / ".sbom"
    target_dir.mkdir(parents=True, exist_ok=True)

    session.run(
        "cyclonedx-py",
        "environment",
        "--output-format",
        "JSON",
        "--outfile",
        target_dir / f"cyclonedx-py.{session.name}.json",
        env=ENV,
    )

    session.run(
        "bash",
        "-c",
        f"pipdeptree --mermaid > {target_dir}/pipdeptree.{session.name}.mermaid",
        env=ENV,
        external=True,
    )

    session.run(
        "bash",
        "-c",
        f"pipdeptree --graph-output dot > {target_dir}/pipdeptree.{session.name}.dot",
        env=ENV,
        external=True,
    )


#######################################################################################################################


#######################################################################################################################
# Coverage
@nox.session(python=VERSIONS, tags=["coverage"])
def coverage(session):
    """
    Runs coverage

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session coverage
    # nox --tags coverage

    session.install("-e", ".[coverage]")

    session.run(
        "coverage", "run", "--source", "src", "-m", "pytest", "-sv", env=ENV
    )  # ./.coverage
    session.run("coverage", "report")  # report to console
    # session.run("coverage", "json", "-o", ".coverage", "coverage.json")  # report to json
    session.run("coverage", "json", "-o", "coverage.json")  # report to json
    # session.run("coverage", "xml")  # ./coverage.xml
    # session.run("coverage", "html")  # ./htmlcov/


#######################################################################################################################


#######################################################################################################################
# Lint
@nox.session(python=VERSIONS, tags=["lint"])
def lint(session):
    """
    Runs linters and fixers

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session lint
    # nox --tags lint

    session.install("-e", ".[lint]")

    # exclude = [
    #     # Add one line per exclusion:
    #     # "--extend-exclude '^.ext'",
    #     "--extend-exclude", "'^.svg'",
    # ]

    # session.run("black", "src", *exclude, *session.posargs)
    session.run("black", "src", *session.posargs)
    session.run("isort", "--profile", "black", "src", *session.posargs)

    if pathlib.PosixPath(".pre-commit-config.yaml").absolute().exists():
        session.run("pre-commit", "run", "--all-files", *session.posargs)

    # # nox > Command pylint src failed with exit code 30
    # # nox > Session lint-3.12 failed.
    # session.run("pylint", "src")
    # # https://github.com/actions/starter-workflows/issues/2303#issuecomment-1973743119
    session.run("pylint", "--exit-zero", "src")
    # session.run("pylint", "--disable=C0114,C0115,C0116", "--exit-zero", "src")
    # https://stackoverflow.com/questions/7877522/how-do-i-disable-missing-docstring-warnings-at-a-file-level-in-pylint
    # C0114 (missing-module-docstring)
    # C0115 (missing-class-docstring)
    # C0116 (missing-function-docstring)


#######################################################################################################################


#######################################################################################################################
# Testing
@nox.session(python=VERSIONS, tags=["testing"])
def testing(session):
    """
    Runs pytests.

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session testing
    # nox --tags testing

    session.install("-e", ".[testing]", silent=True)

    session.run(
        "pytest",
        *session.posargs,
        env=ENV,
    )


#######################################################################################################################


#######################################################################################################################
# Readme
@nox.session(python=VERSIONS_README, tags=["readme"])
def readme(session):
    """
    Generate dynamically created README file for
    OpenStudioLandscapes modules.

    Scope:
    - [ ] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session readme
    # nox --tags readme

    session.install("-e", ".[readme]", silent=True)

    session.run("generate-readme", "--versions", *VERSIONS)


#######################################################################################################################


#######################################################################################################################
# Release
# Todo
@nox.session(python=VERSIONS, tags=["release"])
def release(session):
    """
    Build and release to a repository

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session release
    # nox --tags release

    session.install("-e", ".[release]")

    session.skip("Not implemented")

    raise NotImplementedError

    # pypi_user: str = os.environ.get("PYPI_USER")
    # pypi_pass: str = os.environ.get("PYPI_PASS")
    # if not pypi_user or not pypi_pass:
    #     session.error(
    #         "Environment variables for release: PYPI_USER, PYPI_PASS are missing!",
    #     )
    # session.run("poetry", "install", external=True)
    # session.run("poetry", "build", external=True)
    # session.run(
    #     "poetry",
    #     "publish",
    #     "-r",
    #     "testpypi",
    #     "-u",
    #     pypi_user,
    #     "-p",
    #     pypi_pass,
    #     external=True,
    # )


#######################################################################################################################


#######################################################################################################################
# Docs
@nox.session(reuse_venv=True, tags=["docs"])
def docs(session):
    """
    Creates Sphinx documentation.

    Scope:
    - [x] Engine
    - [x] Modules
    """
    # Ex:
    # nox --session docs
    # nox --tags docs

    session.install("-e", ".[docs]", silent=True)

    deptree_out = (
        pathlib.Path(__file__).parent
        / "docs"
        / "dot"
        / f"graphviz_pipdeptree.{session.name}.dot"
    )
    deptree_out.parent.mkdir(parents=True, exist_ok=True)

    # Update Dot
    # Reference: /home/michael/git/repos/My-Skeleton-Package/
    session.run(
        "bash",
        "-c",
        f"pipdeptree --graph-output dot > {deptree_out}",
        env=ENV,
        external=True,
    )

    # sphinx-build [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]
    # HTML
    session.run("sphinx-build", "--builder", "html", "docs/", "build/docs")
    # LATEX/PDF
    # session.run("sphinx-build", "--builder", "latex", "docs/", "build/pdf")
    # session.run("make", "-C", "latexmk", "docs/", "build/pdf")

    # Copy images in img to build/docs/_images
    # Relative image paths in md files outside the
    # sphinx project are not compatible out of the box

    # defining source and destination
    # paths
    src = pathlib.Path(__file__).parent / "_images"
    trg = pathlib.Path(__file__).parent / "build" / "docs" / "_images"

    files = os.listdir(src)

    # iterating over all the files in
    # the source directory
    for fname in files:
        # copying the files to the
        # destination directory
        shutil.copy2(src / fname, trg)


#######################################################################################################################


# @nox.session(name="docs-live", tags=["docs-live"])
# def docs_live(session):
#     # nox --session docs_live
#     # nox --tags docs-live
#     session.install("-e", ".[doc]", silent=True)
#     session.run(
#         "sphinx-autobuild", "--builder", "html", "docs/", "build/docs", *session.posargs
#     )
