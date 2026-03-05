<!-- TOC -->
* [Rez](#rez)
  * [`rez`](#rez-1)
    * [`bind`](#bind)
    * [`env`](#env)
    * [`bundle`](#bundle)
<!-- TOC -->

---

# Rez

Resources:
- https://commandmasters.com/commands/docker-run-common/

Rez Environment Variables
- https://rez.readthedocs.io/en/stable/environment.html#environment-variables

Configure Rez
- https://rez.readthedocs.io/en/stable/configuring_rez.html#configuring-rez

Helpful commands
- `rez config packages_path`

```dotenv
# https://rez.readthedocs.io/en/stable/configuring_rez.html#local_packages_path
REZ_LOCAL_PACKAGES_PATH=/rez/packages/local

# https://rez.readthedocs.io/en/stable/configuring_rez.html#release_packages_path
REZ_RELEASE_PACKAGES_PATH=/rez/packages/deployed/internal

# External packages Variable??
EXT_PACKAGES_PATH=/data/share/rez-packages/packages

# https://rez.readthedocs.io/en/stable/configuring_rez.html#packages_path
REZ_PACKAGES_PATH=$REZ_LOCAL_PACKAGES_PATH:$REZ_RELEASE_PACKAGES_PATH:$EXT_PACKAGES_PATH
```

```shell
REZ_IMAGE="registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image_rez:2026-03-04_07-48-32__odd-open-flaxen-stetson"
docker run \
--name rez \
--hostname rez \
--interactive \
--tty \
--rm \
--env-file ./.env \
--volume ${HOME}/rez/bakes:/rez/bakes \
--volume ${HOME}/rez/bundles:/rez/bundles \
--volume ${HOME}/rez/packages/local:/rez/packages/local \
--volume ${HOME}/rez/packages/deployed/internal:/rez/packages/deployed/internal \
--volume /data/share:/data/share:rw \
--entrypoint bash \
${REZ_IMAGE}
```

## `rez`

Create `alias`

```shell
REZ_IMAGE="registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image_rez:2026-03-04_07-48-32__odd-open-flaxen-stetson"
alias rez="docker run \
--name rez \
--hostname rez \
--interactive \
--tty \
--rm \
--env-file ./.env \
--volume ${HOME}/rez/bakes:/rez/bakes \
--volume ${HOME}/rez/bundles:/rez/bundles \
--volume ${HOME}/rez/packages/local:/rez/packages/local \
--volume ${HOME}/rez/packages/deployed/internal:/rez/packages/deployed/internal \
--volume /data/share:/data/share:rw \
${REZ_IMAGE}"
```

`unalias`

```shell
unalias rez
```

### `bind`

```shell
rez bind --quickstart
```

```shell
# rez-bind --quickstart is equivalent to:
rez bind platform \
    && rez-bind arch \
    && rez-bind os \
    && rez-bind python \
    && rez-bind rez \
    && rez-bind rezgui \
    && rez-bind setuptools \
    && rez-bind pip
```

### `env`

```shell
rez env python -- which python
```

Save to Context (`rxt`)
- [Bakine Resolves](https://rez.readthedocs.io/en/stable/context.html#baking-resolves)

```shell
rez env maya blender --output bakes/my_bake.rxt
```

Load from Context

```shell
rez context bakes/my_bake.rxt
```

### `bundle`

Context bundles are:
- self contained
- relocatable

References:
- [Context bundles](https://rez.readthedocs.io/en/stable/context_bundles.html#context-bundles)

```shell
rez bundle bakes/my_bake.rxt bundles/bundle_from_my_bake
```
