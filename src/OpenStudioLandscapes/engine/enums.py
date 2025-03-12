__all__ = [
    # "ComposeScope",
    "ComposeNetworkMode",
]


import enum


# class ComposeScope(enum.StrEnum):
#     DEFAULT = "default"
#     WORKER = "worker"


class ComposeNetworkMode(enum.StrEnum):
    # https://docs.docker.com/engine/network/
    # Docker Compose Ports settings
    # will be ignored if other than "default"
    DEFAULT = "default"
    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"
    OVERLAY = "overlay"
    IPVLAN = "ipvlan"
    MACVLAN = "macvlan"
