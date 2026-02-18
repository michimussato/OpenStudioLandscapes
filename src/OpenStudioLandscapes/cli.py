import argparse
import logging
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import textwrap

import git

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__url__ = "https://github.com/michimussato/OpenStudioLandscapes"
__license__ = "GNU Affero General Public License v3.0"

LOGGER = logging.getLogger(__name__)


class CLIException(Exception):
    pass


# ---- Python API ----


def run_openstudiolandscapes_postgres(args):
    LOGGER.info("Welcome!")
    LOGGER.info("OpenStudioLandscapes args: %s", args)

    if bool(int(args.attach_grafana_alloy_to_compose_scope)):
        os.environ["OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE"] = "1"
    if bool(int(args.attach_pangolin_site_to_compose_scope)):
        os.environ["OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE"] = "1"
    if bool(int(args.run_as_systemd_unit)):
        os.environ["OPENSTUDIOLANDSCAPES__RUN_AS_SYSTEMD_UNIT"] = "1"
    if bool(int(args.run_as_systemd_unit)):
        os.environ["OPENSTUDIOLANDSCAPES__RUN_AS_SYSTEMD_UNIT"] = "1"
    if args.domain_wan is not None:
        os.environ["OPENSTUDIOLANDSCAPES__DOMAIN_WAN"] = args.domain_wan

    os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT"] = args.config_store
    os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS"] = args.config_store_vcs

    if args.landscapes_root is not None:
        os.environ["OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT"] = args.landscapes_root

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
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
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

    # Todo
    #  - [ ] is this still needed?
    parser.add_argument(
        "--run-as-systemd-unit",
        dest="run_as_systemd_unit",
        metavar="OPENSTUDIOLANDSCAPES__RUN_AS_SYSTEMD_UNIT",
        default=os.environ.get("OPENSTUDIOLANDSCAPES__RUN_AS_SYSTEMD_UNIT", "0"),
        action="store_const",
        const="1",
        required=False,
        help="If specified, the discovery service will *not* wait for "
        "human interaction for incomplete "
        "`config.yml` files to be fixed. You will have to "
        "monitor the logs (`journald`) in this case.",
    )

    parser.add_argument(
        "--domain-wan",
        dest="domain_wan",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__DOMAIN_WAN",
        default=os.environ.get("OPENSTUDIOLANDSCAPES__DOMAIN_WAN", None),
        # action="store_true",
        required=False,
        help="Set the WAN domain name (i.e. openstudiolandscapes.com).",
    )

    parser.add_argument(
        "--config-store",
        dest="config_store",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
            "~/.config/OpenStudioLandscapes/config-store",
        ),
        # action="store_true",
        required=False,
        help="Set the configuration store path.",
    )

    parser.add_argument(
        "--config-store-vcs",
        dest="config_store_vcs",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS",
            "~/.config/OpenStudioLandscapes/config-store",
        ),
        # action="store_true",
        required=False,
        help="If the config store is part of a Git repository already, "
        "you can specify the path to the repo here. Defaults to the same "
        "value like `OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT`.",
    )

    parser.add_argument(
        "--landscapes-root",
        dest="landscapes_root",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT",
            None,
        ),
        # action="store_true",
        required=False,
        help="Set the Landscape root path. A `.landscapes` "
        "subdirectory will be created and used.",
    )

    parser.add_argument(
        "--landscapes-id",
        dest="landscapes_id",
        type=str,
        metavar="OPENSTUDIOLANDSCAPES__LANDSCAPE_ID",
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__LANDSCAPE_ID",
            None,
        ),
        # action="store_true",
        required=False,
        help="Lock the landscape_id to this value.",
    )

    update_group = parser.add_mutually_exclusive_group(required=False)

    update_group.add_argument(
        "--skip-update-check",
        dest="skip_update_check",
        # type=str,
        # metavar="OPENSTUDIOLANDSCAPES__LANDSCAPE_ID",
        default=False,
        action="store_true",
        required=False,
        help="Skip checking for codebase updates.",
    )

    update_group.add_argument(
        "--auto-update",
        dest="auto_update",
        # type=str,
        # metavar="OPENSTUDIOLANDSCAPES__LANDSCAPE_ID",
        default=False,
        action="store_true",
        required=False,
        help="Automatically pull codebase updates.",
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

    # Todo
    #  - [x] "install-feature" should actually be "clone-feature" (it's not actually installing)
    subparser_install_feature = subparsers.add_parser(
        "clone-feature",
        # aliases=["install-feature"],
        help="Clone a feature from a given repository and "
        "print installation instructions.",
    )

    # Todo
    #  - [ ] set branch, default=main `--branch`

    subparser_install_feature.add_argument(
        "--repo",
        "-r",
        dest="repo",
        metavar="REPO",
        # type=git.Repo,
        type=str,
        required=True,
    )

    # subparser_install_feature.add_argument(
    #     "--feature-name",
    #     "-n",
    #     dest="feature_name",
    #     metavar="FEATURE_NAME",
    #     # type=git.Repo,
    #     type=str,
    #     required=True,
    # )

    # parser.add_argument(
    #     "--uniform",
    #     dest="uniform",
    #     default=False,
    #     action="store_true",
    #     required=False,
    #     help="Use uniform color columns.",
    # )
    #
    # parser.add_argument(
    #     "--out-dir",
    #     dest="out_dir",
    #     metavar="OUT_DIR",
    #     required=False,
    #     default=pathlib.Path().cwd(),
    #     type=pathlib.Path,
    #     help="Where to save the output file.",
    # )
    #
    # parser.add_argument(
    #     "--width",
    #     dest="width",
    #     metavar="WIDTH",
    #     required=False,
    #     default=2560,
    #     type=int,
    #     help="Width of the barcoded image.",
    # )
    #
    # parser.add_argument(
    #     "--height",
    #     dest="height",
    #     metavar="HEIGHT",
    #     required=False,
    #     default=1280,
    #     type=int,
    #     help="Height of the barcoded image.",
    # )
    #
    # parser.add_argument(
    #     "--sample-height",
    #     dest="sample_height",
    #     metavar="SAMPLE_HEIGHT",
    #     required=False,
    #     default=8,
    #     type=int,
    #     help="Sample Height of the barcoded image. "
    #          "In compressed mode, each frame is resized into a 1xSAMPLE_HEIGHT vector. "
    #          "SAMPLE_HEIGHT should be at most the input height and at least 1 (which "
    #          "is equivalent to uniform mode). Smaller values yield smoother results.",
    # )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    loglevel = loglevel or logging.INFO
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def checks(args):
    LOGGER.info("Checking OpenStudioLandscapes dependencies...")

    def check_sys_deps():
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
            # "Foo": {
            #     "executable": "foo",
            #     "version": "-V",
            # },
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

    check_sys_deps()

    def check_updates_available():
        # https://knowledge.buka.sh/how-to-check-for-remote-git-changes-without-pulling/

        # if any(sc == args.sub_command for sc in ["update"]):

        repos = {
            "engine": None,
            "features": {},
        }

        LOGGER.info("Checking for OpenStudioLandscapes Engine and Features updates...")
        repo = git.Repo(".")
        LOGGER.debug(f"{repo = }")
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
        if args.auto_update:
            if dirty:
                LOGGER.critical("Repo is dirty, auto-update skipped.")
            else:
                result_pull = git_cmd.pull()
                LOGGER.info(f"Changes: {result_pull}")

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
            if args.auto_update:
                if dirty:
                    LOGGER.critical("Repo is dirty, auto-update skipped.")
                else:
                    result_pull_feature = git_cmd_feature.pull()
                    LOGGER.info(f"Changes: {result_pull_feature}")
        # repo.git.pull()
        return

    if not args.skip_update_check:
        check_updates_available()


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
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

    elif any(sc == args.sub_command for sc in ["clone-feature", "if"]):
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

        # result_ = subprocess.run(
        #     install_cmd,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT,
        #     shell=True,
        #     cwd=pathlib.Path(repo_engine.working_dir),
        # )
        #
        # result = result_.stdout.decode().strip()
        #
        # LOGGER.info(f"{result = }")

        return

    run_openstudiolandscapes(args)
    # ret = run_openstudiolandscapes(args)
    #
    # sys.exit(ret)


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
