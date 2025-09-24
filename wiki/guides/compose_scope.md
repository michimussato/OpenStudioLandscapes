<!-- TOC -->
* [Compose Scopes](#compose-scopes)
  * [Create Compose Scope](#create-compose-scope)
  * [Assign Compose Scope to Feature](#assign-compose-scope-to-feature)
<!-- TOC -->

---

# Compose Scopes

## Create Compose Scope

1. Duplicate a directory structure in `engine/compose_scopes`, i.e. `license_server` and
   rename it to (in this example) `new_composescope`
2. Edit `OpenStudioLandscapes.engine.constants`
   1. Add a section as follows:
      ```
      from OpenStudioLandscapes.engine.compose_scopes.new_composescope import (
          constants as constants_compose_new_composescope,
      )

      GROUP_COMPOSE_NEW_COMPOSESCOPE = constants_compose_new_composescope.GROUP
      KEY_COMPOSE_NEW_COMPOSESCOPE = constants_compose_new_composescope.KEY
      ASSET_HEADER_COMPOSE_NEW_COMPOSESCOPE = constants_compose_new_composescope.ASSET_HEADER
      ENVIRONMENT_COMPOSE_NEW_COMPOSESCOPE = constants_compose_new_composescope.ENVIRONMENT
      ```
   2. Edit `__all__`:
      ```
      __all__ = [
          ...
          ASSET_HEADER_COMPOSE_NEW_COMPOSESCOPE
          ...
      ]
      ```
3. Edit `OpenStudioLandscapes.engine.definitions`
   1. Extend `imports_engine`:
      ```
      imports_engine.extend(
          [
              ...
              "OpenStudioLandscapes.engine.compose_scopes.new_composescope.definitions",
              ...
          ]
      )
      ```
4. Edit `OpenStudioLandscapes.engine.enums`
   1. Edit `ComposeScope`
      ```
      class ComposeScope(enum.StrEnum):
          DEFAULT = "default"
          LICENSE_SERVER = "license_server"
          TELEPORT = "teleport"
          WORKER = "worker"
          ...
          NEW_COMPOSESCOPE = "new_composescope
      ```

## Assign Compose Scope to Feature

1. Assign `NEW_COMPOSESCOPE` to Feature in `OpenStudioLandscapes.engine.features`
   1. Edit `FEATURES`:
      ```
      FEATURES = [
          ...
          "OpenStudioLandscapes-SomeFeature": {
              ...
              "compose_scope": ComposeScope.NEW_COMPOSESCOPE,
              ...
          },
          ...
      ]
      ```
2. Maybe do `pip install -e .[dev]` (to be verified)
