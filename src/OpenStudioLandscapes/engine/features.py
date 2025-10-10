from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *

FEATURES: dict[
    str, dict[str, bool | str | ComposeScope | OpenStudioLandscapesConfig]
] = {
    # "OpenStudioLandscapes-Ayn": {
    #     # To test faulty Feature definitions
    #     # Make sure things don't break if misconfigured
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.Ayn.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    "OpenStudioLandscapes-Ayon": {
        "enabled": True
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_AYON"
        ),
        "module": "OpenStudioLandscapes.Ayon.definitions",
        "definitions": "OpenStudioLandscapes.Ayon.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Kitsu": {
        "enabled": True
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_KITSU"
        ),
        "module": "OpenStudioLandscapes.Kitsu.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Dagster": {
        "enabled": True
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DAGSTER"
        ),
        "module": "OpenStudioLandscapes.Dagster.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Deadline-10-2": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DEADLINE_10_2"
        ),
        "module": "OpenStudioLandscapes.Deadline_10_2.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Deadline-10-2-Worker": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DEADLINE_10_2_WORKER"
        ),
        "module": "OpenStudioLandscapes.Deadline_10_2_Worker.definitions",
        "compose_scope": ComposeScope.WORKER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-filebrowser": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_FILEBROWSER"
        ),
        "module": "OpenStudioLandscapes.filebrowser.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Grafana": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_GRAFANA"
        ),
        "module": "OpenStudioLandscapes.Grafana.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_SESI_GCC_9_3_HOUDINI_20"
        ),
        "module": "OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-NukeRLM-8": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_NUKERLM_8"
        ),
        "module": "OpenStudioLandscapes.NukeRLM_8.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-RustDeskServer": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_RUSTDESKSERVER"
        ),
        "module": "OpenStudioLandscapes.RustDeskServer.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-OpenCue": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_OPENCUE"
        ),
        # error: no health check configured
        "module": "OpenStudioLandscapes.OpenCue.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-LikeC4": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_LIKEC4"
        ),
        # error This project's package.json defines "packageManager": "yarn@pnpm@10.6.2". However, the current global version of Yarn is 1.22.22.
        "module": "OpenStudioLandscapes.LikeC4.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Syncthing": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_SYNCTHING"
        ),
        "module": "OpenStudioLandscapes.Syncthing.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Twingate": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_TWINGATE"
        ),
        "module": "OpenStudioLandscapes.Twingate.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Watchtower": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_WATCHTOWER"
        ),
        "module": "OpenStudioLandscapes.Watchtower.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    # OpenStudioLandscapes-Template
    "OpenStudioLandscapes-Template": {
        "enabled": False
        or get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_TEMPLATE"
        ),
        "module": "OpenStudioLandscapes.Template.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
}


# Todo:
#  - [ ] move from OpenStudioLandscapes.ReadmeGenerator.readme_generator._generator to OpenStudioLandscapes.engine or maybe nox
# # discord = "https://discord.com/channels/1357343453364748419"
# # slack = "https://app.slack.com/client/T08L6M6L0S3"
#
# community_channels = {
#     "OpenStudioLandscapes": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes",
#         },
#         "discord": {
#             "channel_name": "# openstudiolandscapes-general",
#             "channel_id": "1357343454065328202",
#             "invite": "https://discord.gg/F6bDRWsHac",
#         },
#         # "slack": {
#         #     "channel_name": "# openstudiolandscapes-general",
#         #     "channel_id": "C08LK80NBFF",
#         # },
#     },
#     "OpenStudioLandscapes-Ayon": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Ayon",
#         },
#         "discord": {
#             "channel_name": "# openstudiolandscapes-ayon",
#             "channel_id": "1357722468336271411",
#             "invite": "https://discord.gg/gd6etWAF3v",
#         },
#         # "slack": {
#         #     "channel_name": "# openstudiolandscapes-ayon",
#         #     "channel_id": "C08LLBC7CB0",
#         # },
#     },
#     "OpenStudioLandscapes-Dagster": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Dagster",
#         },
#         "discord": {
#             "channel_name": "# openstudiolandscapes-dagster",
#             "channel_id": "1358016764608249856",
#             "invite": "https://discord.gg/jwB3DwmKvs",
#         },
#         # "slack": {
#         #     "channel_id": "C08LZR5JFA6",
#         #     "channel_name": "# openstudiolandscapes-dagster",
#         # },
#     },
#     "OpenStudioLandscapes-Kitsu": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Kitsu",
#         },
#         "discord": {
#             "channel_name": "# openstudiolandscapes-kitsu",
#             "channel_id": "1357638253632688231",
#             "invite": "https://discord.gg/6cc6mkReJ7",
#         },
#         # "slack": {
#         #     "channel_name": "# openstudiolandscapes-kitsu",
#         #     "channel_id": "C08L6M70ZB9",
#         # },
#     },
#     # "OpenStudioLandscapes-Deadline-10-2": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-Deadline-10-2",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1358017409276973088",
#     #         "channel_name": "# openstudiolandscapes-deadline-10-2",
#     #         "invite": "https://discord.gg/p2UjxHk4Y3",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "C08LZR963A6",
#     #     #     "channel_name": "# openstudiolandscapes-deadline-10-2",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-Deadline-10-2-Worker": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-Deadline-10-2-Worker",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1358024594409259059",
#     #         "channel_name": "# openstudiolandscapes-deadline-10-2-worker",
#     #         "invite": "https://discord.gg/ttkbfkzUmf",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "C08LZSBM998",
#     #     #     "channel_name": "# openstudiolandscapes-deadline-10-2-worker",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-filebrowser": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-filebrowser",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1364746200175083520",
#     #         "channel_name": "# openstudiolandscapes-filebrowser",
#     #         "invite": "https://discord.gg/stzNsZBmwk",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-NukeRLM-8": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-NukeRLM-8",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1358017656732782672",
#     #         "channel_name": "# openstudiolandscapes-nukerlm-8",
#     #         "invite": "https://discord.gg/bMVqrNrMg2",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "C08LZDLFTMH",
#     #     #     "channel_name": "# openstudiolandscapes-nukerlm-8",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-n8n": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-n8n",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1420384480526602320",
#     #         "channel_name": "# openstudiolandscapes-n8n",
#     #         "channel_name": "https://discord.gg/zVFJUEaAwK",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "# openstudiolandscapes-n8n",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1358018027190484993",
#     #         "channel_name": "# openstudiolandscapes-sesi-gcc-9-3-houdini-20",
#     #         "invite": "https://discord.gg/Zwmn3VAMDx",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "C08LUTR1WG5",
#     #     #     "channel_name": "# openstudiolandscapes-sesi-gcc-9-3-houdini-20",
#     #     # },
#     # },
#     "OpenStudioLandscapes-RustDeskServer": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-RustDeskServer",
#         },
#         "discord": {
#             "channel_id": "1414567463227621510",
#             "channel_name": "# openstudiolandscapes-rustdeskserver",
#             "invite": "https://discord.gg/nJ8Ffd2xY3",
#         },
#         # "slack": {
#         #     "channel_id": "C09E6HA0ZPW",
#         #     "channel_name": "# openstudiolandscapes-rustdeskserver",
#         # },
#     },
#     "OpenStudioLandscapes-Teleport": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Teleport",
#         },
#         "discord": {
#             "channel_id": "1420385295026884659",
#             "channel_name": "# openstudiolandscapes-teleport",
#             "invite": "https://discord.gg/SNMCw5aDfm",
#         },
#         # "slack": {
#         #     "channel_id": "C09E6HA0ZPW",
#         #     "channel_name": "# openstudiolandscapes-rustdeskserver",
#         # },
#     },
#     "OpenStudioLandscapes-Twingate": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Twingate",
#         },
#         "discord": {
#             "channel_id": "1414768065174044844",
#             "channel_name": "# openstudiolandscapes-twingate",
#             "invite": "https://discord.gg/tREYa6UNJf",
#         },
#         # "slack": {
#         #     "channel_id": "C09E6HA0ZPW",
#         #     "channel_name": "# openstudiolandscapes-rustdeskserver",
#         # },
#     },
#     # "OpenStudioLandscapes-Syncthing": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-Syncthing",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1364746871381168138",
#     #         "channel_name": "# openstudiolandscapes-syncthing",
#     #         "invite": "https://discord.gg/upb9MCqb3X",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-Watchtower": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-Watchtower",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1364747275938562079",
#     #         "channel_name": "# openstudiolandscapes-watchtower",
#     #         "invite": "https://discord.gg/5CQEjBaHg8",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-OpenCue": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-OpenCue",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1379799680807997500",
#     #         "channel_name": "# openstudiolandscapes-opencue",
#     #         "invite": "https://discord.gg/3DdCZKkVyZ",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "",
#     #     # },
#     # },
#     # "OpenStudioLandscapes-Grafana": {
#     #     "github": {
#     #         "repo_name": "OpenStudioLandscapes-Grafana",
#     #     },
#     #     "discord": {
#     #         "channel_id": "1379800002179760159",
#     #         "channel_name": "# openstudiolandscapes-grafana",
#     #         "invite": "https://discord.gg/gEDQ8vJWDb",
#     #     },
#     #     # "slack": {
#     #     #     "channel_id": "",
#     #     #     "channel_name": "",
#     #     # },
#     # },
#     # Template
#     "OpenStudioLandscapes-Template": {
#         "github": {
#             "repo_name": "OpenStudioLandscapes-Template",
#         },
#         "discord": {
#             "channel_id": "1414568696860512358",
#             "channel_name": "# openstudiolandscapes-template",
#             "invite": "https://discord.gg/J59GYp3Wpy",
#         },
#         # "slack": {
#         #     "channel_id": "C09DMN2LH71",
#         #     "channel_name": "# openstudiolandscapes-rustdeskserver",
#         # },
#     },
# }
