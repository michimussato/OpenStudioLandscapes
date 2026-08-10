
# DB

## Up

```shell
nox -s "dagster_postgres_up_detach"
```

## Down

```shell
nox -s "dagster_postgres_down"
```

# Code Locations

## Individual

- [x] `/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base`
    ```shell
    dagster dev --workspace /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/workspace.yaml
    ```
- [x] `/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu`
    ```shell
    dagster dev --workspace /home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/workspace.yaml
    ```
- [x] `/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/compose_scopes`
    ```shell
    dagster dev --workspace /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/compose_scopes/workspace.yaml
    ```

## Combined

- [x] `/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine`
    ```shell
    dagster dev --workspace /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/workspaces.yaml
    ```

## Dagster

```shell
export DAGSTER_HOME=/home/michael/git/repos/OpenStudioLandscapes/.dagster-postgres
dagster dev --workspace /home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/workspaces.yaml --host 0.0.0.0
```
