# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Run OpenStudioLandscapes from Manual Installation](#run-openstudiolandscapes-from-manual-installation)
  * [Requirements](#requirements)
  * [up](#up)
  * [down](#down)
<!-- TOC -->

---

# Run OpenStudioLandscapes from Manual Installation

Work in progress (there's more to do than that), but _conceptually_, here's how.

## Requirements

- Harbor up and running
- `.venv/bin/activate` (`nox`)

## up

```shell
nox --sessions dagster_postgres_up_detach dagster_postgres
# With Harbor:
# nox --sessions harbor_up_detach dagster_postgres_up_detach dagster_postgres
```

## down

```shell
nox --sessions dagster_postgres_down
# With Harbor
# nox --sessions dagster_postgres_down harbor_down
```