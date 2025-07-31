<!-- TOC -->
* [Release / Branching Strategy](#release--branching-strategy)
  * [Tags](#tags)
    * [Release Candidates](#release-candidates)
    * [Releases](#releases)
  * [Examples](#examples)
  * [Sequential Branches](#sequential-branches)
  * [Concurrent Branches](#concurrent-branches)
<!-- TOC -->

---

# Release / Branching Strategy

Based on [Semantic Versioning]()

## Tags

### Release Candidates

| Branch Name                     | Tag                                        | Increment |
|---------------------------------|--------------------------------------------|-----------|
| `<issue#>-<issue_descpription>` | `v<major>.<minor>.<patch>-rc.<issue#>.<#>` | `<#>`     |

```shell
TAG_VERSION="v<major>.<minor>.<patch>-rc.<issue#>-<#>"


git tag --annotate "${TAG_VERSION}" --message "RC Release Version ${TAG_VERSION}" --force

git push --tags --force


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    git pull --tags

    git tag --annotate "${TAG_VERSION}" --message "RC Release Version ${TAG_VERSION}" --force
    # git tag --annotate "latest" --message "Latest Release Version (pointing to ${TAG_VERSION})" "${TAG_VERSION}^{}" --force

    git push --tags --force

    popd || exit
done;

popd || exit
```

### Releases

| Branch Name | Tag                        | Increment                           |
|-------------|----------------------------|-------------------------------------|
| `main`      | `v<major>.<minor>.<patch>` | `<major>` or `<minor>` or `<patch>` |

```shell
TAG_VERSION="v<major>.<minor>.<patch>"
# BRANCH="main"


git pull --tags

git tag --annotate "${TAG_VERSION}" --message "Main Release Version ${TAG_VERSION}" --force
git tag --annotate "latest" --message "Latest Release Version (pointing to ${TAG_VERSION})" "${TAG_VERSION}^{}" --force

git push --tags --force


pushd .features || exit

for dir in */; do
    pushd "${dir}" || exit

    git pull --tags

    git tag --annotate "${TAG_VERSION}" --message "Main Release Version ${TAG_VERSION}" --force
    git tag --annotate "latest" --message "Latest Release Version (pointing to ${TAG_VERSION})" "${TAG_VERSION}^{}" --force

    git push --tags --force

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