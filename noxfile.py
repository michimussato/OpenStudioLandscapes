import shutil
import os
import nox
import pathlib


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
# Harbor
# # Harbor up
@nox.session(python=None, tags=["harbor_up"])
def harbor_up(session):
    """
    Start Harbor with `sudo`.
    """
    # Ex:
    # nox --session harbor_up
    # nox --tags harbor_up

    # /usr/bin/sudo \
    #     /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/docker-compose.yml \
    #     --project-name openstudiolandscapes-harbor up --remove-orphans

    compose = (
        pathlib.Path.cwd() / ".landscapes" / ".harbor" / "bin" / "docker-compose.yml"
    )

    session.run(
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        compose.as_posix(),
        "--project-name",
        "openstudiolandscapes-harbor",
        "up",
        "--remove-orphans",
        env=ENV,
        external=True,
    )


# # Harbor Down
@nox.session(python=None, tags=["harbor_down"])
def harbor_down(session):
    """
    Stop Harbor with `sudo`.
    """
    # Ex:
    # nox --session harbor_down
    # nox --tags harbor_down

    # /usr/bin/sudo \
    #     /usr/bin/docker \
    #     compose \
    #     --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/docker-compose.yml \
    #     --project-name openstudiolandscapes-harbor down

    compose = (
        pathlib.Path.cwd() / ".landscapes" / ".harbor" / "bin" / "docker-compose.yml"
    )

    session.run(
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        compose.as_posix(),
        "--project-name",
        "openstudiolandscapes-harbor",
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
    """
    # Ex:
    # nox --session dagster_mysql
    # nox --tags dagster_mysql

    # cd ~/git/repos/OpenStudioLandscapes
    # source .venv/bin/activate
    # export DAGSTER_HOME="$(pwd)/.dagster"
    # dagster dev
    session.run(
        shutil.which("dagster"),
        "dev",
        env={"DAGSTER_HOME": f"{pathlib.Path.cwd()}/.dagster"},
        external=True,
    )


# # Dagster Postgres
@nox.session(python=None, tags=["dagster_postgres"])
def dagster_postgres(session):
    """
    Start Dagster with Postgres as backend.
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
    # dagster dev
    # with session.chdir(".dagster-postgres"):
    session.run(
        shutil.which("dagster"),
        "dev",
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
