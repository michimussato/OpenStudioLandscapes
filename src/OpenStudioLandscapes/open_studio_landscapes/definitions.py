from dagster import Definitions

from OpenStudioLandscapes.open_studio_landscapes.base import definitions as definitions_base

defs = Definitions.merge(
    definitions_base.defs
)
