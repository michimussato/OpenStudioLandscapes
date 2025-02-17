```
cd code_locations
dagster project scaffold --name LikeC4
cd LikeC4
mkdir -p src/OpenStudioLandscapes
mv LikeC4 src/OpenStudioLandscapes 
mv LikeC4_tests src/OpenStudioLandscapes 
```

Add `where = ["src"]` to `code_locations/LikeC4/pyproject.toml`

Change `module_name = "LikeC4.definitions"` to `module_name = "OpenStudioLandscapes.LikeC4.definitions"`

```
pip install -e .[dev]
```





```shell
cd code_locations
dagster project scaffold --name LikeC4
```

```workspace.yaml
  - python_module:
      working_directory: src/code_locations/LikeC4
      module_name: LikeC4.definitions
      location_name: "LikeC4"
      # executable_path: ../.venv/bin/python
```