import pathlib
import shlex
import shutil
from typing import Generator, MutableMapping
from collections import ChainMap
from functools import reduce
import copy
import json

import yaml

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from docker_compose_graph.utils import *
from OpenStudioLandscapes.engine.base.ops import (
    op_compose,
    op_docker_compose_graph,
    op_group_out,
)


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_BASE_ENV, "env"])
        ),
    },
    deps=[
        AssetKey([*ASSET_HEADER_PI_HOLE['key_prefix'], "constants_pi_hole"])
    ],
)
def env(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    env_in = copy.deepcopy(env)

    # Todo
    #  - [ ] externalize
    # expanding variables in OpenStudioLandscapes.Kitsu.constants.ENVIRONMENT
    for k, v in ENVIRONMENT_PI_HOLE.items():
        if isinstance(v, str):
            ENVIRONMENT_PI_HOLE[k] = v.format(**env_in)

    env_in.update(ENVIRONMENT_PI_HOLE)

    env_in.update(
        {
            "COMPOSE_SCOPE": ComposeScope.PI_HOLE,
        },
    )

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            "ENVIRONMENT_PI_HOLE": MetadataValue.json(ENVIRONMENT_PI_HOLE),
        },
    )


@asset(
    **ASSET_HEADER_PI_HOLE,
)
def compose_networks(
    context: AssetExecutionContext,
) -> Generator[
    Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization, None, None
]:

    compose_network_mode = ComposeNetworkMode.DEFAULT

    if compose_network_mode == ComposeNetworkMode.DEFAULT:
        docker_dict = {
            "networks": {
                "pi-hole": {
                    "name": "network_pi-hole",
                },
            },
        }

    else:
        docker_dict = {
            "network_mode": compose_network_mode.value,
        }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "compose_network_mode": MetadataValue.text(compose_network_mode.value),
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_PI_HOLE, "env"]),
        ),
        "compose_networks": AssetIn(
            AssetKey([*KEY_PI_HOLE, "compose_networks"]),
        ),
    },
)
def compose_pi_hole_unbound(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose_networks: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """
    https://github.com/mpgirro/docker-pihole-unbound
    https://github.com/mpgirro/docker-pihole-unbound/blob/main/example/compose.yaml
    """

    network_dict = {}
    ports_dict = {}

    if "networks" in compose_networks:
        network_dict = {
            "networks": list(compose_networks.get("networks", {}).keys())
        }
        ports_dict = {
            "ports": [
                # DNS Ports
                "53:53/tcp",
                "53:53/udp",
                # Default HTTP Port
                f"{env['PIHOLE_WEB_PORT']}:80/tcp",
                # Default HTTPs Port. FTL will generate a self-signed certificate
                "443:443/tcp",
                # Uncomment the line below if you are using Pi-hole as your DHCP server
                # - "67:67/udp"
                # Uncomment the line below if you are using Pi-hole as your NTP server
                # - "123:123/udp"
            ]
        }
    elif "network_mode" in compose_networks:
        network_dict = {
            "network_mode": compose_networks.get("network_mode")
        }

    pi_hole_data = pathlib.Path(env['PI_HOLE_DATABASE_INSTALL_DESTINATION'])
    pi_hole_data.mkdir(parents=True, exist_ok=True)

    unbound_data = pathlib.Path(env['UNBOUND_DATABASE_INSTALL_DESTINATION'])
    unbound_data.mkdir(parents=True, exist_ok=True)

    volumes_dict = {
        "volumes": [
            # For persisting Pi-hole's databases and common configuration file
            f"{pi_hole_data.as_posix()}:/etc/pihole:rw",
            f"{unbound_data.as_posix()}:/etc/dnsmasq.d:rw",
            # Uncomment the below if you have custom dnsmasq config files that you want to persist. Not needed for most starting fresh with Pi-hole v6. If you're upgrading from v5 you and have used this directory before, you should keep it enabled for the first v6 container start to allow for a complete migration. It can be removed afterwards. Needs environment variable FTLCONF_misc_etc_dnsmasq_d: 'true'
            # f"./etc-dnsmasq.d:/etc/dnsmasq.d"
        ],
    }

    service_name = "pihole-unbound"
    container_name = service_name
    host_name = ".".join([service_name, env["ROOT_DOMAIN"]])

    docker_dict = {
        "services": {
            service_name: {
                "container_name": container_name,
                "hostname":  host_name,
                "domainname": env.get("ROOT_DOMAIN"),
                "restart": "unless-stopped",
                "image": "docker.io/mpgirro/pihole-unbound:latest",
                **copy.deepcopy(volumes_dict),
                **copy.deepcopy(network_dict),
                **copy.deepcopy(ports_dict),
                "environment": {
                    # Set the appropriate timezone for your location (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g:
                    "TZ": env['PIHOLE_TIMEZONE'],
                    # Set a password to access the web interface. Not setting one will result in a random password being assigned
                    "FTLCONF_webserver_api_password": env['PIHOLE_WEB_PASSWORD'],
                    # If using Docker's default `bridge` network setting the dns listening mode should be set to 'all'
                    # Unbound
                    # "FTLCONF_LOCAL_IPV4": "0.0.0.0",
                    "FTLCONF_webserver_interface_theme": env['PIHOLE_WEB_THEME'],
                    # "FTLCONF_dns_revServers": "${REV_SERVER:-false},${REV_SERVER_CIDR},${REV_SERVER_TARGET},${REV_SERVER_DOMAIN}",
                    "FTLCONF_dns_upstreams": "127.0.0.1#5335",
                    "FTLCONF_dns_dnssec": env['PIHOLE_DNS_DNSSEC'],
                    "FTLCONF_dns_listeningMode": env['PIHOLE_DNS_LISTENING_MODE'],
                    # "FTLCONF_webserver_port": "82",
                    "REV_SERVER": env['PIHOLE_REV_SERVER'],
                    # If REV_SERVER is "false", these are not necessary:
                    # "REV_SERVER_CIDR": "",
                    # "REV_SERVER_TARGET": "",
                    # "REV_SERVER_DOMAIN": "",
                },
                "cap_add": [
                    # Todo
                    # See https://github.com/pi-hole/docker-pi-hole#note-on-capabilities
                    # Required if you are using Pi-hole as your DHCP server, else not needed
                    # "NET_ADMIN",
                    # Required if you are using Pi-hole as your NTP client to be able to set the host's system time
                    # "SYS_TIME",
                    # Optional, if Pi-hole should get some more processing time
                    # "SYS_NICE",
                ]
                # "healthcheck": {
                # },
                # "command": [
                # ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_PI_HOLE, "env"]),
        ),
    },
)
def pi_hole_root(
        context: AssetExecutionContext,
        env: dict,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    root_dir = pathlib.Path(
        env["DOT_LANDSCAPES"],
        ".pi_hole",
    )

    root_dir.mkdir(parents=True, exist_ok=True)

    yield Output(root_dir)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(root_dir),
        },
    )


# @asset(
#     **ASSET_HEADER_PI_HOLE,
#     ins={
#         "write_yaml": AssetIn(
#             AssetKey([*KEY_PI_HOLE, "write_yaml"]),
#         ),
#     },
# )
# def prepare(
#         context: AssetExecutionContext,
#         write_yaml: pathlib.Path,
# ) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
#     """Is Harbor installed in the designated destination so that
#     we can write a docker compose file to that destination?"""
#
#     cmd_prepare = [
#         shutil.which("sudo"),
#         shutil.which("bash"),
#         pathlib.Path(write_yaml.parent / "prepare").as_posix(),
#     ]
#
#     # MUST run as root apparently
#     # cmd_chmod = [
#     #     shutil.which("sudo"),
#     #     shutil.which("chmod"),
#     #     "-R",
#     #     "a+r",
#     #     pathlib.Path(get_harbor).as_posix(),
#     # ]
#
#     if not pathlib.Path(write_yaml).exists():
#         raise FileNotFoundError(f"Run prepare first: '{shlex.join(cmd_prepare)}'")
#
#     docker_compose = write_yaml.parent / "docker-compose.yml"
#
#     if not pathlib.Path(docker_compose).exists():
#         raise FileNotFoundError(f"Run prepare first: '{shlex.join(cmd_prepare)}'")
#
#     yield Output(docker_compose)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "pi_hole_yml": MetadataValue.path(write_yaml),
#             "docker_compose_yml": MetadataValue.path(docker_compose),
#             "cmd_prepare": MetadataValue.path(shlex.join(cmd_prepare)),
#         },
#     )


# @asset(
#     **ASSET_HEADER_PI_HOLE,
#     ins={
#         "pi_hole_root": AssetIn(
#             AssetKey([*KEY_PI_HOLE, "pi_hole_root"]),
#         ),
#         "env": AssetIn(
#             AssetKey([*KEY_PI_HOLE, "env"]),
#         ),
#     },
#     description="Returns the docker-compose path."
# )
# def write_yaml(
#         context: AssetExecutionContext,
#         pi_hole_root: pathlib.Path,
#         env: dict,
# ) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
#
#     yaml_out = pi_hole_root / "bin" / "pi_hole.yml"
#     registry_data_root = pi_hole_root / "data"
#
#     pi_hole_dict = {
#         'hostname': env["PI_HOLE_HOSTNAME"],
#         'http': {'port': env["PI_HOLE_PORT"]},
#         'pi_hole_admin_password': env["PI_HOLE_PASSWORD"],
#         'database': {
#             'password': 'root123',
#             'max_idle_conns': 100,
#             'max_open_conns': 900,
#             'conn_max_idle_time': 0
#         },
#         'data_volume': registry_data_root.as_posix(),
#         'trivy': {
#             'ignore_unfixed': False,
#             'skip_update': False,
#             'skip_java_db_update': False,
#             'offline_scan': False,
#             'security_check': 'vuln',
#             'insecure': False,
#             'timeout': '5m0s'
#         },
#         'jobservice': {
#             'max_job_workers': 10,
#             'job_loggers': ['STD_OUTPUT', 'FILE'],
#             'logger_sweeper_duration': 1
#         },
#         'notification': {
#             'webhook_job_max_retry': 3,
#             'webhook_job_http_client_timeout': 3
#         },
#         # 'log': {
#         #     'level': 'info',
#         #     'local': {
#         #         'rotate_count': 50,
#         #         'rotate_size': '200M',
#         #         'location': '/var/log/harbor'
#         #     }
#         # },
#         '_version': '2.12.0',
#         'proxy': {
#             'http_proxy': None,
#             'https_proxy': None,
#             'no_proxy': None,
#             'components': ['core', 'jobservice', 'trivy']
#         },
#         'upload_purging': {
#             'enabled': True,
#             'age': '168h',
#             'interval': '24h',
#             'dryrun': False
#         },
#         'cache': {
#             'enabled': False,
#             'expire_hours': 24
#         }
#     }
#
#     pi_hole_yml: str = yaml.dump(pi_hole_dict)
#
#     with open(yaml_out, "w") as fw:
#         fw.write(pi_hole_yml)
#
#     yield Output(yaml_out)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.path(yaml_out),
#             "pi_hole_yml": MetadataValue.md(f"```yaml\n{pi_hole_yml}\n```"),
#         },
#     )


# @asset(
#     **ASSET_HEADER_PI_HOLE,
#     ins={
#         "compose_pi_hole": AssetIn(
#             AssetKey([*KEY_PI_HOLE, "compose_pi_hole_unbound"]),
#         ),
#         "compose_networks": AssetIn(
#             AssetKey([*KEY_PI_HOLE, "compose_networks"]),
#         ),
#         # "env": AssetIn(
#         #     AssetKey([*KEY_PI_HOLE, "env"]),
#         # ),
#     },
# )
# def compose(
#         context: AssetExecutionContext,
#         compose_pi_hole: dict,
#         compose_networks: dict,
#         # env: dict,
# ) -> Generator[Output[dict] | AssetMaterialization, None, None]:
#
#     with open(prepare, "r") as fw:
#         docker_compose_yaml = fw.read()
#         docker_compose_dict = yaml.safe_load(docker_compose_yaml)
#
#     # compose_project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"
#     compose_project_name = "openstudiolandscapes-pi_hole"
#
#     cmd_docker_compose_up = [
#         shutil.which("sudo"),
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         prepare.as_posix(),
#         "--project-name",
#         compose_project_name,
#         "up",
#         "--remove-orphans",
#     ]
#
#     cmd_docker_compose_down = [
#         shutil.which("sudo"),
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         prepare.as_posix(),
#         "--project-name",
#         compose_project_name,
#         "down",
#     ]
#
#     yield Output(docker_compose_dict)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(docker_compose_dict),
#             "cmd_docker_compose_up": MetadataValue.path(
#                 " ".join(
#                     shlex.quote(s) if not s in ["&&", ";"] else s
#                     for s in cmd_docker_compose_up
#                 )
#             ),
#             "cmd_docker_compose_down": MetadataValue.path(
#                 " ".join(
#                     shlex.quote(s) if not s in ["&&", ";"] else s
#                     for s in cmd_docker_compose_down
#                 )
#             ),
#             "docker_compose_yaml": MetadataValue.md(f"```yaml\n{docker_compose_yaml}\n```"),
#         },
#     )


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        "compose_pi_hole": AssetIn(
            AssetKey([*KEY_PI_HOLE, "compose_pi_hole_unbound"]),
        ),
    },
)
def compose_maps(
    context: AssetExecutionContext,
    **kwargs,  # pylint: disable=redefined-outer-name
) -> Generator[Output[list[dict]] | AssetMaterialization, None, None]:

    ret = list(kwargs.values())

    context.log.info(ret)

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        "compose_networks": AssetIn(
            AssetKey([*KEY_PI_HOLE, "compose_networks"])
        ),
        "compose_maps": AssetIn(
            AssetKey([*KEY_PI_HOLE, "compose_maps"])
        ),
    },
    # out={
    #     "compose": Out(dict),
    # },
)
def compose(
    context: AssetExecutionContext,
    compose_networks: dict,  # pylint: disable=redefined-outer-name
    # **kwargs,  # pylint: disable=redefined-outer-name
    compose_maps: list[dict],  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    if "networks" in compose_networks:
        network_dict = copy.deepcopy(compose_networks)
    else:
        network_dict = {}

    docker_chainmap = ChainMap(
        network_dict,
        *compose_maps,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)

    docker_yaml = yaml.dump(docker_dict)

    yield Output(
        # output_name="compose",
        value=docker_dict,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


@asset(
    **ASSET_HEADER_PI_HOLE,
    ins={
        # "prepare": AssetIn(
        #     AssetKey([*KEY_PI_HOLE, "prepare"]),
        # ),
        "env": AssetIn(
            AssetKey([*KEY_PI_HOLE, "env"]),
        ),
        "compose": AssetIn(
            AssetKey([*KEY_PI_HOLE, "compose"]),
        ),
    },
)
def cmd_docker_compose_up(
        context: AssetExecutionContext,
        # prepare: pathlib.Path,
        env: dict,
        compose: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    docker_compose_yaml = yaml.dump(compose)

    # with open(prepare, "r") as fw:
    #     docker_compose_yaml = fw.read()
    #     docker_compose_dict = yaml.safe_load(docker_compose_yaml)

    # compose_project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"
    compose_project_name = "openstudiolandscapes-pi-hole"

    # # Todo:
    # #  Maybe there is a better way but it does not matter yet
    # #  as long as there are only AssetKey([PREFIX, KEY]) with
    # #  no sub-prefixes inbetween
    # key_group_out = context.asset_key_for_output("group_out").path[0]

    docker_compose = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{GROUP_PI_HOLE}__{'__'.join(KEY_PI_HOLE)}",
        # "__".join(context.asset_key_for_output("group_out").path),
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, mode="w", encoding="utf-8") as fw:
        fw.write(docker_compose_yaml)

    cmd_docker_compose_up = [
        # shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        compose_project_name,
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        compose_project_name,
        "down",
    ]

    yield Output(compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "cmd_docker_compose_up": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_up
                )
            ),
            "cmd_docker_compose_down": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_down
                )
            ),
            "__".join(context.asset_key.path): MetadataValue.json(compose),
            "docker_compose_yaml": MetadataValue.md(f"```yaml\n{docker_compose_yaml}\n```"),
        },
    )


# compose = AssetsDefinition.from_op(
#     op_compose,
#     tags_by_output_name={
#         "compose": {
#             "compose": "third_party",
#         },
#     },
#     group_name=GROUP_PI_HOLE,
#     key_prefix=KEY_PI_HOLE,
#     keys_by_input_name={
#         "compose_networks": AssetKey([*KEY_PI_HOLE, "compose_networks"]),
#         "compose_maps": AssetKey([*KEY_PI_HOLE, "compose_maps"]),
#     },
# )


# # # Todo
# # #  - [ ] cmd_docker_compose_up creates an additional docker-compose.yaml which
# # #        is undesirable in this instance as it creates the wrong paths while docker compose up
# # #        ignore for now
# group_out = AssetsDefinition.from_op(
#     op_group_out,
#     can_subset=True,
#     group_name=GROUP_PI_HOLE,
#     tags_by_output_name={
#         "group_out": {
#             "group_out": "third_party",
#         },
#     },
#     key_prefix=KEY_PI_HOLE,
#     keys_by_input_name={
#         "compose": AssetKey(
#             [*KEY_PI_HOLE, "compose"]
#         ),
#         "env": AssetKey(
#             [*KEY_PI_HOLE, "env"]
#         ),
#         # "group_in": AssetKey(
#         #     [*KEY_PI_HOLE, "group_out"]
#         # ),
#     },
# )


# docker_compose_graph = AssetsDefinition.from_op(
#     op_docker_compose_graph,
#     group_name=GROUP_PI_HOLE,
#     key_prefix=KEY_PI_HOLE,
#     keys_by_input_name={
#         "group_out": AssetKey(
#             [*KEY_PI_HOLE, "group_out"]
#         ),
#         "compose_project_name": AssetKey(
#             [*KEY_PI_HOLE, "compose_project_name"]
#         ),
#     },
# )
