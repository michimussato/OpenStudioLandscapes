import shlex
import shutil
import os
import tempfile

from dotenv import load_dotenv

import git
import nox
import re
import pathlib
import requests
import logging
import platform
from typing import Tuple

import yaml

logging.basicConfig(level=logging.DEBUG)


try:
    load_dotenv(dotenv_path=".env")
except Exception as e:
    logging.error(f"Unable to load .env file: {e}")


DOCKER_PROGRESS = [
    "auto",
    "quiet",
    "plain",
    "tty",
    "rawjson",
][2]

USE_TEMP_DIR = False


def _get_terminal_size() -> Tuple[int, int]:
    # https://stackoverflow.com/a/14422538
    # https://stackoverflow.com/a/18243550
    cols, rows = shutil.get_terminal_size((80, 20))
    return cols, rows


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


# nox Configuration & API
# https://nox.thea.codes/en/stable/config.html
# # nox.sessions.Session.run
# https://nox.thea.codes/en/stable/config.html#nox.sessions.Session.run


# https://www.youtube.com/watch?v=ImBvrDvK-1U&ab_channel=HynekSchlawack
# https://codewitholi.com/_posts/python-nox-automation/


# reuse_existing_virtualenvs:
# global: nox.options.reuse_existing_virtualenvs = True
nox.options.reuse_existing_virtualenvs = False
# per session: @nox.session(reuse_venv=True)
if USE_TEMP_DIR:
    temp_dir = tempfile.mkdtemp()
    print("Using temporary directory: %s" % temp_dir)
    nox.options.envdir = temp_dir

SESSION_INSTALL_SILENT = False
SESSION_RUN_SILENT = False

# default sessions when none is specified
# nox --session [SESSION] [SESSION] [...]
# or
# nox --tag [TAG] [TAG] [...]
nox.options.sessions = [
    "coverage",  # Todo
    "pyproject_engine",
    "pyproject_features",
    "sbom",
    "lint",
    "readme",
    "release",  # Todo
    "testing",  # Todo
]

BATCH_EXCLUDED = []

# Python versions to test against
# dagster==1.9.11 needs >=3.9 but 3.13 does not seem to be working
PYTHON_TEST_VERSIONS = [
    "3.11",
    # "3.12",
    # "3.13",
]

PYTHON_VERSION_MAIN = PYTHON_TEST_VERSIONS[0]

ENV = {}


GIT_MAIN_BRANCH = "main"


# Semantic Versioning
# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
# RE_SEMVER = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
RE_SEMVER = re.compile(
    r"^(?P<major>0|v[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


#######################################################################################################################
# Parameterized Features
engine_dir: pathlib.Path = pathlib.Path(__file__).parent
features_dir: pathlib.Path = engine_dir / ".features"
landscapes_dir: pathlib.Path = engine_dir / ".landscapes"
FEATURES_PARAMETERIZED: list[pathlib.Path] = []

for dir_ in features_dir.iterdir():
    # dir_ is always the full path
    if any(dir_.name == i for i in BATCH_EXCLUDED):
        logging.info(f"Skipped: {dir_ = }")
        continue
    if dir_.is_dir():
        if pathlib.Path(dir_ / ".git").exists():
            FEATURES_PARAMETERIZED.append(dir_.relative_to(engine_dir.parent))


#######################################################################################################################
# Feature Template
# Todo:
#  - [ ] Maybe create a Feature from Template via `nox`?


#######################################################################################################################


#######################################################################################################################
# Git

# # REPOSITORY ENGINE

REPO_ENGINE = "OpenStudioLandscapes"


# # REPOSITORIES FEATURES
REPOS_FEATURE = {
    "OpenStudioLandscapes-Ayon": "https://github.com/michimussato/OpenStudioLandscapes-Ayon.git",
    "OpenStudioLandscapes-Dagster": "https://github.com/michimussato/OpenStudioLandscapes-Dagster.git",
    "OpenStudioLandscapes-Kitsu": "https://github.com/michimussato/OpenStudioLandscapes-Kitsu.git",
}

# # MAIN BRANCH
MAIN_BRANCH = "main"

# # clone_features
@nox.session(python=None, tags=["clone_features"])
def clone_features(session):
    """
    `git clone` all listed (REPOS_FEATURE) Features into .features.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Todo
    #  - [ ] create pull_features() session?

    # Could be more elegant:
    # openstudiolandscapes-engine           | Traceback (most recent call last):
    # openstudiolandscapes-engine           |   File "/home/openstudiolandscapes/mount/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/nox/sessions.py", line 1101, in execute
    # openstudiolandscapes-engine           |     self.func(session)
    # openstudiolandscapes-engine           |   File "/home/openstudiolandscapes/mount/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/nox/_decorators.py", line 94, in __call__
    # openstudiolandscapes-engine           |     return self.func(*args, **kwargs)
    # openstudiolandscapes-engine           |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
    # openstudiolandscapes-engine           |   File "/home/openstudiolandscapes/mount/git/repos/OpenStudioLandscapes/noxfile.py", line 244, in clone_features
    # openstudiolandscapes-engine           |     raise FileExistsError(
    # openstudiolandscapes-engine           | FileExistsError: The repo /home/openstudiolandscapes/mount/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Ayon already exists. Please remove it before cloning.
    # openstudiolandscapes-engine           | nox > Session clone_features failed

    # Ex:
    # nox --session clone_features
    # nox --tags clone_features

    # git -C .features clone https://github.com/michimussato/OpenStudioLandscapes-<Feature>

    # Todo
    #  - [ ] sync OPENSTUDIOLANDSCAPES_VERSION_TAG with make

    repo = git.Repo(engine_dir)

    # git fetch --tags --all
    repo.git.fetch(tags=True, all=True, force=True)

    input_message = "Checkout branch:\n"

    tag_or_branch = menu_from_choices(
        input_message=input_message,
        choices=[
            "Tag",
            "Branch",
        ],
        description="",
        manual_value=True,
    )

    checkout = None

    if tag_or_branch == "Tag":

        tags = repo.tags

        tag_ = os.environ.get("TAG", None)
        if tag_ is None:
            input_message = "Checkout tag:\n"

            tag_ = menu_from_choices(
                input_message=input_message,
                choices=tags,
                description="",
                manual_value=True,
            )

            os.environ["TAG"] = tag_

        checkout = tag_

    elif tag_or_branch == "Branch":

        branches = repo.branches

        branch_ = os.environ.get("BRANCH", None)
        if branch_ is None:
            input_message = "Checkout branch:\n"

            branch_ = menu_from_choices(
                input_message=input_message,
                choices=branches,
                description="",
                manual_value=True,
            )

            os.environ["BRANCH"] = branch_

        checkout = branch_

    # OPENSTUDIOLANDSCAPES_VERSION_TAG: str = os.environ.get(
    #     "OPENSTUDIOLANDSCAPES_VERSION_TAG", None
    # )
    #
    # if OPENSTUDIOLANDSCAPES_VERSION_TAG is None:
    #     print(
    #         f"OPENSTUDIOLANDSCAPES_VERSION_TAG is not set, checking out {MAIN_BRANCH} branch."
    #     )

    sudo = False

    for name, repo in REPOS_FEATURE.items():

        logging.info("Cloning %s" % name)

        # Todo
        #  - [ ] git clone fatal if directory exists

        # if cd repo; then git pull; else git clone https://server/repo repo; fi

        repo_dest = pathlib.Path.cwd() / ".features" / name

        if repo_dest.exists():
            # Update the repository
            cmd_clone = [
                shutil.which("git"),
                "-C",
                repo_dest.parent.as_posix(),
                "pull",
                "--tags",
                "--force",
                repo,
            ]

        else:
            logging.info("Cloning %s" % name)

            # Clone the repository
            cmd_clone = [
                shutil.which("git"),
                "-C",
                repo_dest.parent.as_posix(),
                "clone",
                "--tags",
                repo,
            ]

        # if OPENSTUDIOLANDSCAPES_VERSION_TAG is not None:
        # Checkout a specific Git tag or branch
        cmd_checkout = [
            shutil.which("git"),
            "-C",
            repo_dest.as_posix(),
            "checkout",
            "--force",
            {
                "Tag": f"tags/{checkout}",
                "Branch": f"origin/{checkout}",
            }[tag_or_branch],
            "-B",
            checkout,
        ]

        if sudo:
            cmd_clone.insert(0, shutil.which("sudo"))
            cmd_clone.insert(1, "--reset-timestamp")

            # if OPENSTUDIOLANDSCAPES_VERSION_TAG is not None:
            #     cmd_checkout.insert(0, shutil.which("sudo"))
            #     cmd_checkout.insert(1, "--reset-timestamp")

        logging.info(f"{cmd_clone = }")

        session.run(
            *cmd_clone,
            external=True,
            silent=SESSION_RUN_SILENT,
        )

        # if OPENSTUDIOLANDSCAPES_VERSION_TAG is not None:

        logging.info(f"{cmd_checkout = }")

        session.run(
            *cmd_checkout,
            external=True,
            silent=SESSION_RUN_SILENT,
        )


# # # pull_features
# @nox.session(python=None, tags=["pull_features"])
# def pull_features(session):
#     """
#     `git pull` all listed (REPOS_FEATURE) Features.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session pull_features
#     # nox --tags pull_features
#
#     for name, repo in REPOS_FEATURE.items():
#
#         logging.info("Pulling %s" % name)
#
#         session.run(
#             shutil.which("git"),
#             "-C",
#             pathlib.Path.cwd() / ".features" / name,
#             "pull",
#             "--verbose",
#             "origin",
#             MAIN_BRANCH,
#             "--rebase=true",
#             "--tags",
#             external=True,
#         )


# # # stash_features
# @nox.session(python=None, tags=["stash_features"])
# def stash_features(session):
#     """
#     `git stash` all listed (REPOS_FEATURE) Features.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session stash_features
#     # nox --tags stash_features
#
#     sudo = False
#
#     for name, repo in REPOS_FEATURE.items():
#
#         logging.info("Stashing %s" % name)
#
#         cmd = [
#             shutil.which("git"),
#             "-C",
#             pathlib.Path.cwd() / ".features" / name,
#             "stash",
#         ]
#
#         if sudo:
#             cmd.insert(0, shutil.which("sudo"))
#             cmd.insert(1, "--reset-timestamp")
#             # cmd.insert(2, "--stdin")
#
#         logging.info(f"{cmd = }")
#
#         session.run(
#             *cmd,
#             external=True,
#             silent=SESSION_RUN_SILENT,
#         )


# # # stash_apply_features
# @nox.session(python=None, tags=["stash_apply_features"])
# def stash_apply_features(session):
#     """
#     `git stash apply` all listed (REPOS_FEATURE) Features.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session stash_apply_features
#     # nox --tags stash_apply_features
#
#     sudo = False
#
#     for name, repo in REPOS_FEATURE.items():
#
#         logging.info("Stashing %s" % name)
#
#         cmd = [
#             shutil.which("git"),
#             "-C",
#             pathlib.Path.cwd() / ".features" / name,
#             "stash",
#             "apply",
#         ]
#
#         if sudo:
#             cmd.insert(0, shutil.which("sudo"))
#             cmd.insert(1, "--reset-timestamp")
#             # cmd.insert(2, "--stdin")
#
#         logging.info(f"{cmd = }")
#
#         session.run(
#             *cmd,
#             external=True,
#             silent=SESSION_RUN_SILENT,
#         )


# # # pull_engine
# @nox.session(python=None, tags=["pull_engine"])
# def pull_engine(session):
#     """
#     `git pull` engine.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session pull_engine
#     # nox --tags pull_engine
#
#     sudo = False
#
#     logging.info("Pulling %s" % REPO_ENGINE)
#
#     cmd = [
#         shutil.which("git"),
#         "pull",
#         "--verbose",
#         "origin",
#         MAIN_BRANCH,
#         "--rebase=true",
#         "--tags",
#     ]
#
#     if sudo:
#         cmd.insert(0, shutil.which("sudo"))
#         cmd.insert(1, "--reset-timestamp")
#         # cmd.insert(2, "--stdin")
#
#     logging.info(f"{cmd = }")
#
#     session.run(
#         *cmd,
#         external=True,
#         silent=SESSION_RUN_SILENT,
#     )


# # # stash_engine
# @nox.session(python=None, tags=["stash_engine"])
# def stash_engine(session):
#     """
#     `git stash` engine.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session stash_engine
#     # nox --tags stash_engine
#
#     sudo = False
#
#     logging.info("Stashing %s" % REPO_ENGINE)
#
#     cmd = [
#         shutil.which("git"),
#         "stash",
#     ]
#
#     if sudo:
#         cmd.insert(0, shutil.which("sudo"))
#         cmd.insert(1, "--reset-timestamp")
#         # cmd.insert(2, "--stdin")
#
#     logging.info(f"{cmd = }")
#
#     session.run(
#         *cmd,
#         external=True,
#         silent=SESSION_RUN_SILENT,
#     )


# # # stash_apply_engine
# @nox.session(python=None, tags=["stash_apply_engine"])
# def stash_apply_engine(session):
#     """
#     `git stash apply` engine.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session stash_apply_engine
#     # nox --tags stash_apply_engine
#
#     sudo = False
#
#     logging.info("Stashing %s" % REPO_ENGINE)
#
#     cmd = [
#         shutil.which("git"),
#         "stash",
#         "apply",
#     ]
#
#     if sudo:
#         cmd.insert(0, shutil.which("sudo"))
#         cmd.insert(1, "--reset-timestamp")
#         # cmd.insert(2, "--stdin")
#
#     logging.info(f"{cmd = }")
#
#     session.run(
#         *cmd,
#         external=True,
#         silent=SESSION_RUN_SILENT,
#     )


#######################################################################################################################


#######################################################################################################################
# venv

# This will probably not work...
# we can't run `nox` before the `venv` is even
# present in the first place.

# # # create_venv_engine
# @nox.session(python=None, tags=["create_venv_engine"])
# def create_venv_engine(session):
#     """
#     Create a `venv` after cloning OpenStudioLandscapes engine and install
#     the package into it.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session create_venv_engine
#     # nox --tags create_venv_engine
#
#     session.run(
#         shutil.which("python3.11"),
#         "-m",
#         "venv",
#         ".venv",
#         external=True,
#     )
#
#     session.run(
#         ".venv/bin/python",
#         "-m",
#         "pip",
#         "install",
#         "--upgrade",
#         "pip",
#         "setuptools",
#         external=True,
#     )
#
#     session.run(
#         ".venv/bin/python",
#         "-m",
#         "pip",
#         "install",
#         "--editable",
#         ".[dev]",
#         external=True,
#     )


# # create_venv_features
@nox.session(python=None, tags=["create_venv_features"])
def create_venv_features(session):
    """
    Create a `venv`s in .features/<Feature> after `nox --session clone_features` and installing the Feature into its own `.venv`.

    ```
    cd .features/<Feature>
    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session create_venv_features
    # nox --tags create_venv_features

    sudo = False

    features_dir = pathlib.Path.cwd() / ".features"

    for dir_ in features_dir.iterdir():
        # dir_ is always the full path
        if dir_.is_dir():
            if pathlib.Path(dir_ / ".git").exists():
                with session.chdir(dir_):

                    cmd1 = [
                        shutil.which("python3.11"),
                        "-m",
                        "venv",
                        ".venv",
                    ]

                    if sudo:
                        cmd1.insert(0, shutil.which("sudo"))
                        cmd1.insert(1, "--reset-timestamp")
                        # cmd.insert(2, "--stdin")

                    logging.info(f"{cmd1 = }")

                    session.run(
                        *cmd1,
                        external=True,
                        silent=SESSION_RUN_SILENT,
                    )

                    cmd2 = [
                        ".venv/bin/python",
                        "-m",
                        "pip",
                        "install",
                        "--upgrade",
                        "pip",
                        "setuptools",
                    ]

                    if sudo:
                        cmd2.insert(0, shutil.which("sudo"))
                        cmd2.insert(1, "--reset-timestamp")
                        # cmd.insert(2, "--stdin")

                    logging.info(f"{cmd2 = }")

                    session.run(
                        *cmd2,
                        external=True,
                        silent=SESSION_RUN_SILENT,
                    )

                    cmd3 = [
                        ".venv/bin/python",
                        "-m",
                        "pip",
                        "install",
                        "--editable",
                        ".[dev]",
                    ]

                    if sudo:
                        cmd3.insert(0, shutil.which("sudo"))
                        cmd3.insert(1, "--reset-timestamp")
                        # cmd.insert(2, "--stdin")

                    logging.info(f"{cmd3 = }")

                    session.run(
                        *cmd3,
                        external=True,
                        silent=SESSION_RUN_SILENT,
                    )


# # install_features_into_engine
@nox.session(python=None, tags=["install_features_into_engine"])
def install_features_into_engine(session):
    """
    Installs the Features after `nox --session clone_features` into the engine `.venv`.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session install_features_into_engine
    # nox --tags install_features_into_engine

    # Todo:
    #  - [ ] option to install local package instead of
    #        being limited to install from Github
    #        `for i in .features/*; do pip install --editable "$(pwd)/${i}[dev]"; done; pip install --editable ".[dev]"`

    sudo = False

    features_dir = pathlib.Path.cwd() / ".features"

    session.run(
        ".venv/bin/python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        # "--force-reinstall",
        "pip",
        "setuptools",
        external=True,
        silent=SESSION_RUN_SILENT,
    )

    for dir_ in features_dir.iterdir():
        # dir_ is always the full path
        if dir_.is_dir():
            if pathlib.Path(dir_ / ".git").exists():
                logging.info("Installing features from %s" % dir_)

                cmd = [
                    ".venv/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "--editable",
                    f"{dir_}[dev]",
                ]

                if sudo:
                    cmd.insert(0, shutil.which("sudo"))
                    cmd.insert(1, "--reset-timestamp")
                    # cmd.insert(2, "--stdin")

                logging.info(f"{cmd = }")

                session.run(
                    *cmd,
                    external=True,
                    silent=SESSION_RUN_SILENT,
                )


#######################################################################################################################


#######################################################################################################################
# Hard Links

LINKED_FILES = [
    ".obsidian/plugins/obsidian-excalidraw-plugin/main.js",
    ".obsidian/plugins/obsidian-excalidraw-plugin/manifest.json",
    ".obsidian/plugins/obsidian-excalidraw-plugin/styles.css",
    ".obsidian/plugins/templater-obsidian/data.json",
    ".obsidian/plugins/templater-obsidian/main.js",
    ".obsidian/plugins/templater-obsidian/manifest.json",
    ".obsidian/plugins/templater-obsidian/styles.css",
    ".obsidian/app.json",
    ".obsidian/appearance.json",
    ".obsidian/canvas.json",
    ".obsidian/community-plugins.json",
    ".obsidian/core-plugins.json",
    ".obsidian/core-plugins-migration.json",
    ".obsidian/daily-notes.json",
    ".obsidian/graph.json",
    # ".obsidian/hotkeys.json",
    ".obsidian/templates.json",
    ".obsidian/types.json",
    # ".obsidian/workspace.json",
    # ".obsidian/workspaces.json",
    ".gitattributes",
    ".sbom/.gitkeep",
    ".payload/bin/.gitkeep",
    ".payload/config/.gitkeep",
    ".payload/data/.gitkeep",
    "media/images/.gitkeep",
    ".gitignore",
    ".pre-commit-config.yaml",
    "noxfile.py",
    "LICENSE.txt",
]

# # fix_hardlinks_in_features
@nox.session(python=None, tags=["fix_hardlinks_in_features"])
def fix_hardlinks_in_features(session):
    """
    See https://github.com/michimussato/OpenStudioLandscapes?tab=readme-ov-file#hard-links-sync-files-and-directories-across-repositories-de-duplication

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session fix_hardlinks_in_features
    # nox --tags fix_hardlinks_in_features

    # ln -f ../../../OpenStudioLandscapes/noxfile.py  noxfile.py

    sudo = False

    cwd = pathlib.Path.cwd()
    features_dir = cwd / ".features"

    for dir_ in features_dir.iterdir():
        # dir_ is always the full path
        if dir_.is_dir():
            if pathlib.Path(dir_ / ".git").exists():
                for file_ in LINKED_FILES:

                    file_ = pathlib.Path(file_)

                    file_path = file_.parent
                    link_name = file_.name

                    with session.chdir(dir_ / file_path):

                        logging.info(
                            "Working director is %s" % pathlib.Path.cwd().as_posix()
                        )

                        logging.info("Fixing hardlink for file %s" % file_)

                        # Target can be absolute
                        target = pathlib.Path(cwd / file_)

                        logging.info("Target: %s" % target.as_posix())
                        logging.info("Link name: %s" % link_name)

                        if platform.system() == "Linux":

                            cmd = [
                                shutil.which("ln"),
                                "--force",
                                "--backup=numbered",
                                target.as_posix(),
                                link_name,
                            ]

                        elif platform.system() == "Darwin":

                            cmd = [
                                shutil.which("ln"),
                                "-f",
                                target.as_posix(),
                                link_name,
                            ]

                        if sudo:
                            cmd.insert(0, shutil.which("sudo"))
                            cmd.insert(1, "--reset-timestamp")
                            # cmd.insert(2, "--stdin")

                        logging.info(f"{cmd = }")

                        session.run(
                            *cmd,
                            external=True,
                            silent=SESSION_RUN_SILENT,
                        )


#######################################################################################################################


#######################################################################################################################
# Dagster

# # ENVIRONMENT
ENVIRONMENT_DAGSTER = {
    # Todo:
    #  - [ ] maybe better to source .env instead of hardcoding these values
    "OPENSTUDIOLANDSCAPES__DOMAIN_LAN": os.environ["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"],
    # Todo:
    #  - [ ] move these two into `.landscapes`
    "DAGSTER_POSTGRES_ROOT_DIR": pathlib.Path.cwd() / ".dagster-postgres",
    "DAGSTER_MYSQL_ROOT_DIR": pathlib.Path.cwd() / ".dagster",
    "DAGSTER_POSTGRES_DB_DIR_DIR": ".postgres",
    "DAGSTER_POSTGRES_DB_USERNAME": "postgres",
    "DAGSTER_POSTGRES_DB_PASSWORD": "mysecretpassword",
    "DAGSTER_POSTGRES_DB_NAME": "postgres",
    "DAGSTER_POSTGRES_DB_PORT_CONTAINER": 5432,
    # Make sure DAGSTER_POSTGRES_DB_PORT_HOST does not clash with other Postgres instances (i.e. OpenCue)
    #
    # - kitsu-init-db--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39                          |    ...done.
    #   kitsu-init-db--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39                          | Stopping redis-server: redis-server.
    #   syncthing--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39                              | [YVSC6] 2025/04/24 14:56:11 INFO: Failed to acquire [::]:22000/TCP open port on NAT-PMP@172.27.0.1: getting new lease on NAT-PMP@172.27.0.1 (external port 35113 -> internal port 22000): read udp 172.27.0.2:48310->172.27.0.1:5351: recvfrom: connection refused
    #   syncthing--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39                              | [YVSC6] 2025/04/24 14:56:11 INFO: Detected 1 NAT service
    #   kitsu-init-db--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39 exited with code 0
    #   Gracefully stopping... (press Ctrl+C again to force)
    #   Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint opencue-db (b0598f47d9cf106a2cabb934f07e7f4a732aac61c298c9a54bd1bc8081fa0a1a): Bind for 0.0.0.0:5432 failed: port is already allocated
    # - repository-installer-10-2--2025-04-24-16-22-05-ec4f3f438cfa4f2bb252e83f78356a39 exited with code 0
    #   Gracefully stopping... (press Ctrl+C again to force)
    #   Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint opencue-db (c779b0000eddcd26175adb69cc4e405131ce93f8a37825c7386e47dba9eb92ed): Bind for 0.0.0.0:5432 failed: port is already allocated
    "DAGSTER_POSTGRES_DB_PORT_HOST": 2345,
}

yml_dagster_postgres = ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_ROOT_DIR"] / "dagster.yaml"
compose_dagster_postgres = (
    ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_ROOT_DIR"] / "docker-compose.yml"
)

SERVICE_NAME_DAGSTER = "openstudiolandscapes-dagster"
SERVICE_NAME_DAGSTER_POSTGRES = "openstudiolandscapes-dagster-postgres"

HOSTNAME_DAGSTER_DEV = (
    [
        # For Dagster to be accessible via Pangolin, use
        # 0.0.0.0
        "0.0.0.0",  # respond to requests from everywhere
        "127.0.0.1",  # respond to requests from localhost
        f"{SERVICE_NAME_DAGSTER}.{ENVIRONMENT_DAGSTER['OPENSTUDIOLANDSCAPES__DOMAIN_LAN']}",  # also only responds to limited sources
    ][0]
)
HOSTNAME_DAGSTER_POSTGRES = f"{SERVICE_NAME_DAGSTER_POSTGRES}.{ENVIRONMENT_DAGSTER['OPENSTUDIOLANDSCAPES__DOMAIN_LAN']}"

cmd_dagster_dev = [
    shutil.which("dagster"),
    "dev",
    "--host",
    HOSTNAME_DAGSTER_DEV,
]

cmd_dagster_postgres = [
    shutil.which("docker"),
    "compose",
    "--progress",
    DOCKER_PROGRESS,
    "--file",
    compose_dagster_postgres.as_posix(),
    "--project-name",
    "openstudiolandscapes-dagster-postgres",
]


def write_dagster_postgres_yml(
    # yaml_out: pathlib.Path,
) -> pathlib.Path:

    # Example:
    # https://github.com/docker-library/docs/blob/master/postgres/README.md#-via-docker-compose-or-docker-stack-deploy

    dagster_postgres_root_dir: pathlib.Path = ENVIRONMENT_DAGSTER[
        "DAGSTER_POSTGRES_ROOT_DIR"
    ]
    dagster_postgres_root_dir.mkdir(parents=True, exist_ok=True)

    service_name = "openstudiolandscapes-dagster-postgres"
    # network_name = service_name
    # container_name = service_name
    host_name = ".".join(
        [service_name, ENVIRONMENT_DAGSTER["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]]
    )

    # https://docs.dagster.io/guides/limiting-concurrency-in-data-pipelines
    dagster_postgres_dict = {
        "run_queue": {
            "max_concurrent_runs": 1,
            "block_op_concurrency_limited_runs": {
                "enabled": True,
            },
        },
        "telemetry": {
            "enabled": False,
        },
        "auto_materialize": {
            "enabled": True,
            "use_sensors": True,
        },
        "storage": {
            "postgres": {
                "postgres_db": {
                    "username": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_USERNAME"],
                    "password": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_PASSWORD"],
                    "hostname": host_name,
                    "db_name": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_NAME"],
                    # Todo:
                    #  - [ ] Which one is it?
                    # "port": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_PORT_CONTAINER"],
                    "port": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_PORT_HOST"],
                },
            },
        },
        # run_monitoring:
        #  enabled: true
        #  free_slots_after_run_end_seconds: 300
        # concurrency:
        #  default_op_concurrency_limit: 1
    }

    dagster_postgres_yml: str = yaml.dump(
        dagster_postgres_dict,
        indent=2,
    )

    with open(yml_dagster_postgres.as_posix(), "w") as fw:
        fw.write(dagster_postgres_yml)

    logging.debug(
        "Contents Dagster-Postgres `dagster.yaml`: \n%s" % dagster_postgres_yml
    )

    return yml_dagster_postgres


def write_dagster_postgres_compose() -> pathlib.Path:

    dagster_postgres_root_dir: pathlib.Path = ENVIRONMENT_DAGSTER[
        "DAGSTER_POSTGRES_ROOT_DIR"
    ]
    dagster_postgres_root_dir.mkdir(parents=True, exist_ok=True)

    dagster_postgres_db_dir: pathlib.Path = (
        dagster_postgres_root_dir / ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_DIR_DIR"]
    )
    dagster_postgres_db_dir.mkdir(parents=True, exist_ok=True)

    service_name = SERVICE_NAME_DAGSTER_POSTGRES
    network_name = service_name
    container_name = service_name
    host_name = HOSTNAME_DAGSTER_POSTGRES

    dagster_postgres_dict = {
        "networks": {
            network_name: {
                "name": f"network_{network_name}",
            },
        },
        "services": {
            service_name: {
                "container_name": container_name,
                "hostname": host_name,
                "domainname": ENVIRONMENT_DAGSTER["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"],
                "restart": "unless-stopped",
                # Using "latest" (+18), the following issue occured:
                # Container postgres-dagster  Starting
                # Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/home/user/git/repos/OpenStudioLandscapes/.dagster-postgres/.postgres" to rootfs at "/var/lib/postgresql/data": change mount propagation through procfd: open o_path procfd: open /var/lib/docker/overlay2/ba0ae2dde0bc547b16a339100ed558b2e787a297fe9f3df37668223a2ad5433e/merged/var/lib/postgresql/data: no such file or directory: unknown
                #
                # Todo: check Postgres compatibility
                #  - [ ] 16 (seems fine - stay with this one for now to be safe)
                #  - [x] 17 This was the default before;
                #  - [ ] 18
                "image": "docker.io/postgres:17",
                "volumes": [
                    f"{dagster_postgres_db_dir.as_posix()}:/var/lib/postgresql/data:rw",
                ],
                "networks": [network_name],
                "ports": [
                    f"{ENVIRONMENT_DAGSTER['DAGSTER_POSTGRES_DB_PORT_HOST']}:{ENVIRONMENT_DAGSTER['DAGSTER_POSTGRES_DB_PORT_CONTAINER']}",
                ],
                "environment": {
                    "POSTGRES_USER": ENVIRONMENT_DAGSTER[
                        "DAGSTER_POSTGRES_DB_USERNAME"
                    ],
                    "POSTGRES_PASSWORD": ENVIRONMENT_DAGSTER[
                        "DAGSTER_POSTGRES_DB_PASSWORD"
                    ],
                    "POSTGRES_DB": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_DB_NAME"],
                    "PGDATA": "/var/lib/postgresql/data/pgdata",
                },
                # "healthcheck": {
                # },
                # "command": [
                # ],
            },
        },
    }

    dagster_postgres_yml: str = yaml.dump(
        dagster_postgres_dict,
        indent=2,
    )

    with open(compose_dagster_postgres.as_posix(), "w") as fw:
        fw.write(dagster_postgres_yml)

    logging.debug(
        "Contents Dagster-Postgres `docker-compose.yml`: \n%s" % dagster_postgres_yml
    )

    return compose_dagster_postgres


#######################################################################################################################
# # Dagster Postgres

# # dagster_postgres_up
@nox.session(python=None, tags=["dagster_postgres_up"])
def dagster_postgres_up(session):
    """
    Start Postgres backend for Dagster in attached mode.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_postgres_up
    # nox --tags dagster_postgres_up

    sudo = False

    write_dagster_postgres_yml()
    write_dagster_postgres_compose()

    cmd = [
        *cmd_dagster_postgres,
        "up",
        "--remove-orphans",
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    logging.info(f"{cmd = }")

    session.run(
        *cmd,
        env=ENV,
        external=True,
        silent=SESSION_RUN_SILENT,
    )


# # dagster_postgres_clear
@nox.session(python=None, tags=["dagster_postgres_clear"])
def dagster_postgres_clear(session):
    """
    Clear Dagster-Postgres with `sudo`. WARNING: DATA LOSS!

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_postgres_clear
    # nox --tags dagster_postgres_clear

    sudo = True

    dagster_postgres_root_dir: pathlib.Path = ENVIRONMENT_DAGSTER[
        "DAGSTER_POSTGRES_ROOT_DIR"
    ]

    logging.debug("Clearing Dagster-Postgres...")
    logging.debug("Removing Dir %s" % dagster_postgres_root_dir.as_posix())

    cmd = [
        shutil.which("git"),
        "clean",
        "-x",
        "--force",
        dagster_postgres_root_dir.as_posix(),
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    if dagster_postgres_root_dir.exists():
        logging.warning(
            "Clearing out Dagster-Postgres...\nContinue? Type `yes` to confirm."
        )
        answer = input()
        if answer.lower() == "yes":

            logging.info(f"{cmd = }")

            session.run(
                *cmd,
                env=ENV,
                external=True,
                silent=SESSION_RUN_SILENT,
            )
        else:
            logging.info(
                "Clearing %s was aborted." % dagster_postgres_root_dir.as_posix()
            )
            return 1

    logging.debug("%s removed" % dagster_postgres_root_dir.as_posix())

    return 0


# # dagster_postgres_up_detach
@nox.session(python=None, tags=["dagster_postgres_up_detach"])
def dagster_postgres_up_detach(session):
    """
     Start Postgres backend for Dagster in detached mode.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_postgres_up_detach
    # nox --tags dagster_postgres_up_detach

    sudo = False

    write_dagster_postgres_yml()
    write_dagster_postgres_compose()

    cmd = [
        *cmd_dagster_postgres,
        "up",
        "--remove-orphans",
        "--detach",
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    logging.info(f"{cmd = }")

    session.run(
        *cmd,
        env=ENV,
        external=True,
        silent=SESSION_RUN_SILENT,
    )


# # dagster_postgres_down
@nox.session(python=None, tags=["dagster_postgres_down"])
def dagster_postgres_down(session):
    """
    Shut down Postgres backend for Dagster.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_postgres_up
    # nox --tags dagster_postgres_up

    sudo = False

    cmd = [
        *cmd_dagster_postgres,
        "down",
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    logging.info(f"{cmd = }")

    session.run(
        *cmd,
        env=ENV,
        external=True,
        silent=SESSION_RUN_SILENT,
    )


@nox.session(python=None, tags=["dagster_postgres"])
def dagster_postgres(session):
    """
    Start Dagster with Postgres as backend after `nox --session dagster_postgres_up_detach`.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_postgres
    # nox --tags dagster_postgres

    sudo = False

    cmd = cmd_dagster_dev

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    logging.info(f"{cmd = }")

    session.run(
        *cmd,
        env={
            "DAGSTER_HOME": ENVIRONMENT_DAGSTER["DAGSTER_POSTGRES_ROOT_DIR"],
        },
        external=True,
        silent=SESSION_RUN_SILENT,
    )


# # dagster_mysql_clear
@nox.session(python=None, tags=["dagster_mysql_clear"])
def dagster_mysql_clear(session):
    """
    Clear Dagster-Postgres with `sudo`. WARNING: DATA LOSS!

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_mysql_clear
    # nox --tags dagster_mysql_clear

    sudo = True

    dagster_mysql_root_dir: pathlib.Path = ENVIRONMENT_DAGSTER["DAGSTER_MYSQL_ROOT_DIR"]

    logging.debug("Clearing Dagster-MySQL...")
    logging.debug("Removing Dir %s" % dagster_mysql_root_dir.as_posix())

    cmd = [
        shutil.which("git"),
        "clean",
        "-x",
        "--force",
        dagster_mysql_root_dir.as_posix(),
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        cmd.insert(1, "--reset-timestamp")
        # cmd.insert(2, "--stdin")

    if dagster_mysql_root_dir.exists():
        logging.warning(
            "Clearing out Dagster-MySQL...\nContinue? Type `yes` to confirm."
        )
        answer = input()
        if answer.lower() == "yes":

            logging.info(f"{cmd = }")

            session.run(
                *cmd,
                env=ENV,
                external=True,
                silent=SESSION_RUN_SILENT,
            )
        else:
            logging.info("Clearing %s was aborted." % dagster_mysql_root_dir.as_posix())
            return 1

    logging.debug("%s removed" % dagster_mysql_root_dir.as_posix())

    return 0


@nox.session(python=None, tags=["dagster_mysql"])
def dagster_mysql(session):
    """
    Start Dagster with MySQL as backend (not recommended).

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session dagster_mysql
    # nox --tags dagster_mysql

    sudo = False

    cmd = cmd_dagster_dev

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        # cmd.insert(1, "--stdin")

    session.run(
        *cmd,
        env={
            "DAGSTER_HOME": ENVIRONMENT_DAGSTER["DAGSTER_MYSQL_ROOT_DIR"],
        },
        external=True,
        silent=SESSION_RUN_SILENT,
    )


#######################################################################################################################


# I guess it's better if this is not even implemented because
# MySQL is wonky and Postgres should be the default backend anyway
# #######################################################################################################################
# # # Dagster MySQL
# @nox.session(python=None, tags=["dagster_mysql"])
# def dagster_mysql(session):
#     """
#     Start Dagster with MySQL (default) as backend.
#
#     Scope:
#     - [x] Engine
#     - [ ] Features
#     """
#     # Ex:
#     # nox --session dagster_mysql
#     # nox --tags dagster_mysql
#
#     dagster_mysql_root_dir: pathlib.Path = ENVIRONMENT_DAGSTER["DAGSTER_MYSQL_ROOT_DIR"]
#     dagster_mysql_root_dir.mkdir(parents=True, exist_ok=True)
#
#     # dagster_postgres_db_dir: pathlib.Path = (
#     #     dagster_mysql_root_dir / ENVIRONMENT_DAGSTER_POSTGRES['DAGSTER_POSTGRES_DB_DIR_DIR']
#     # )
#     # dagster_postgres_db_dir.mkdir(parents=True, exist_ok=True)
#
#     session.run(
#         shutil.which("dagster"),
#         "dev",
#         "--host",
#         "0.0.0.0",
#         env={
#             "DAGSTER_HOME": dagster_mysql_root_dir.as_posix(),
#         },
#         external=True,
#     )
#
#
# #######################################################################################################################


#######################################################################################################################
# SBOM
@nox.session(python=PYTHON_TEST_VERSIONS, tags=["sbom"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def sbom(session, working_directory):
    """
    Runs Software Bill of Materials (SBOM).

    Scope:
    - [x] Engine
    - [ ]
    """
    # Ex:
    # nox --session sbom
    # nox --tags sbom

    # https://pypi.org/project/pipdeptree/

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[sbom]",
            silent=SESSION_INSTALL_SILENT,
        )

        sbom_dir = pathlib.Path.cwd() / ".sbom"
        sbom_dir.mkdir(parents=True, exist_ok=True)

        session.run(
            "cyclonedx-py",
            "environment",
            "--output-format",
            "JSON",
            "--output-file",
            sbom_dir / f"cyclonedx-py.{session.python}.json",
            env=ENV,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )

        session.run(
            "bash",
            "-c",
            f"pipdeptree --mermaid > {sbom_dir}/pipdeptree.{session.python}.mermaid",
            env=ENV,
            external=True,
            silent=SESSION_RUN_SILENT,
        )

        session.run(
            "bash",
            "-c",
            f"pipdeptree --graph-output dot > {sbom_dir}/pipdeptree.{session.python}.dot",
            env=ENV,
            external=True,
            silent=SESSION_RUN_SILENT,
        )


#######################################################################################################################


#######################################################################################################################
# Coverage
@nox.session(python=PYTHON_TEST_VERSIONS, tags=["coverage"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def coverage(session, working_directory):
    """
    Runs coverage (not implemented).

    Scope:
    - [x] Engine
    - [x] Features
    """
    # Ex:
    # nox --session coverage
    # nox --tags coverage

    session.skip("Not implemented")

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[coverage]",
            silent=SESSION_INSTALL_SILENT,
        )

        session.run(
            "coverage",
            "run",
            "--source",
            "src",
            "-m",
            "pytest",
            "-sv",
            env=ENV,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )  # ./.coverage
        session.run(
            "coverage",
            "report",
            # external=True,
            silent=SESSION_RUN_SILENT,
        )  # report to console
        # session.run("coverage", "json", "-o", ".coverage", "coverage.json")  # report to json
        session.run(
            "coverage",
            "json",
            "-o",
            "coverage.json",
            # external=True,
            silent=SESSION_RUN_SILENT,
        )  # report to json
        # session.run("coverage", "xml")  # ./coverage.xml
        # session.run("coverage", "html")  # ./htmlcov/


#######################################################################################################################


#######################################################################################################################
# Lint
@nox.session(python=PYTHON_TEST_VERSIONS, tags=["lint"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def lint(session, working_directory):
    """
    Runs linters and fixers

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session lint
    # nox --tags lint

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[lint]",
            silent=SESSION_INSTALL_SILENT,
        )

        # exclude = [
        #     # Add one line per exclusion:
        #     # "--extend-exclude '^.ext'",
        #     "--extend-exclude", "'^.svg'",
        # ]

        session.run(
            "black",
            "src",
            *session.posargs,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )
        session.run(
            "isort",
            "--profile",
            "black",
            "src",
            *session.posargs,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )

        # # pre-commit maybe not as part of lint?
        # # Seems like black and pre-commit hook black are competing with each other
        # if pathlib.PosixPath(".pre-commit-config.yaml").absolute().exists():
        #     session.run(
        #         "pre-commit",
        #         "run",
        #         "--all-files",
        #         *session.posargs,
        #         # external=True,
        #         silent=SESSION_RUN_SILENT,
        #     )

        # # nox > Command pylint src failed with exit code 30
        # # nox > Session lint-3.12 failed.
        # session.run("pylint", "src")
        # # https://github.com/actions/starter-workflows/issues/2303#issuecomment-1973743119
        pylint_report_dir = pathlib.Path.cwd() / ".nox"
        pylint_report_dir.mkdir(parents=True, exist_ok=True)
        session.run(
            "pylint",
            "--exit-zero",
            "--persistent=y",
            f"--output-format=json:{pylint_report_dir.as_posix()}/pylint-report.json,text:{pylint_report_dir.as_posix()}/pylint-report.txt,colorized",
            "src",
            # external=True,
            silent=SESSION_RUN_SILENT,
        )
        # session.run("pylint", "--disable=C0114,C0115,C0116", "--exit-zero", "src")
        # https://stackoverflow.com/questions/7877522/how-do-i-disable-missing-docstring-warnings-at-a-file-level-in-pylint
        # C0114 (missing-module-docstring)
        # C0115 (missing-class-docstring)
        # C0116 (missing-function-docstring)

        # # pyreverse
        # # https://pylint.pycqa.org/en/latest/additional_tools/pyreverse/index.html
        # pyreverse_dir = pathlib.Path.cwd() / ".nox" / "pyreverse"
        # pyreverse_dir.mkdir(parents=True, exist_ok=True)
        # session.run(
        #     "pyreverse",
        #     f"--output-directory",
        #     pyreverse_dir.as_posix(),
        #     "--output",
        #     [
        #         "dot",
        #         "puml",
        #         "plantuml",
        #         "mmd",
        #         "html",
        #     ][4],
        #     "OpenStudioLandscapes.engine",
        #     "OpenStudioLandscapes.Ayon",
        #     "OpenStudioLandscapes.Dagster",
        #     ...,
        #     silent=SESSION_RUN_SILENT,
        # )


#######################################################################################################################


#######################################################################################################################
# Testing
@nox.session(python=PYTHON_TEST_VERSIONS, tags=["testing"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def testing(session, working_directory):
    """
    Runs pytests (not implemented).

    Scope:
    - [x] Engine
    - [x] Features
    """
    # Ex:
    # nox --session testing
    # nox --tags testing

    session.skip("Not implemented")

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[testing]",
            silent=SESSION_INSTALL_SILENT,
        )

        session.run(
            "pytest",
            *session.posargs,
            env=ENV,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )


#######################################################################################################################


#######################################################################################################################
# Readme
@nox.session(python=PYTHON_VERSION_MAIN, tags=["readme"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        # nox.param(engine_dir.name, id=engine_dir.name),  # readme is not built for OpenStudioLandscapes.engine
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED]
    ],
)
def readme(session, working_directory):
    """
    Generate dynamic README.md file for OpenStudioLandscapes modules.

    Scope:
    - [ ] Engine
    - [x] Features
    """
    # Ex:
    # nox --session readme
    # nox --tags readme

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[readme]",
            silent=SESSION_INSTALL_SILENT,
        )

        session.run(
            "generate-readme",
            "--versions",
            *PYTHON_TEST_VERSIONS,
            # external=True,
            silent=SESSION_RUN_SILENT,
        )


#######################################################################################################################


#######################################################################################################################
# pyproject.toml

# Todo:
#  - [ ] Test this for a while and try to merge `pyproject_engine`
#        and `pyproject_features` eventually

@nox.session(python=PYTHON_VERSION_MAIN, tags=["pyproject_engine"])
def pyproject_engine(session):
    """
    Generate dynamic pyproject.toml file for OpenStudioLandscapes engine and modules.

    Scope:
    - [x] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session pyproject_engine
    # nox --tags pyproject_engine

    sudo = False

    session.log(
        f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
    )

    session.install(
        "--no-cache-dir",
        "-e",
        ".[pyproject]",
        silent=SESSION_INSTALL_SILENT,
    )

    session.run(
        "openstudiolandscapesutil-versionbumper",
        "yamls-to-toml",
        "--root-yaml",
        pathlib.Path(__file__).parent / "pyproject_layers" / "pyproject_layer_0_root.yaml",
        "--yaml-layers",
        pathlib.Path(__file__).parent / "pyproject_layers" / "pyproject_layer_engine.yaml",
        pathlib.Path(__file__).parent / "pyproject_layer.yaml",
        "--toml-out",
        pathlib.Path(__file__).parent / "pyproject.toml",
        silent=SESSION_RUN_SILENT,
    )


@nox.session(python=PYTHON_VERSION_MAIN, tags=["pyproject_features"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        # nox.param(engine_dir.name, id=engine_dir.name)
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED]
    ],
)
def pyproject_features(session, working_directory):
    """
    Generate dynamic pyproject.toml file for OpenStudioLandscapes engine and modules.

    Scope:
    - [ ] Engine
    - [x] Features
    """
    # Ex:
    # nox --session pyproject_features
    # nox --tags pyproject_features

    sudo = False

    session.install(
        "--no-cache-dir",
        "-e",
        ".[pyproject]",
        silent=SESSION_INSTALL_SILENT,
    )

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.run(
            "openstudiolandscapesutil-versionbumper",
            "yamls-to-toml",
            "--root-yaml",
            pathlib.Path(__file__).parent / "pyproject_layers" / "pyproject_layer_0_root.yaml",
            "--yaml-layers",
            pathlib.Path(__file__).parent / "pyproject_layers" / "pyproject_layer_features.yaml",
            pathlib.Path.cwd() / "pyproject_layer.yaml",
            "--toml-out",
            pathlib.Path.cwd() / "pyproject.toml",
            silent=SESSION_RUN_SILENT,
        )


#######################################################################################################################


#######################################################################################################################
# Release
# Todo
@nox.session(python=PYTHON_TEST_VERSIONS, tags=["release"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def release(session, working_directory):
    """
    Build and release to a repository (not implemented).

    Scope:
    - [x] Engine
    - [x] Features
    """
    # Ex:
    # nox --session release
    # nox --tags release

    session.skip("Not implemented")

    sudo = False

    with session.chdir(engine_dir.parent / working_directory):

        session.log(
            f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
        )

        session.install(
            "--no-cache-dir",
            "-e",
            ".[release]",
            silent=SESSION_INSTALL_SILENT,
        )

        pypi_user: str = os.environ.get("PYPI_USER")
        pypi_pass: str = os.environ.get("PYPI_PASS")
        if not pypi_user or not pypi_pass:
            session.error(
                "Environment variables for release: PYPI_USER, PYPI_PASS are missing!",
            )
        session.run("poetry", "install", external=True)
        session.run("poetry", "build", external=True)
        session.run(
            "poetry",
            "publish",
            "-r",
            "testpypi",
            "-u",
            pypi_user,
            "-p",
            pypi_pass,
            external=True,
        )


#######################################################################################################################


def menu_from_choices(
    input_message: str,
    choices: list,
    description: str,
    manual_value: bool = False,
    regex: re.Pattern = None,
):
    """
    Create a menu from a list of choices.
    The choices can be extended by a manual one.
    The final choice can be matched against an `re.Pattern`.

    :param input_message: The message shown to the user.
    :param choices: list of choices.
    :param description: arbitrary description string.
    :param manual_value: Will there be a manual value or not.
    :param regex: match choice against a regular expression if regex is specified.
    :return: string of the choice.
    """

    print(f"\nDescription:\n{description}")

    if manual_value:
        choices.append("Manual")

    for index, item in enumerate(choices):
        input_message += f"{index + 1}) {item}\n"

    input_message += "Choice: "

    user_input = ""

    while user_input not in map(str, range(1, len(choices) + 1)):
        user_input = input(input_message)

    if user_input not in map(str, range(1, len(choices) + 1)):
        user_input = input(input_message)

    choice = str(choices[int(user_input) - 1])

    if choice == "Manual":
        choice = input("Specify value: ")

        if regex is not None:
            while not regex.match(choice):
                choice = input(f"Match regex: {regex.pattern}\nSpecify value: ")

    return choice


#######################################################################################################################
# Tag
# @nox.session(python=None, tags=["tag"])
# @nox.parametrize(
#     "working_directory",
#     # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
#     [
#         nox.param(engine_dir.name, id=engine_dir.name),
#         *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
#     ],
# )
# def tag(session, working_directory):
#     """
#     Git tag OpenStudioLandscapes modules.
#     See wiki/guides/release_strategy.md#main-release
#
#     Scope:
#     - [x] Engine
#     - [x] Features
#     """
#     # Ex:
#     # nox --session tag
#     # nox --tags tag
#
#     # TAG
#     repo = git.Repo(engine_dir.parent / working_directory)
#     repo.git.fetch(tags=True, all=True, force=True)
#     tags = repo.tags
#
#     tag_ = os.environ.get("TAG", None)
#     if tag_ is None:
#         input_message = "Version tag:\n"
#
#         tag_ = menu_from_choices(
#             input_message=input_message,
#             choices=tags,
#             description="",
#             manual_value=True,
#         )
#
#         os.environ["TAG"] = tag_
#
#     # RELEASE_TYPE
#     release_type = os.environ.get("RELEASE_TYPE", None)
#     if release_type is None:
#
#         release_types = ["rc", "main"]
#
#         input_message = "Tag type:\n"
#
#         release_type = menu_from_choices(
#             input_message=input_message,
#             choices=release_types,
#             description="- `rc` will only create/update given tag\n"
#             "- `main` will create/update given tag and also "
#             "update latest with a pointer the same commit as given tag\n",
#             manual_value=False,
#         )
#
#         os.environ["RELEASE_TYPE"] = release_type
#
#     # FORCE
#     force = os.environ.get("FORCE", None)
#     if force is None:
#         forced = ["no", "yes"]
#
#         input_message = "Force:\n"
#
#         force = menu_from_choices(
#             input_message=input_message,
#             choices=forced,
#             description="",
#             manual_value=False,
#         )
#
#         os.environ["FORCE"] = force
#
#     session.log(f"{tag_ = }")
#     session.log(f"{release_type = }")
#     session.log(f"{force = }")
#
#     cmds = []
#
#     # cmd_fetch = [
#     #     shutil.which("git"),
#     #     "fetch",
#     #     "--tags",
#     #     "--force",
#     # ]
#     # cmds.append(cmd_fetch)
#
#     if release_type == "rc":
#         msg = f"Release Candidate Version {tag_}"
#     elif release_type == "main":
#         msg = f"Main Release Version {tag_}"
#
#     cmd_annotate = [
#         shutil.which("git"),
#         "tag",
#         "--annotate",
#         tag_,
#         "--message",
#         msg,
#     ]
#     if force == "yes":
#         cmd_annotate.append("--force")
#     cmds.append(cmd_annotate)
#
#     if release_type == "main":
#
#         cmd_annotate_latest = [
#             shutil.which("git"),
#             "tag",
#             "--annotate",
#             "latest",
#             "--message",
#             f"Latest Release Version (pointing to {tag_}",
#             "%s^{}" % tag_,
#         ]
#         if force == "yes":
#             cmd_annotate_latest.append("--force")
#         cmds.append(cmd_annotate_latest)
#
#     cmd_push = [
#         shutil.which("git"),
#         "push",
#         "--tags",
#     ]
#     if force == "yes":
#         cmd_push.append("--force")
#     cmds.append(cmd_push)
#
#     with session.chdir(engine_dir.parent / working_directory):
#
#         session.log(
#             f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
#         )
#
#         for cmd in cmds:
#
#             session.log(f"Running Command:\n\t{shlex.join(cmd)}")
#
#             session.run(
#                 *cmd,
#                 env=ENV,
#                 external=True,
#                 silent=SESSION_RUN_SILENT,
#             )


# @nox.session(python=None, tags=["tag_delete"])
# @nox.parametrize(
#     "working_directory",
#     # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
#     [
#         nox.param(engine_dir.name, id=engine_dir.name),
#         *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
#     ],
# )
# def tag_delete(session, working_directory):
#     """
#     Git tag delete OpenStudioLandscapes modules.
#     See wiki/guides/release_strategy.md#delete-tags
#
#     Scope:
#     - [x] Engine
#     - [x] Features
#     """
#     # Ex:
#     # nox --session tag_delete
#     # nox --tags tag_delete
#
#     # TAG
#     repo = git.Repo(engine_dir.parent / working_directory)
#     repo.git.fetch(tags=True, all=True, force=True)
#     tags = repo.tags
#
#     tag_ = os.environ.get("TAG", None)
#     if tag_ is None:
#         input_message = "Existing tags:\n"
#
#         tag_ = menu_from_choices(
#             input_message=input_message,
#             choices=tags,
#             description="- force delete tag if it exists\n",
#             manual_value=True,
#             regex=RE_SEMVER,
#         )
#
#         os.environ["TAG"] = tag_
#
#     cmds = []
#
#     # cmd_fetch = [
#     #     shutil.which("git"),
#     #     "fetch",
#     #     "--tags",
#     #     "--force",
#     # ]
#     # cmds.append(cmd_fetch)
#
#     cmd_delete_tag = [
#         shutil.which("git"),
#         "tag",
#         "-d",
#         tag_,
#     ]
#     cmds.append(cmd_delete_tag)
#
#     cmd_push = [
#         shutil.which("git"),
#         "push",
#         "origin",
#         f":refs/tags/{tag_}",
#     ]
#     cmds.append(cmd_push)
#
#     with session.chdir(engine_dir.parent / working_directory):
#
#         session.log(
#             f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
#         )
#
#         for cmd in cmds:
#
#             session.log(f"Running Command:\n\t{shlex.join(cmd)}")
#
#             session.run(
#                 *cmd,
#                 env=ENV,
#                 external=True,
#                 silent=SESSION_RUN_SILENT,
#             )

# # Checkout
# @nox.session(python=None, tags=["checkout_branch"])
# @nox.parametrize(
#     "working_directory",
#     # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
#     [
#         nox.param(engine_dir.name, id=engine_dir.name),
#         *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
#     ],
# )
# def checkout_branch(session, working_directory):
#     """
#     Git checkout OpenStudioLandscapes modules.
#     See wiki/guides/release_strategy.md#main-release
#
#     Scope:
#     - [x] Engine
#     - [x] Features
#     """
#     # Ex:
#     # nox --session checkout_branch
#     # nox --tags checkout_branch
#
#     # BRANCHES
#     repo = git.Repo(engine_dir.parent / working_directory)
#     repo.git.fetch(tags=True, all=True, force=True)
#     branches = repo.branches
#
#     branch_ = os.environ.get("BRANCH", None)
#     if branch_ is None:
#         input_message = "Branch:\n"
#
#         branch_ = menu_from_choices(
#             input_message=input_message,
#             choices=branches,
#             description="",
#             manual_value=True,
#         )
#
#         os.environ["BRANCH"] = branch_
#
#     session.log(f"{branch_ = }")
#
#     cmds = []
#
#     cmd_checkout = [
#         shutil.which("git"),
#         "checkout",
#         branch_,
#     ]
#
#     cmds.append(cmd_checkout)
#
#     with session.chdir(engine_dir.parent / working_directory):
#
#         session.log(
#             f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
#         )
#
#         for cmd in cmds:
#
#             session.log(f"Running Command:\n\t{shlex.join(cmd)}")
#
#             session.run(
#                 *cmd,
#                 env=ENV,
#                 external=True,
#                 silent=SESSION_RUN_SILENT,
#             )


#######################################################################################################################


#######################################################################################################################
# PR
# Todo:
#  - [x] gh_login
#        See wiki/guides/release_strategy.md#pull-requests-gh
#  - [ ] gh_pr_create
#        See wiki/guides/release_strategy.md#create-pr
#  - [ ] gh_pr_edit
#        See wiki/guides/release_strategy.md#edit-pr
#  - [ ] gh_pr_close
#        See wiki/guides/release_strategy.md#close-pr
#  - [ ] gh_pr_merge
#  - [ ] gh_pr_close


@nox.session(python=None, tags=["gh_login"])
def gh_login(session):
    """
    GitHub CLI Login.
    See wiki/guides/release_strategy.md#pull-requests-gh

    Scope:
    - [ ] Engine
    - [ ] Features
    """
    # Ex:
    # nox --session gh_login
    # nox --tags gh_login

    # sudo = False

    cmds = []

    gh = shutil.which("gh")

    if bool(gh):

        cmd_gh_login = [
            gh,
            "auth",
            "login",
            "--web",
        ]
        cmds.append(cmd_gh_login)

        for cmd in cmds:

            session.log(f"Running Command:\n\t{shlex.join(cmd)}")

            session.run(
                *cmd,
                env=ENV,
                external=True,
                silent=SESSION_RUN_SILENT,
            )

    else:
        msg = "No Github CLI Found."
        session.skip(msg)


# Todo:
#  - [ ] refactor
@nox.session(python=None, tags=["gh_pr_create"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def gh_pr_create(session, working_directory):
    """
    Create PR (draft) for OpenStudioLandscapes modules.
    See wiki/guides/release_strategy.md#create-pr

    Scope:
    - [x] Engine
    - [x] Features
    """
    # Ex:
    # nox --session gh_pr_create
    # nox --tags gh_pr_create

    session.skip("Not implemented")

#
#     # BRANCH
#     repo = git.Repo(engine_dir.parent / working_directory)
#     branches = repo.branches
#
#     branch = os.environ.get("BRANCH", None)
#     if branch is None:
#         input_message = "Branch:\n"
#
#         branch = menu_from_choices(
#             input_message=input_message,
#             choices=branches,
#             description="",
#             manual_value=True,
#         )
#
#         os.environ["BRANCH"] = branch
#
#     # DRY_RUN
#     dry_run = os.environ.get("DRY_RUN", None)
#     if dry_run is None:
#         options = ["yes", "no"]
#
#         input_message = "Dry run:\n"
#
#         dry_run = menu_from_choices(
#             input_message=input_message,
#             choices=options,
#             description="",
#             manual_value=False,
#         )
#
#         os.environ["DRY_RUN"] = dry_run
#
#     cmds = []
#
#     gh = shutil.which("gh")
#
#     # body_file = str(os.environ.get("BODY_FILE", ""))
#     # session.log(f"{body_file = }")
#
#     if bool(gh):
#
#         cmd_gh_pr_create = [
#             gh,
#             "pr",
#             "create",
#             "--draft",
#             "--title",
#             branch,
#             "--head",
#             branch,
#             "--base",
#             GIT_MAIN_BRANCH,
#             # Todo
#             #  - [ ] --body-file
#             "--body",
#             "",
#         ]
#         if dry_run == "yes":
#             cmd_gh_pr_create.append("--dry-run")
#         cmds.append(cmd_gh_pr_create)
#
#         with session.chdir(engine_dir.parent / working_directory):
#
#             session.log(
#                 f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
#             )
#
#             if dry_run:
#                 session.warn(f"DRY_RUN is set to {dry_run}")
#
#             for cmd in cmds:
#
#                 session.log(f"Running Command:\n\t{shlex.join(cmd)}")
#
#                 session.run(
#                     *cmd,
#                     env=ENV,
#                     external=True,
#                     silent=SESSION_RUN_SILENT,
#                 )
#
#     else:
#         msg = "No Github CLI Found."
#         session.skip(msg)


# Todo:
#  - [ ] refactor
@nox.session(python=None, tags=["gh_pr_set_mode"])
@nox.parametrize(
    "working_directory",
    # https://nox.thea.codes/en/stable/config.html#giving-friendly-names-to-parametrized-sessions
    [
        nox.param(engine_dir.name, id=engine_dir.name),
        *[nox.param(i, id=i.name) for i in FEATURES_PARAMETERIZED],
    ],
)
def gh_pr_set_mode(session, working_directory):
    """
    Set mode for OpenStudioLandscapes PRs.
    See wiki/guides/release_strategy.md#edit-pr

    Scope:
    - [x] Engine
    - [x] Features
    """
    # Ex:
    # nox --session gh_pr_set_mode
    # nox --tags gh_pr_set_mode

    session.skip("Not implemented")

#     # BRANCH
#     repo = git.Repo(engine_dir.parent / working_directory)
#     branches = repo.branches
#
#     branch = os.environ.get("BRANCH", None)
#     if branch is None:
#         input_message = "Branch:\n"
#
#         branch = menu_from_choices(
#             input_message=input_message,
#             choices=branches,
#             description="",
#             manual_value=True,
#         )
#
#         os.environ["BRANCH"] = branch
#
#     # RELEASE_TYPE
#     mode = os.environ.get("MODE", None)
#     if mode is None:
#         modes = ["draft", "ready"]
#
#         input_message = "PR mode:\n"
#
#         mode = menu_from_choices(
#             input_message=input_message,
#             choices=modes,
#             description="",
#             manual_value=False,
#         )
#
#         os.environ["MODE"] = mode
#
#     cmds = []
#
#     gh = shutil.which("gh")
#
#     # # defaults to draft if not overridden
#     # _mode = os.environ.get("MODE", "draft").lower()
#     # if _mode not in ["draft", "ready"]:
#     #     session.error("MODE must be draft or ready.")
#     # modes = str(_mode)
#
#     # body_file = str(os.environ.get("BODY_FILE", ""))
#     # session.log(f"{body_file = }")
#
#     if bool(gh):
#
#         # branch_name = session.posargs
#         #
#         # if len(branch_name) != 1:
#         #     msg = "Invalid branch name. Tag argument must be exactly 1 argument."
#         #     session.warn(msg)
#         #     raise ValueError(msg)
#         #
#         # branch_name = branch_name[0]
#
#         cmd_gh_pr_set_mode = [
#             gh,
#             "pr",
#             "ready",
#             branch,
#         ]
#         if mode == "draft":
#             cmd_gh_pr_set_mode.append("--undo")
#         cmds.append(cmd_gh_pr_set_mode)
#
#         with session.chdir(engine_dir.parent / working_directory):
#
#             session.log(
#                 f"Current Session Working Directory:\n\t{pathlib.Path.cwd().as_posix()}"
#             )
#
#             session.warn(f"MODE is set to '{mode}'")
#
#             for cmd in cmds:
#
#                 session.log(f"Running Command:\n\t{shlex.join(cmd)}")
#
#                 session.run(
#                     *cmd,
#                     env=ENV,
#                     external=True,
#                     silent=SESSION_RUN_SILENT,
#                 )
#
#     else:
#         msg = "No Github CLI Found."
#         session.skip(msg)


#######################################################################################################################


#######################################################################################################################
# stow (switch .env)

# Todo
#######################################################################################################################


#######################################################################################################################
# nox_clean

# Todo
#######################################################################################################################


#######################################################################################################################
# Create new Feature from Template

# Todo
#  A set of sessions to facilitate Feature creation process
#  - https://github.com/michimussato/OpenStudioLandscapes-Template
#
# v1.2.0-rc1 -> v1.2.0
#
# - pyproject.toml [all]
# - wiki/installation/basic_installation_from_script.md
# - wiki/README.md (https://github.com/michimussato/OpenStudioLandscapes/blob/main -> https://github.com/michimussato/OpenStudioLandscapes/blob/v1.2.0)
#
#
# - Create step by step guide
# - update OpenStudioLandscapes.ReadmeGenerator.readme_generator (_generator() -> community_channels)
# - include tag updates in OpenStudioLandscapesUtil-ReadmeGenerator
# fetch:  git fetch --tags --force
# # tag commit: https://graphite.dev/guides/add-tag-to-git-commit
# tag:
#         main:   TAG=v1.3.0 && git tag --annotate ${TAG} --message "Main Release Version ${TAG}" --force
#         rc:     TAG=v1.4.0-rc1 && git tag --annotate ${TAG} --message "Release Candidate Version ${TAG}" --force
# push:   git push --tags --force
# - update README.md#current-feature-statuses
#
# main tags only on main branch
# rc tags only on work branches
#
#
# create new feature:
# checkout main
# create new feature OpenStudioLandscapes-<Feature> from template on github
# clone new feature into .features
# add new repo as project in pycharm
# - create .venv `python3.11 -m venv .venv`
# - project settings: dependencies
#   - project structure: `src` mark directory as sources root
#   - project dependencies: mark `OpenStudioLandscapes` engine as dependency
# add feature pyproject.toml to bookmarks
# checkout feature `feature-openstudiolandscapes-<feature>` branch
# nox -s fix_hardlinks_in_features
# version bump in pyproject.toml to main tag+1(minor)-rc1
# update .env
# update src/OpenStudioLandscapes/engine/features.py
# update README.md#current-feature-statuses
# replace Template with Feature:
# - rename feature/src/OpenStudioLandscapes/Template to feature/src/OpenStudioLandscapes/Feature
# - edit feature/pyproject.toml
# - update src/OpenStudioLandscapes/Feature/__init__.py
# - update src/OpenStudioLandscapes/Feature/assets.py
# - update src/OpenStudioLandscapes/Feature/constants.py
# - update src/OpenStudioLandscapes/Feature/definitions.py
# update wiki/README.md paths from [...]/blob/v1.4.0/wiki/[...] to [...]/blob/v1.5.0-rc1/wiki/[...]
# update wiki/installation/basic_installation_from_script.md OPENSTUDIOLANDSCAPES_VERSION_TAG from v1.4.0 to v1.5.0-rc1
# git push
# nox -s tag rc
# git tag ReadmeGenerator with same rc
#
# nox -s gh_pr_create
#
# pip install -e .features/OpenStudioLandscapes-Feature[dev]
# pip install -e .[dev]
#######################################################################################################################
