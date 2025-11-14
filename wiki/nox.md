# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Nox](#nox)
  * [Current Sessions](#current-sessions)
  * [Python Versions](#python-versions)
  * [SBOM](#sbom)
    * [Python 3.11](#python-311)
    * [Python 3.12](#python-312)
<!-- TOC -->

---

# Nox

`OpenStudioLandscapes` comes with several convenience shortcuts for
repetitive tasks unsing `nox` as its task runner.

```shell
nox --help
```

## Current Sessions

```shell
nox --list-sessions
Sessions defined in OpenStudioLandscapes/noxfile.py:

[...]

sessions marked with * are selected, sessions marked with - are skipped.
```

## Python Versions

- `python3.11`
- `python3.12`

## SBOM

### Python 3.11

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.11.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.11.mermaid)

### Python 3.12

- [cyclonedx-bom](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/cyclonedx-py.sbom-3.12.json)
- [pipdeptree (Dot)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.dot)
- [pipdeptree (Mermaid)](https://github.com/michimussato/OpenStudioLandscapes/tree/main/.sbom/pipdeptree.sbom-3.12.mermaid)
