from dagster import Definitions, load_assets_from_modules
from Deadline.deadline_docker import assets, assets_10_2

assets_base = load_assets_from_modules([assets])
assets_10_2 = load_assets_from_modules([assets_10_2])

defs = Definitions(
    assets=[
        *assets_base,
        *assets_10_2,
    ],
)
