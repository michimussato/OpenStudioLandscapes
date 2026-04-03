__all__ = [
    "docker_build_cmd",
    "docker_push_cmd",
    "docker_do",
]

import pathlib
import shutil
from typing import List, Union

from dagster import AssetExecutionContext, OpExecutionContext, get_dagster_logger

from OpenStudioLandscapes.DagsterCodeLocation.StreamingProcess import submit_cmds

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


# An alias for submit_cmds so that we don't
# have to refactor all OpenStudioLandscapes (yet)
# Todo
#  - [ ] replace references to `docker_do`
docker_do = submit_cmds
