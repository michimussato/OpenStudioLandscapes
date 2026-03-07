<!-- TOC -->
* [Rez](#rez)
  * [`rez`](#rez-1)
    * [`bind`](#bind)
    * [`env`](#env)
    * [`bundle`](#bundle)
* [Docker Volumes](#docker-volumes)
* [Run GUI Applications in Docker](#run-gui-applications-in-docker)
<!-- TOC -->

---

# Rez

Rez in Docker:
- https://github.com/AcademySoftwareFoundation/rez/issues/1732

Resources:
- https://commandmasters.com/commands/docker-run-common/

Rez Environment Variables
- https://rez.readthedocs.io/en/stable/environment.html#environment-variables

Configure Rez
- https://rez.readthedocs.io/en/stable/configuring_rez.html#configuring-rez

Helpful commands
- `rez config packages_path`

```shell
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}/rez"

tee ${XDG_CONFIG_HOME:-$HOME/.config}/rez/env << EOF

REZ_IMAGE="openstudiolandscapes_base_build_docker_image:2026-03-07_09-13-51__yielding-wirehaired-rare-wedge"

# https://rez.readthedocs.io/en/stable/configuring_rez.html#local_packages_path
REZ_LOCAL_PACKAGES_PATH=/rez/packages/local

# https://rez.readthedocs.io/en/stable/configuring_rez.html#release_packages_path
REZ_RELEASE_PACKAGES_PATH=/rez/packages/deployed/internal

# External packages Variable??
EXT_PACKAGES_PATH=/data/share/rez-packages/packages

# https://rez.readthedocs.io/en/stable/configuring_rez.html#packages_path
REZ_PACKAGES_PATH=\$REZ_LOCAL_PACKAGES_PATH:\$REZ_RELEASE_PACKAGES_PATH:\$EXT_PACKAGES_PATH
EOF
```

```shell
source ${XDG_CONFIG_HOME:-$HOME/.config}/rez/env
docker run \
--name rez \
--hostname rez \
--interactive \
--tty \
--rm \
--env-file ${XDG_CONFIG_HOME:-~/.config}/rez/env \
--volume ${HOME}/rez/bakes:/rez/bakes \
--volume ${HOME}/rez/bundles:/rez/bundles \
--volume ${HOME}/rez/packages/local:/rez/packages/local \
--volume ${HOME}/rez/packages/deployed/internal:/rez/packages/deployed/internal \
--volume /data/share:/data/share:rw \
--entrypoint bash \
"${REZ_IMAGE}"
```

## `rez`

Create `alias`

```shell
source "${XDG_CONFIG_HOME:-$HOME/.config}/rez/env"
alias rez="docker run \
--name rez \
--hostname rez \
--interactive \
--tty \
--entrypoint /opt/python3.11/bin/rez \
--rm \
--env-file ${XDG_CONFIG_HOME:-~/.config}/rez/env \
--volume ${HOME}/rez/bakes:/rez/bakes \
--volume ${HOME}/rez/bundles:/rez/bundles \
--volume ${HOME}/rez/packages/local:/rez/packages/local \
--volume ${HOME}/rez/packages/deployed/internal:/rez/packages/deployed/internal \
--volume /data/share:/data/share:rw \
${REZ_IMAGE}"
```

```shell
alias rez="source ${XDG_CONFIG_HOME:-~/.config}/rez/env \
&& docker run \
--name rez \
--hostname rez \
--rm \
--env-file ${XDG_CONFIG_HOME:-~/.config}/rez/env \
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
# Deprecated
# See open PR: https://github.com/AcademySoftwareFoundation/rez/pull/1982/changes
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
rez env blender --output bakes/blender.rxt
```

Load from Context

```shell
rez context bakes/blender.rxt
```

### `bundle`

Context bundles are:
- self contained
- relocatable

References:
- [Context bundles](https://rez.readthedocs.io/en/stable/context_bundles.html#context-bundles)

```shell
rez bundle bakes/blender.rxt bundles/bundle_from_blender
```

# Docker Volumes

- https://dev.to/rimelek/everything-about-docker-volumes-1ib0#custom-volume-path-overview

# Run GUI Applications in Docker

- https://unix.stackexchange.com/a/359244
- https://github.com/mviereck/x11docker
- https://github.com/mviereck/dockerfile-x11docker-xwayland
- https://kravemir.org/how-to/run-graphical-application-in-container-with-sommelier-wayland-and-xwayland/



```shell
result=$(rez env blender -- which blender)
$result

$(echo $(rez env blender -- which blender)|tr -d $'\r') 
$(echo $(rez env blender -- blender)|tr -d $'\r') 
```