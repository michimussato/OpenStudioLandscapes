## pre-commit

- https://pre-commit.com/
- https://pre-commit.com/hooks.html

### Install

```shell
pre-commit install
```

For all Features:

```shell
# Todo
#  - [ ] move to `nox`
pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit
    
    if [ ! -d .venv ]; then
        python3.11 -m venv .venv
    fi;
    
    source .venv/bin/activate
    echo "venv activated."
    
    echo "Installing pre-commit in ${dir}..."
    pre-commit install
    echo "Installed."
    
    deactivate
    echo "deactivated."

    popd || exit
done;

popd || exit
```

### Run

```shell
pre-commit run --all-files
```
