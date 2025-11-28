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
        docker_dict_include:

    Returns: None
    """
    service_dict = get_pangolin_newt_service_skeleton(
        compose_scope=compose_scope,
        landscape_id=landscape_id,
    )

    services = {
        "services": {f"newt.{compose_scope.value}.{landscape_id}": service_dict},
    }

    networks = {"networks": {"default": {"name": "pangolin_default"}}}

    service_dict["networks"] = [
        *networks["networks"].keys(),
        *scrape_networks.keys(),
    ]

    docker_dict_include.update(services)
    docker_dict_include.update(networks)

    return None
