<!-- TOC -->
* [OpenStudioLandscapes](#openstudiolandscapes)
  * [Sphinx](#sphinx)
    * [Builders](#builders)
    * [Markdown Support](#markdown-support)
    * [Mermaid Support](#mermaid-support)
    * [Graphviz Support](#graphviz-support)
  * [Dagster](#dagster)
  * [Development](#development)
    * [Adding new Python dependencies](#adding-new-python-dependencies)
    * [Unit testing](#unit-testing)
    * [Schedules and sensors](#schedules-and-sensors)
  * [Deploy on Dagster Cloud](#deploy-on-dagster-cloud)
<!-- TOC -->

---

# OpenStudioLandscapes

```
python3.9 -venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e git+https://github.com/michimussato/My-Skeleton-Package.git@main
```

```
pip install --upgrade pip
pip install --upgrade pyscaffold
```

```
putup --namespace PackageNamespace --name My-Skeleton-Package --package my_skeleton_package ./My-Skeleton-Package
```

```
pip install -e ./My-Skeleton-Package[testing]
```

```
tox -e docs  # to build your documentation
tox -e build  # to build your package distribution
tox -e publish  # to test your project uploads correctly in test.pypi.org
tox -e publish -- --repository pypi  # to release your package to PyPI
tox -av  # to list all the tasks available
```

```
gh repo create animallogic-sandbox/My-Skeleton-Package --push --disable-issues --disable-wiki --internal --source ./My-Skeleton-Package --remote=upstream
```

## Sphinx

### Builders

https://www.sphinx-doc.org/en/master/usage/builders/index.html#builders

### Markdown Support

https://www.sphinx-doc.org/en/master/usage/markdown.html

It looks like we can't reference this Markdown
if it lives in a parent directory - this seems
to be working for `.rst` with the
`.. include:: ../MyFile.rst` directive.

```
pip install myst-parser
```

- Add `"myst_parser"` to `docs/conf.py:extensions`
- Edit `docs/conf.py:souce_suffix = {".rst": "restructuredtext", ".md": "markdown"}`
  - https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-source_suffix

Optional: (configure `myst-parser`)[https://myst-parser.readthedocs.io/en/latest/syntax/optional.html]

### Mermaid Support

https://github.com/mgaitan/sphinxcontrib-mermaid

### Graphviz Support

https://www.sphinx-doc.org/en/master/usage/extensions/graphviz.html#module-sphinx.ext.graphviz

Add `"sphinx.ext.graphviz"` to `docs/conf.py:extensions`

Embed:

```
.. graphviz::

   digraph foo {
      "bar" -> "baz";
   }
```

Reference:

```
.. graphviz:: external.dot
```

```bash
nox -s doc
```

## Dagster

```
dagster project scaffold --name my-skeleton-package
```

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

Then, start the Dagster UI web server:

```bash
export DAGSTER_HOME=$(realpath dagster/.dagster)    # `realpath` vs `readlink -f`
dagster dev --workspace $(realpath dagster/workspace.yaml)  # `realpath` vs `readlink -f`
```

Open http://localhost:3000 with your browser to see the project.

You can start writing assets in `My_Skeleton_Package.my_skeleton_mackage/assets.py`. The assets are automatically loaded into the Dagster code location as you define them.

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

### Unit testing

Tests are in the `my_skeleton_mackage_tests` directory and you can run tests using `pytest`:

```bash
pytest my_skeleton_mackage_tests
```

```bash
nox -s test
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Deploy on Dagster Cloud

The easiest way to deploy your Dagster project is to use Dagster Cloud.

Check out the [Dagster Cloud Documentation](https://docs.dagster.cloud) to learn more.
