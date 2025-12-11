import pathlib
from importlib import metadata
from importlib.metadata import Distribution

pkg: str = pathlib.Path(__file__).parent.parent.parent.parent.parent.name

dist: Distribution = metadata.distribution(pkg)
