import shutil
import shlex

from Deadline.deadline_docker.constants import *

from dagster import MetadataValue


__all__ = [
    "compile_cmds",
    "cmd_list_to_str",
    "deep_merge",
]


def compile_cmds(
        docker_file,
        tag,
        volumes: [list, None] = None,
        networks: [list, None] = None,
) -> dict[str, MetadataValue]:

    if volumes is None:
        volumes = []

    if networks is None:
        networks = []

    _volumes = ' '.join([f'--volume {i}' for i in volumes])
    _networks = ' '.join([f'--network {i}' for i in networks])

    cmd_docker_run = [
        shutil.which("docker"),
        "run",
        _volumes,
        _networks,
        "--rm",
        "--interactive",
        "--tty",
        "--entrypoint",
        "bash",
        tag,
    ]
    cmd_docker_build = [
        shutil.which("docker"),
        "build",
        "--tag",
        tag,
        docker_file.parent.as_posix(),
        '--no-cache' if DOCKER_USE_CACHE else '',
    ]

    metadata_values = {
        "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        "cmd_docker_build": MetadataValue.path(cmd_list_to_str(cmd_docker_build)),
    }

    return metadata_values


def cmd_list_to_str(
        cmd_list: list[str],
) -> str:
    cmd_str = " ".join(shlex.quote(s) for s in cmd_list)
    return cmd_str


def deep_merge(dict1, dict2):
    """https://sqlpey.com/python/solved-top-5-methods-to-deep-merge-dictionaries-in-python/"""
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            deep_merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


# def docker_cleanup(
#         context: AssetExecutionContext = None,
# ):
#     """
# from Deadline.deadline_docker.assets import docker_cleanup
# docker_cleanup()
#     """
#     # out = {
#     #     "stdout": context.log.info,
#     #     "stderr": context.log.error,
#     # }
#
#     containers = docker.container.list(
#         all=True
#     )
#
#     docker.container.stop(
#         containers=containers,
#     )
#
#     stream_container_prune = docker.container.prune(
#         stream_logs=True,
#     )
#
#     # log_container_prune_stdout: str = ""
#     # log_container_prune_stderr: str = ""
#
#     # for msg in stream_container_prune:
#     #     out[msg[0]](msg)
#     #     # context.log.debug(msg)
#     #     # locals(f"")
#     #     # log_container_prune += msg
#
#     docker.image.prune(
#         all=True,
#     )
#
#     docker.volume.prune(
#         all=True,
#     )
#
#     stream_buildx_prune = docker.buildx.prune(
#         all=True,
#         stream_logs=True,
#     )
#
#     # log_buildx_prune: str = ""
#
#     # for msg in stream_buildx_prune:
#     #     out[msg[0]](msg)
#
#     docker.network.prune()
#
#     return None
