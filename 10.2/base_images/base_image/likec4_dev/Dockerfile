FROM michimussato/base_image:latest AS likec4_dev
LABEL authors="michimussato@gmail.com"

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install \
    -y \
    --no-install-recommends \
    unzip  \
    gpg  \
    gpg-agent

WORKDIR /ENTRYPOINT

COPY ./entrypoint/setup.sh .
COPY ./entrypoint/run.sh .

RUN chmod -R +x /ENTRYPOINT/*.sh

RUN /usr/bin/env bash /ENTRYPOINT/setup.sh

# https://stackoverflow.com/a/40454758/2207196
ENTRYPOINT ["/usr/bin/env", "bash", "/ENTRYPOINT/run.sh", "yarn", "dev"]
#CMD --host 0.0.0.0 --port ${LIKEC4_DEV_PORT_CONTAINER}
