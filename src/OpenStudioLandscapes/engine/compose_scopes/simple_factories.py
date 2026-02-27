import json
import pathlib
import shutil
import textwrap
from typing import Any, Dict, Generator

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.compose_scopes.constants import *
from OpenStudioLandscapes.engine.config.models import (
    ComposeScopeBaseModel,
)
from OpenStudioLandscapes.engine.enums import (
    DockerComposeNetworkMode,
    DockerComposePolicies,
)
from OpenStudioLandscapes.engine.utils import get_relative_path_via_common_root
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import (
    DockerComposeServiceDefinition,
)


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
        description=textwrap.dedent("""
            This wrapper is disabled by default.
            To enable it, launch OpenStudioLandscapes with
            - `OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE=1` or `--attach-pangolin-site-to-compose-scope`
            
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
            """),
    )
    def _asset(
        context: AssetExecutionContext,
        **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")

        # group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")
        # # env_base: Dict = group_out_base.env
        # config_engine: ConfigEngine = group_out_base.config_engine

        if CONFIG.attach_pangolin_site_to_compose_scope:

            env: Dict = CONFIG.env
            landscape_id: str = env.get("LANDSCAPE", "default")

            newt_service = "newt-worker"

            scrape_networks: Dict = kwargs.pop("scrape_networks")

            _unique_suffix = f"compose_scope-{compose_scope}.{landscape_id}"

            service_dict: DockerComposeServiceDefinition = {
                "image": "docker.io/fosrl/newt",
                "container_name": f"{newt_service}.{landscape_id}",
                "hostname": f"newt-{compose_scope}",
                "restart": DockerComposePolicies.RESTART_POLICY.ALWAYS,
                "environment": {
                    "TZ": CONFIG.config_engine.tz,
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
                    **CONFIG.config_engine.global_environment_variables,
                },
                "volumes": list(
                    {
                        "/var/run/docker.sock:/var/run/docker.sock",
                        *CONFIG.config_engine.global_bind_volumes,
                    }
                ),
                # "command": [
                #     "newt",
                #     # -ping-interval string
                #     #         Interval for pinging the server (default 3s) (default "3s")
                #     #   -ping-timeout string
                #     #                 Timeout for each ping (default 5s) (default "5s")
                # ],
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
                    newt_service: service_dict,
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
                "enabled": MetadataValue.bool(
                    CONFIG.attach_pangolin_site_to_compose_scope
                ),
                "service": MetadataValue.md(
                    f"```json\n{json.dumps(service, indent=2, default=str)}\n```"
                ),
                "compose_yaml": MetadataValue.md(f"```yaml\n{compose_yaml}\n```"),
            },
        )

    return _asset


def simple_factory_alloy(
    ASSET_HEADER: Dict,
    compose_scope: str,
    port_range_pool: set,
    name: str,
    ins: Dict[str, AssetIn],
) -> AssetsDefinition:

    @asset(
        **ASSET_HEADER,
        name=name,
        ins=ins,
        description=textwrap.dedent("""
            This wrapper is disabled by default.
            To enable it, launch OpenStudioLandscapes with
            - `OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE=1` or `--attach-grafana-alloy-to-compose-scope`
            
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
            """),
    )
    def _asset(
        context: AssetExecutionContext,
        **kwargs,
    ) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")

        alloy_config: pathlib.Path = kwargs.pop("alloy_config")

        build_docker_image_alloy: Dict = kwargs.pop("build_docker_image_alloy")

        cmd_append = {"cmd": [], "exclude_from_quote": []}
        exclude_from_quote = []
        cmd_docker_compose_set_dynamic_hostnames = []

        if CONFIG.attach_grafana_alloy_to_compose_scope:

            env: Dict = CONFIG.env
            landscape_id: str = env.get("LANDSCAPE", "default")

            scrape_networks: Dict = kwargs.pop("scrape_networks")

            _unique_suffix = f"compose_scope-{compose_scope}.{landscape_id}"

            # service_dict = get_grafana_alloy_service_skeleton(
            #     # compose_scope=compose_scope,
            #     unique_suffix=_unique_suffix,
            # )

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
                "volumes": list(
                    {
                        # Add named volume for workers
                        # With bind volumes, all workers try to access the
                        # same directory on the server, leading to errors like:
                        # [...]
                        # ts=2026-02-25T20:34:21.288457728Z level=error msg="Failed to create existing container: /system.slice/docker-7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f.scope: failed to identify the read-write layer ID for container \"7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.2947955Z level=error msg="Failed to create existing container: /system.slice/docker-e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52.scope: failed to identify the read-write layer ID for container \"e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.309287945Z level=error msg="Failed to create existing container: /system.slice/docker-21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d.scope: failed to identify the read-write layer ID for container \"21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.322206762Z level=error msg="Failed to create existing container: /system.slice/docker-3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682.scope: failed to identify the read-write layer ID for container \"3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.328600629Z level=error msg="Failed to create existing container: /system.slice/docker-faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c.scope: failed to identify the read-write layer ID for container \"faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.33229662Z level=error msg="Failed to create existing container: /system.slice/docker-f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709.scope: failed to identify the read-write layer ID for container \"f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.355671359Z level=error msg="Failed to create existing container: /system.slice/docker-f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709.scope: failed to identify the read-write layer ID for container \"f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/f3e16f4759f45f9204bf301b46d54c680f686e6ef9a20a1ffd2e342980f68709/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.359779736Z level=error msg="Failed to create existing container: /system.slice/docker-e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52.scope: failed to identify the read-write layer ID for container \"e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/e366ae8d3756d76c08d9696c0e0153ded8451d784a7ed631b846d01425f20b52/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.365427448Z level=error msg="Failed to create existing container: /system.slice/docker-7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f.scope: failed to identify the read-write layer ID for container \"7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/7ef95d79314e8670e41b1253a1ced907ff9840df080777ac0cfd1b7855e5ee9f/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.372840298Z level=error msg="Failed to create existing container: /system.slice/docker-21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d.scope: failed to identify the read-write layer ID for container \"21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.377242361Z level=error msg="Failed to create existing container: /system.slice/docker-3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682.scope: failed to identify the read-write layer ID for container \"3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.381073248Z level=error msg="Failed to create existing container: /system.slice/docker-faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c.scope: failed to identify the read-write layer ID for container \"faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/faf83c438a6b2dcaed762b18a6f88c10d63d43d6c446b7acc98028d3c7f6891c/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.381502091Z level=info msg="finished node evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d node_id=prometheus.exporter.cadvisor.example duration=407.691454ms
                        # ts=2026-02-25T20:34:21.382775195Z level=info msg="finished node evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d node_id=discovery.relabel.example duration=1.092146ms
                        # ts=2026-02-25T20:34:21.385314351Z level=info msg="finished node evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d node_id=prometheus.scrape.scraper duration=2.320388ms
                        # ts=2026-02-25T20:34:21.385911581Z level=info msg="finished node evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d node_id=discovery.relabel.docker duration=363.897µs
                        # ts=2026-02-25T20:34:21.391175821Z level=info msg="Failed to process watch event {EventType:0 Name:/system.slice/docker-21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d.scope WatchSource:0}: failed to identify the read-write layer ID for container \"21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/21694a0c41f2e2a4985fc255f5a1d495769dc10f21f8986bcab962b1f62f1a1d/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # ts=2026-02-25T20:34:21.394921864Z level=info msg="finished node evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d node_id=loki.source.docker.docker duration=8.403253ms
                        # ts=2026-02-25T20:34:21.395142692Z level=info msg="finished complete graph evaluation" controller_path=/ controller_id="" trace_id=a0ff776240535fc0368178e9ee23e07d duration=442.259628ms
                        # Error: /etc/alloy/config.alloy:34:1: Failed to build component: building component: get segment range: segments are not sequential
                        # 33 |   // Configure a prometheus.remote_write component to send metrics to a Prometheus server.
                        # 34 |   prometheus.remote_write "demo" {
                        #    |  _^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        # 35 | |   endpoint {
                        # 36 | |     // Endpoints"
                        # 37 | |     // - https://prometheus.io/docs/prometheus/latest/querying/api/
                        # 38 | |     //
                        # 39 | |     // Verify operational:
                        # 40 | |     // - http://10.1.2.15:9090/api/v1/status/config
                        # 41 | |     url = "http://10.1.2.15:9090/api/v1/write"
                        # 42 | |   }
                        # 43 | | }
                        #    | |_^
                        # 44 |
                        # ts=2026-02-25T20:34:21.398344034Z level=info msg="Failed to process watch event {EventType:0 Name:/system.slice/docker-3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682.scope WatchSource:0}: failed to identify the read-write layer ID for container \"3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682\". - open /rootfs/var/lib/docker/image/overlayfs/layerdb/mounts/3009777d142ed8a9623fb9fe7cfcd07cf1bf9c4dcb9f3e5fc3481a5b9dac4682/mount-id: no such file or directory" component_path=/ component_id=prometheus.exporter.cadvisor.example
                        # Error: could not perform the initial load successfully
                        # 2026/02/25 20:34:21 collector server run finished with error: could not perform the initial load successfully
                        #
                        # This is necessary because we cannot specify dynamic host mount
                        # points using environment variables specified inside the container
                        # (not yet at least). So, named volumes are an easy workaround
                        # to create container specific, persistent volumes.
                        # Data in here is probably not that important anyway - just
                        # work data for the worker. The results of computations will
                        # end up in the mounted bind volume.
                        "alloy-worker-files:/var/lib/alloy/data:rw",
                        *_volume_relative,
                        # Non relative paths:
                        "/:/rootfs:ro",
                        "/var/run/docker.sock:/var/run/docker.sock",
                        "/run:/run:ro",
                        "/var/log:/var/log:ro",
                        "/sys:/sys:ro",
                        "/var/lib/docker:/var/lib/docker:ro",
                        "/run/udev/data:/run/udev/data:ro",
                        # [ ] /dev/disk/:/dev/disk:ro
                        # [ ] /dev/zfs/:/dev/zfs:ro
                        *CONFIG.config_engine.global_bind_volumes,
                    }
                )
            }

            # Avoid port conflicts:
            # - https://christian-schou.com/blog/how-port-mapping-works-in-docker-compose/
            # - https://labex.io/tutorials/docker-how-to-solve-docker-network-port-conflicts-493644
            if len(port_range_pool) <= 1:
                port_mapping = f"{CONFIG.grafana_alloy_listen_port_host}:{CONFIG.grafana_alloy_listen_port_container}"
            else:
                port_mapping = f"{CONFIG.grafana_alloy_listen_port_host}-{CONFIG.grafana_alloy_listen_port_host + len(port_range_pool) - 1}:{CONFIG.grafana_alloy_listen_port_container}"

            alloy_service = "alloy-worker"

            # combination of
            # - https://github.com/grafana/alloy-scenarios/blob/main/docker-monitoring/docker-compose-linux.yml
            # - https://www.youtube.com/watch?v=E654LPrkCjo
            service_dict: DockerComposeServiceDefinition = {
                # "image": "docker.io/grafana/alloy:latest",
                "image": "%s%s:%s"
                % (
                    build_docker_image_alloy["image_prefixes"],
                    build_docker_image_alloy["image_name"],
                    build_docker_image_alloy["image_tags"][0],
                ),
                "privileged": True,
                "container_name": f"{alloy_service}.{landscape_id}",
                # Some fixed hostname is needed.
                # Otherwise, the Grafana references in Dashboards no longer work.
                # Not setting a hostname means that a random name will be assigned.
                "restart": DockerComposePolicies.RESTART_POLICY.ON_FAILURE_3,
                "environment": {
                    "TZ": CONFIG.config_engine.tz,
                    **CONFIG.config_engine.global_environment_variables,
                },
                # "entrypoint": [
                #     "/usr/bin/hostname",
                #     "alloy-minion01",
                #     "&&",
                #     "/bin/alloy",
                # ],
                "command": [
                    "run",
                    f"--server.http.listen-addr={CONFIG.grafana_alloy_listen_address}:{CONFIG.grafana_alloy_listen_port_container}",
                    "--storage.path=/var/lib/alloy/data",
                    "/etc/alloy/config.alloy",
                ],
                **volumes_dict,
                # "network_mode": DockerComposePolicies.NETWORK_MODE.HOST,
                "networks": [*scrape_networks.keys()],
                "ports": [
                    port_mapping,
                ],
            }

            # unique_alloy_service = f"{alloy_service}.{_unique_suffix}"
            # unique_alloy_network = f"newt_network.{_unique_suffix}"

            service = {
                "services": {
                    alloy_service: service_dict,
                },
            }

            docker_dict: Dict[Any, Any] = {

            # https://docs.docker.com/engine/storage/volumes/#use-a-volume-with-docker-compose
                **service,
                "volumes": {
                    "alloy-worker-files": {
                        "external": False,
                    },
                }
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

            container_name = ".".join([alloy_service, env.get("LANDSCAPE", "default")])

            target_worker = (
                "\"$($(which docker) inspect --format '{{ .State.Pid }}' %s)\""
                % container_name
            )
            hostname_worker = f"${{HOSTNAME}}-{alloy_service}"

            # hostname_worker_truncated = hostname_worker.replace(".", "_")[:45]

            exclude_from_quote.extend(
                [
                    target_worker,
                    hostname_worker,
                    # hostname_worker_truncated,
                ]
            )

            cmd_docker_compose_set_dynamic_hostname_worker = [
                shutil.which("sudo"),
                "--stdin",
                # https://man7.org/linux/man-pages/man1/nsenter.1.html
                shutil.which("nsenter"),
                "--target",
                target_worker,
                "--uts",
                "hostname",
                hostname_worker,
            ]

            cmd_docker_compose_set_dynamic_hostnames.extend(
                [
                    "&&",
                    *cmd_docker_compose_set_dynamic_hostname_worker,
                    "||",
                    "echo",
                    f"could not set hostname for {container_name}",
                ]
            )

            cmd_append["cmd"].extend(cmd_docker_compose_set_dynamic_hostnames)
            cmd_append["exclude_from_quote"].extend(
                [
                    "$(which docker)",
                    "&&",
                    ";",
                    "||",
                    *exclude_from_quote,
                ]
            )

        else:

            service = {}

            docker_dict: Dict[Any, Any] = {
                **service,
            }

        compose_yaml = yaml.safe_dump(docker_dict)

        ret = {
            "docker_dict": docker_dict,
            "cmd_append": cmd_append,
        }

        yield Output(ret)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "enabled": MetadataValue.bool(
                    CONFIG.attach_grafana_alloy_to_compose_scope
                ),
                "alloy_config": MetadataValue.path(alloy_config),
                "docker_dict": MetadataValue.md(
                    f"```json\n{json.dumps(docker_dict, indent=2, default=str)}\n```"
                ),
                "compose_yaml": MetadataValue.md(f"```yaml\n{compose_yaml}\n```"),
                "cmd_append": MetadataValue.json(cmd_append),
            },
        )

    return _asset
