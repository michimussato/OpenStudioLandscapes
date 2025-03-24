__all__ = [
    "docker_buildx_build",
    "get_builder_by_name",
]

import pathlib
import shutil
import subprocess
from python_on_whales import docker, Builder

from dagster import (
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *


def docker_buildx_build(
        context: AssetExecutionContext,
        docker_config: DockerConfig,
        context_path: pathlib.Path,
        docker_file: pathlib.Path,
        # docker_use_cache: bool,
        # builder: Builder,
        image_data: dict,
) -> dict[str, str]:

    _docker_config = docker_config.value

    ret = {}

    context.log.warning(docker_config.value)

    docker_repository = _docker_config["docker_repository"]  # 'michimussato'
    docker_registry_url = _docker_config["docker_registry_url"]  # 'localhost'
    docker_registry_port = _docker_config["docker_registry_port"]  # '5000'


    context.log.warning(image_data)

    image_name = image_data["image_name"]  # 'base_build_docker_image'
    image_path = image_data["image_path"]  # 'localhost:5000/michimussato/base_build_docker_image'
    image_tags = image_data["image_tags"]  # ['2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1']

    _tags_local = []
    _tags_registry = []
    for image_tag in image_tags:
        tags_local = f"{docker_repository}/{image_name}:{image_tag}"  # michimussato/base_build_docker_image:2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1
        _tags_local.append(tags_local)
        ret["tags_local"] = tags_local

        tags_registry = f"{docker_registry_url}:{docker_registry_port}/{docker_repository}/{image_name}:{image_tag}"  # michimussato/base_build_docker_image:2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1
        _tags_registry.append(tags_registry)
        ret["tags_registry"] = tags_registry

    # login

    server = _docker_config["docker_registry_url"]

    cmd_login = []

    if not _docker_config["docker_use_local"]:

        username = _docker_config.get("docker_registry_username", None)
        password = _docker_config.get("docker_registry_password", None)

        if not all([username, password]):
            raise Exception("Both username and password are required")

        cmd_login.extend([
            shutil.which("docker"),
            "--username", username,
            "--password", password,
            server,
        ])

    context.log.warning(" ".join(cmd_login))

    # build image

    logs = {}

    cmd_build = [
        shutil.which("docker"),
        "buildx",
        "build",
        "--progress", ["auto", "quiet", "plain", "tty", "rawjson"][2],
        "--debug",
        "--load",
        # "--output", "\"type=registry\"",
        # "--builder", f"\"{builder.name}\"",
    ]

    for tag in _tags_local:
        cmd_build.extend(["--tag", tag])

    cmd_build.extend([
        "--file", docker_file.as_posix(),
        context_path.as_posix(),
    ])

    context.log.warning(" ".join(cmd_build))

    proc_build = subprocess.Popen(
        cmd_build,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    handles_build = (proc_build.stdout, proc_build.stderr)
    labels_build = ("stdout", "stderr")
    functions_build = (context.log.info, context.log.debug)
    logs["build"] = iterate_fds(
        handles=handles_build,
        labels=labels_build,
        functions=functions_build,
        live_print=True,
    )

    # push image

    context.log.warning(f"{_tags_local = }")
    context.log.warning(f"{_tags_registry = }")

    ## tag image

    for _tag in _tags_local:
        cmd_tag = [
            shutil.which("docker"),
            "image",
            "tag",
            _tag,
            _tags_registry[_tags_local.index(_tag)],
        ]

        context.log.warning(" ".join(cmd_tag))

        proc_tag = subprocess.Popen(
            cmd_tag,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        handles_tag = (proc_tag.stdout, proc_tag.stderr)
        labels_tag = ("stdout", "stderr")
        functions_tag = (context.log.info, context.log.debug)
        logs[f"tag_{_tag}"] = iterate_fds(
            handles=handles_tag,
            labels=labels_tag,
            functions=functions_tag,
            live_print=True,
        )

        cmd_push = [
            shutil.which("docker"),
            "image",
            "push",
            _tags_registry[_tag.index(_tag)],
        ]

        context.log.warning(" ".join(cmd_push))

        proc_push = subprocess.Popen(
            cmd_push,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        handles_push = (proc_push.stdout, proc_push.stderr)
        labels_push = ("stdout", "stderr")
        functions_push = (context.log.info, context.log.debug)
        logs[f"push_{_tag}"] = iterate_fds(
            handles=handles_push,
            labels=labels_push,
            functions=functions_push,
            live_print=True,
        )

    # or:

    # cmd_push = [
    #     shutil.which("docker"),
    #     "image",
    #     "push",
    #     "--all-tags",
    #     _tags_registry[_tag.index(_tag)], minus tag
    # ]

    return ret


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
