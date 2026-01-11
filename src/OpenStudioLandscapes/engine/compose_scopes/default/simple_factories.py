import json
import pathlib
import textwrap
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
from OpenStudioLandscapes.engine.compose_scopes.default.constants import *


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
        description=textwrap.dedent(
            """
            This wrapper is disabled by default.
            To enable it, launch OpenStudioLandscapes with
            - `OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE=1`
            
            ---
            
            `newt` is the Pangolin tunnel service. It is the core component to
            make containerized Features publicly (securely) accessible on the web. 
            It is irrelevant whether Pangolin and `newt` are running on the same
            physical network or not - `newt` tunnels connect _over the web_ to the
            Pangolin instance while Pangolin controls access and permissions to 
            [Sites](https://docs.pangolin.net/manage/sites/install-site) and 
            [Resources](https://docs.pangolin.net/manage/resources/understanding-resources).
            
            - [Source](https://github.com/fosrl/newt)
            
            `newt` service connects to Pangolin Site
            - [Pangolin Site](https://docs.pangolin.net/manage/sites/install-site)
            
            When you create a new Site in Pangolin and you choose
            _Newt Tunnel (Recommended)_ as __Tunnel Type__ and pick 
            _Docker_ with _Docker Compose_ method for __Operating System__,
            you'll be provided with the following environment variables:
            - `PANGOLIN_ENDPOINT`
            - `NEWT_ID`
            - `NEWT_SECRET`
            
            This information is required for a Compose Scope to be able
            to connect to the Pangolin Site.
            
            More info on the 
            - `ComposeScopes / ComposeScope_<COMPOSE_SCOPE> / docker_compose_commands`
            Assets.
            """
        ),
    )
    def _asset(
            context: AssetExecutionContext,
            **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")

        if CONFIG.attach_pangolin_site_to_compose_scope:

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

        else:

            service = {}

        compose_yaml = yaml.safe_dump(service)

        yield Output(service)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "enabled": MetadataValue.bool(CONFIG.attach_pangolin_site_to_compose_scope),
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
        description=textwrap.dedent(
            """
            This wrapper is disabled by default.
            To enable it, launch OpenStudioLandscapes with
            - `OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE=1`
            
            ---
            
            Grafana Alloy is a telemetry data collector.
            
            I'm not entirely sure yet where exactly Alloy fits in the Grafana ecosystem.
            I've used Promtail so far and I'm still learning how to make the switch.
            [Grafana Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/)
            is deprecated and Alloy is taking its place:
            
            > Caution
            > 
            > Promtail is now deprecated and will enter into Long-Term 
            > Support (LTS) beginning Feb. 13, 2025. This means that 
            > Promtail will no longer receive any new feature updates, 
            > but it will receive critical bug fixes and security fixes. 
            > Commercial support will end after the LTS phase, which we 
            > anticipate will extend for about 12 months until 
            > February 28, 2026. End-of-Life (EOL) phase for Promtail will 
            > begin once LTS ends. Promtail is expected to reach EOL on 
            > March 2, 2026, afterwards no future support or updates will 
            > be provided. All future feature development will occur in 
            > Grafana Alloy.
            > 
            > If you are currently using Promtail, you should plan your 
            > migration to Alloy. The Alloy migration documentation 
            > includes a migration tool for converting your Promtail 
            > configuration to an Alloy configuration with a single command.
            
            So, Alloy collects
            - logs and sends them to Loki
            - metrics and sends them to Prometheus
            
            Resources:
            - [Monitor Docker Containers](https://grafana.com/docs/alloy/latest/monitor/monitor-docker-containers/)
            - [Use Alloy to send logs to Loki](https://grafana.com/docs/alloy/latest/tutorials/send-logs-to-loki/)
            - [Use Alloy to send metrics to Prometheus](https://grafana.com/docs/alloy/latest/tutorials/send-metrics-to-prometheus/)
            - [Christian Lempa](https://www.youtube.com/watch?v=E654LPrkCjo)
            """
        ),
    )
    def _asset(
            context: AssetExecutionContext,
            **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")

        alloy_config: pathlib.Path = kwargs.pop("alloy_config")

        if CONFIG.attach_grafana_alloy_to_compose_scope:

            env: Dict = CONFIG.env
            landscape_id: str = env.get("LANDSCAPE", "default")

            scrape_networks: Dict = kwargs.pop("scrape_networks")

            _unique_suffix = f"compose_scope-{compose_scope}.{landscape_id}"

            # service_dict = get_grafana_alloy_service_skeleton(
            #     # compose_scope=compose_scope,
            #     unique_suffix=_unique_suffix,
            # )

            alloy_data = pathlib.Path(
                env["DOT_LANDSCAPES"],
                env.get("LANDSCAPE", "default"),
                f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
                "alloy",
                "data",
            )

            volumes_dict = {
                "volumes": [
                    f"{alloy_config.as_posix()}:/etc/alloy/config.alloy:ro",
                    f"{alloy_data.as_posix()}:/var/lib/alloy/data",
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
                    # Non relative paths:
                    "/:/rootfs:ro",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "/run:/run:ro",
                    "/var/log:/var/log:ro",
                    "/sys:/sys:ro",
                    "/var/lib/docker:/var/lib/docker:ro",
                    "/run/udev/data:/run/udev/data:ro",
                ]
            }

            # combination of
            # - https://github.com/grafana/alloy-scenarios/blob/main/docker-monitoring/docker-compose-linux.yml
            # - https://www.youtube.com/watch?v=E654LPrkCjo
            service_dict: DockerComposeServiceDefinition = {
                "image": "docker.io/grafana/alloy:latest",
                # "privileged": True,
                "container_name": f"alloy_container.{_unique_suffix}",
                "restart": DockerComposePolicies.RESTART_POLICY.ON_FAILURE_3,
                # "environment": {},
                "command": [
                    "run",
                    f"--server.http.listen-addr={CONFIG.grafana_alloy_listen_address}",
                    "--storage.path=/var/lib/alloy/data",
                    "/etc/alloy/config.alloy",
                ],
                **volumes_dict,
                # "network_mode": DockerComposePolicies.NETWORK_MODE.HOST,
                "networks": [
                    *scrape_networks.keys()
                ],
                "ports": [
                    "12345:12345",
                ],
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

        else:

            service = {}

        compose_yaml = yaml.safe_dump(service)

        yield Output(service)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "enabled": MetadataValue.bool(CONFIG.attach_grafana_alloy_to_compose_scope),
                "alloy_config": MetadataValue.path(alloy_config),
                "service": MetadataValue.md(f"```json\n{json.dumps(service, indent=2, default=str)}\n```"),
                "compose_yaml": MetadataValue.md(f"```yaml\n{compose_yaml}\n```"),
            },
        )

    return _asset
