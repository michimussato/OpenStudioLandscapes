<!-- TOC -->
* [`pyproject.toml` Layers](#pyprojecttoml-layers)
  * [Structure](#structure)
<!-- TOC -->

---

# `pyproject.toml` Layers

https://github.com/michimussato/OpenStudioLandscapesUtil-VersionBumper

Detailed information: todo

Make sure to check the `pyproject_layer.yaml` for Features that depend
on other Features, like:
- `OpenStudioLandscapes-Watchtower` which depends on `OpenStudioLandscapes-Kitsu`
- `OpenStudioLandscapes-Deadline-10-2-Worker` which depends on `OpenStudioLandscapes-Deadline-10-2-Worker`
- `OpenStudioLandscapes-Flamenco-Worker` which depends on `OpenStudioLandscapes-Flamenco-Worker`
- etc.

## Structure

```mermaid
---
title: Layered pyproject
---
flowchart BT
    subgraph engine
        subgraph base_structure 
            pyproject_layer_0_root["pyproject_layer_0_root.yaml"]
            pyproject_layer_engine["pyproject_layer_engine.yaml"]
            pyproject_layer_features["pyproject_layer_features.yaml"]
        end
        pyproject_layer_engine_["pyproject_layer.yaml"]
    end
    
    subgraph feature 
        pyproject_layer["pyproject_layer.yaml"]
    end
    
    pyproject_layer_engine -- extends --> pyproject_layer_0_root
    pyproject_layer_engine_ -- extends --> pyproject_layer_engine
    pyproject_layer_features -- extends --> pyproject_layer_0_root
    pyproject_layer -- extends ---> pyproject_layer_features
```