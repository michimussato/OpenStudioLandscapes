import pathlib
import shlex
import shutil
import textwrap
from typing import Generator

from python_on_whales import docker, Builder
import docker as docker_py
from docker.types.services import Mount

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    AssetIn,
    AssetKey,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *


"""
buildkit.toml
# https://docs.docker.com/build/buildkit/

# cat > ~/.config/buildkit/buildkitd.toml << EOF

sudo bash -c 'mkdir -p /etc/buildkit

cat > /etc/buildkit/buildkitd.toml << EOF
insecure-entitlements = [ "network.host", "security.insecure" ]

EOF'


# sudo -s << EOF
# rm -f -- /tmp/installbuilder_installer*.log
# 
# export PACKAGE=Deadline-10.4.0.10-linux-installers
# ${NFS_INSTALLERS_ROOT}/${PACKAGE}/DeadlineClient-10.4.0.10-linux-x64-installer.run \
#     --mode unattended \
#     --prefix /opt/Thinkbox/Deadline10 \
#     --connectiontype Remote \
#     --proxyrootdir ${IP_MASTER}:${DEADLINE_RCS_PORT_TLS} \
#     --proxycertificate /nfs/deadline/Deadline10/certs/certs/Deadline10RemoteClient.pfx \
#     --proxycertificatepassword $DEADLINE_RCS_CERTIFICATE_PASSWORD \
#     --remotecontrol NotBlocked \
#     --blockautoupdateoverride NotBlocked \
#     --launcherservicedelay 30 30 &
#     
# while [[ ! -f /tmp/installbuilder_installer.log ]]; do sleep 1; done; tail -f /tmp/installbuilder_installer.log | grep -E --color=always '|^Script exit code: 1|^Executing ' &
# 
# EOF
"""


@asset(
    **ASSET_HEADER_BASE,
)
def run_builder(
    context: AssetExecutionContext,
) -> Generator[Output[Builder] | AssetMaterialization, None, None]:

    _builder = None
    builder_name = "openstudiolandscapes-builder"

    builders = docker.buildx.list()
    context.log.info(builders)

    for builder_ in builders:
        if builder_.name == builder_name:
            _builder = builder_

    buildkitd_flags = [
        "--allow-insecure-entitlement=network.host",
        "--allow-insecure-entitlement=security.insecure",
    ]

    if _builder is None:
        builder: Builder = docker.buildx.create(
            driver="docker-container",
            name=builder_name,
            bootstrap=True,
            platforms=["linux/amd64"],
            buildkitd_flags=shlex.join(buildkitd_flags),
            config=pathlib.Path("/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/docker/builder.toml")
        )
    else:
        builder: Builder = _builder

    cmd_inspect = [
        shutil.which("docker"),
        "buildx",
        "inspect",
        "--builder",
        # "--bootstrap",  # ensure builder has stopped before inspect
        builder_name,
    ]

    cmd_rm = [
        shutil.which("docker"),
        "buildx",
        "rm",
        builder_name,
    ]

    yield Output(builder)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(str(builder)),
            "dir": MetadataValue.json(dir(builder)),
            "buildkitd_flags": MetadataValue.json(buildkitd_flags),
            "name": MetadataValue.path(builder.name),
            "inspect": MetadataValue.path(shlex.join(cmd_inspect)),
            "rm": MetadataValue.path(shlex.join(cmd_rm)),
        },
    )


if DOCKER_CONFIG.value["docker_use_local"]:
    # @asset(
    #     **ASSET_HEADER_BASE,
    #     # name="Run_Local_Registry",
    #     ins={
    #         "env": AssetIn(AssetKey([*KEY_BASE, "env"])),
    #         # "docker_config": AssetIn(AssetKey([*KEY_BASE, "docker_config"])),
    #     },
    #     description="https://www.youtube.com/watch?v=fVXkh7NVvww&ab_channel=ProgrammerGuide",
    # )
    # def run_registry(
    #     context: AssetExecutionContext,
    #     env: dict,  # pylint: disable=redefined-outer-name
    #     # docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    # ) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    #     # Todo
    #     #  - [ ] Write daemon for this
    #
    #     docker_config = DOCKER_CONFIG
    #
    #     # Target command:
    #     # /usr/bin/docker container run \
    #     #     --domainname farm.evil \
    #     #     --hostname openstudiolandscapes-registry \
    #     #     --name openstudiolandscapes-registry \
    #     #     --rm \
    #     #     --publish 5000:5000 \
    #     #     --volume /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/docker/daemon.json:/etc/docker/daemon.json:ro \
    #     #     --mount source=local-registry-vol,destination=/var/lib/registry \
    #     #     registry:2
    #
    #     # Insecure Registries:
    #     # https://wiki.archlinux.org/title/Docker
    #
    #     client = docker_py.from_env()
    #     containers = client.containers.list()
    #
    #     domainname = "farm.evil"
    #     host_name="openstudiolandscapes-registry"
    #     container_name="openstudiolandscapes-registry"
    #
    #     repo_dir = pathlib.Path(
    #         env["DOT_LANDSCAPES"],
    #         env.get("LANDSCAPE", "default"),
    #         f"{GROUP_BASE}__{'__'.join(KEY_BASE)}",
    #         "__".join(context.asset_key.path),
    #         "repo_dir",
    #     )
    #
    #     repo_dir.parent.mkdir(parents=True, exist_ok=True)
    #
    #     # stopping running instance helpful for debugging probably.
    #     # if not helpful, just return container instance
    #     for container in containers:
    #         if container.name == container_name:
    #             context.log.info(f"Container {container.name} is running already.")
    #             context.log.info(f"Stopping...")
    #             container.stop()
    #             context.log.info(f"Stopped.")
    #             try:
    #                 container.remove(
    #                     force=True,
    #                 )
    #             except Exception as e:
    #                 context.log.warning(e)
    #             finally:
    #                 context.log.info(f"Removed.")
    #
    #     volumes=[
    #         (
    #             pathlib.Path(
    #                 get_git_root(path=pathlib.Path(
    #                     __file__)) / "src" / "OpenStudioLandscapes" / "engine" / "docker" / "daemon.json"
    #             ).as_posix(),
    #             "/etc/docker/daemon.json",
    #             "ro",
    #         ),
    #         (
    #             repo_dir.as_posix(),
    #             "/var/lib/registry",
    #             "rw",
    #         ),
    #     ]
    #     mounts=[
    #         # {
    #         #     "source": "local-registry-vol",
    #         #     "target": "/var/lib/registry",
    #         # }
    #     ]
    #
    #     publish = {
    #         f"{str(docker_config.value['docker_registry_port']) or '5000'}": 5000,
    #     }
    #
    #     volumes_ = []
    #     for volume in volumes:
    #         volumes_.append(
    #             ":".join(volume),
    #         )
    #
    #     mounts_ = []
    #     for mount in mounts:
    #         mounts_.append(
    #             Mount(**mount)
    #         )
    #
    #     container_registry = client.containers.run(
    #         image="docker.io/registry:2",
    #         remove=True,
    #         detach=True,
    #         domainname=domainname,
    #         hostname=host_name,
    #         name=container_name,
    #         ports=publish,
    #         stream=True,
    #         volumes=volumes_,
    #         mounts=mounts_,
    #     )
    #
    #     context.log.info(dir(container_registry))
    #
    #     cmd_interactive = [
    #         shutil.which("docker"),
    #         "exec",
    #         "--interactive",
    #         "--tty",
    #         container_registry.id,
    #         "sh"
    #     ]
    #
    #     cmd_logs = [
    #         shutil.which("docker"),
    #         "logs",
    #         "--follow",
    #         container_registry.id,
    #     ]
    #
    #     yield Output(container_registry.attrs)
    #
    #     yield AssetMaterialization(
    #         asset_key=context.asset_key,
    #         metadata={
    #             "__".join(context.asset_key.path): MetadataValue.json(container_registry.attrs),
    #             "container_id": MetadataValue.path(container_registry.id),
    #             "container_name": MetadataValue.path(container_registry.name),
    #             "cmd_interactive": MetadataValue.path(shlex.join(cmd_interactive)),
    #             "cmd_logs": MetadataValue.path(shlex.join(cmd_logs)),
    #         },
    #     )
    @asset(
        **ASSET_HEADER_BASE,
        ins={
            "env": AssetIn(AssetKey([*KEY_BASE, "env"])),
        },
        description="https://www.youtube.com/watch?v=fVXkh7NVvww&ab_channel=ProgrammerGuide",
    )
    def write_registry_env(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
    ) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

        docker_config = DOCKER_CONFIG

        daemon_json: tuple = (
            pathlib.Path(
                get_git_root(path=pathlib.Path(
                    __file__)) / "src" / "OpenStudioLandscapes" / "engine" / "docker" / "daemon.json"
            ).as_posix(),
            "/etc/docker/daemon.json",
            "ro",
        )

        registry_root = pathlib.Path(
            get_git_root(__file__),
            ".registry",
            "registry_root",
        )

        registry_root.mkdir(parents=True, exist_ok=True)

        registry_env = pathlib.Path(
            get_git_root(__file__),
            ".registry",
            "registry.env",
        )

        registry_env.parent.mkdir(parents=True, exist_ok=True)

        registry_root_volume: tuple = (
            registry_root.as_posix(),
            "/var/lib/registry",
            "rw",
        )

        certs_root = registry_root.parent / "OpenStudioLandscapes-RootCA"

        certs_root_volume: tuple = (
            certs_root.as_posix(),
            "/certs",
            "ro",
        )

        ca_cert = registry_root.parent / "OpenStudioLandscapes-RootCA" / "OpenStudioLandscapes-RootCA.crt"

        ca_cert_volume: tuple = (
            ca_cert.as_posix(),
            "/usr/local/share/ca-certificates/OpenStudioLandscapes-RootCA.crt",
            "ro",
        )

        port_container = "443"

        registry_env_str = textwrap.dedent(
            """
            DOMAIN_NAME="{domain_name}"
            HOST_NAME="{host_name}"
            CONTAINER_NAME="{container_name}"
            PUBLISH="{publish}"
            DAEMON_JSON="{daemon_json}"
            REGISTRY_ROOT="{registry_root}"
            CERTS_ROOT="{certs_root}"
            CA_CERT="{ca_cert}"
            REGISTRY="{registry}"
            ENV_REGISTRY_HTTP_ADDR="{env_registry_http_addr}"
            ENV_REGISTRY_HTTP_TLS_CERTIFICATE="{env_registry_http_tls_certificate}"
            ENV_REGISTRY_HTTP_TLS_KEY="{env_registry_http_tls_key}"
            """
        ).format(
            domain_name = "farm.evil",
            host_name="openstudiolandscapes-registry",
            container_name="openstudiolandscapes-registry",
            publish=f"{str(docker_config.value['docker_registry_port']) or '5000'}:{port_container}",
            # publish=f"443:{port_container}",
            daemon_json=":".join(daemon_json),
            registry_root=":".join(registry_root_volume),
            certs_root=":".join(certs_root_volume),
            ca_cert=":".join(ca_cert_volume),
            registry="docker.io/registry:2",
            env_registry_http_addr=f"REGISTRY_HTTP_ADDR=0.0.0.0:{port_container}",
            env_registry_http_tls_certificate=f"REGISTRY_HTTP_TLS_CERTIFICATE=/certs/openstudiolandscapes-registry.crt",
            env_registry_http_tls_key=f"REGISTRY_HTTP_TLS_KEY=/certs/openstudiolandscapes-registry.key",
        )

        with open(registry_env, "w") as fw:
            fw.write(registry_env_str)

        with open(registry_env, "r") as fr:
            registry_env_content = fr.read()

        cmd_restart = f"sudo {shutil.which('systemctl')} restart openstudiolandscapes-registry.service"
        cmd_journalctl = f"sudo {shutil.which('journalctl')} --follow --unit openstudiolandscapes-registry.service"

        cmd_interactive = [
            shutil.which("docker"),
            "exec",
            "--interactive",
            "--tty",
            "<container_id>",
            "sh"
        ]

        yield Output(registry_env)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.path(registry_env),
                "registry_env": MetadataValue.md(
                    f"```shell\n{registry_env_content}\n```"
                ),
                "registry_root": MetadataValue.path(registry_root),
                "cmd_restart": MetadataValue.path(cmd_restart),
                "cmd_journalctl": MetadataValue.path(cmd_journalctl),
                "cmd_interactive": MetadataValue.path(shlex.join(cmd_interactive)),
            },
        )
