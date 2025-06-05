# docker build --tag openstudiolandscapes:0.1 --no-cache . --build-arg PYTHON_MAJ=3 --build-arg PYTHON_MIN=11 --build-arg PYTHON_PAT=11
FROM ubuntu:22.04 AS openstudiolandscapes
LABEL authors="michael"

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG PYTHON_PAT

SHELL ["/bin/bash", "-c"]

USER root

# RUN systemctl disable --now unattended-upgrades
# Get Python
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends  \
    curl  \
    file  \
    ca-certificates
# Build Python
RUN apt-get install -y --no-install-recommends  \
    build-essential  \
    pkg-config  \
    zlib1g-dev  \
    libncurses5-dev  \
    libgdbm-dev  \
    libnss3-dev  \
    libssl-dev  \
    libreadline-dev  \
    libffi-dev  \
    libsqlite3-dev  \
    libbz2-dev  \
    iproute2  \
    liblzma-dev
# Additional Packages
RUN apt-get install -y --no-install-recommends  \
    ssh  \
    git  \
    htop  \
    vim  \
    graphviz
# RUN apt-get clean

# RUN systemctl enable --now ssh

RUN useradd -ms /bin/bash openstudiolandscapes

# Clone Repo
# Pull if Repo already cloned
# RUN git clone --tags git@github.com:michimussato/OpenStudioLandscapes.git
#RUN git -C OpenStudioLandscapes pull

# USER root

WORKDIR /build/python

RUN curl "https://www.python.org/ftp/python/$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT/Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT.tgz" -o Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT.tgz
RUN file Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT.tgz
RUN tar -xvf Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT.tgz

RUN cd Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT && ./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
RUN cd Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT && make -j $(nproc)
RUN cd Python-$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT && make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

RUN python$PYTHON_MAJ.$PYTHON_MIN -m pip install --upgrade pip setuptools setuptools_scm wheel

# RUN thinkbox-ssl-gen --help

RUN rm -rf /build/python

RUN apt-get clean

USER openstudiolandscapes

WORKDIR /home/openstudiolandscapes/git/repos

# Clone Repo
# Pull if Repo already cloned
RUN git clone --verbose --tags https://github.com/michimussato/OpenStudioLandscapes.git
# RUN git -C OpenStudioLandscapes pull
WORKDIR OpenStudioLandscapes
RUN python$PYTHON_MAJ.$PYTHON_MIN -m venv .venv

RUN ./.venv/bin/pip --verbose install -e .[dev]

RUN ./.venv/bin/nox --session clone_features
RUN ./.venv/bin/nox --session install_features_into_engine


ENTRYPOINT ["top", "-b"]