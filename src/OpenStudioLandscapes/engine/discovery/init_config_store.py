import pathlib
from typing import Tuple

import git

from OpenStudioLandscapes.engine.logging.loggers import DISCOVERY_LOGGER as LOGGER


def init_config_store(
    root: pathlib.Path,
) -> Tuple[git.Repo, bool]:

    # Get Git repo
    try:
        fresh_repo = False
        r = git.Repo(root.expanduser())
        LOGGER.info(f"Using existing repo: {r.common_dir}.")
    except git.exc.InvalidGitRepositoryError:
        fresh_repo = True
        # Create Repo if dir is not a Git repo
        # https://gitpython.readthedocs.io/en/stable/tutorial.html#initializing-a-repository
        r = git.Repo.init(root.expanduser())
        LOGGER.info(f"New repo created: {r.common_dir}.")

    return r, fresh_repo


def commit_configs(
    fresh_repo: bool,
    config_store_repo: git.Repo,
) -> None:

    # Add all files to tracked files in Git repo
    if fresh_repo:
        LOGGER.info(f"Add files to tracked file...")
        config_store_repo.index.add("*")
        LOGGER.info(f"Making initial commit...")
        config_store_repo.index.commit("Initial Commit")
        LOGGER.info(f"Initial Commit successful.")
    else:
        if config_store_repo.is_dirty():
            # config_store_repo.git.status("--porcelain")
            LOGGER.warning(
                f"Config Store '{config_store_repo.common_dir}' has uncommited changes:\n"
                f"{config_store_repo.git.status()}"
            )
            LOGGER.warning("Manual commit necessary.")

    return None
