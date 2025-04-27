__all__ = [
    "docker_build",
]

import pathlib

from python_on_whales import DockerClient, Image, DockerException

from dagster import (
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.enums import *


"""
The workflow is as follows:

1. build image, i.e. with tag michimussato/new_image:tag-1234
2a. if no push, that's enough
2b. if push to dockhub, that's enough
  3. docker push michimussato/new_image:tag-1234
2c. if push to other registry, tag michimussato/new_image:tag-1234 with
    registry:port/michimussato/new_image:tag-1234
  3. if push registry:port/michimussato/new_image:tag-1234

4. pull image
  5a. if pull from dockerhub: docker pull michimussato/new_image:tag-1234
  5b. if pull from other registry: docker pull registry:port/michimussato/new_image:tag-1234
    6a. tag registry:port/michimussato/new_image:tag-1234 michimussato/new_image:tag-1234
"""



def docker_build(
    *,
    context: AssetExecutionContext,
    docker_config: DockerConfig,
    docker_file: pathlib.Path,
    context_path: pathlib.Path,
    docker_use_cache: bool = True,
    image_data: dict = None,
) -> list[str] | None:

    _docker_config = docker_config.value

    # https://docs.docker.com/build/cache/backends/local/

    docker_client = DockerClient(
        client_call=["docker"],
        client_type="docker",
    )

    # in case we are logged in
    docker_client.logout()

    log: str = ""

    try:

        server = f"{_docker_config['docker_registry_url']}:{_docker_config['docker_registry_port']}"

        if not _docker_config["docker_use_local"]:

            username = _docker_config.get("docker_registry_username", None)
            password = _docker_config.get("docker_registry_password", None)

            if not all([username, password]):
                raise Exception("Both username and password are required")

            context.log.debug("Attempting registry authentication...")
            try:
                docker_client.login(
                    server=server,
                    username=username,
                    password=password,
                )
                context.log.debug("Authentication successful.")
            except DockerException as e:
                context.log.exception(e)

        context.log.debug("docker_client.info() = %s", docker_client.info())

        image_name = image_data["image_name"]
        image_prefix_local = image_data["image_prefix_local"]
        image_prefix_full = image_data["image_prefix_full"]
        image_tags = image_data["image_tags"]
        parent_image: dict = image_data["image_parent"]

        context.log.debug(image_data)

        tags_local = [f"{image_prefix_local}{image_name}:{tag}" for tag in image_tags]
        tags_full = [f"{image_prefix_full}{image_name}:{tag}" for tag in image_tags]

        tags = [
            *tags_local,
            *tags_full,
        ]

        context.log.debug(tags)

        context.log.info(f"Building docker image {image_name}...")

        # maybe build and push in separate steps?

        # After an odyssey of trial and error frustration
        # using buildx I decided to continue with legacy_build here
        try:
            image: Image = docker_client.legacy_build(
                file=docker_file.as_posix(),
                context_path=context_path.as_posix(),
                cache=docker_use_cache,
                tags=tags,
                pull=True,
                dagster_context=context,
            )
        except DockerException as docker_e:

            context.log.exception(docker_e)
            raise Exception("Is Harbor running?") from docker_e

        context.log.info(f"Docker image successfully built: {image_name} ({image})")

        push = _docker_config["docker_push"]
        context.log.debug(f"Pushing image is {push}...")
        if push:
            context.log.debug(f"Pushing image {image_name}...")
            _docker_push(
                context=context,
                docker_client=docker_client,
                tags_full=tags_full,
            )
            context.log.debug(f"Push successful.")

    except Exception as e:

        context.log.exception(e)
        raise e

    finally:

        context.log.debug("Logging out from registry...")
        docker_client.logout()
        context.log.debug("Log out successful.")

    return tags


def _docker_push(
    context: AssetExecutionContext,
    docker_client: DockerClient,
    tags_full: list[str],
) -> None:

    context.log.info(f"Pushing {', '.join(tags_full)}...")

    try:
        docker_client.push(
            x=tags_full
        )
    except DockerException as e:
        context.log.exception(e)
        raise Exception("Can't push. Is Harbor running? Check "
                        "http://127.0.0.1:3000/assets/Compose_harbor/compose") from e

    context.log.info(f"Pushed {len(tags_full)} tag(s).")

    return None
