import pathlib
import shlex
import shutil
from typing import Generator

from python_on_whales import docker, Builder, Container

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
from OpenStudioLandscapes.engine.docker import *


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


@asset(
    **ASSET_HEADER_BASE,
    ins={
        # "env": AssetIn(AssetKey([*KEY_BASE, "env"])),
        "docker_config": AssetIn(AssetKey([*KEY_BASE, "docker_config"])),
    },
    description="https://www.youtube.com/watch?v=fVXkh7NVvww&ab_channel=ProgrammerGuide",
)
def run_registry(
    context: AssetExecutionContext,
    # env: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
):
# ) -> Generator[Output[Container] | AssetMaterialization, None, None]:

    # Insecure Registries:
    # https://wiki.archlinux.org/title/Docker

    """
sudo bash -c 'mkdir -p /etc/docker

cat > /etc/docker/daemon.json << EOF
{
  "insecure-registries" : [
    "192.168.1.162:5000",
    "127.0.0.1:5000",
    "localhost:5000",
    "10.1.2.15:5000",
    "0.0.0.0:5000",
    "[::1]:5000",
    "http://192.168.1.162:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "http://10.1.2.15:5000",
    "http://0.0.0.0:5000",
    "http://[::1]:5000"
  ]
}

EOF'

sudo systemctl daemon-reload
sudo systemctl restart docker
    """

    container = docker_run_registry(
        context=context,
        docker_config=docker_config,
        detach=False,
        domainname="farm.evil",
        container_name="openstudiolandscapes-registry",
        host_name="openstudiolandscapes-registry",
        # publish=[
        #     f"{str(docker_config.value['docker_registry_port']) or '5000'}:5000",
        # ],
        volumes=[
            (
                pathlib.Path(
                    get_git_root(path=pathlib.Path(
                        __file__)) / "src" / "OpenStudioLandscapes" / "engine" / "docker" / "daemon.json"
                ).as_posix(),
                "/etc/docker/daemon.json",
                "ro",
            ),
        ],
        mounts=[
            {
                "source": "local-registry-vol",
                "target": "/var/lib/registry",
            }
        ]
    )

    context.log.info(dir(container))

    return None

    # meta_data = {}
    #
    # # Only launch if "docker_use_local" is True:
    # if docker_config.value["docker_use_local"]:
    #
    #     _container = None
    #     container_name = "openstudiolandscapes-registry"
    #
    #     containers = docker.container.list()
    #
    #     context.log.info(containers)
    #
    #     for container_ in containers:
    #         if container_.name == container_name:
    #             _container = container_
    #
    #     if _container is None:
    #         # /usr/bin/docker buildx build --builder openstudiolandscapes-builder --pull --load --tag localhost:5000/michimussato/base_build_docker_image:2025-03-22_15-34-40__3769b1bdf71b4ef8a5c94002fce3b98f /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-22_15-34-40__3769b1bdf71b4ef8a5c94002fce3b98f/Base__Base/Base__build_docker_image/Dockerfiles
    #         # /usr/bin/docker push localhost:5000/michimussato/base_build_docker_image:2025-03-22_15-34-40__3769b1bdf71b4ef8a5c94002fce3b98f
    #         # # /usr/bin/docker push --all-tags localhost:5000/michimussato/base__build_docker_image
    #
    #         # /usr/bin/docker container run --detach --domainname farm.evil --hostname openstudiolandscapes-registry --mount source=local-registry-vol,destination=/var/lib/registry --name openstudiolandscapes-registry -p 5000:5000 --rm --volume /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/docker/daemon.json:/etc/docker/daemon.json:ro registry:2
    #         container: Container = docker.container.run(
    #             detach=True,
    #             remove=True,
    #             domainname="farm.evil",
    #             # network_mode="host",  # does not exist
    #             hostname=container_name,
    #             image="registry:2",  # 3 is RC
    #             name=container_name,
    #             publish=[
    #                 (int(docker_config.value["docker_registry_port"]) or 5000, 5000),
    #             ],
    #             volumes=(
    #                 [
    #                     (
    #                         pathlib.Path(
    #                             get_git_root(path=pathlib.Path(__file__)) / "src" / "OpenStudioLandscapes" / "engine" / "docker" / "daemon.json"
    #                         ).as_posix(),
    #                         "/etc/docker/daemon.json",
    #                         "ro",
    #                     ),
    #                 ]
    #             ),
    #             mounts=(
    #                 [
    #                     (
    #                         "source=local-registry-vol",
    #                         "destination=/var/lib/registry",
    #                     )
    #                 ]
    #             )
    #         )
    #
    #     else:
    #         container: Container = _container
    #
    #     cmd_interactive = [
    #         shutil.which("docker"),
    #         "exec",
    #         "--interactive",
    #         "--tty",
    #         # container_name,
    #         container.id,
    #         "sh"
    #     ]
    #
    #     cmd_logs = [
    #         shutil.which("docker"),
    #         "logs",
    #         "--follow",
    #         # container_name,
    #         container.id,
    #     ]
    #
    #     cmd_stop = [
    #         shutil.which("docker"),
    #         "container",
    #         "stop",
    #         # container_name,
    #         container.id,
    #     ]
    #
    #     # cmd_rm = [
    #     #     shutil.which("docker"),
    #     #     # "buildx",
    #     #     "rm",
    #     #     # container_name,
    #     #     container.id,
    #     # ]
    #
    #     # context.pdb.set_trace()
    #     # NetworkSettings(bridge='', sandbox_id='267e9c32fe946b9a4665b52627ccf9b26b3f50cedf08920ed0c1e903e1ce77cf', hairpin_mode=False, link_local_ipv6_address='', link_local_ipv6_prefix_length=0, ports={'5000/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '5000'}, {'HostIp': '::', 'HostPort': '5000'}]}, sandbox_key=PosixPath('/var/run/docker/netns/267e9c32fe94'), secondary_ip_addresses=None, secondary_ipv6_addresses=None, endpoint_id='34685ce658074786f8d9d54d9e66ebfd33ce767073c58ae3a6e0a494d0380db2', gateway='172.17.0.1', global_ipv6_address='', global_ipv6_prefix_length=0, ip_address='172.17.0.3', ip_prefix_length=16, ipv6_gateway='', mac_address='9a:47:f7:2f:05:51', networks={'bridge': NetworkInspectResult(ipam_config=None, links=None, aliases=None, network_id='472718e79828dfb762c3b2792802238587d661be25e4e5c7795f150009e15190', endpoint_id='34685ce658074786f8d9d54d9e66ebfd33ce767073c58ae3a6e0a494d0380db2', gateway='172.17.0.1', ip_address='172.17.0.3', ip_prefix_length=16, ipv6_gateway='', global_ipv6_address='', global_ipv6_prefix_length=0, mac_address='9a:47:f7:2f:05:51', driver_options=None)})
    #     # ip_address = container.network_settings.ip_address
    #     # ports = container.network_settings.ports["5000/tcp"]
    #     # for port in ports:
    #     #     if port["HostIp"] != "::":
    #     #         host_port = port["HostIp"]
    #     #         host_ip = port["HostPort"]
    #     #         break
    #
    #     meta_data["__".join(context.asset_key.path)] = MetadataValue.path(str(container))
    #     meta_data["dir"] = MetadataValue.json(dir(container))
    #     meta_data["name"] = MetadataValue.path(container.name)
    #     meta_data["id"] = MetadataValue.path(container.id)
    #     meta_data["interactive"] = MetadataValue.path(shlex.join(cmd_interactive))
    #     meta_data["logs"] = MetadataValue.path(shlex.join(cmd_logs))
    #     meta_data["stop"] = MetadataValue.path(shlex.join(cmd_stop))
    #
    #     yield Output(container)
    #
    # # meta_data["launched"] = MetadataValue.bool(docker_config.value["docker_use_local"]),
    #
    # yield AssetMaterialization(
    #     asset_key=context.asset_key,
    #     metadata=meta_data,
    # )
