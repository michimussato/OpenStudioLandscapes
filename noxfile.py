import nox
import pathlib


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
    "sbom",
    "coverage",
    "lint",
    "test",
    "docs",
    # "docs_live",
    # "release",
]

# Python versions to test agains
VERSIONS = [
    "3.9",
    "3.10",
    "3.11",
    "3.12",
]

ENV = {
}


@nox.session(python=VERSIONS, tags=["sbom"])
def sbom(session):
    """Runs Software Bill of Materials (SBOM)."""

    session.install("-e", ".[sbom]")

    target_dir = pathlib.Path().cwd() / ".sbom"
    target_dir.mkdir(parents=True, exist_ok=True)

    # cyclonedx-py environment --output-format JSON --outfile {toxinidir}/.sbom
    session.run(
        "cyclonedx-py",
        "environment",
        "--output-format",
        "JSON",
        "--outfile",
        target_dir / f".cyclonedx-py.{session.name}.json",
        env=ENV,
    )

    session.run(
        "bash",
        "-c",
        f"pipdeptree --mermaid > {target_dir}/.pipdeptree.{session.name}.mermaid",
        env=ENV,
        external=True,
    )

    session.run(
        "bash",
        "-c",
        f"pipdeptree --graph-output dot > {target_dir}/.pipdeptree.{session.name}.dot",
        env=ENV,
        external=True,
    )


@nox.session(python=VERSIONS, tags=["coverage"])
def coverage(session):
    """Runs coverage"""

    session.install("-e", ".[coverage]")

    session.run(
        "coverage", "run", "--source", "src", "-m", "pytest", "-sv", env=ENV
    )  # ./.coverage
    session.run("coverage", "report")  # report to console
    # session.run("coverage", "xml")  # ./coverage.xml
    # session.run("coverage", "html")  # ./htmlcov/


@nox.session(python=VERSIONS, tags=["lint"])
def lint(session):
    """Runs linters and fixers"""

    session.install("-e", ".[lint]")

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


@nox.session(python=VERSIONS, tags=["test"])
def test(session):
    # nox --session test,docs
    # nox --tags docs-live
    session.install("-e", ".[test]", silent=True)

    session.run(
        "pytest",
        *session.posargs,
        env=ENV,
    )


@nox.session(python=VERSIONS, tags=["release"])
def release(session):
    """Build and release to a repository"""
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


@nox.session(reuse_venv=True, tags=["docs"])
def docs(session):
    # nox --session docs
    # nox --tags docs
    session.install("-e", ".[docs]", silent=True)

    # Update Dot
    session.run(
        "bash",
        "-c",
        f"pipdeptree --graph-output dot > docs/graphviz_example_pipdeptree.{session.name}.dot",
        env=ENV,
        external=True,
    )

    # sphinx-build [OPTIONS] SOURCEDIR OUTPUTDIR [FILENAMES...]
    # HTML
    session.run("sphinx-build", "--builder", "html", "docs/", "build/docs")
    # LATEX/PDF
    # session.run("sphinx-build", "--builder", "latex", "docs/", "build/pdf")
    # session.run("make", "-C", "latexmk", "docs/", "build/pdf")


# @nox.session(name="docs-live", tags=["docs-live"])
# def docs_live(session):
#     # nox --session docs_live
#     # nox --tags docs-live
#     session.install("-e", ".[doc]", silent=True)
#     session.run(
#         "sphinx-autobuild", "--builder", "html", "docs/", "build/docs", *session.posargs
#     )
