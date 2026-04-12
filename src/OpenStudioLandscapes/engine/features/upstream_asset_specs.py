# from dagster import AssetKey, AssetSpec
#
# from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE
#
# assets_external = []
#
# group_out_base = AssetSpec(
#     key=AssetKey(
#         # ComposeScopes / ComposeScope_DEV_default / docker_compose_graph_dot
#         [
#             *ASSET_HEADER_BASE["key_prefix"],
#             "group_out_base",
#         ]
#     ),
#     group_name=ASSET_HEADER_BASE["group_name"],
#     description="`AssetSpec` for `AssetDefinition` specified in "
#     "`OpenStudioLandscapes.engine.base.assets.group_out_base`.",
# )
#
# assets_external.append(group_out_base)
#
# # I believe this can go...