import pathlib
from importlib import metadata

pkg = pathlib.Path(__file__).parent.parent.parent.parent.parent.name

dist = metadata.distribution(pkg)
