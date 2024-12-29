FROM ubuntu:20.04 AS repo_base
LABEL authors="michimussato@gmail.com"

ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG PYTHON_PAT
ENV PYTHON_MAJ=${PYTHON_MAJ}
ENV PYTHON_MIN=${PYTHON_MIN}
ENV PYTHON_PAT=${PYTHON_PAT}

ENV CONTAINER_TIMEZONE="Europe/Zurich"
ENV SET_CONTAINER_TIMEZONE=true

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install \
    -y \
    --no-install-recommends \
    git \
    ca-certificates \
    file  \
    tzdata  \
    curl  \
    ffmpeg  \
    xvfb  \
    libegl1  \
    libsm6  \
    libglu1-mesa  \
    libxss1

RUN apt-get install  \
    -y  \
    --no-install-recommends  \
    make  \
    build-essential  \
    zlib1g-dev  \
    libncurses5-dev  \
    libgdbm-dev  \
    libnss3-dev  \
    libssl-dev  \
    libreadline-dev  \
    libffi-dev  \
    libsqlite3-dev  \
    libbz2-dev

WORKDIR /build/python

RUN curl https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
RUN file Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
RUN tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz

RUN cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} && ./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
RUN cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} && make -j $(nproc)
RUN cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} && make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install pip --upgrade

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/SSLGeneration.git@packaging
RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/DeadlineWrapper.git@main
RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "deadline-dagster @ git+https://github.com/michimussato/deadline-dagster.git@main"
RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared @ git+https://github.com/michimussato/dagster-shared.git@main"
# RUN thinkbox-ssl-gen --help

RUN rm -rf /build/python

RUN apt-get clean

ENTRYPOINT []



FROM repo_base AS likec4_dev
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

COPY ./docker-third-party/likec4/setup.sh .
COPY ./docker-third-party/likec4/run.sh .

RUN chmod -R +x /ENTRYPOINT/*.sh

RUN /usr/bin/env bash /ENTRYPOINT/setup.sh

# https://stackoverflow.com/a/40454758/2207196
ENTRYPOINT /usr/bin/env bash /ENTRYPOINT/run.sh
CMD yarn dev --host 0.0.0.0 --port ${LIKEC4_DEV_PORT_CONTAINER}



FROM repo_base AS dagster_dev
LABEL authors="michimussato@gmail.com"

#ARG DAGSTER_HOME
#ENV DAGSTER_HOME=${DAGSTER_HOME}

#ARG DAGSTER_WORKSPACE
#ENV DAGSTER_WORKSPACE=${DAGSTER_WORKSPACE}

#ARG DAGSTER_DEV_PORT_CONTAINER
#ENV DAGSTER_DEV_PORT_CONTAINER=${DAGSTER_DEV_PORT_CONTAINER}

WORKDIR /dagster
COPY ./configs/dagster_shared/workspace.yaml .

WORKDIR /dagster/materializations
COPY ./configs/dagster_shared/dagster.yaml .

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

ENTRYPOINT dagster dev --workspace ${DAGSTER_WORKSPACE} --port ${DAGSTER_DEV_PORT_CONTAINER} --host 0.0.0.0



FROM repo_base AS repo_installer
LABEL authors="michimussato@gmail.com"

#ARG MONGO_DB_PORT_CONTAINER
#ENV MONGO_DB_PORT_CONTAINER=$MONGO_DB_PORT_CONTAINER

#ARG DEADLINE_VERSION
#ENV DEADLINE_VERSION=$DEADLINE_VERSION
#
#ARG INSTALLERS_ROOT
#ENV INSTALLERS_ROOT=$INSTALLERS_ROOT
#
#WORKDIR ${INSTALLERS_ROOT}/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    install-repository  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/DeadlineRepository10"  \
    --dbtype "MongoDB"  \
    --dbhost ${DB_HOST}  \
    --dbport ${MONGO_DB_PORT_CONTAINER}  \
    --dbname ${MONGO_DB_NAME}



FROM repo_base AS client_installer

ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

# ARG INSTALLERS_ROOT
ENV INSTALLERS_ROOT=$INSTALLERS_ROOT

LABEL authors="michimussato@gmail.com"

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    install-client  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/Deadline10"  \
    --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
    --httpport ${RCS_HTTP_PORT_CONTAINER}  \
    --webservice-httpport ${WEBSERVICE_HTTP_PORT_CONTAINER}



FROM client_installer AS rcs_runner

LABEL authors="michimussato@gmail.com"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinercs"



FROM client_installer AS pulse_runner

LABEL authors="michimussato@gmail.com"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinepulse"  \
    --arguments "['-nogui', '-nosplash']"



FROM client_installer AS worker_runner

LABEL authors="michimussato@gmail.com"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlineworker"  \
    --arguments "['-nogui', '-nosplash']"



FROM client_installer AS webservice_runner

LABEL authors="michimussato@gmail.com"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinewebservice"
