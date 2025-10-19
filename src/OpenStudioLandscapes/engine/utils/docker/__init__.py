__all__ = [
    "docker_build_cmd",
    "docker_push_cmd",
    "docker_process_cmds",
]

import pathlib
import queue
import threading
import shlex
import shutil
import subprocess
from typing import Generator, List, MutableMapping, Any

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
        "--config",
        docker_config_json.as_posix(),
        "build",
        "--progress",
        "plain",
        "--pull",
        "--file",
        docker_file.as_posix(),
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
        for line in iter(self.stream.readline, b''):
            self.output_queue.put(line.decode().strip())


def execute_in_threads(
        context: AssetExecutionContext,
        command: str,
) -> Generator[int | Any, None, None]:

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
        try:
            while not stdout_queue.empty():
                stdout = stdout_queue.get()
                context.log.debug(f"{stdout = }")
                yield stdout
                stdout = None
                # print('STDOUT:', stdout_queue.get())
            while not stderr_queue.empty():
                stderr = stderr_queue.get()
                context.log.debug(f"{stderr = }")
                yield stderr
                stderr = None
                # print('STDERR:', stderr_queue.get())

            returncode = process.poll()
            if returncode is not None:
                context.log.debug(f"{returncode = }")
                yield f"{returncode = }"
                break
        except KeyboardInterrupt as e:
            context.log.error(e)
            break


def docker_process_cmds(
    context: AssetExecutionContext,
    cmds: list[list[str]],
) -> Generator[int | Any, Any, None]:

    for cmd in cmds:

        context.log.info(f"Processing command: \"{' '.join(cmd)}\"")

        for s in execute_in_threads(
            context=context,
            command=shlex.join(cmd),
        ):
            # context.log.info(s)
            yield s
