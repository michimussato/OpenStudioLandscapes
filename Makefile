# env
# REPO_DIR=~/git/repos/OpenStudioLandscapes
# VERSION_TAG=v1.6.0-rc1

include .env

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

install: \
		disable_unattended \
		install_deps \
		install_gh_cli \
		install_python \
		install_docker \
		edit_hosts_file \
		harbor_prepare \
		harbor_up \
		harbor_init \
		add_aliases \
		reboot

disable_unattended:
	echo "Starting prep..."
	sudo systemctl disable --now unattended-upgrades

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

install_gh_cli:
	# $ make install_gh_cli
	#(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	#	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	#	&& out= && wget -nv -Out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	#	&& cat ut | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	#	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	#	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	#	&& echo "deb [arch= signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	#	&& sudo apt update \
	#	&& sudo apt install gh -y
	#E: Malformed entry 1 in list file /etc/apt/sources.list.d/github-cli.list ([option] no value)
	#E: The list of sources could not be read.
	#make: *** [Makefile:40: install_gh_cli] Error 100
	(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
		&& sudo mkdir -p -m 755 /etc/apt/keyrings \
		&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
		&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
		&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
		&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
		&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
		&& sudo apt update \
		&& sudo apt install gh -y

## REPO_DIR=~/git/repos/OpenStudioLandscapes
#backup_previous:
#	if [ -d ${REPO_DIR} ]; then;\
#		echo "Backing up previous Installation...";\
#		mv ${REPO_DIR} ${REPO_DIR}_$(date +"%Y-%m-%d_%H-%m-%S");\
#	fi

## VERSION_TAG=v1.6.0-rc1
#clone_repo:
#	if [ ! -d ${REPO_DIR} ]; then;\
#		mkdir -p ${REPO_DIR};\
#	fi
#	git -C ${REPO_DIR} clone --tags https://github.com/michimussato/OpenStudioLandscapes.git
#	git -C ${REPO_DIR} checkout tags/${VERSION_TAG} -B ${VERSION_TAG}


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

	pushd "$(mktemp -d)" || exit 1
	curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
	tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
	cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} || exit 1
	./configure --enable-optimizations
	make -j "$(nproc)"
	sudo make altinstall
	popd || exit 1

install_docker:
	for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do;\
		sudo apt-get remove $pkg;\
	done

	sudo apt autoremove -y
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		ca-certificates \
		curl

	sudo install -m 0755 -d /etc/apt/keyrings
	sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
	sudo chmod a+r /etc/apt/keyrings/docker.asc

	sudo -s << EOF
	mkdir -p /etc/docker
	touch /etc/docker/daemon.json
	cat > /etc/docker/daemon.json
	{
		"features": {
		"buildkit": true
	},
		"max-concurrent-uploads": 1,
		"insecure-registries" : [
			"http://harbor.farm.evil:80",
			"http://192.168.1.162:5000",
			"http://192.168.1.163:5000",
			"http://192.168.1.164:80",
			"http://192.168.1.165:80",
			"http://127.0.0.1:5000",
			"http://localhost:5000",
			"http://10.1.2.15:5000",
			"http://[::1]:5000"
		]
	}
	EOF

	echo \
		"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
		$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		docker-ce \
		docker-ce-cli \
		containerd.io \
		docker-buildx-plugin \
		docker-compose-plugin
	sudo groupadd --force --gid 959 docker
	sudo usermod --append --groups docker "${USER}"

	sudo systemctl daemon-reload
	# sudo systemctl restart docker

	sudo git config --global --add safe.directory ${REPO_DIR}
	sudo git -C ${REPODIR} clean -d -x --force ${REPODIR}/.landscapes/.harbor

	echo "Your /etc/docker/daemon.json file looks like:
	cat /etc/docker/daemon.json

#install_openstudiolandscapes:
#	cd ${REPO_DIR}
#	source .venv/bin/activate
#	pip install --upgrade pip setuptools setuptools_scm wheel
#	pip install -e .[dev]
#	nox -s clone_features
#	nox -s install_features_into_engine
#	deactivate

edit_hosts_file:
	for fqdn in \
		dagster.farm.evil \
		postgres-dagster.farm.evil \
		harbor.farm.evil \
		pi-hole.farm.evil \
	do;\
		sed -i -e "\$a127.0.0.1    $fqdn" -e "/127.0.0.1    ${fqdn}/d" /etc/hosts;\
	done

	echo "Your /etc/hosts file looks like:"
	cat /etc/hosts

harbor_prepare:
	cd ${REPO_DIR}
	source .venv/bin/activate
	openstudiolandscapesutil-harborcli prepare download --destination-directory ./.harbor/download
	openstudiolandscapesutil-harborcli prepare extract --extract-to ./.harbor/bin --tar-file ./.harbor/download/harbor-*.tgz
	openstudiolandscapesutil-harborcli prepare configure --destination-directory ./.harbor/bin
	openstudiolandscapesutil-harborcli prepare install --prepare-script ./.harbor/bin/prepare
	deactivate

harbor_up:
	cd ${REPO_DIR}
	source .venv/bin/activate
	eval $(openstudiolandscapesutil-harborcli systemd install --enable --start --outfile ./.harbor/bin/harbor.service --su-method sudo)
	deactivate

harbor_init:
	cd ${REPO_DIR}
	source .venv/bin/activate
	openstudiolandscapesutil-harborcli project create --project-name openstudiolandscapes --host 127.0.0.1 --port 80
	openstudiolandscapesutil-harborcli project delete --project-name library --host 127.0.0.1 --port 80
	deactivate

add_aliases:
	sed -i -e '$asource ${REPO_DIR}/\.openstudiolandscapesrc' -e '/source $(${REPO_DIR} | tr "/" "\/")\/\.openstudiolandscapesrc/d' "~/.bashrc"

reboot:
	read -r -e -p "Reboot now? " choice_reboot
	[[ "$choice_reboot" == [Yy]* ]] \
		&& sudo systemctl reboot \
		|| echo "Ok, let\'s reboot later."

#initial_checks:
##	#$ make initial_checks
##	#mkdir -p /home/user/git/repos/OpenStudioLandscapes || sudo mkdir -p /home/user/git/repos/OpenStudioLandscapes
##	#if [  -eq 0 ]; then
##	#/bin/sh: 1: Syntax error: end of file unexpected (expecting "fi")
##	#make: *** [Makefile:216: initial_checks] Error 2
##	mkdir -p ${REPO_DIR}
##	# sudo mkdir -p ${REPO_DIR}
#
#	UID := $(shell id -u)
#	ifeq ($(UID),0)
#		echo "Operation not permitted."
#		echo
#		echo "This OpenStudioLandscapes installer must not be executed as user root!"
#		echo "Re-run as regular user."
#		echo
#		exit 1
#	endif
#
##	if ! groups $$USER | grep -qw "docker"; then;\
##		sudo groupadd --force --gid 959 docker || exit 1;\
##		sudo usermod --append --groups docker "$${USER}" || exit 1;\
##		echo "User $$USER has been added to group \`docker\`.";\
##		echo "Reboot now and re-run this scrip.";\
##	fi
##
##	if command -v "docker/"; then;\
##		if docker ps | grep "goharbor/"; then;\
##			echo "Docker Container Harbor is running!";\
##			echo "It is not advisable to perform this installation while Harbor is running.";\
##			echo;\
##			echo "Stop the containers and re-run the installer.";\
##			echo "Run `docker stop $(docker ps -q)` to stop all running containers.";\
##			echo;\
##			exit 1;\
##		fi
##	fi