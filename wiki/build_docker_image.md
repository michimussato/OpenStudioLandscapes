<!-- TOC -->
* [Build Docker Image](#build-docker-image)
  * [Build](#build)
  * [Push](#push)
  * [Run Interactive Session](#run-interactive-session)
<!-- TOC -->

---

# Build Docker Image

```shell
#!/bin/sh

# Credits:
# https://gist.github.com/CSTDev/08c127680e3b5fae38c051da3e489351

#get highest tag number
#VERSION=`git describe --abbrev=0 --tags --match="v[0-9]*"`
VERSION=`git describe --abbrev=0 --tags --match="v[0-9]*" || echo "v0.0.1"`
V=""
if [[ $VERSION =~ "v" ]]; then
    V="v"
fi
#get number parts and increase last one by 1
VNUM1=$(echo "$VERSION" | cut -d"." -f1)
VNUM2=$(echo "$VERSION" | cut -d"." -f2)
VNUM3=$(echo "$VERSION" | cut -d"." -f3)
VNUM1=`echo $VNUM1 | sed 's/v//'`

# Check for #major or #minor in commit message and increment the relevant version number
MAJOR=`git log --format=%B -n 1 HEAD | grep '#major'`
MINOR=`git log --format=%B -n 1 HEAD | grep '#minor'`

if [ "$MAJOR" ]; then
    echo "Update major version"
    VNUM1=$((VNUM1+1))
    VNUM2=0
    VNUM3=0
elif [ "$MINOR" ]; then
    echo "Update minor version"
    VNUM2=$((VNUM2+1))
    VNUM3=0
else
    echo "Update patch version"
    VNUM3=$((VNUM3+1))
fi


#create new tag
NEW_TAG="$V$VNUM1.$VNUM2.$VNUM3"

if [ $NEW_TAG = "..1" ]; then
    NEW_TAG="v0.0.1"
fi

echo "Updating $VERSION to $NEW_TAG"

#get current hash and see if it already has a tag
GIT_COMMIT=`git rev-parse HEAD`
NEEDS_TAG=`git describe --contains $GIT_COMMIT 2>/dev/null`

#only tag if no tag already (would be better if the git describe command above could have a silent option)
if [ -z "$NEEDS_TAG" ]; then
    echo "Tagged with $NEW_TAG (Ignoring fatal:cannot describe - this means commit is untagged) "
    git tag $NEW_TAG
    git push --tags
else
    echo "Already a tag on this commit"
fi
```

## Build

> [!IMPORTANT]
> Group `docker` must exist.
> See [Add `$USER` to group `docker`](installation/basic_installation.md#add-user-to-group-docker)

```shell
docker build \
    --tag docker.io/michimussato/openstudiolandscapes:<VERSION> \
    --tag docker.io/michimussato/openstudiolandscapes:latest \
    --progress plain \
    --no-cache-filter=openstudiolandscapes-never-cache \
    --file docker/Dockerfile \
    --build-arg PYTHON_MAJ=3 \
    --build-arg PYTHON_MIN=11 \
    --build-arg PYTHON_PAT=11 \
    --build-arg DOCKER_GID=$(getent group docker | cut -d: -f3)
```

## Push

```shell
docker login
```

```shell
docker image push --all-tags michimussato/openstudiolandscapes
```

## Run Interactive Session

> [!NOTE]
> Only for testing. Not actually used in day to day OpenStudioLandscape usage.

```shell
docker run -v /var/run/docker.sock:/var/run/docker.sock:rw --rm -it --entrypoint bash michimussato/openstudiolandscapes:latest
```