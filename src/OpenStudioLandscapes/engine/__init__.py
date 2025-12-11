import sys
from pathlib import Path
from importlib import metadata

if sys.version_info[:2] >= (3, 9):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version, Distribution  # pragma: no cover
else:
    raise RuntimeError("Python version >= 3.9 required.")

try:
    # Change here if project is renamed and does not equal the package name
    package: str = Path(__file__).parent.parent.parent.parent.name
    dist: Distribution = metadata.distribution(package)
    __version__: str = version(dist.name)
except PackageNotFoundError:  # pragma: no cover
    __version__: str = "unknown"
finally:
    del version, PackageNotFoundError
