# from typing import Any, Generator, Union
#
# from dagster import (
#     asset,
#     Output,
#     AssetMaterialization,
#     AssetsDefinition,
#     Definitions,
#     # RetryPolicy,
#     # Backoff,
#     # Jitter,
# )
#
#
# # Further Readings:
# # - https://dagster.io/blog/unlocking-flexible-pipelines-customizing-asset-decorator
#
#
# def asset_factory(
#         # group_name: str,
#         spec: dict[
#             str, Union[dict, str, callable],
#         ],
# # ) -> AssetsDefinition:
# ) -> Definitions:
#
#     @asset(
#         group_name=spec["asset_header"]["group_name"],
#         compute_kind="python",
#         key_prefix=spec["asset_header"]["key_prefix"],
#         name=spec["name"],
#         deps=spec["deps"],
#         ins=spec["ins"]
#         # retry_policy=RetryPolicy(
#         #     max_retries=5,
#         #     delay=2,
#         #     backoff=Backoff.EXPONENTIAL,
#         #     jitter=Jitter.FULL,
#         # ),
#     )
#     def _asset() -> Generator[Output[str | Any] | AssetMaterialization | Any, Any, None]:
#
#         yield Output(spec["value"])
#
#         yield AssetMaterialization(
#             asset_key=[
#                 *spec["asset_header"]["key_prefix"],
#                 spec["name"],
#             ],
#             metadata={
#                 spec["name"]: spec["type"](spec["value"]),
#             },
#         )
#
#     # return _asset
#     return Definitions(
#         assets=[_asset],
#     )
