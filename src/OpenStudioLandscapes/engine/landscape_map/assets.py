import base64
import enum
import shutil
import subprocess
from typing import Any, Generator
import yaml

import pydot
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)
from pydot import Dot

from OpenStudioLandscapes.engine.compose_scopes.assets import (
    COMPOSE_SCOPE_GROUP_PREFIX,
)
from OpenStudioLandscapes.engine.config import dist
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesBaseOut
from OpenStudioLandscapes.engine.utils import get_dynamic_ins

feature_ins = get_dynamic_ins(
    imported_features=discovery.DISCOVERED_MODELS,
)


LOGGER.debug(f"{feature_ins = }")
# feature_ins = {'default': {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_VERT': AssetIn(key=AssetKey(['VERT', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}


ins = {}
compose_scopes = set()

compose_scope: str
feature: Dict[str, AssetIn]
for compose_scope, _ in feature_ins.items():
    # get_dynamic_ins() filters for enabled Features already
    if compose_scope in compose_scopes:
        continue
    compose_scopes.update(compose_scope)
    ins[f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}"] = AssetIn(
        AssetKey(
            # ComposeScopes / ComposeScope_DEV_default / docker_compose_graph_dot
            [
                "ComposeScopes",
                f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
                "docker_compose_graph_dot",
            ]
        )
    )

# for testing:
# if assets_external is empty at this point,
# just add a dummy
if not bool(ins):
    compose_scope = "dummy_compose_scope"
    ins[f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}"] = AssetIn(
        AssetKey(
            # ComposeScopes / dummy_compose_scope / docker_compose_graph_dot
            [
                "ComposeScopes",
                f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
                "docker_compose_graph_dot",
            ]
        )
    )


# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    enum.Enum,
    yaml.representer.SafeRepresenter.represent_str,
)


@asset(
    **ASSET_HEADER_LANDSCAPE_MAP,
    ins={
        "group_out_base": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)]),
        ),
        **ins,
    },
)
def landscape_map(
    context: AssetExecutionContext,
    group_out_base: OpenStudioLandscapesBaseOut,  # pylint: disable=redefined-outer-name
    **kwargs,
) -> Generator[Output[Dot] | AssetMaterialization | Any, None, None]:

    context.log.debug(kwargs)

    env: Dict = group_out_base.env

    landscape_packed_out = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
        "__".join(context.asset_key.path),
        "landscape_map_gvpacked.dot",
    )

    landscape_packed_out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        shutil.which("gvpack"),
        " ".join([i.as_posix() for i in list(kwargs.values())]),
        "|",
        "sed 's/_gv[0-9]\+//g'",
        ">",
        landscape_packed_out.as_posix(),
    ]

    proc = subprocess.Popen(
        " ".join(cmd),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = proc.communicate()

    stdout_stderr = {
        "stdout": MetadataValue.md(f"```shell\n{stdout.decode(encoding='utf-8')}\n```"),
        "stderr": MetadataValue.md(f"```shell\n{stderr.decode(encoding='utf-8')}\n```"),
    }

    # https://stackoverflow.com/questions/16488216/graph-of-graphs-in-graphviz
    # gvpack /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_default__Compose_default/Compose_default__group_out/docker_compose/Compose_default__docker_compose_graph/Compose_default__docker_compose_graph.dot /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_worker__Compose_worker/Compose_worker__group_out/docker_compose/Compose_worker__docker_compose_graph/Compose_worker__docker_compose_graph.dot -o /home/michael/git/repos/OpenStudioLandscapes/merge_gvpack.dot
    # gvpack /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_default__Compose_default/Compose_default__group_out/docker_compose/Compose_default__docker_compose_graph/Compose_default__docker_compose_graph.dot /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_worker__Compose_worker/Compose_worker__group_out/docker_compose/Compose_worker__docker_compose_graph/Compose_worker__docker_compose_graph.dot | sed 's/_gv[0-9]\+//g' > /home/michael/git/repos/OpenStudioLandscapes/merge_dotpack.dot

    graph = pydot.graph_from_dot_file(path=landscape_packed_out)[0]

    landscape_map_dir = landscape_packed_out.parent

    landscape_map_dir.mkdir(parents=True, exist_ok=True)

    # SVG
    svg = landscape_map_dir / f"{'__'.join(context.asset_key.path)}.svg"
    graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    # PNG
    png = landscape_map_dir / f"{'__'.join(context.asset_key.path)}.png"
    graph.write(
        path=png,
        format="png",
    )

    # SLOW
    # with open(png, "rb") as fr:
    #     png_bytes = fr.read()
    #
    # png_base64 = base64.b64encode(png_bytes).decode("utf-8")
    # png_md = f"![Image](data:image/png;base64,{png_base64})"

    yield Output(graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "svg": MetadataValue.md(svg_md),
            "dot": MetadataValue.md(
                f"```\n{graph.to_string(indent=2)}\n```"
            ),
            "svg_path": MetadataValue.path(svg),
            "png_path": MetadataValue.path(png),
            "cmd": MetadataValue.path(" ".join(cmd)),
            **stdout_stderr,
        },
    )
