# __all__ = [
#     "DOCKER_USE_CACHE",
#     "PIHOLE_USE_UNBOUND",
#     "GROUP",
#     "KEY",
#     "ASSET_HEADER",
#     "ENVIRONMENT",
#     "COMPOSE_SCOPE",
# ]

import pathlib
from typing import Generator, MutableMapping

from dagster import (
    asset,
    Output,
    AssetMaterialization,
    MetadataValue,
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.constants import DOCKER_USE_CACHE_GLOBAL


DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False
PIHOLE_USE_UNBOUND = True


GROUP = f"Compose_{ComposeScope.PI_HOLE}"
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
    "compute_kind": "python",
}

# @formatter:off
ENVIRONMENT = {
    "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
    "PIHOLE_USE_UNBOUND": PIHOLE_USE_UNBOUND,
    "PIHOLE_WEB_PORT": "81",
    "PIHOLE_WEB_PASSWORD": "myp4ssword",
    "PIHOLE_TIMEZONE": "Europe/Zurich",
    "PIHOLE_REV_SERVER": "false",
    "PIHOLE_DNS_DNSSEC": "true",
    "PIHOLE_DNS_LISTENING_MODE": [
        "all",
        "single",
    ][0],
    "PIHOLE_WEB_THEME": [
        "default-dark",
        "default-darker",
        "default-light",
        "default-auto",
        "lcars",
    ][0],
    "PI_HOLE_DATABASE_INSTALL_DESTINATION": {
        #################################################################
        # DB will be created in (hardcoded):
        #################################################################
        #################################################################
        # Inside Landscape:
        "default": pathlib.Path(
            "{DOT_LANDSCAPES}",
            "{LANDSCAPE}",
            f"{GROUP}__{'__'.join(KEY)}",
            "data",
            "etc-pihole",
        )
        .expanduser()
        .as_posix(),
        #################################################################
        #
        #################################################################
        #################################################################
        # Landscapes global:
        "global": pathlib.Path(
            "{DOT_LANDSCAPES}",
            ".pi-hole",
            "etc-pihole",
        )
        .expanduser()
        .as_posix(),
        #################################################################
        # # Prod DB:
        # "prod_db": pathlib.Path(
        #     "{NFS_ENTRY_POINT}",
        #     "services",
        #     "kitsu",
        # ).as_posix(),
        # #################################################################
        # # Test DB:
        # "test_db": pathlib.Path(
        #     "{NFS_ENTRY_POINT}",
        #     "test_data",
        #     "10.2",
        #     "kitsu",
        # ).as_posix(),
    }["global"],
    "UNBOUND_DATABASE_INSTALL_DESTINATION": {
        #################################################################
        # DB will be created in (hardcoded):
        #################################################################
        #################################################################
        # Inside Landscape:
        "default": pathlib.Path(
            "{DOT_LANDSCAPES}",
            "{LANDSCAPE}",
            f"{GROUP}__{'__'.join(KEY)}",
            "data",
            "etc-dnsmasq",
        )
        .expanduser()
        .as_posix(),
        #################################################################
        #
        #################################################################
        #################################################################
        # Landscape global:
        "global": pathlib.Path(
            "{DOT_LANDSCAPES}",
            ".pi-hole",
            "etc-dnsmasq",
        )
        .expanduser()
        .as_posix(),
        #################################################################
        # # Prod DB:
        # "prod_db": pathlib.Path(
        #     "{NFS_ENTRY_POINT}",
        #     "services",
        #     "kitsu",
        # ).as_posix(),
        # #################################################################
        # # Test DB:
        # "test_db": pathlib.Path(
        #     "{NFS_ENTRY_POINT}",
        #     "test_data",
        #     "10.2",
        #     "kitsu",
        # ).as_posix(),
    }["global"],
    # "CONFIGS_ROOT": pathlib.Path(
    #     get_configs_root(pathlib.Path(__file__)),
    # )
    # .expanduser()
    # .as_posix(),
    # "DATA_ROOT": pathlib.Path(
    #     get_data_root(pathlib.Path(__file__)),
    # )
    # .expanduser()
    # .as_posix(),
    # "BIN_ROOT": pathlib.Path(
    #     get_bin_root(pathlib.Path(__file__)),
    # )
    # .expanduser()
    # .as_posix(),
}
# @formatter:on


@asset(
    **ASSET_HEADER,
    description="",
)
def constants_pi_hole(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = dict()

    # _constants["DOCKER_USE_CACHE"] = DOCKER_USE_CACHE
    # _constants["ASSET_HEADER"] = ASSET_HEADER
    # _constants["ENVIRONMENT"] = ENVIRONMENT

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )
