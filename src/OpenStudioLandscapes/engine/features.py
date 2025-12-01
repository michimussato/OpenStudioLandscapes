from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *

FEATURES: dict[
    str, dict[str, bool | str | ComposeScope | OpenStudioLandscapesConfig]
] = {
    "OpenStudioLandscapes-Ayon": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_AYON"
        ),
        "module": "OpenStudioLandscapes.Ayon.definitions",
        "definitions": "OpenStudioLandscapes.Ayon.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Kitsu": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_KITSU"
        ),
        "module": "OpenStudioLandscapes.Kitsu.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Dagster": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DAGSTER"
        ),
        "module": "OpenStudioLandscapes.Dagster.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Deadline-10-2": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DEADLINE_10_2"
        ),
        "module": "OpenStudioLandscapes.Deadline_10_2.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Deadline-10-2-Worker": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_DEADLINE_10_2_WORKER"
        ),
        "module": "OpenStudioLandscapes.Deadline_10_2_Worker.definitions",
        "compose_scope": ComposeScope.WORKER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-filebrowser": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_FILEBROWSER"
        ),
        "module": "OpenStudioLandscapes.filebrowser.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Flamenco": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_FLAMENCO"
        ),
        "module": "OpenStudioLandscapes.Flamenco.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Flamenco-Worker": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_FLAMENCO_WORKER"
        ),
        "module": "OpenStudioLandscapes.Flamenco_Worker.definitions",
        "compose_scope": ComposeScope.WORKER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Grafana": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_GRAFANA"
        ),
        "module": "OpenStudioLandscapes.Grafana.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_SESI_GCC_9_3_HOUDINI_20"
        ),
        "module": "OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-NukeRLM-8": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_NUKERLM_8"
        ),
        "module": "OpenStudioLandscapes.NukeRLM_8.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-RustDeskServer": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_RUSTDESKSERVER"
        ),
        "module": "OpenStudioLandscapes.RustDeskServer.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-OpenCue": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_OPENCUE"
        ),
        # error: no health check configured
        "module": "OpenStudioLandscapes.OpenCue.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-LikeC4": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_LIKEC4"
        ),
        # error This project's package.json defines "packageManager": "yarn@pnpm@10.6.2". However, the current global version of Yarn is 1.22.22.
        "module": "OpenStudioLandscapes.LikeC4.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Syncthing": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_SYNCTHING"
        ),
        "module": "OpenStudioLandscapes.Syncthing.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Twingate": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_TWINGATE"
        ),
        "module": "OpenStudioLandscapes.Twingate.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Watchtower": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_WATCHTOWER"
        ),
        "module": "OpenStudioLandscapes.Watchtower.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-VERT": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_VERT"
        ),
        "module": "OpenStudioLandscapes.VERT.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    # OpenStudioLandscapes-Template
    "OpenStudioLandscapes-Template": {
        "enabled": get_bool_env(
            "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_TEMPLATE"
        ),
        "module": "OpenStudioLandscapes.Template.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
}
