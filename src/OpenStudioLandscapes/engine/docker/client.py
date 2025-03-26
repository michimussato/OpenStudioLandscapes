__all__ = [
    "get_docker_client",
    "build",
    "docker_push",
]

import pathlib
from typing import Union

import docker

from dagster import (
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.enums import DockerConfig


def get_docker_client(
    context: AssetExecutionContext,
    docker_config: DockerConfig,
    timeout: int = 600,
) -> docker.APIClient:

    client = docker.APIClient(
        timeout=timeout,
    )

    _docker_config = docker_config.value

    registry = _docker_config.get("docker_registry_url", "docker.io")
    username = _docker_config.get("docker_registry_username", None)
    password = _docker_config.get("docker_registry_password", None)

    if all([username, password]):
        context.log.debug(f"Logging in to {registry}...")
        client.login(
            registry=registry,
            username=username,
            password=password,
        )

        context.log.debug("Log successful.")

    elif username or password:
        raise RuntimeError("Docker registry username and password are required")

    else:
        context.log.debug(f"No log in credentials to {registry} provided.")

    return client


def build(
    *,
    context: AssetExecutionContext,
    client: docker.APIClient,
    docker_config: DockerConfig,
    docker_context: pathlib.Path,
    docker_file: pathlib.Path,
    use_cache: bool,
    image_data: dict,
) -> str:

    _docker_config = docker_config.value

    # https://stackoverflow.com/a/48232574
    # https://peps.python.org/pep-0448/
    *response, final_msg = client.build(
        path=docker_context.as_posix(),
        dockerfile=docker_file.as_posix(),
        nocache=not use_cache,
        encoding="utf-8",
        decode=True,
        # tag="asdf"
    )

    for chunk in response:
        recurse_chunk(context, chunk)

    context.log.debug(final_msg["stream"])
    image_id = str(final_msg["stream"]).rstrip().split(" ")[-1]
    context.log.info(f"{image_id = }")

    return image_id


def docker_push(
    context: AssetExecutionContext,
    docker_client: docker.APIClient,
    image_path: str,
    tag: str,
    stream: bool = True,
    decode: bool = True,
):
    """
    Limit concurrent uploads:
    - https://stackoverflow.com/a/48348339

    ```
    Open /etc/docker/daemon.json and add:

    {
        "max-concurrent-uploads": 1
    }
    ```

    """

    retries = 5

    for trial in range(retries):

        retries += 1

        if trial <= retries:
            context.log.warning(f"Attempt {retries} out of {retries}...")

        else:
            raise Exception(f"Failed to push image {image_path}. "
                            f"Giving up after {retries} attempts.")

        try:
            response = docker_client.push(
                repository=image_path,
                tag=tag,
                stream=stream,
                decode=decode,
            )

            for chunk in response:
                # context.log.debug(chunk)
                recurse_chunk(context, chunk)
                if "error" in chunk:
                    raise Exception(f"{chunk['error']} (Detail: {chunk['errorDetail']})")

        except Exception as e:
            context.log.error(e)

    # context.log.debug(final_msg["stream"])
    # image_id = str(final_msg["stream"]).rstrip().split(" ")[-1]
    # context.log.info(f"{image_id = }")
    #
    # return image_id


def recurse_chunk(
        context: AssetExecutionContext,
        chunk: Union[dict, str],
) -> None:

    if isinstance(chunk, dict):
        for key, value in chunk.items():
            recurse_chunk(context, value)
    elif isinstance(chunk, str):
        context.log.debug(chunk)