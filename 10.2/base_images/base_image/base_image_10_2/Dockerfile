FROM michimussato/base_image:latest AS base_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG GOOGLE_API_KEY
#ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

ARG GOOGLE_ID_AWSPortalLink_10_2
#ENV GOOGLE_ID_AWSPortalLink_10_2=${GOOGLE_ID_AWSPortalLink_10_2}

ARG GOOGLE_ID_DeadlineClient_10_2
#ENV GOOGLE_ID_DeadlineClient_10_2=${GOOGLE_ID_DeadlineClient_10_2}

ARG GOOGLE_ID_DeadlineRepository_10_2
#ENV GOOGLE_ID_DeadlineRepository_10_2=${GOOGLE_ID_DeadlineRepository_10_2}

RUN apt-get update \
    && apt-get upgrade -y


WORKDIR /installers

#RUN wget -O AWSPortalLink.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_AWSPortalLink_10_2}?alt=media&key=AIzaSyBBH8zUH4VC1Bov-3EdVbjG0gBauroMd9E"
RUN echo "Downloading AWSPortalLink..."  \
    && wget -O AWSPortalLink.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_AWSPortalLink_10_2}?alt=media&key=${GOOGLE_API_KEY}" \
    && echo "Download AWSPortalLink done."
RUN echo "Downloading DeadlineClient..."  \
    && wget -O DeadlineClient.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_DeadlineClient_10_2}?alt=media&key=${GOOGLE_API_KEY}" \
    && echo "Download DeadlineClient done."
RUN echo "Downloading DeadlineRepository..." \
    && wget -O DeadlineRepository.run "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID_DeadlineRepository_10_2}?alt=media&key=${GOOGLE_API_KEY}" \
    && echo "Download DeadlineRepository done."

# wget -O DeadlineRepository.run https://www.googleapis.com/drive/v3/files/1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz?alt=media&key=AIzaSyBBH8zUH4VC1Bov-3EdVbjG0gBauroMd9E

# RUN thinkbox-ssl-gen --help

RUN apt-get clean

ENTRYPOINT []
