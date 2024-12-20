#!/usr/bin/env bash


# Based on
# https://github.com/michimussato/deadline-setup/blob/main/README_ENVIRONMENT.md

export NFS_SHARE_ROOT_NFS=nfs
export NFS_MOUNT_ROOT=/data/share/${NFS_SHARE_ROOT_NFS}


mkdir -p ${NFS_MOUNT_ROOT}
mkdir -p /data_replica
ln -sfn ${NFS_MOUNT_ROOT} /${NFS_SHARE_ROOT_NFS}
mkdir -p /data/local


mkdir -p repos
git -C ./repos clone https://github.com/ynput/ayon-docker
git -C ./repos clone
