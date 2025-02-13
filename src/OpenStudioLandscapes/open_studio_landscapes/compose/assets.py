import copy
import importlib
import yaml
import pathlib
import json

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

GROUP = "Compose_Hack"
KEY = "Compose"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python",
}

def_locs = [
    # "OpenStudioLandscapes.open_studio_landscapes.base",
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


# @asset(
#     **asset_header,
# )
# def get_code_locations(
#     context: AssetExecutionContext,
# ) -> list:
#
#     global ins
#
#     context.log.info(f"{ins = }")
#     context.log.info(f"{json.dumps(ins, indent=2) = }")
#
#     yield Output(ins)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             # "__".join(context.asset_key.path): MetadataValue.json(json.dumps(ins, indent=2)),
#             context.asset_key.path: MetadataValue.str(ins),
#         },
#     )


@asset(
    **asset_header,
    # group_name="Environment",
    deps=[
        AssetKey([KEY_BASE, "group_out"]),
    ],
)
def load_base(
    context: AssetExecutionContext,
) -> dict:
    # @formatter:off

    # load asset data from external code location into memory
    # and provide it as the Output of this asset
    load_from = AssetKey([KEY_BASE, "group_out"])
    defs = importlib.import_module("OpenStudioLandscapes.open_studio_landscapes.base.definitions").defs
    df: dict = defs.load_asset_value(
        asset_key=load_from,
        instance=context.instance,
    )

    context.log.info(f"loaded data from Asset {load_from}: {json.dumps(df, indent=2)}")

    yield Output(df)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(df),
        },
    )


@asset(
    **asset_header,
    # group_name="Environment",
    ins={
        "base": AssetIn(AssetKey([KEY, "load_base"])),
    },
)
def env(
    context: AssetExecutionContext,
    base: dict,
) -> dict:

    ret = base.get("env", {})

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **asset_header,
    # ins={
    #     "code_locations": AssetIn(AssetKey([KEY, "get_code_locations"])),
    # },
    deps=[
        *[i["asset_key"] for i in ins],
    ],
)
def group_in(
    context: AssetExecutionContext,
    # code_locations: list,
) -> list:

    # context.pdb.set_trace()

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
        yaml_path: pathlib.Path = dep["def_dict"]
        context.log.info(yaml_path)
        yamls.append(yaml_path.as_posix())

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


# Todo
#  - [ ] we need the env here
#  "OpenStudioLandscapes.open_studio_landscapes.base"
group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey(
            [KEY, "compose"]
        ),
        "env": AssetKey(
            [KEY, "env"]
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
