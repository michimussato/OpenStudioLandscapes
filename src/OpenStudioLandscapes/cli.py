import argparse
import logging
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import textwrap
from typing import Tuple

import git

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__url__ = "https://github.com/michimussato/OpenStudioLandscapes"
__license__ = "GNU Affero General Public License v3.0"

from OpenStudioLandscapes.engine.logging.loggers import CLI_LOGGER as LOGGER


class CLIException(Exception):
    pass


# ---- Python API ----


def _get_terminal_size() -> Tuple[int, int]:
    # Todo
    #  - [ ] how does this behave in systemd?
    # https://stackoverflow.com/a/14422538
    # https://stackoverflow.com/a/18243550
    cols, rows = shutil.get_terminal_size((80, 20))
    return cols, rows


def run_openstudiolandscapes_postgres(args):
    print(" STARTING OPENSTUDIOLANDSCAPES ".center(_get_terminal_size()[0], "="))
    LOGGER.info("Welcome!")
    LOGGER.debug("OpenStudioLandscapes args: %s", args)

    if bool(int(args.attach_grafana_alloy_to_compose_scope)):
        os.environ["OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE"] = "1"
    if bool(int(args.attach_pangolin_site_to_compose_scope)):
        os.environ["OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE"] = "1"
    if args.domain_wan is not None:
        os.environ["OPENSTUDIOLANDSCAPES__DOMAIN_WAN"] = args.domain_wan

    os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT"] = args.config_store.as_posix()
    os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS"] = (
        args.config_store_vcs.as_posix()
    )

    os.environ["OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT"] = (
        args.landscapes_root.as_posix()
    )

    os.environ["OPENSTUDIOLANDSCAPES__LOGS_ROOT"] = args.logs_root.as_posix()

    if args.landscapes_id is not None:
        os.environ["OPENSTUDIOLANDSCAPES__LANDSCAPE_ID"] = args.landscapes_id

    # Simply use `nox` as the entry point:
    # try:
    result: subprocess.CompletedProcess = subprocess.run(
        [
            shutil.which("nox"),
            "--sessions",
            "dagster_postgres_up_detach",
            "dagster_postgres",
        ],
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        shell=False,
    )

    if result.returncode != 0:
        LOGGER.error(
            "OpenStudioLandscapes failed with return code: %s", result.returncode
        )
        # LOGGER.debug(result.stdout.decode("utf-8"))
        # LOGGER.debug(result.stderr.decode("utf-8"))
        LOGGER.critical(
            "Run `openstudiolandscapes` from within the Git repository "
            "root. Cannot proceed."
        )

    # LOGGER.info(result.stderr)
    # LOGGER.info(result.returncode)

    # return result.returncode


def run_openstudiolandscapes_mysql(args):
    LOGGER.info("Welcome!")
    LOGGER.info("OpenStudioLandscapes args: %s", args)

    # Simply use `nox` as the entry point:
    subprocess.run(
        [
            shutil.which("nox"),
            "--sessions",
            "dagster_mysql",
        ],
        shell=False,
    )


# Aliases
run_openstudiolandscapes = run_openstudiolandscapes_postgres


# ---- CLI ----


def parse_args(args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--verbosity",
        "-v",
        dest="verbosity",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__VERBOSITY",
        default=logging.getLevelName(logging.WARNING),
        choices=[
            logging.getLevelName(logging.ERROR),
            logging.getLevelName(logging.CRITICAL),
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.DEBUG),
        ],
        required=False,
        help="Verbosity level.",
    )

    parser.add_argument(
        "--attach-grafana-alloy-to-compose-scope",
        dest="attach_grafana_alloy_to_compose_scope",
        metavar="OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE", "0"
        ),
        action="store_const",
        const="1",
        help="Attach Alloy container to Compose Scope.",
    )

    parser.add_argument(
        "--attach-pangolin-site-to-compose-scope",
        dest="attach_pangolin_site_to_compose_scope",
        metavar="OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE", "0"
        ),
        action="store_const",
        const="1",
        required=False,
        help="Attach Newt container to Compose Scope.",
    )

    parser.add_argument(
        "--domain-wan",
        dest="domain_wan",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__DOMAIN_WAN",
        default=os.environ.get("OPENSTUDIOLANDSCAPES__DOMAIN_WAN", None),
        required=False,
        help="Set the WAN domain name (i.e. openstudiolandscapes.com).",
    )

    parser.add_argument(
        "--config-store",
        dest="config_store",
        type=pathlib.Path,
        metavar="OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
        default=pathlib.Path("~/.config/OpenStudioLandscapes/config-store"),
        required=False,
        help="Set the configuration store path.",
    )

    parser.add_argument(
        "--config-store-vcs",
        dest="config_store_vcs",
        type=pathlib.Path,
        metavar="OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS",
        default=pathlib.Path("~/.config/OpenStudioLandscapes/config-store"),
        required=False,
        help="If the config store is part of a Git repository already, "
        "you can specify the path to the repo here. Defaults to the same "
        "value like `OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT`.",
    )

    parser.add_argument(
        "--landscapes-root",
        dest="landscapes_root",
        type=pathlib.Path,
        metavar="OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT",
        default=pathlib.Path("~/.local/share/OpenStudioLandscapes"),
        required=False,
        help="Set the Landscape root path. A `.landscapes` "
        "subdirectory will be created and used.",
    )

    parser.add_argument(
        "--logs-root",
        dest="logs_root",
        type=pathlib.Path,
        metavar="OPENSTUDIOLANDSCAPES__LOGS_ROOT",
        default=pathlib.Path("~/.config/OpenStudioLandscapes"),
        required=False,
        help="Set the OpenStudioLandscapes logs root path. A `.logs` "
        "subdirectory will be created and used.",
    )

    parser.add_argument(
        "--landscapes-id",
        dest="landscapes_id",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__LANDSCAPE_ID",
        default=None,
        required=False,
        help="Lock the landscape_id to this value.",
    )

    update_group = parser.add_mutually_exclusive_group(required=False)

    update_group.add_argument(
        "--skip-update-check",
        dest="skip_update_check",
        default=False,
        action="store_true",
        required=False,
        help="Skip checking for codebase updates. The update check "
        "itself does nothing but checking whether there are "
        "code updates or not.",
    )

    update_group.add_argument(
        "--auto-update",
        dest="auto_update",
        default=False,
        action="store_true",
        required=False,
        help="Automatically pull codebase updates. Specifiying this "
        "will imply *not* to `--skip-update-check`, hence, these "
        "are mutually exclusive.",
    )

    update_group.add_argument(
        "--keepalive",
        dest="keepalive",
        default=1,
        type=int,
        required=False,
        help="Automatically try to restart if CLI fails. "
        "Helpful for self healing when used in `systemd` for "
        "example. This is the third option and *will always* imply "
        "`--auto-update` in order to pull and apply latest codebase updates "
        "before restarting for a new attempt. "
        "If the supplied value is exceeded, keepalive will stop and exit for good. "
        "A supplied value of `1` is usually fine because if things fail even after "
        "applying code base updates, there is little chance that another "
        "iteration will fix the problem. However, it might give `systemd` more slack "
        "before failing and stopping an `openstudiolandscapes.service` unit.",
    )

    subparsers = parser.add_subparsers(
        dest="sub_command",
        required=False,
    )

    subparser_update = subparsers.add_parser(
        "update",
    )

    # subparser_update.add_argument(
    #     "--pull",
    #     dest="pull",
    #     default=False,
    #     action="store_true",
    #     required=False,
    #     help="git pull.",
    # )

    subparser_install_feature = subparsers.add_parser(
        "clone-feature",
        help="Clone a feature from a given repository and "
        "print installation instructions.",
    )

    # Todo
    #  - [ ] set branch, default=main `--branch`

    subparser_install_feature.add_argument(
        "--repo",
        dest="repo",
        metavar="REPO",
        # type=git.Repo,
        type=str,
        required=True,
    )

    subparser_install_feature = subparsers.add_parser(
        "switch-branch",
        help="Switch branch across the Engine and all Features.",
    )

    # Todo
    #  - [ ] set branch, default=main `--branch`

    subparser_install_feature.add_argument(
        "--branch",
        dest="branch",
        metavar="BRANCH",
        default="main",
        # type=git.Repo,
        type=str,
        required=True,
    )

    # Todo
    #  - [ ] update config.yml files after model has changed
    #        - subparser_update = subparsers.add_parser(
    #              "migrate",
    #          )

    LOGGER.debug(f"{args = }")

    try:
        LOGGER.info("Parsing arguments...")
        parsed = parser.parse_args(args)
    except SystemExit as e:  # argparse raises SystemExit on error
        if any(x in ["-h", "--help"] for x in args):
            # if a help flag is specified, print the help as usual
            # by re-raising the standard exception (will stop)
            raise SystemExit from e

        # if any(x in ["--keepalive"] for x in args):
        #     raise SystemExit from e

        LOGGER.debug(f"{sys.argv = }")
        LOGGER.critical("Could not parse arguments: %s", args)

        # Todo:
        #  - [ ] maybe pip install is needed after changes?
        #  - [ ] pip install --upgrade pip?

        if "--keepalive" not in sys.argv:
            LOGGER.info("No `--keepalive` supplied. Exiting...")
            raise SystemExit from e

        else:
            print(" KEEP ALIVE ROUTINE ".center(_get_terminal_size()[0], "="))
            keepalive_index = sys.argv.index("--keepalive")
            keepalive_value = int(sys.argv[keepalive_index + 1])
            # LOGGER.debug(f"{keepalive_index = }")
            LOGGER.debug(f"{keepalive_value = }")

            if keepalive_value > 0:
                print(
                    " TRYING TO KEEPALIVE OPENSTUDIOLANDSCAPES ".center(
                        _get_terminal_size()[0], "-"
                    )
                )
                print(
                    f" (max. {keepalive_value} more time{'s' if keepalive_value > 1 else ''}) ".center(
                        _get_terminal_size()[0], "-"
                    )
                )

                keepalive_index_sys_argv: int = sys.argv.index("--keepalive")
                keepalive_value_sys_argv: int = int(
                    sys.argv[keepalive_index_sys_argv + 1]
                )
                LOGGER.debug(f"{sys.argv = }")
                # LOGGER.debug(f"{keepalive_index_sys_argv = }")
                LOGGER.debug(f"{keepalive_value_sys_argv = }")

                LOGGER.debug(
                    f"Before decrement: {sys.argv[keepalive_index_sys_argv + 1] = }"
                )
                # decrement the keepalive value by 1
                sys.argv[keepalive_index_sys_argv + 1] = str(
                    keepalive_value_sys_argv - 1
                )
                LOGGER.debug(
                    f"After decrement: {sys.argv[keepalive_index_sys_argv + 1] = }"
                )

                LOGGER.critical("Let's try to update the repos before retrying...")
                check_updates_available(args)
                LOGGER.critical(
                    "Update done. Trying to launch OpenStudioLandscapes again..."
                )

                LOGGER.critical("Initiating new process...")
                print(
                    " RESTARTING OPENSTUDIOLANDSCAPES ".center(
                        _get_terminal_size()[0], "-"
                    )
                )
                # Replace the current process with a new one
                # - https://stackoverflow.com/questions/36018401/how-to-make-a-script-automatically-restart-itself#36018657
                os.execv(sys.argv[0], sys.argv)

            else:
                LOGGER.critical("`--keepalive` exhausted. Exiting.")
                sys.stderr.write(
                    " OPENSTUDIOLANDSCAPES KEEPALIVE ROUTINE EXHAUSTED ".center(
                        _get_terminal_size()[0], "="
                    )
                )
                raise SystemExit from e

    return parsed


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """

    LOGGER.setLevel(loglevel)

    LOGGER.critical("Setting CLI logging to: level %s...", loglevel)
    LOGGER.critical(
        "CLI logging configured: level (%i) %s"
        % (LOGGER.level, logging.getLevelName(LOGGER.level))
    )
    LOGGER.critical(
        "CLI logging configured: effective level %s", LOGGER.getEffectiveLevel()
    )
    os.environ["OPENSTUDIOLANDSCAPES__VERBOSITY"] = logging.getLevelName(
        LOGGER.getEffectiveLevel()
    )


def check_updates_available(autoupdate: bool = False):
    # https://knowledge.buka.sh/how-to-check-for-remote-git-changes-without-pulling/

    # if any(sc == args.sub_command for sc in ["update"]):

    LOGGER.info("Checking for OpenStudioLandscapes updates...")

    repos = {
        "engine": None,
        "features": {},
    }

    LOGGER.info("Checking for OpenStudioLandscapes Engine and Features updates...")
    repo = git.Repo(".")
    LOGGER.debug(f"{repo = }")
    LOGGER.info(f"{repo.active_branch = }")
    LOGGER.debug(f"{repo.working_dir = }")
    LOGGER.info(
        f"Checking for {pathlib.Path(repo.working_dir).name} (Engine) updates..."
    )
    repos["engine"] = repo
    git_cmd = repo.git
    dirty = repo.is_dirty()
    if dirty:
        LOGGER.critical("Local repo has uncommitted changes.")
        # status = git_cmd.status()
        # LOGGER.info(status)
    # else:
    fetch = git_cmd.fetch()
    LOGGER.info(f"Fetch: {fetch}")
    status = git_cmd.status()
    LOGGER.info(f"Status: {status}")
    if autoupdate:
        if dirty:
            LOGGER.critical(f"Repo is dirty, auto-update skipped.")
        else:
            result_pull = git_cmd.pull()
            LOGGER.info(f"Changes: {result_pull}")

    for d in pathlib.Path(repo.working_tree_dir).joinpath(".features").iterdir():
        if d.is_file():
            continue
        LOGGER.debug(f"{d = }")
        repo_feature = git.Repo(d)
        LOGGER.debug(f"{repo_feature = }")
        LOGGER.info(f"{repo.active_branch = }")
        LOGGER.debug(f"{repo_feature.working_dir = }")
        LOGGER.info(
            f"Checking for {pathlib.Path(repo_feature.working_dir).name} updates..."
        )
        repos["features"][pathlib.Path(repo_feature.working_dir).name] = repo_feature
        git_cmd_feature = repo_feature.git
        feature_dirty = repo_feature.is_dirty()
        if feature_dirty:
            LOGGER.critical("Can't update: repo has uncommitted changes.")
            # status_feature = git_cmd_feature.status()
            # LOGGER.info(status_feature)
        # else:
        fetch_feature = git_cmd_feature.fetch()
        LOGGER.info(f"Fetch: {fetch_feature}")
        status_feature = git_cmd_feature.status()
        LOGGER.info(f"Status: {status_feature}")
        if autoupdate:
            if dirty:
                LOGGER.critical("Repo is dirty, auto-update skipped.")
            else:
                result_pull_feature = git_cmd_feature.pull()
                LOGGER.info(f"Changes: {result_pull_feature}")
    # repo.git.pull()

    LOGGER.info("Done checking for OpenStudioLandscapes updates.")
    return 0


def checks(args):
    LOGGER.info("Running OpenStudioLandscapes pre-flight checks...")

    def check_illegal_args(args):

        LOGGER.info("Checking for illegal CLI values...")

        args.landscapes_root: pathlib.Path

        try:
            assert ".landscapes" not in args.landscapes_root.parts, (
                "`--landscapes-root` contains `.landscapes` path element ('%s'). "
                "Can't continue." % args.landscapes_root.as_posix()
            )

        except AssertionError as e:
            msg = textwrap.dedent("""
                #########################################################
                `--landscapes-root` path must not contain `.landscapes`. 
                A `.landscapes` subdirectory will be created 
                automatically.
                #########################################################
                Initialization terminated.
                #########################################################
                """)
            LOGGER.error(msg)
            raise AssertionError(msg) from e

        LOGGER.info("Done checking for illegal CLI values.")
        return 0

    check_illegal_args(args)

    def check_sys_deps():

        LOGGER.info("Checking OpenStudioLandscapes dependencies...")

        sys_deps = {
            "Docker": {
                "executable": "docker",
                "version": "version",
                # "min": (3, 11, 11),
                # "max": ()
            },
            "Graphviz": {
                "executable": "dot",
                "version": "-V",
            },
            "Git": {
                "executable": "git",
                "version": "--version",
            },
            "Python": {
                "executable": "python3.11",
                "version": "-V",
            },
            "Nox": {
                "executable": "nox",
                "version": "--version",
            },
        }

        LOGGER.info(
            "Dependencies: %s."
            % ", ".join(f"{k} ({v['executable']})" for k, v in sys_deps.items())
        )

        for dep, params in sys_deps.items():

            LOGGER.info("Checking for system dependency: '%s'..." % dep)
            try:
                assert shutil.which(params["executable"]) is not None, (
                    "Dependency '%s' is not installed"
                    % f"{dep} ({params['executable']})"
                )
            except AssertionError as e:
                msg = textwrap.dedent("""
                    #########################################################
                    Dependencies not fulfilled.
                    Maybe you forgot to run `make sys_deps_install`?
                    #########################################################
                    IMPORTANT: Reboot system after installing dependencies!!!
                    #########################################################
                    """)
                LOGGER.error(msg)
                raise AssertionError(msg) from e

            LOGGER.info("Dependency '%s' is installed." % dep)

            LOGGER.info("Checking version...")
            result = subprocess.run(
                [
                    shutil.which(params["executable"]),
                    params["version"],
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=False,
            )

            LOGGER.info("%s version is: `%s`" % (dep, result.stdout.decode().strip()))

        LOGGER.info("Done checking dependencies.")
        return 0

    check_sys_deps()

    if not args.skip_update_check:
        check_updates_available(autoupdate=args.auto_update)


def main(args):
    args = parse_args(args)
    setup_logging(args.verbosity)
    LOGGER.info(f"Launching OpenStudioLandscapes...")

    checks(args)

    if any(sc == args.sub_command for sc in ["update"]):

        repos = {
            "engine": None,
            "features": {},
        }

        LOGGER.info("Updating OpenStudioLandscapes Engine and Features...")
        repo = git.Repo(".")
        LOGGER.debug(f"{repo = }")
        LOGGER.debug(f"{repo.working_dir = }")
        LOGGER.info(
            f"Checking for {pathlib.Path(repo.working_dir).name} (Engine) updates..."
        )
        repos["engine"] = repo
        git_cmd = repo.git
        if repo.is_dirty():
            LOGGER.critical("Can't update: repo has uncommitted changes.")
            status = git_cmd.status()
            LOGGER.info(status)
        else:
            result = git_cmd.pull()
            LOGGER.info(f"Changes: {result}")

        for d in pathlib.Path(repo.working_tree_dir).joinpath(".features").iterdir():
            if d.is_file():
                continue
            LOGGER.debug(f"{d = }")
            repo_feature = git.Repo(d)
            LOGGER.debug(f"{repo_feature = }")
            LOGGER.debug(f"{repo_feature.working_dir = }")
            LOGGER.info(
                f"Checking for {pathlib.Path(repo_feature.working_dir).name} updates..."
            )
            repos["features"][
                pathlib.Path(repo_feature.working_dir).name
            ] = repo_feature
            git_cmd_feature = repo_feature.git
            if repo_feature.is_dirty():
                LOGGER.critical("Can't update: repo has uncommitted changes.")
                status_feature = git_cmd_feature.status()
                LOGGER.info(status_feature)
            else:
                result_feature = git_cmd_feature.pull()
                LOGGER.info(f"Changes: {result_feature}")
        # repo.git.pull()
        return

    elif any(sc == args.sub_command for sc in ["switch-branch"]):

        repos = {
            "engine": None,
            "features": {},
        }

        LOGGER.info("Switching branch for OpenStudioLandscapes Engine and Features...")
        repo = git.Repo(".")
        LOGGER.debug(f"{repo = }")
        LOGGER.debug(f"{repo.working_dir = }")
        # LOGGER.info(
        #     f"Checking for {pathlib.Path(repo.working_dir).name} (Engine) updates..."
        # )
        repos["engine"] = repo
        git_cmd = repo.git
        if repo.is_dirty():
            LOGGER.critical("Can't switch: repo has uncommitted changes.")
            status = git_cmd.status()
            LOGGER.info(status)
        else:
            result = git_cmd.checkout(args.branch)
            LOGGER.info(f"Checkout: {result}")

        for d in pathlib.Path(repo.working_tree_dir).joinpath(".features").iterdir():
            if d.is_file():
                continue
            LOGGER.debug(f"{d = }")
            repo_feature = git.Repo(d)
            LOGGER.debug(f"{repo_feature = }")
            LOGGER.debug(f"{repo_feature.working_dir = }")
            # LOGGER.info(
            #     f"Checking for {pathlib.Path(repo_feature.working_dir).name} updates..."
            # )
            repos["features"][
                pathlib.Path(repo_feature.working_dir).name
            ] = repo_feature
            git_cmd_feature = repo_feature.git
            if repo_feature.is_dirty():
                LOGGER.critical("Can't switch: repo has uncommitted changes.")
                status_feature = git_cmd_feature.status()
                LOGGER.info(status_feature)
            else:
                result_feature = git_cmd_feature.checkout(args.branch)
                LOGGER.info(f"Changes: {result_feature}")
        # repo.git.pull()
        return

    elif any(sc == args.sub_command for sc in ["clone-feature"]):
        # Todo
        #  - [x] rename install-feature to clone-feature, cause that's essentially what it is
        #  - [ ] for dependent Features, make sure to also install the parent (i.e. for Workers)
        repo_engine = git.Repo(".")
        repo_name = args.repo.split("/")[-1].replace(".git", "")

        repo_dir = pathlib.Path(repo_engine.working_dir).joinpath(
            ".features", repo_name
        )

        try:
            # Raises git.exc.InvalidGitRepositoryError if it is not a Git Repository
            repo = git.Repo(repo_dir)
            # Pull updates
            git_cmd = repo.git
            dirty = repo.is_dirty()
            if dirty:
                LOGGER.critical("Local repo has uncommitted changes.")
                # status = git_cmd.status()
                # LOGGER.info(status)
            # else:
            fetch = git_cmd.fetch()
            LOGGER.info(f"Fetch: {fetch}")
            status = git_cmd.status()
            LOGGER.info(f"Status: {status}")
            # if args.auto_update:
            if dirty:
                LOGGER.critical("Repo is dirty, auto-update skipped.")
            else:
                result_pull = git_cmd.pull()
                LOGGER.info(f"Changes: {result_pull}")
        except (
            # Directory exists but is not a Git repo:
            git.exc.InvalidGitRepositoryError,
            # Directory does not exist:
            git.exc.NoSuchPathError,
        ):
            # Clone if not cloned yet
            try:
                repo = git.Repo().clone_from(
                    url=args.repo,
                    to_path=pathlib.Path(repo_engine.working_dir).joinpath(
                        ".features", repo_name
                    ),
                )
                LOGGER.info(f"Repo {repo} cloned.")
            except git.exc.GitCommandError as git_command_error:
                LOGGER.error(f"Failed to clone repo {repo}: {git_command_error}")
                raise CLIException from git_command_error
        install_cmd = f"source {pathlib.Path(repo_engine.working_dir).joinpath('.venv', 'bin', 'activate')} && pip install --editable {repo.working_dir}"

        LOGGER.info(
            f"\n\nInstall Feature with:\n"
            f"\t`{install_cmd}`\n"
            f"\tIn Dagster: 'Reload definitions`.\n"
            f"\tthis will create:\n"
            f"\t- '<CONFIG_STORE>/{repo_name}/config.yml'\n"
            f"\tEdit this file according to your needs.\n\n"
        )

        return

    run_openstudiolandscapes(args)


# https://stackoverflow.com/a/1112350/2207196
def signal_handler(sig, frame):
    LOGGER.warning("You pressed Ctrl+C!")
    LOGGER.debug(f"{sig = }")
    LOGGER.debug(f"{frame = }")

    LOGGER.info(f"Shutting down OpenStudioLandscapes...")
    subprocess.run(
        [
            shutil.which("nox"),
            "--sessions",
            "dagster_postgres_down",
        ],
        shell=False,
    )
    LOGGER.info(f"Shut down successful.")

    # Clean shut down with return code 0
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(textwrap.dedent("""
            Wrong entry point.
            Use `openstudiolandscapes --help` for more information.
            """))
