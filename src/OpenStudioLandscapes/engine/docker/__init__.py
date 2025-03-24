__all__ = [
    "docker_buildx_build",
    "docker_run_registry",
    # "docker_build",
    "get_builder_by_name",
]

import pathlib
import shutil
import subprocess
from typing import Iterator
import docker as docker_py
from docker.models.containers import Container
from docker.types.services import Mount
from python_on_whales import docker, Builder, DockerClient, DockerException

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


def docker_run_registry(
        context: AssetExecutionContext,
        detach: bool,
        domainname: str,
        container_name: str,
        host_name: str,
        # publish: list[str],
        volumes: list[tuple],
        mounts: list[dict],
        docker_config: DockerConfig,
        # context_path: pathlib.Path,
        # docker_file: pathlib.Path,
        # # docker_use_cache: bool,
        # # builder: Builder,
        # image_data: dict,
) -> Container:
# ) -> dict[str, str]:

    client = docker_py.from_env()
    containers = client.containers.list()

    registry_is_running = False
    container_registry = None

    for container in containers:
        if container.name == container_name:
            registry_is_running = True
            container_registry = container
            context.log.info(f"Container {container.name} is running already. Leaving as is.")
            return container_registry

    publish = {
        f"{str(docker_config.value['docker_registry_port']) or '5000'}": 5000,
    }

    # publishes = []
    # for publish_ in publish:
    #     publishes.extend(
    #         [
    #             "--publish",
    #             publish_,
    #         ]
    #     )

    volumes_ = []
    for volume in volumes:
        volumes_.append(
            ":".join(volume),
        )

    mounts_ = []
    for mount in mounts:
        mounts_.append(
            Mount(**mount)
        )

    container_registry = client.containers.run(
        image="docker.io/registry:2",
        remove=True,
        detach=True,
        domainname=domainname,
        hostname=host_name,
        name=container_name,
        ports=publish,
        stream=True,
        volumes=volumes_,
        mounts=mounts_,
    )

    return container_registry

    ret = {}

    # context.log.warning(docker_config.value)
    #
    # docker_repository = docker_config.value["docker_repository"]  # 'michimussato'
    # docker_registry_url = docker_config.value["docker_registry_url"]  # 'localhost'
    # docker_registry_port = docker_config.value["docker_registry_port"]  # '5000'
    #
    #
    # context.log.warning(image_data)
    #
    # image_name = image_data["image_name"]  # 'base_build_docker_image'
    # image_path = image_data["image_path"]  # 'localhost:5000/michimussato/base_build_docker_image'
    # image_tags = image_data["image_tags"]  # ['2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1']
    #
    # _tags_local = []
    # _tags_registry = []
    # for image_tag in image_tags:
    #     tags_local = f"{docker_repository}/{image_name}:{image_tag}"  # michimussato/base_build_docker_image:2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1
    #     _tags_local.append(tags_local)
    #     ret["tags_local"] = tags_local
    #
    #     tags_registry = f"{docker_registry_url}:{docker_registry_port}/{docker_repository}/{image_name}:{image_tag}"  # michimussato/base_build_docker_image:2025-03-23_14-56-19__586373b4553841cfadf3713e37d2e9e1
    #     _tags_registry.append(tags_registry)
    #     ret["tags_registry"] = tags_registry
    #
    # # build image
    #
    # logs = {}

    cmd_run = [
        shutil.which("docker"),
        "container",
        "run",
        "--domainname", domainname,
        "--hostname", host_name,
        # "--mount", "source=local-registry-vol,destination=/var/lib/registry",
        "--name", container_name,
        "--rm",
        # "--volume", "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/docker/daemon.json:/etc/docker/daemon.json:ro",
    ]

    for publish_ in publish:
        cmd_run.extend(
            [
                "--publish",
                publish_,
            ]
        )

    for volume in volumes:
        cmd_run.extend(
            [
                "--volume",
                ":".join(volume),
            ]
        )

    for mount in mounts:
        cmd_run.extend(
            [
                "--mount",
                ",".join(mount),
            ]
        )

    cmd_run.append("registry:2")

    if detach:
        cmd_run.append("--detach")

    context.log.warning(cmd_run)
    context.log.warning(" ".join(cmd_run))

    # proc_build = subprocess.Popen(
    #     cmd_run,
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )
    #
    # handles_run = (proc_build.stdout, proc_build.stderr)
    # labels_run = ("stdout", "stderr")
    # functions_run = (context.log.info, context.log.debug)
    # logs["build"] = iterate_fds(
    #     handles=handles_run,
    #     labels=labels_run,
    #     functions=functions_run,
    #     live_print=True,
    # )

    # push image

    # context.log.warning(f"{_tags_local = }")
    # context.log.warning(f"{_tags_registry = }")

    ## tag image

    # for _tag in _tags_local:
    #     cmd_tag = [
    #         shutil.which("docker"),
    #         "image",
    #         "tag",
    #         _tag,
    #         _tags_registry[_tags_local.index(_tag)],
    #     ]
    #
    #     context.log.warning(" ".join(cmd_tag))
    #
    #     proc_tag = subprocess.Popen(
    #         cmd_tag,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #     )
    #
    #     handles_tag = (proc_tag.stdout, proc_tag.stderr)
    #     labels_tag = ("stdout", "stderr")
    #     functions_tag = (context.log.info, context.log.debug)
    #     logs[f"tag_{_tag}"] = iterate_fds(
    #         handles=handles_tag,
    #         labels=labels_tag,
    #         functions=functions_tag,
    #         live_print=True,
    #     )
    #
    #     cmd_push = [
    #         shutil.which("docker"),
    #         "image",
    #         "push",
    #         _tags_registry[_tag.index(_tag)],
    #     ]
    #
    #     context.log.warning(" ".join(cmd_push))
    #
    #     proc_push = subprocess.Popen(
    #         cmd_push,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #     )
    #
    #     handles_push = (proc_push.stdout, proc_push.stderr)
    #     labels_push = ("stdout", "stderr")
    #     functions_push = (context.log.info, context.log.debug)
    #     logs[f"push_{_tag}"] = iterate_fds(
    #         handles=handles_push,
    #         labels=labels_push,
    #         functions=functions_push,
    #         live_print=True,
    #     )

    # or:

    # cmd_push = [
    #     shutil.which("docker"),
    #     "image",
    #     "push",
    #     "--all-tags",
    #     _tags_registry[_tag.index(_tag)], minus tag
    # ]

    return ret


# def docker_build(
#     context: AssetExecutionContext,
#     docker_config: DockerConfig,
#     context_path: pathlib.Path,
#     builder: Builder,
#     docker_use_cache: bool = True,
#     image_data: dict = None,
#     pull_all_tags: bool = True,
#     push_all_tags: bool = True,
# ) -> str:
#
#     _docker_config = docker_config.value
#
#     # https://docs.docker.com/build/cache/backends/local/
#
#     # docker run --rm -p 5010:5000 --name registry registry:2
#     # docker push localhost:5010/michimussato/base__build_docker_image:latest
#     # docker pull localhost:5010/michimussato/base__build_docker_image:latest
#     # docker run --rm -v /home/michael/git/repos/OpenStudioLandscapes/daemon.json:/etc/docker/daemon.json -p 5010:5000 --name registry registry:latest
#
#     docker_client = DockerClient(
#         client_call=["docker"],
#         client_type="docker",
#     )
#
#     # in case we are logged in
#     docker_client.logout()
#
#     log: str = ""
#
#     try:
#
#         server = _docker_config["docker_registry_url"]
#
#         if not _docker_config["docker_use_local"]:
#
#             username = _docker_config.get("docker_registry_username", None)
#             password = _docker_config.get("docker_registry_password", None)
#
#             if not all([username, password]):
#                 raise Exception("Both username and password are required")
#
#             context.log.debug("Attempting registry authentication...")
#             try:
#                 docker_client.login(
#                     server=server,
#                     username=username,
#                     password=password,
#                 )
#                 context.log.debug("Authentication successful.")
#             except DockerException as e:
#                 context.log.exception(e)
#
#         context.log.debug("docker_client.info() = %s", docker_client.info())
#
#         image_path = image_data["image_path"]
#         image_tags = image_data["image_tags"]
#         parent_image: dict = image_data["image_parent"]
#
#         tags = [f"{image_path}:{tag}" for tag in image_tags]
#
#         context.log.warning(tags)
#
#         # maybe build and push in separate steps?
#
#         stream: Iterator[str] = docker_client.buildx.build(
#             context_path=context_path.as_posix(),
#             cache=docker_use_cache,
#             tags=tags,
#             stream_logs=True,
#             builder=builder,
#             # push=True,
#             pull=True,
#             load=True,
#             # **_extra_args,
#         )
#
#         docker_client.image.push(
#             x=tags,
#         )
#
#         for msg in stream:
#             context.log.debug(msg)
#             log += msg
#
#     except Exception as e:
#
#         context.log.exception(e)
#         raise e
#
#     finally:
#
#         docker_client.logout()
#
#     return log


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