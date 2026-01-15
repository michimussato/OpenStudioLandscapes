import argparse
import pathlib

import git
import logging
import shutil
import signal
import subprocess
import sys
import textwrap

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__url__ = "https://github.com/michimussato/OpenStudioLandscapes"
__license__ = "GNU Affero General Public License v3.0"

LOGGER = logging.getLogger(__name__)


# ---- Python API ----


def run_openstudiolandscapes_postgres(args):
    LOGGER.info("Welcome!")
    LOGGER.info("OpenStudioLandscapes args: %s", args)

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
        "--pull",
        dest="pull",
        default=False,
        action="store_true",
        required=False,
        help="git pull.",
    )

    subparsers = parser.add_subparsers(
        dest="sub_command",
        required=False,
    )

    subparser_install_feature = subparsers.add_parser(
        "install-feature",
        aliases=["if"],
    )

    subparser_install_feature.add_argument(
        "--repo",
        "-r",
        dest="repo",
        metavar="REPO",
        # type=git.Repo,
        type=str,
        required=True,
    )

    subparser_install_feature.add_argument(
        "--feature-name",
        "-n",
        dest="feature_name",
        metavar="FEATURE_NAME",
        # type=git.Repo,
        type=str,
        required=True,
    )

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
                "Dependency '%s' is not installed" % f"{dep} ({params['executable']})"
            )
        except AssertionError as e:
            msg = textwrap.dedent(
                """
                #########################################################
                Dependencies not fulfilled.
                Maybe you forgot to run `make sys_deps_install`?
                #########################################################
                IMPORTANT: Reboot system after installing dependencies!!!
                #########################################################
                """
            )
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


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    LOGGER.info(f"Launching OpenStudioLandscapes...")

    checks(args)

    if args.pull:

        repos = {
            "engine": None,
            "features": {},
        }

        LOGGER.info("Updating OpenStudioLandscapes...")
        repo = git.Repo(".")
        repos["engine"] = repo
        LOGGER.debug(f"{repo = }")
        git_cmd = repo.git
        if repo.is_dirty():
            LOGGER.error("Can't update: repo has uncommitted changes.")
            status = git_cmd.status()
            LOGGER.info(status)
        else:
            git_cmd.pull()

        for d in pathlib.Path(repo.working_tree_dir).joinpath(".features").iterdir():
            if d.is_file():
                continue
            LOGGER.debug(f"{d = }")
            repo_feature = git.Repo(d)
            LOGGER.info(f"{repo_feature.working_dir = }")
            repos["features"][pathlib.Path(repo_feature.working_dir).name] = repo_feature
            LOGGER.info(f"{repo_feature = }")
            git_cmd_feature = repo_feature.git
            if repo_feature.is_dirty():
                LOGGER.error("Can't update: repo has uncommitted changes.")
                status_feature = git_cmd_feature.status()
                LOGGER.info(status_feature)
            else:
                git_cmd_feature.pull()
        # repo.git.pull()
        return

    elif any(sc == args.sub_command for sc in ["install-feature", "if"]):
        repo_engine = git.Repo(".")
        repo = git.Repo().clone_from(
            url=args.repo,
            to_path=pathlib.Path(repo_engine.working_dir).joinpath(".features", args.feature_name),
        )
        LOGGER.info(f"Repo {repo} cloned.")
        LOGGER.info(f"Install Feature with:\n\t`source {pathlib.Path(repo_engine.working_dir).joinpath('.venv', 'bin', 'activate')} && pip install --editable {repo.working_dir}`")
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
    raise SystemExit(
        textwrap.dedent(
            """
            Wrong entry point.
            Use `openstudiolandscapes --help` for more information.
            """
        )
    )
