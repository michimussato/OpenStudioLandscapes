#!/usr/bin/env bash

curl --version

docker build  \
    --tag michimussato/base_image_10_2:latest  \
    --build-arg GOOGLE_ID_AWSPortalLink_10_2="1VOQa6OyYUZj_7VILcD6EVl7YOfYVlCrU"  \
    --build-arg GOOGLE_ID_DeadlineClient_10_2="1cGxCPkrJ1ujWqie2yXTrOpShkEgSXR0F"  \
    --build-arg GOOGLE_ID_DeadlineRepository_10_2="1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz"  \
    .
