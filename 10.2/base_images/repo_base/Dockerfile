FROM ubuntu:20.04 AS repo_base
LABEL authors="michimussato@gmail.com"

ARG DEBIAN_FRONTEND=noninteractive

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
