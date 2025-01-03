FROM michimussato/base_image:latest AS base_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG PYTHON_PAT
ARG GOOGLE_API_KEY
ARG GOOGLE_ID_AWSPortalLink_10_2
ARG GOOGLE_ID_DeadlineClient_10_2
ARG GOOGLE_ID_DeadlineRepository_10_2

RUN apt-get update \
    && apt-get upgrade -y

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/SSLGeneration.git@packaging
RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/DeadlineWrapper.git@main

WORKDIR /installers

RUN wget -O AWSPortalLink.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_AWSPortalLink_10_2}?alt=media&key=${GOOGLE_API_KEY}"
RUN chmod a+x AWSPortalLink.run
RUN wget -O DeadlineClient.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_DeadlineClient_10_2}?alt=media&key=${GOOGLE_API_KEY}"
RUN chmod a+x DeadlineClient.run
RUN wget -O DeadlineRepository.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_DeadlineRepository_10_2}?alt=media&key=${GOOGLE_API_KEY}"
RUN chmod a+x DeadlineRepository.run

# RUN thinkbox-ssl-gen --help

RUN apt-get clean

ENTRYPOINT []
