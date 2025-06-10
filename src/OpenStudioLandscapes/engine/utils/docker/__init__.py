__all__ = [
    "docker_build_cmd",
    "docker_push_cmd",
    "docker_process_cmds",
]

import shutil
import pathlib
import subprocess
from typing import Generator, MutableMapping, List

from dagster import AssetExecutionContext

from OpenStudioLandscapes.engine.utils import iterate_fds


class OpenStudioLandscapesDockerException(Exception):
    pass


def docker_build_cmd(
        context: AssetExecutionContext,
        docker_config_json: pathlib.Path,
        docker_file: pathlib.Path,
        tags_local: list[str],
        tags_full: list[str],
) -> list:

    # with buildx, the target command could look like:
    # /usr/bin/docker buildx build \
    #     --progress plain \
    #     --debug \
    #     --load \
    #     --tag tag1 \
    #     --tag tagN \
    #     --file /full/path/to/context/Dockerfile \
    #     /full/path/to/context

    cmd_build = [
        shutil.which("docker"),
        "--debug",
        "--config", docker_config_json.as_posix(),
        "build",
        "--progress", "plain",
        "--pull",
        "--file", docker_file.as_posix(),
        "--no-cache",
        # https://stackoverflow.com/a/11869360
        *[i(tag) for tag in tags_local for i in (lambda x: "--tag", lambda x: tag)],
        *[i(tag) for tag in tags_full for i in (lambda x: "--tag", lambda x: tag)],
        docker_file.parent.as_posix(),
    ]

    context.log.info(f"{cmd_build = }")
    context.log.info(f"{' '.join(cmd_build) = }")

    return cmd_build


def docker_push_cmd(
        context: AssetExecutionContext,
        docker_config_json: pathlib.Path,
        tags_full: list[str],
) -> list[list[str]]:

    push_cmds = []

    for tag in tags_full:

        cmd_push = [
            shutil.which("docker"),
            "--config", docker_config_json.as_posix(),
            "push",
            tag,
        ]

        push_cmds.append(cmd_push)

        context.log.info(f"{cmd_push = }")
        context.log.info(f"{' '.join(cmd_push) = }")

    return push_cmds


def docker_process_cmds(
        context: AssetExecutionContext,
        cmds: list[str],
) -> Generator[MutableMapping[str, List[str]], None, None]:

    for cmd in cmds:

        context.log.info(f"Processing command: \"{' '.join(cmd)}\"")

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        handles = (proc.stdout, proc.stderr)
        labels = ("stdout", "stderr")
        functions = (context.log.debug, context.log.debug)
        logs = iterate_fds(
            handles=handles,
            labels=labels,
            functions=functions,
            live_print=True,
        )

        for _label, _function in zip(labels, functions):
            if bool(logs[_label]):
                _function(logs[_label])

        logs_ = {
            "cmd": cmd,
            "stdout": logs["stdout"],
            "stderr": logs["stderr"],
        }

        returncode = proc.poll()
        context.log.debug(f"{returncode = }")

        if bool(returncode):
            err_ = "\n".join(logs_["stderr"])
            context.log.error(err_)
            str_ = ""
            str_ += f"Command failed {returncode = }: {cmd = }\n"
            str_ += "Is Harbor running? Try `nox --session harbor_up` or `nox --session harbor_up_detach`.\n"
            str_ += "\n"
            str_ += "Full trace:\n"
            str_ += err_
            raise OpenStudioLandscapesDockerException(str_)

        yield logs_
