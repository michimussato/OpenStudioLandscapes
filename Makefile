# env
-include .env

SHELL := $(shell which bash)

ifdef PYTHON_MAJ
PYTHON_MAJ := $(PYTHON_MAJ)
else
PYTHON_MAJ := 3
endif

ifdef PYTHON_MIN
PYTHON_MIN := $(PYTHON_MIN)
else
PYTHON_MIN := 11
endif

ifdef PYTHON_PAT
PYTHON_PAT := $(PYTHON_PAT)
else
PYTHON_PAT := 11
endif


sys_deps_install: \
	install_deps \
	install_python \
	prepare_install_docker \
	install_docker

install_deps:
	sudo apt-get update
	sudo apt-get -y autoremove
	sudo apt-get -y upgrade
	sudo apt-get install --no-install-recommends -y \
		openssh-server \
		git \
		htop \
		vim \
		graphviz
	sudo apt-get clean
	sudo systemctl enable --now ssh

install_python:
	sudo apt-get install --no-install-recommends -y \
		build-essential \
		zlib1g-dev \
		libncurses5-dev \
		libgdbm-dev \
		libnss3-dev \
		libssl-dev \
		libreadline-dev \
		libffi-dev \
		pkg-config \
		liblzma-dev \
		libbz2-dev \
		libsqlite3-dev \
		curl

	cd "$$(mktemp -d)" || exit 1 && \
		curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz \
		&& tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz \
		&& cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} || exit 1 \
		&& ./configure --enable-optimizations \
		&& make -j "$$(nproc)" \
		&& sudo make altinstall \
	# popd || exit 1

prepare_install_docker:
	# https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
	sudo groupadd --force --gid 959 docker
	sudo usermod --append --groups docker $${USER}

# Todo:
#  - [ ] Check for OS Version here!
#        - https://github.com/michimussato/OpenStudioLandscapes/issues/71
install_docker:
	# https://docs.docker.com/engine/install/ubuntu/
	for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do \
		sudo apt-get remove $$pkg ; \
	done

	sudo apt autoremove -y
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		ca-certificates \
		curl

	sudo install -m 0755 -d /etc/apt/keyrings
	sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
	sudo chmod a+r /etc/apt/keyrings/docker.asc

	echo \
		"deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
		$$(. /etc/os-release && echo "$${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		docker-ce \
		docker-ce-cli \
		containerd.io \
		docker-buildx-plugin \
		docker-compose-plugin

	sudo systemctl status --no-pager --full docker.service
	sudo systemctl status --no-pager --full containerd.service

# edit_hosts_file:
# 	for fqdn in \
# 		openstudiolandscapes-dagster.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
# 		openstudiolandscapes-dagster-postgres.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
# 	; do \
# 		sudo sed -i -e "\$$a127.0.0.1    $$fqdn" -e "/127.0.0.1    $${fqdn}/d" /etc/hosts; \
# 	done
#
# 	echo "Your /etc/hosts file looks like:"
# 	cat /etc/hosts

setup_venv:
	python3.11 -m venv .venv

openstudiolandscapes_install:
	python3.11 -m venv .venv \
		&& source .venv/bin/activate \
		&& pip install --upgrade pip setuptools setuptools_scm wheel \
		&& pip install -e . \
		&& deactivate
###############################################################################


###############################################################################
# CLEAN UP

#nox_CLEAR_ALL:
#	rm -r ./.nox/*/
###############################################################################

help:
	# https://stackoverflow.com/a/26339924
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
