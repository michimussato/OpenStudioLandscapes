__all__ = [
    "docker_build",
    "get_builder_by_name",
]

import pathlib
import shutil
import subprocess
from typing import Iterator, List
from python_on_whales import docker, Builder, Image
# from python_on_whales import DockerClient

from dagster import (
    AssetExecutionContext,
)


def docker_build(
    context: AssetExecutionContext,
    context_path: pathlib.Path,
    tags: List[str],
    builder: Builder,
    docker_use_cache: bool = True,
    parent_image: str = None,
    # cache_dir: pathlib.Path = None,
    # images_dir: pathlib.Path = None,
) -> str:
    # https://docs.docker.com/build/cache/backends/local/

    # docker run --rm -p 5010:5000 --name registry registry:latest
    # docker push localhost:5010/michimussato/base__build_docker_image:latest
    # docker pull localhost:5010/michimussato/base__build_docker_image:latest
    # docker run --rm -v /home/michael/git/repos/OpenStudioLandscapes/daemon.json:/etc/docker/daemon.json -p 5010:5000 --name registry registry:latest

    # _extra_args = {}
    #
    # if docker_use_cache:
    #     # https://docs.docker.com/reference/cli/docker/buildx/build/#cache-from
    #     # _extra_args["cache_from"] = f"type=local,src={cache_dir.as_posix()}"
    #     # _extra_args["cache_from"] = f"type=registry,ref=localhost:5010"
    #     _extra_args["cache_from"] = f"type=registry,ref=localhost:5010/{tags[0]}"
    #     # _extra_args["cache_from"] = f"type=registry"
    #     # # https://docs.docker.com/reference/cli/docker/buildx/build/#cache-to
    #     # # _extra_args["cache_to"] = f"type=local,dest={cache_dir.as_posix()},compression=zstd,compression-level=22"
    #     _extra_args["cache_to"] = f"type=registry,ref=localhost:5010"
    #     # _extra_args["cache_to"] = f"type=registry,ref=localhost:5010/{tags[0]}"
    #     # https://docs.docker.com/reference/cli/docker/buildx/build/#output
    #     # https://docs.docker.com/build/exporters/oci-docker/#synopsis
    #     # _image_name = "__".join(context.asset_key.path).lower()
    #     # _tar = f"{pathlib.Path(images_dir / _image_name).as_posix()}"
    #     _extra_args["output"] = {
    #         # "type": "oci",
    #         # "type": "tar",
    #         # "type": "local",
    #         "type": "image",
    #         "push": "false",
    #         "registry.insecure": "true",
    #         # "dest": _tar,
    #         # "name": f"michimussato/{_image_name}",
    #         # "compression": "zstd",
    #         # "compression": "gzip",
    #         # "compression_level": "22",
    #         # "compression_level": "9",
    #         # # https://docs.docker.com/build/exporters/oci-docker/#annotations
    #         # "annotation.io.containerd.image.name": tags[-1].split(":")[0],
    #         # "annotation.org.opencontainers.image.ref.name": tags[-1].split(":")[-1],
    #     }
    #
    #     # "annotations":{"io.containerd.image.name":"docker.io/michimussato/base__build_docker_image:2025-03-18_09-19-42__166f3f88e138406a8f88e879a505cbba","org.opencontainers.image.created":"2025-03-18T08:20:08Z","org.opencontainers.image.ref.name":"2025-03-18_09-19-42__166f3f88e138406a8f88e879a505cbba"}

    # img: Image = docker.build(
    #     context_path=context_path.as_posix(),
    #     cache=docker_use_cache,
    #     # tags=tags[-1],
    #     stream_logs=False,
    #     builder=_get_builder(),
    #     push=True,
    #     pull=True,
    #     load=True,
    #     **_extra_args,
    # )

    # for tag in tags:
    #     img.tag(
    #         new_tag=tag
    #     )

    # docker_client = DockerClient(
    #     client_call=["docker"],
    # )

    # docker_client.login(
    #     server="localhost:5010",
    #     username='""',
    #     password='""',
    # )

    # docker_client.buildx.

    if parent_image is not None:
        stdout = subprocess.check_output(
            [
                f"{shutil.which('docker')}",
                "pull",
                "--all",
                f"{parent_image}",
            ]
        )

        context.log.info(stdout.decode("utf-8"))

    stream: Iterator[str] = docker.build(
        context_path=context_path.as_posix(),
        cache=docker_use_cache,
        tags=tags,
        stream_logs=True,
        builder=builder,
        # add_hosts={"localhost": "http://localhost:5010"},
        # push=True,
        # pull=True,
        load=True,
        # **_extra_args,
    )

    log: str = ""

    for msg in stream:
        context.log.debug(msg)
        log += msg

    # if docker_use_cache:
    #     img: Image = docker.import_(
    #         source=_tar,
    #     )

    # for tag in tags:
    #     # docker tag michimussato/base__build_docker_image:2025-03-18_14-02-09__55959d1912a941c4a3f981ff4e560687 localhost:5010/michimussato/base__build_docker_image:2025-03-18_14-41-23__8f401ef0889649138d7f82b8661390b2
    #     # repo, tag = tag.split(":")  # michimussato/base__build_docker_image, 2025-03-18_14-02-09__55959d1912a941c4a3f981ff4e560687
    #
    #     os.system(f"docker tag {tag} localhost:5000/{tag}")
    #     # os.system(f"docker tag localhost:5010/{tag}")
    #     # img.tag(
    #     #     new_tag=tag
    #     # )

    for tag in tags:
        stdout = subprocess.check_output(
            [
                f"{shutil.which('docker')}",
                "push",
                # "--all-tags",
                f"{tag}",
            ]
        )
        # os.system(f"docker push {tag}")

        context.log.info(stdout.decode("utf-8"))

    return log


def get_builder_by_name(
    context: AssetExecutionContext,
    builder_name: str,
) -> Builder:

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