# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Run OpenStudioLandscapes from Manual Installation](#run-openstudiolandscapes-from-manual-installation)
  * [Requirements](#requirements)
  * [up/down](#updown)
    * [With Harbor](#with-harbor)
<!-- TOC -->

---

# Run OpenStudioLandscapes from Manual Installation

Work in progress (there's more to do than that), but _conceptually_, here's how.

## Requirements

- Harbor up and running
- `.venv/bin/activate` (`nox`)

## up/down

```shell
cd ../../
nox --sessions dagster_postgres_up_detach dagster_postgres; nox --sessions dagster_postgres_down
```

### With Harbor

> [!IMPORTANT]
> Information about setting up Harbor can be found here:
> [harbor.md](../guides/harbor.md)

Provided Harbor can be controlled by `systemd`:

```shell
sudo systemctl enable --now harbor.service
```
