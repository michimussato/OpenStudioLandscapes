__all__ = [
    "docker_build",
    "get_builder_by_name",
]

import pathlib
from typing import Iterator
from python_on_whales import docker, Builder, DockerClient, DockerException

from dagster import (
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.enums import *


def docker_build(
    context: AssetExecutionContext,
    docker_config: DockerConfig,
    context_path: pathlib.Path,
    builder: Builder,
    docker_use_cache: bool = True,
    image_data: dict = None,
    pull_all_tags: bool = True,
    push_all_tags: bool = True,
) -> str:

    _docker_config = docker_config.value

    # https://docs.docker.com/build/cache/backends/local/

    # docker run --rm -p 5010:5000 --name registry registry:latest
    # docker push localhost:5010/michimussato/base__build_docker_image:latest
    # docker pull localhost:5010/michimussato/base__build_docker_image:latest
    # docker run --rm -v /home/michael/git/repos/OpenStudioLandscapes/daemon.json:/etc/docker/daemon.json -p 5010:5000 --name registry registry:latest

    docker_client = DockerClient(
        client_call=["docker"],
        client_type="docker",
    )

    # in case we are logged in
    docker_client.logout()

    log: str = ""

    try:

        if not _docker_config["docker_use_local"]:
            server = _docker_config["docker_registry_url"]
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

        context.log.info(docker_client.info())

        image_path = image_data["image_path"]
        image_tags = image_data["image_tags"]
        parent_image: dict = image_data["image_parent"]

        tags = [f"{image_path}:{tag}" for tag in image_tags]

        stream: Iterator[str] = docker_client.buildx.build(
            context_path=context_path.as_posix(),
            cache=docker_use_cache,
            tags=tags,
            stream_logs=True,
            builder=builder,
            push=True,
            # pull=True,
            load=True,
            # **_extra_args,
        )

        for msg in stream:
            context.log.debug(msg)
            log += msg

    except Exception as e:

        context.log.exception(e)
        raise e

    finally:

        docker_client.logout()

    return log


def get_builder_by_name(
    context: AssetExecutionContext,
    builder_name: str,
) -> Builder:

    assert isinstance(builder_name, str)

    _builder = None

    builders = docker.buildx.list()
    context.log.info(builders)

    if not bool(builders):
        raise Exception("No builders found")

    for builder_ in builders:
        if builder_.name == builder_name:
            _builder = builder_

    if _builder is None:
        raise Exception(f"No builder called \"{builder_name}\" found")

    return _builder


# def _get_builder(
#         # client: DockerClient,
# ) -> Builder:
#
#     builder_name = "Driver-OpenStudioLandscapes"
#
#     try:
#         builder: Builder = docker.buildx.inspect(
#             x=builder_name,
#             bootstrap=True,
#         )
#     # except docker.errors.BuildError as e:
#     except Exception as e:
#         builder: Builder = docker.create(
#             driver=[
#                 "docker",
#                 "docker-container",
#                 "kubernetes",
#                 "remote",
#             ][1],
#             name=builder_name,
#             platforms=[
#                 "linux/amd64",
#             ],
#             use=True,
#             bootstrap=True,
#         )
#
#     return builder


"""
# Run Registry
# https://k21academy.com/docker-kubernetes/how-to-set-up-your-own-local-docker-registry-a-step-by-step-guide/
docker run --rm -v /home/michael/git/repos/OpenStudioLandscapes/daemon.json:/etc/docker/daemon.json -p 5000:5000 --name local-registry registry:latest

# Create Builder
export BUILDER_NAME=openstudiolandscapes-builder
docker buildx create --driver "docker-container" --name "${BUILDER_NAME}" --platform "linux/amd64" --bootstrap
# docker buildx use --builder "${BUILDER_NAME}"
# docker buildx use --builder "${BUILDER_NAME}" --default --global

    --cache-to "type=registry,ref=localhost:5000/michimussato/base__build_docker_image:1234" \
    --cache-to "type=registry,ref=localhost:5000/michimussato/base__build_docker_image:5678" \
    

# Build Image
docker buildx build \
    --load \
    --output "type=registry" \
    --builder "${BUILDER_NAME}" \
    --tag localhost:5000/michimussato/base__build_docker_image:1234 \
    --tag localhost:5000/michimussato/base__build_docker_image:5678 \
    --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-18_15-51-53__ed200ac53c1445c7b0b89c113fd43164/Base__Base/Base__build_docker_image/Dockerfiles/Dockerfile \
    /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-18_15-51-53__ed200ac53c1445c7b0b89c113fd43164/Base__Base/Base__build_docker_image/Dockerfiles
    
# Push Image
# docker push localhost:5000/michimussato/base__build_docker_image:1234
docker push --all-tags localhost:5000/michimussato/base__build_docker_image

# Pull Image
docker pull localhost:5000/michimussato/base__build_docker_image:1234

# Remove Builder
docker buildx rm "${BUILDER_NAME}"
"""