__all__ = [
    "docker_build_cmd",
    "docker_push_cmd",
    "docker_do",
]

import pathlib
import shutil
from typing import List, Union, Dict, Any

from dagster import (
    AssetExecutionContext,
    OpExecutionContext,
)

from OpenStudioLandscapes.engine.enums import DockerProgress

from OpenStudioLandscapes.DagsterCodeLocation.StreamingProcess import submit_cmds


class OpenStudioLandscapesDockerException(Exception):
    pass


# Todo
#  - [ ] refactor shutil.which


def docker_build_cmd(
    context: Union[OpExecutionContext, AssetExecutionContext],
    docker_config_json: pathlib.Path,
    docker_file: pathlib.Path,
    tags: List[str],
    pull: bool,
    target: Union[str, None] = None,
    no_cache: bool = False,
    build_context: Union[None, pathlib.Path] = None,
    env: Union[None, Dict] = None,
    build_args: Union[None, Dict[str, str]] = None,
    *args,
) -> Dict[str, List | Dict | Dict[Any, Any]]:
    """
    Returns single a dictionary with the command as a list
    and the desired environment.

    Args:
        build_args:
            - https://docs.docker.com/reference/cli/docker/buildx/build/#build-arg
            - https://docs.docker.com/reference/dockerfile/#arg
        context:
        docker_config_json:
        docker_file:
        tags:
        pull:
        target:
        no_cache:
        build_context:
        env:

    Returns:

    """

    if env is None:
        env = {}

    if build_args is None:
        build_args = {}

    _build_args: List[str] = []
    for key, value in build_args.items():
        _build_args.append(f"--build-arg={key}={value}")

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
        f"--config={docker_config_json.as_posix()}",
        "build",
        *_build_args,
        f"--target={target}" if target else None,
        f"--progress={DockerProgress.PLAIN}",
        f"--pull={bool(pull)}",
        f"--file={docker_file.as_posix()}",
        *args,
        f"--no-cache={bool(no_cache)}",
        # https://stackoverflow.com/a/11869360
        #*[i(tag) for tag in tags for i in (lambda x: "--tag", lambda x: tag)],
        *[f"--tag={tag}" for tag in tags],
        build_context.as_posix() if build_context else docker_file.parent.as_posix(),
    ]

    # As cmd_build_ can have falsy values, we filter them out
    cmd_build = list(filter(None, cmd_build_))

    cmd_dict = {
        "cmd": cmd_build,
        "env": env,
    }

    context.log.info(f"docker_build_cmd: {cmd_dict}")
    context.log.info(f"docker_build_cmd (as str): {' '.join(cmd_dict['cmd'])}")

    return cmd_dict


def docker_push_cmd(
    context: Union[OpExecutionContext, AssetExecutionContext],
    docker_config_json: pathlib.Path,
    tags_full: List[str],
    env: Union[None, Dict] = None,
) -> List[Dict[str, List | Dict]]:
    """
    Returns a list (one for each tag) of dictionaries with the command as a list
    together with the desired environment.

    Args:
        context:
        docker_config_json:
        tags_full:
        env:

    Returns:
        List[Dict[str, List | Dict]]
    """

    if env is None:
        env = {}

    push_cmds = []

    for tag in tags_full:

        cmd_push = [
            shutil.which("docker"),
            "--config",
            docker_config_json.as_posix(),
            "push",
            tag,
        ]

        cmd_dict = {
            "cmd": cmd_push,
            "env": env,
        }

        push_cmds.append(cmd_dict)

        context.log.info(f"docker_push_cmd: {cmd_dict}")
        context.log.info(f"docker_push_cmd (as str): {' '.join(cmd_dict['cmd'])}")

    return push_cmds


# An alias for submit_cmds so that we don't
# have to refactor all OpenStudioLandscapes (yet)
# Todo
#  - [ ] replace references to `docker_do`
docker_do = submit_cmds
