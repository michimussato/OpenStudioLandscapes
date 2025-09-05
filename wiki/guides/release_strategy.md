<!-- TOC -->
* [Release / Branching Strategy](#release--branching-strategy)
  * [Tags](#tags)
    * [Releases](#releases)
      * [Release Candidate](#release-candidate)
      * [Main Release](#main-release)
      * [Delete Tags](#delete-tags)
  * [Pull Requests (`gh`)](#pull-requests-gh)
    * [Create PR](#create-pr)
    * [Edit PR](#edit-pr)
      * [Ready for Review](#ready-for-review)
      * [Set to Draft](#set-to-draft)
    * [Close PR](#close-pr)
  * [Examples](#examples)
  * [Sequential Branches](#sequential-branches)
  * [Concurrent Branches](#concurrent-branches)
<!-- TOC -->

---

# Release / Branching Strategy

Based on [Semantic Versioning]()

## Tags

### Releases

| Branch Name | Tag                                      | Increment                           |
|-------------|------------------------------------------|-------------------------------------|
| `feature`   | `v<major>.<minor>.<patch>-rc<increment>` | `<increment>`                       |
| `main`      | `v<major>.<minor>.<patch>`               | `<major>` or `<minor>` or `<patch>` |

#### Release Candidate

```shell
echo "Version Tag (Release Candidate):"
echo "v<major>.<minor>.<patch>-rc<increment>"
read -p "v" TAG_VERSION
RELEASE_TYPE=rc

nox --session tag -- ${TAG_VERSION}
```

Manual:

```shell
echo "Version Tag (Release Candidate):"
echo "v<major>.<minor>.<patch>-rc<increment>"
read -p "v" TAG_VERSION
TAG_VERSION="v${TAG_VERSION}"
# BRANCH="feature"


read -r -d '' COMMAND <<'EOF'
git fetch --tags --force
git tag --annotate "${TAG_VERSION}" --message "Release Candidate Version ${TAG_VERSION}" --force
git push --tags --force
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

#### Main Release

```shell
echo "Version Tag (Main Release):"
echo "v<major>.<minor>.<patch>"
read -p "v" TAG_VERSION
RELEASE_TYPE=main

nox --session tag -- ${TAG_VERSION}
```

Manual:

```shell
echo "Version Tag (Main Release):"
echo "v<major>.<minor>.<patch>"
read -p "v" TAG_VERSION
TAG_VERSION="v${TAG_VERSION}"
# BRANCH="main"


read -r -d '' COMMAND <<'EOF'
git fetch --tags --force
git tag --annotate "${TAG_VERSION}" --message "Main Release Version ${TAG_VERSION}" --force
git tag --annotate "latest" --message "Latest Release Version (pointing to ${TAG_VERSION})" "${TAG_VERSION}^{}" --force
git push --tags --force
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

#### Delete Tags

This deletes a local _and_ remote Git tag. a tag.

```shell
echo "Version Tag (Delete Tag):"
read -p "v" TAG_VERSION
TAG_VERSION="v${TAG_VERSION}"

nox --session tag_delete -- ${TAG_VERSION}
```

Manual:

Ref: [How To Delete Local and Remote Tags on Git](https://devconnected.com/how-to-delete-local-and-remote-tags-on-git/)

```shell
echo "Version Tag (Delete Tag):"
read -p "v" TAG_VERSION
TAG_VERSION="v${TAG_VERSION}"
# BRANCH="feature"


read -r -d '' COMMAND <<'EOF'
git fetch --tags --force
git tag -d ${TAG_VERSION}
git push origin :refs/tags/${TAG_VERSION}
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

## Pull Requests (`gh`)

```shell
nox --session gh_login
```

Manual:

```shell
gh auth login
```

### Create PR

```shell
echo "Create PR (draft):"
read -p "Branch: " BRANCH
read -p "Dry run [1]: " DRY_RUN
DRY_RUN=${DRY_RUN:-1}

nox --session gh_pr_create -- ${BRANCH}
```

Manual:

```shell
gh pr create --title "Pull request title" --body "Pull request body"
```

```shell
echo "Create PR:"
read -p "Branch: " BRANCH  # feature-openstudiolandscapes-n8n
# echo -n "Body: "
# read BODY


read -r -d '' COMMAND <<'EOF'
gh pr create \
    --draft \
    --title ${BRANCH} \
    --head ${BRANCH} \
    --base main \
    --dry-run \
    --body ""
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

### Edit PR

```shell
echo "Edit PR:"
read -p "Mode [draft]: " MODE
MODE=${MODE:-draft}
read -p "Branch: " BRANCH

nox --session gh_pr_set_mode -- ${BRANCH}
```

Manual:

#### Ready for Review

```shell
echo "PR Ready for Review:"
read -p "Branch: " BRANCH  # feature-openstudiolandscapes-n8n


read -r -d '' COMMAND <<'EOF'
gh pr ready ${BRANCH}
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

#### Set to Draft

```shell
echo "PR Set to Draft:"
read -p "Branch: " BRANCH  # feature-openstudiolandscapes-n8n


read -r -d '' COMMAND <<'EOF'
gh pr ready ${BRANCH} --undo
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

### Close PR

```shell
gh pr close {<number> | <url> | <branch>} [flags]
```

```shell
echo "Close PR:"
echo -n "Branch: "  # feature-openstudiolandscapes-n8n
read BRANCH
echo -n "Comment: "
read COMMENT


COMMAND=""


read -r -d '' COMMAND <<'EOF'
gh pr close ${BRANCH} --comment "${COMMENT}"
EOF


eval "${COMMAND}"


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    eval "${COMMAND}"

    popd || exit
done;

popd || exit
```

## Examples

## Sequential Branches

```mermaid
---
title: Sequential Branches
---
gitGraph
   commit tag: "v1.0.0"
   commit tag: "v1.0.1"
   branch 1-issue1
   checkout 1-issue1
   commit id: "1-wip-1"
   commit id: "1-fixed-2" tag: "v1.0.1-rc.1.1"
   commit id: "1-wip-3"
   commit id: "1-fixed-4" tag: "v1.0.1-rc.1.2"
   commit id: "1-wip-5"
   commit id: "1-fixed-6" tag: "v1.0.1-rc.1.3"
   checkout main
   merge 1-issue1 tag: "v1.0.2"
   branch 2-issue2
   checkout 2-issue2
   commit id: "2-wip-1"
   commit id: "2-wip-2" tag: "v1.0.2-rc.2.1"
   commit id: "2-wip-3"
   commit id: "2-fixed-4" tag: "v1.0.2-rc.2.2"
   checkout main
   merge 2-issue2 tag: "v1.0.3"
   branch 3-issue3
   commit id: "3-wip-1"
   commit id: "3-wip-2" tag: "v1.0.3-rc.3.1"
   checkout main
   commit tag: "v1.0.4"
   commit tag: "v1.0.5, latest"
```

## Concurrent Branches

```mermaid
---
title: Concurrent Branches
---
gitGraph
   commit tag: "v1.0.0"
   commit tag: "v1.0.1"
   branch 1-issue1
   branch 2-issue2
   checkout 1-issue1
   commit id: "1-wip-1"
   commit id: "1-fixed-2" tag: "v1.0.1-rc.1.1"
   commit id: "1-wip-3"
   commit id: "1-fixed-4" tag: "v1.0.1-rc.1.2"
   commit id: "1-wip-5"
   commit id: "1-fixed-6" tag: "v1.0.1-rc.1.3"
   checkout main
   merge 1-issue1 tag: "v1.0.2"
   branch 3-issue3
   commit id: "3-wip-1"
   commit id: "3-wip-2" tag: "v1.0.2-rc.3.1"
   checkout main
   checkout 2-issue2
   commit id: "2-wip-1"
   commit id: "2-wip-2" tag: "v1.0.1-rc.2.1"
   commit id: "2-wip-3"
   commit id: "2-fixed-4" tag: "v1.0.1-rc.2.2"
   checkout main
   merge 2-issue2 tag: "v1.0.3"
   commit tag: "v1.0.4"
   commit tag: "v1.0.5, latest"
```

To run `nox -s readme`, change the deps in `setup.cfg` from something like
```
OpenStudioLandscapes @ git+https://github.com/michimussato/OpenStudioLandscapes@v1.1.0-rc1
OpenStudioLandscapes-Deadline-10-2 @ git+https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2@v1.1.0-rc1
```
to something like
```
OpenStudioLandscapes @ file://localhost/home/michael/git/repos/OpenStudioLandscapes
OpenStudioLandscapes-Deadline-10-2 @ file://localhost/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Deadline-10-2
```
