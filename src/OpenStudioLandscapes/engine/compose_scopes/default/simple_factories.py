import json
import pathlib
from typing import Any, Generator, Dict

import yaml
from dagster import (
    asset,
    Output,
    AssetMaterialization,
    AssetsDefinition,
    AssetExecutionContext,
    MetadataValue,
)

from OpenStudioLandscapes.engine.config.models import ComposeScopeBaseModel
from OpenStudioLandscapes.engine.enums import DockerComposePolicies, DockerComposeNetworkMode
from OpenStudioLandscapes.engine.utils import get_relative_path_via_common_root
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import DockerComposeServiceDefinition


def simple_factory_newt(
        ASSET_HEADER,
        compose_scope,
        name,
        ins,
) -> AssetsDefinition:

    @asset(
        **ASSET_HEADER,
        name=name,
        ins=ins,
    )
    def _asset(
            context: AssetExecutionContext,
            **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")
        env: Dict = CONFIG.env
        landscape_id: str = env.get("LANDSCAPE", "default")

        scrape_networks: Dict = kwargs.pop("scrape_networks")

        _unique_suffix = f"compose_scope-{compose_scope}.{landscape_id}"

        service_dict: DockerComposeServiceDefinition = {
            "image": "docker.io/fosrl/newt",
            "container_name": f"newt_container.{_unique_suffix}",
            "restart": DockerComposePolicies.RESTART_POLICY.ALWAYS,
            "environment": {
                "PANGOLIN_ENDPOINT": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__PANGOLIN_ENDPOINT}"
                                     % compose_scope.upper(),
                "NEWT_ID": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_ID}"
                           % compose_scope.upper(),
                "NEWT_SECRET": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_SECRET}"
                               % compose_scope.upper(),
                "ACCEPT_CLIENTS": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__ACCEPT_CLIENTS:-false}"
                                  % compose_scope.upper(),
                # "ACCEPT_CLIENTS": True,
                "DOCKER_SOCKET": "/var/run/docker.sock",
            },
            "volumes": [
                "/var/run/docker.sock:/var/run/docker.sock",
            ],
            "networks": [],
        }

        # service_dict = get_pangolin_newt_service_skeleton(
        #     compose_scope=compose_scope,
        #     unique_suffix=_unique_suffix,
        # )

        unique_newt_service = f"newt_service.{_unique_suffix}"
        unique_newt_network = f"newt_network.{_unique_suffix}"

        networks = {
            "networks": {
                unique_newt_network: {
                    "name": unique_newt_network,
                    "driver": DockerComposeNetworkMode.BRIDGE,
                },
            }
        }

        service_dict["networks"] = [
            *networks["networks"].keys(),
            *scrape_networks.keys(),
        ]

        service = {
            "services": {
                unique_newt_service: service_dict,
            },
            **networks,
        }

        # docker_dict_include["services"].update(service)
        # docker_dict_include.update(networks)

        compose_yaml = yaml.safe_dump(service)

        yield Output(service)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "service": MetadataValue.md(f"```json\n{json.dumps(service, indent=2, default=str)}\n```"),
                "compose_yaml": MetadataValue.md(f"```yaml\n{compose_yaml}\n```"),
            },
        )

    return _asset


def simple_factory_alloy(
        ASSET_HEADER,
        compose_scope,
        name,
        ins,
) -> AssetsDefinition:

    @asset(
        **ASSET_HEADER,
        name=name,
        ins=ins,
    )
    def _asset(
            context: AssetExecutionContext,
            **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")
        env: Dict = CONFIG.env
        landscape_id: str = env.get("LANDSCAPE", "default")

        _unique_suffix = f"compose_scope-{compose_scope}.{landscape_id}"

        # service_dict = get_grafana_alloy_service_skeleton(
        #     # compose_scope=compose_scope,
        #     unique_suffix=_unique_suffix,
        # )

        alloy_config: pathlib.Path = kwargs.pop("alloy_config")

        volumes_dict = {
            "volumes": [
                f"{alloy_config.as_posix()}:/etc/alloy/config.alloy:ro",
            ]
        }

        # For portability, convert absolute volume paths to relative paths

        _volume_relative = []

        for v in volumes_dict["volumes"]:

            host, container = v.split(":", maxsplit=1)

            volume_dir_host_rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=CONFIG.docker_compose_expanded,
                path_dst=pathlib.Path(host),
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )

            _volume_relative.append(
                f"{volume_dir_host_rel_path.as_posix()}:{container}",
            )

        volumes_dict = {
            "volumes": [
                *_volume_relative,
            ]
        }

        service_dict: DockerComposeServiceDefinition = {
            "image": "docker.io/grafana/alloy:latest",
            "container_name": f"alloy_container.{_unique_suffix}",
            "restart": DockerComposePolicies.RESTART_POLICY.ON_FAILURE_3,
            # "environment": {
            #     "PANGOLIN_ENDPOINT": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__PANGOLIN_ENDPOINT}"
            #     % compose_scope.upper(),
            #     "NEWT_ID": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_ID}"
            #     % compose_scope.upper(),
            #     "NEWT_SECRET": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_SECRET}"
            #     % compose_scope.upper(),
            #     "ACCEPT_CLIENTS": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__ACCEPT_CLIENTS:-false}"
            #     % compose_scope.upper(),
            #     # "ACCEPT_CLIENTS": True,
            #     "DOCKER_SOCKET": "/var/run/docker.sock",
            # },
            "command": [
                "run",
                "--server.http.listen-addr=0.0.0.0:12345",
                "--storage.path=/var/lib/alloy/data",
                "/etc/alloy/config.alloy",
            ],
            **volumes_dict,
            "network_mode": DockerComposePolicies.NETWORK_MODE.HOST
            # "networks": [],
            # "ports": [
            #     "12345:12345",
            # ],
        }

        unique_alloy_service = f"alloy_service.{_unique_suffix}"
        # unique_alloy_network = f"newt_network.{_unique_suffix}"

        service = {
            "services": {
                unique_alloy_service: service_dict,
            },
        }

        # networks = {
        #     "networks": {
        #         unique_alloy_network: {
        #             "name": unique_alloy_network,
        #             "driver": DockerComposeNetworkMode.BRIDGE,
        #         },
        #     }
        # }
        #
        # service_dict["networks"] = [
        #     *networks["networks"].keys(),
        #     *scrape_networks.keys(),
        # ]
        #

        # docker_dict_include["services"].update(service)
        # docker_dict_include.update(networks)

        compose_yaml = yaml.safe_dump(service)

        yield Output(service)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "alloy_config": MetadataValue.path(alloy_config),
                "service": MetadataValue.md(f"```json\n{json.dumps(service, indent=2, default=str)}\n```"),
                "compose_yaml": MetadataValue.md(f"```yaml\n{compose_yaml}\n```"),
            },
        )

    return _asset
