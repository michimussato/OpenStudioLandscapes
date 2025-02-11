import copy
import importlib
import yaml

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    AssetsDefinition,
)

from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_group_out
from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_docker_compose_graph

GROUP = "Compose"
KEY = "Compose"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python",
}

def_locs = [
    "OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu",
    "OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4",
]


ins = list()

for def_loc in def_locs:
    dep = dict()
    key = importlib.import_module(f"{def_loc}.assets").KEY
    load_from = AssetKey([key, "group_out"])
    dep["code_location"] = def_loc
    dep["asset_key"] = load_from
    dep["defs"] = None
    dep["def_dict"] = None

    ins.append(copy.deepcopy(dep))


@asset(
    **asset_header,
    deps=[
        *[i["asset_key"] for i in ins],
    ],
)
def group_in(
    context: AssetExecutionContext,
) -> list:

    # load asset data from external code location into memory
    # and provide it as the Output of this asset

    # for def_loc in def_locs:
    #     key = importlib.import_module(f"{def_loc}.assets").KEY
    #     load_from = AssetKey([key, "group_out"])
    #     defs = importlib.import_module(f"{def_loc}.definitions").defs
    for dep in ins:
        dep["defs"] = importlib.import_module(f"{dep['code_location']}.definitions").defs
        dep["def_dict"]: dict = dep["defs"].load_asset_value(
            asset_key=dep["asset_key"],
            instance=context.instance,
        )

    context.log.info(ins)

    yamls = list()

    for dep in ins:
        yamls.append(dep["def_dict"].as_posix())

    context.log.info(yamls)

    # context.log.info(f"loaded data from Asset {load_from}: {json.dumps(df, indent=2)}")

    yield Output(yamls)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(yamls),
        },
    )


@asset(
    **asset_header,
    ins={
        "group_in": AssetIn(AssetKey([KEY, "group_in"])),
        # "grafana": AssetIn(AssetKey(["Grafana", "group_out"])),
        # "dagster": AssetIn(AssetKey(["Dagster", "group_out"])),
        # "likec4": AssetIn(AssetKey(["LikeC4", "group_out"])),
        # "kitsu": AssetIn(AssetKey(["Kitsu", "group_out"])),
        # "compose_include": AssetIn(AssetKey([KEY, "compose_include"])),
    },
)
def compose(
    context: AssetExecutionContext,
    group_in: list,  # pylint: disable=redefined-outer-name
) -> dict:
    """ """

    docker_dict = {
        "include": [{"path": [i]} for i in group_in],
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


# @asset(
#     **asset_header,
#     ins={
#         "compose": AssetIn(
#             AssetKey([KEY, "compose"]),
#         ),
#         "env": AssetIn(
#             AssetKey([KEY_BASE, "env"]),
#         ),
#     },
# )
# def group_out(
#     context: AssetExecutionContext,
#     compose: dict,  # pylint: disable=redefined-outer-name
#     env: dict,  # pylint: disable=redefined-outer-name
# ) -> pathlib.Path:
#
#     docker_yaml = yaml.dump(compose)
#
#     docker_compose = pathlib.Path(
#         env["DOT_LANDSCAPES"],
#         env.get("LANDSCAPE", "default"),
#         KEY,
#         "docker_compose",
#         "__".join(context.asset_key.path),
#         "docker-compose.yml",
#     )
#
#     docker_compose.parent.mkdir(parents=True, exist_ok=True)
#
#     with open(docker_compose, "w") as fw:
#         fw.write(docker_yaml)
#
#     project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}"
#
#     cmd_docker_compose_up = [
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         docker_compose.as_posix(),
#         "--project-name",
#         project_name,
#         "up",
#         "--remove-orphans",
#     ]
#
#     cmd_docker_compose_down = [
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         docker_compose.as_posix(),
#         "--project-name",
#         project_name,
#         "down",
#         "--remove-orphans",
#     ]
#
#     yield Output(docker_compose)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
#             "cmd_docker_compose_up": MetadataValue.path(
#                 " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
#             ),
#             "cmd_docker_compose_down": MetadataValue.path(
#                 " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
#             ),
#             "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
#         },
#     )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey(
            [KEY, "compose"]
        ),
        "env": AssetKey(
            [KEY_BASE, "env"]
        ),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "group_out": AssetKey(
            [KEY, "group_out"]
        ),
    },
)
