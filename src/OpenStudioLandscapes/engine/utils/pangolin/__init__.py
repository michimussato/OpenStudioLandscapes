__all__ = [
    "add_newt_service_to_compose_scope",
]

from typing import Dict

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils.docker.compose_dicts import *


def add_newt_service_to_compose_scope(
    scrape_networks: Dict,
    docker_dict_include: Dict,
    compose_scope: ComposeScope,
    landscape_id: str,
) -> None:
    """
    Updates `docker_dict_include` with Pangolin `newt` service(s)
    and network(s) so that it directly connects itself with
    a Pangolin Site.

    Args:
        compose_scope: ComposeScope
        scrape_networks: dict of networks
        docker_dict_include: include-dict that will be populated with Pangolin `newt` service(s) and network(s)
        landscape_id: landscape id str

    Returns: None
    """

    _unique_suffix = f"compose_scope-{compose_scope.value}.{landscape_id}"

    service_dict = get_pangolin_newt_service_skeleton(
        compose_scope=compose_scope,
        unique_suffix=_unique_suffix,
    )

    unique_newt_service = f"newt_service.{_unique_suffix}"
    unique_newt_network = f"newt_network.{_unique_suffix}"

    services = {
        "services": {unique_newt_service: service_dict},
    }

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

    docker_dict_include.update(services)
    docker_dict_include.update(networks)

    return None
