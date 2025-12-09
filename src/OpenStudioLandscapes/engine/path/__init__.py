# import pathlib
# from typing import Dict
# from importlib.metadata import Distribution
#
#
# class ExpandablePath(pathlib.Path):
#     def __init__(self, path: pathlib.Path):
#         super().__init__(path)
#
#     def expand(self, env: Dict, dist: Distribution) -> pathlib.Path:
#         ret = pathlib.Path(
#             self
#             .as_posix()
#             .format(
#                 **{
#                     "FEATURE": dist.name,
#                     **env,
#                 }
#             )
#         ).expanduser().resolve()
#
#         return ret
