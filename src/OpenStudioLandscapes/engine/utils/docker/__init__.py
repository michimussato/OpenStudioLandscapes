__all__ = [
    "docker_build_cmd",
    "docker_push_cmd",
    "docker_do",
]

import pathlib
import queue
import shlex
import shutil
import subprocess
import threading
from typing import Any, Generator, List, Union

from dagster import AssetExecutionContext, OpExecutionContext, get_dagster_logger

LOGGER = get_dagster_logger(__name__)


class OpenStudioLandscapesDockerException(Exception):
    pass


def docker_build_cmd(
    context: Union[OpExecutionContext, AssetExecutionContext],
    docker_config_json: pathlib.Path,
    docker_file: pathlib.Path,
    tags: List[str],
    pull: bool,
    no_cache: bool = False,
    build_context: Union[None, pathlib.Path] = None,
) -> List:

    # with buildx, the target command could look like:
    # /usr/bin/docker buildx build \
    #     --progress plain \
    #     --debug \
    #     --load \
    #     --tag tag1 \
    #     --tag tagN \
    #     --file /full/path/to/context/Dockerfile \
    #     /full/path/to/context

    cmd_build_ = [
        shutil.which("docker"),
        "--debug",
        "--config",
        docker_config_json.as_posix(),
        "build",
        "--progress",
        "plain",
        "--pull" if pull else None,
        "--file",
        docker_file.as_posix(),
        "--no-cache" if no_cache else None,
        # https://stackoverflow.com/a/11869360
        *[i(tag) for tag in tags for i in (lambda x: "--tag", lambda x: tag)],
        build_context.as_posix() if build_context else docker_file.parent.as_posix(),
    ]

    # As cmd_build_ can have falsy values, we filter them out
    cmd_build = list(filter(None, cmd_build_))

    context.log.info(f"{cmd_build = }")
    context.log.info(f"{' '.join(cmd_build) = }")

    return cmd_build


def docker_push_cmd(
    context: Union[OpExecutionContext, AssetExecutionContext],
    docker_config_json: pathlib.Path,
    tags_full: List[str],
) -> List[List[str]]:

    push_cmds = []

    for tag in tags_full:

        cmd_push = [
            shutil.which("docker"),
            "--config",
            docker_config_json.as_posix(),
            "push",
            tag,
        ]

        push_cmds.append(cmd_push)

        context.log.info(f"{cmd_push = }")
        context.log.info(f"{' '.join(cmd_push) = }")

    return push_cmds


class OutputReader(threading.Thread):
    def __init__(self, stream, output_queue):
        threading.Thread.__init__(self)
        self.stream = stream
        self.output_queue = output_queue

    def run(self):
        for line in iter(self.stream.readline, b""):
            self.output_queue.put(line.decode().strip())


def execute_in_threads(
    command: str,
) -> Generator[str | Any, None, None]:

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()

    stdout_reader = OutputReader(process.stdout, stdout_queue)
    stderr_reader = OutputReader(process.stderr, stderr_queue)

    stdout_reader.start()
    stderr_reader.start()

    while True:
        # Todo:
        #  - [ ] could run in two threads
        while not stdout_queue.empty():
            stdout = "stdout: %s" % stdout_queue.get()
            yield stdout
        while not stderr_queue.empty():
            stderr = "stderr: %s" % stderr_queue.get()
            yield stderr

        returncode = process.poll()
        if returncode is not None:
            returncode_msg = "return code: %i" % returncode
            if returncode != 0:
                raise OpenStudioLandscapesDockerException(
                    f"Image not built successfully. {returncode = }"
                )
            yield returncode_msg
            break


def docker_process_cmds(
    context: Union[OpExecutionContext, AssetExecutionContext],
    cmds: List[List[str]],
) -> Generator[str | Any, Any, None]:

    for cmd in cmds:

        context.log.info(f"Processing command: \"{' '.join(cmd)}\"")

        for s in execute_in_threads(
            command=shlex.join(cmd),
        ):
            yield s


def docker_do(
    context: Union[OpExecutionContext, AssetExecutionContext],
    cmds: List[List[str]],
) -> List[str]:
    """
    Args:
        context: Union[OpExecutionContext, AssetExecutionContext]
        cmds: list of commands to execute

    Returns:
        list[str]: all collected records (stdout, stderr, return code)
    """

    records = []

    for record in docker_process_cmds(
        context=context,
        cmds=cmds,
    ):
        context.log.info(record)
        records.append(record)

    return records
