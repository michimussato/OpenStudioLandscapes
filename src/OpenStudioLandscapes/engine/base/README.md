<!-- TOC -->
* [Base](#base)
<!-- TOC -->

---

# Base

This is for isolated development, unit testing and debugging.
Instead of the `definitions.py`, the accompanying `workspace.yaml` loads 
the `_definitions_with_upstream_specs.py` which also contains `AssetSpec` 
definitions for upstream dependencies. 

```shell
dagster dev --workspace src/OpenStudioLandscapes/engine/base/workspace.yaml
```
