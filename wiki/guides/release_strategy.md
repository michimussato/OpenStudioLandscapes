<!-- TOC -->
* [Release / Branching Strategy](#release--branching-strategy)
  * [Files and Packages to consider](#files-and-packages-to-consider)
  * [Tags](#tags)
    * [Releases](#releases)
      * [(Re-) Assign Tags](#re--assign-tags)
      * [Delete Tags](#delete-tags)
  * [Pull Requests (`gh`)](#pull-requests-gh)
    * [Create PR](#create-pr)
    * [Edit PR](#edit-pr)
    * [Close PR](#close-pr)
  * [Examples](#examples)
  * [Sequential Branches](#sequential-branches)
  * [Concurrent Branches](#concurrent-branches)
  * [nox (`local` vs `remote`)](#nox-local-vs-remote)
<!-- TOC -->

---

# Release / Branching Strategy

Based on [Semantic Versioning](https://semver.org/)

## Files and Packages to consider

- All OpenStudioLandscapes `pyproject.toml` files
- [wiki/README.md](../../wiki/README.md)
- [wiki/installation/basic_installation_from_script.md](../../wiki/installation/basic_installation_from_script.md)
- [`OpenStudioLandscapesUtil.ReadmeGenerator](https://github.com/michimussato/OpenStudioLandscapesUtil-ReadmeGenerator)

## Tags

OpenStudioLandscapes engine and all Features are currently tagged all simultaneously.
The decision to do so is basically to keep matching version numbers and avoid
a layer of confusion.

### Releases

| Branch Name | Tag                                      | Increment                           |
|-------------|------------------------------------------|-------------------------------------|
| `rc`        | `v<major>.<minor>.<patch>-rc<increment>` | `<increment>`                       |
| `main`      | `v<major>.<minor>.<patch>`               | `<major>` or `<minor>` or `<patch>` |

#### (Re-) Assign Tags

```shell
nox --session tag
```

#### Delete Tags

This deletes a local _and_ remote Git tag. a tag.

```shell
nox --session tag_delete
```

Ref: [How To Delete Local and Remote Tags on Git](https://devconnected.com/how-to-delete-local-and-remote-tags-on-git/)

## Pull Requests (`gh`)

```shell
nox --session gh_login
```

### Create PR

```shell
nox --session gh_pr_create
```

### Edit PR

```shell
nox --session gh_pr_set_mode
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
   commit id: "1-fixed-2" tag: "v1.0.2-rc1"
   commit id: "1-wip-3"
   commit id: "1-fixed-4" tag: "v1.0.2-rc2"
   commit id: "1-wip-5"
   commit id: "1-fixed-6" tag: "v1.0.2-rc3"
   checkout main
   merge 1-issue1 tag: "v1.0.2"
   branch 2-feature1
   checkout 2-feature1
   commit id: "2-wip-1"
   commit id: "2-wip-2" tag: "v1.1.0-rc1"
   commit id: "2-wip-3"
   commit id: "2-fixed-4" tag: "v1.1.0-rc2"
   checkout main
   merge 2-feature1 tag: "v1.1.0"
   branch 3-issue3
   commit id: "3-wip-1"
   commit id: "3-wip-2"
   checkout main
   commit id: "hotfix-1"
   checkout 3-issue3
   merge main
   checkout main
   commit id: "hotfix-2"
   checkout 3-issue3
   merge main
   checkout main
   commit id: "hotfix-3" tag: "v1.1.0, latest"
   checkout 3-issue3
   commit id: "3-wip-3" tag: "v1.1.1-rc1"
```

## Concurrent Branches

Now this is a bit complicated due to its non-linear nature and I'm still not really
sure how to deal with this - so this is more of a problem visualization than an
actual guide.

```mermaid
---
title: Concurrent Branches
---
gitGraph
   commit tag: "v1.0.0"
   commit tag: "v1.0.1"
   branch 1-issue1
   branch 2-issue2
   branch 3-feature1
   checkout 1-issue1
   commit id: "1-wip-1"
   commit id: "1-fixed-2" tag: "v1.0.2-rc1"
   commit id: "1-wip-3"
   checkout 2-issue2
   commit id: "2-wip-1"
   commit id: "2-wip-2" tag: "v1.0.3-rc2"
   checkout main
   %% Maybe use something like "v1.0.1-hf1" here?
   commit id: "hotfix-1" tag: "v1.0.1"
   checkout 1-issue1
   merge main
   checkout 2-issue2
   merge main
   checkout 3-feature1
   merge main
   checkout 1-issue1
   commit id: "1-fixed-4" tag: "v1.0.2-rc2"
   commit id: "1-wip-5"
   commit id: "1-fixed-6" tag: "v1.0.2-rc3"
   checkout main
   merge 1-issue1 tag: "v1.0.2"
   checkout 2-issue2
   merge main
   checkout 3-feature1
   merge main
   commit id: "3-wip-3" tag: "v1.1.0-rc2"
   checkout 2-issue2
   commit id: "2-wip-3"
   commit id: "2-fixed-4" tag: "v1.0.3-rc3"
   checkout main
   merge 2-issue2 tag: "v1.0.3"
   commit id: "hotfix-2" tag: "v1.0.3, latest"
```

## nox (`local` vs `remote`)

Dependencies in `pyproject.toml` generally refer to tagged commits on the `remote` (`@ git+...`):

```
dependencies = [
    [...]
    "docker-compose-graph @ git+https://github.com/michimussato/docker-compose-graph.git@v1.0.0",
    "OpenStudioLandscapes @ git+https://github.com/michimussato/OpenStudioLandscapes@v1.5.0-rc1",
    "OpenStudioLandscapes-Deadline-10-2 @ git+https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2@v1.5.0-rc1",
    [...]
]
```

That means that `nox` sessions pull the `remote` state of the package - 
local changes won't be included in `nox` sessions.

To use `local` code in `nox` sessions, the dependencies have to
point to local (`pip` installable) code (`@ file://...`). Change above block to
something like:

```

dependencies = [
    [...]
    "docker-compose-graph @ file://localhost/home/michael/git/repos/OpenStudioLandscapesUtil-ReadmeGenerator",
    "OpenStudioLandscapes @ file://localhost/home/michael/git/repos/OpenStudioLandscapes",
    "OpenStudioLandscapes-Deadline-10-2 @ file://localhost/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Deadline-10-2",
    [...]
]
```
