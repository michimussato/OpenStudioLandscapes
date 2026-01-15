<!-- TOC -->
* [Convert an ephemeral volume to a permanent one](#convert-an-ephemeral-volume-to-a-permanent-one)
  * [symlink](#symlink)
  * [Config](#config)
<!-- TOC -->

---

# Convert an ephemeral volume to a permanent one

There are many options.

## symlink

```shell
# cd OpenStudioLandscapes/.landscapes
sudo rsync --mkpath -rhav 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data/ .persistent/OpenStudioLandscapes-Kitsu/data/
sudo mv 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data.bak
ln --force --symbolic --relative --target-directory $(pwd)/2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/ $(pwd)/.persistent/OpenStudioLandscapes-Kitsu/data
# sudo rm -rf 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data.bak
```

```
$ stat 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data
  File: 2026-01-14_23-03-18__omniscient-rust-morning-mare/OpenStudioLandscapes-Kitsu/data -> ../../.persistent/OpenStudioLandscapes-Kitsu/data
  Size: 49              Blocks: 1          IO Block: 131072 symbolic link
Device: 27h/39d Inode: 1194202     Links: 1
Access: (0777/lrwxrwxrwx)  Uid: ( 1000/    user)   Gid: ( 1000/    user)
Access: 2026-01-15 00:22:43.220719917 +0000
Modify: 2026-01-15 00:22:41.848700086 +0000
Change: 2026-01-15 00:22:41.848700086 +0000
 Birth: 2026-01-15 00:22:41.848700086 +0000
```

## Config

Use a permanent path to a resource.
