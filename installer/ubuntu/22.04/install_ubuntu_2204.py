#!/usr/bin/env python3
# https://www.baeldung.com/linux/curl-fetched-script-arguments
import base64
import inspect
import json
import shlex
import shutil
import sys
import tempfile
import pathlib
from getpass import getuser
from typing import Tuple
import pty
# import logging
# import ptyprocess.ptyprocess


# import logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("geeksforgeeks.log"),
#         logging.StreamHandler(),
#     ]
# )


# Requirements:
# - python3
# - curl
# - sudo
# Usage:
# python3 <(curl --header 'Cache-Control: no-cache, no-store' --silent https://raw.githubusercontent.com/michimussato/OpenStudioLandscapes/refs/heads/main/ubuntu/22.04/install_ubuntu_2204.py)


# OPENSTUDIOLANDSCAPES_BASE: pathlib.Path = pathlib.Path("~/git/repos")
# OPENSTUDIOLANDSCAPES_SUFFIX: str = "OpenStudioLandscapes"
# OPENSTUDIOLANDSCAPES_DIR: pathlib.Path = OPENSTUDIOLANDSCAPES_BASE / OPENSTUDIOLANDSCAPES_SUFFIX
URL_HARBOR: str = "http://harbor.farm.evil:80"
ADMIN_HARBOR: str = "admin"
PASSWORD_HARBOR: str = "Harbor12345"
DOCKER_GID: str = "959"
# Todo
#  - [ ] Remove this switch after release
USE_SSH: bool = False
# Todo
#  - [ ] Create DOT_LANDSCAPES automatically
DOT_LANDSCAPES: pathlib.Path = pathlib.Path("/opt/openstudiolandscapes/.landscapes")


SHELL_SCRIPTS_PREFIX = "ubuntu_2204"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    BROWN = '\033[43m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _get_terminal_size() -> Tuple[int, int]:
    # https://stackoverflow.com/a/14422538
    # https://stackoverflow.com/a/18243550
    cols, rows = shutil.get_terminal_size((80, 20))
    return cols, rows


def script_run(
    sudo: bool = False,
    *,
    script: pathlib.Path,
) -> int:

    print(" BLOCK START ".center(_get_terminal_size()[0], "="))

    cmd = [
        shutil.which("bash"),
        script.as_posix(),
    ]

    if sudo:
        cmd.insert(0, shutil.which("sudo"))
        # cmd.insert(1, "--stdin")

    with open(script.as_posix(), "r") as f:
        lines = f.readlines()
        print(" COMMAND ".center(_get_terminal_size()[0], "-"))
        print(bcolors.BROWN + f" {shlex.join(cmd)} ".center(_get_terminal_size()[0], " ") + bcolors.ENDC)
        print(" SCRIPT START ".center(_get_terminal_size()[0], "-"))
        lno = 0
        len_ = len(str(len(lines)))
        print(bcolors.OKCYAN)
        for l in lines:
            lno += 1
            print(f"{str(lno).ljust(len_)}: {l.rstrip()}")
        print(bcolors.ENDC)
        print(" SCRIPT END ".center(_get_terminal_size()[0], "-"))

    # We want all command executions to be fully interactive,
    # hence, subprocess.run got me close but is not the best solution
    # when it comes to user input like passwords or other
    # arbitrary data.
    print(" SCRIPT EXECUTION START ".center(_get_terminal_size()[0], "-"))
    result = pty.spawn(cmd)
    print(" SCRIPT EXECUTION END ".center(_get_terminal_size()[0], "-"))
    print(" RETURN CODE ".center(_get_terminal_size()[0], "-"))
    if result == 0:
        print(bcolors.OKGREEN + f"Return Code = {result}" + bcolors.ENDC)
    else:
        print(bcolors.FAIL + f"Return Code = {result}" + bcolors.ENDC)
    print(" BLOCK END ".center(_get_terminal_size()[0], "="))

    return result


def script_disable_unattended_upgrades() -> pathlib.Path:
    print(" DISABLE UNATTENDED UPGRADES ".center(_get_terminal_size()[0], "#"))
    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "sudo systemctl disable --now unattended-upgrades\n",
                "\n",
                "while pgrep unattended-upgr; do\n",
                "    echo \"Wait for Unattended Upgrade to finish. Can't disable Unit while process is active.\"\n",
                "    sleep 5\n",
                "done\n",
                "\n",
                "# sudo apt-get purge -y unattended-upgrades\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_prep() -> pathlib.Path:
    print(" PREP ".center(_get_terminal_size()[0], "#"))
    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:

        prep_pkgs = [
            "openssh-server",
            "git",
            "htop",
            "vim",
            "graphviz",
        ]
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "sudo apt-get update\n",
                "sudo apt-get -y autoremove\n",
                "sudo apt-get upgrade -y\n",
                "\n",
                f"sudo apt-get install --no-install-recommends -y {' '.join(prep_pkgs)}\n",
                "\n",
                "sudo apt-get clean\n",
                "\n",
                "sudo systemctl enable --now ssh\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_clone_openstudiolandscapes(
    openstudiolandscapes_repo_dir: pathlib.Path,
    ssh_key_file: pathlib.Path = pathlib.Path("~/.ssh/id_ed25519").expanduser(),
    known_hosts_file: pathlib.Path = pathlib.Path("~/.ssh/known_hosts").expanduser(),
) -> pathlib.Path:

    # Todo
    #  - [ ] We *could* add some checks here in case git clone fails.
    #        However, ssh authentication is only necessary while repo
    #        private.
    #  - [ ] git clone fails silently if ~/git/repos/OpenStudioLandscapes
    #        already exists. FIX!

    print(" CLONE OPENSTUDIOLANDSCAPES ".center(_get_terminal_size()[0], "#"))

    if USE_SSH:
        if ssh_key_file.exists():
            print("Existing SSH Key file found. You will be prompted whether to overwrite existing keys or not.")

        print(" ENTER EMAIL ".center(_get_terminal_size()[0], "="))
        email = input("Enter your email: ")

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
            ]
        )

        if USE_SSH:
            script.writelines(
                [
                    "\n",
                    # f"{shutil.which('ssh-keygen')}\n",
                    f"ssh-keygen -f {ssh_key_file.as_posix()} -N '' -t ed25519 -C \"{email}\"\n",
                    "eval \"$(ssh-agent -s)\"\n",
                    f"ssh-add {ssh_key_file.as_posix()}\n",
                    "\n",
                    "echo \"Copy/Paste the following Public Key to GitHub:\"\n",
                    "echo \"https://github.com/settings/ssh/new\"\n",
                    f"cat {ssh_key_file.as_posix()}.pub\n",
                    "\n",
                    "while [[ \"$choice_ssh\" != [Yy]* ]]; do\n",
                    "    read -r -e -p \"Type [Yy]es when ready... \" choice_ssh\n",
                    "done\n",
                    "\n",
                    f"ssh-keyscan github.com >> {known_hosts_file.as_posix()}\n",
                ]
            )

        # If openstudiolandscapes_repo_dir already exists, we move it out
        # of the way. At least until there is a more finegrained solution
        # in place to deal with existing installations.
        script.writelines(
            [
                "\n",
                f"if [ -d {openstudiolandscapes_repo_dir.as_posix()} ]; then\n",
                "    echo \"Backing up previous Installation...\"\n",
                f"    mv {openstudiolandscapes_repo_dir.as_posix()} {openstudiolandscapes_repo_dir.as_posix()}_$(date +\"%Y-%m-%d_%H-%m-%S\")\n",
                "fi\n",
            ]
        )

        script.writelines(
            [
                "\n",
                f"if [ ! -d {openstudiolandscapes_repo_dir.as_posix()} ]; then\n",
                f"    mkdir -p {openstudiolandscapes_repo_dir.as_posix()}\n",
                "fi\n",
                f"git -C {openstudiolandscapes_repo_dir.parent.as_posix()} clone --tags {'git@github.com:' if USE_SSH else 'https://github.com/'}michimussato/OpenStudioLandscapes.git\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_install_python(
    PYTHON_MAJ: int = 3,
    PYTHON_MIN: int = 11,
    PYTHON_PAT: int = 11,
) -> pathlib.Path:

    print(f" INSTALL PYTHON {PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
            ],
        )

        script.writelines(
            [
                f"if which python3.11; then\n",
                "    echo \"python3.11 is already installed\"\n",
                "    exit 0\n",
                "fi\n",
                "\n",
                "\n",
            ]
        )

        python_pkgs = [
            "build-essential",
            "zlib1g-dev",
            "libncurses5-dev",
            "libgdbm-dev",
            "libnss3-dev",
            "libssl-dev",
            "libreadline-dev",
            "libffi-dev",
            "pkg-config",
            "liblzma-dev",
            "libbz2-dev",
            "libsqlite3-dev",
            "curl",
        ]
        script.writelines(
            [
                # line 10: [: too many arguments
                "while ! sudo apt-get upgrade -y; do\n",
                "    echo \"Update in progress in the background...\"\n",
                "    sleep 5\n",
                "done;\n",
                "\n",
                # Todo:
                #  - [ ] while [ ! sudo apt-get upgrade -y ]; do
                #        /tmp/ubuntu_2204__211gwqzp.sh: line 10: [: too many arguments
                f"sudo apt-get install --no-install-recommends -y {' '.join(python_pkgs)}\n",
                "\n",
                "pushd \"$(mktemp -d)\" || exit 1\n",
                "\n",
                f"curl \"https://www.python.org/ftp/python/{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}/Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz\" -o Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz\n",
                f"tar -xvf Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz\n",
                f"cd Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT} || exit 1\n",
                "\n",
                "./configure --enable-optimizations\n",
                "make -j \"$(nproc)\"\n",
                "sudo make altinstall\n",
                "\n",
                "popd || exit 1\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_install_docker(
    openstudiolandscapes_repo_dir: pathlib.Path,
    docker_user: str,
    edit_docker_daemon_json: bool = True,
    url_harbor: str = URL_HARBOR,
) -> pathlib.Path:

    print(" INSTALL DOCKER ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        docker1_pkgs = [
            "ca-certificates",
            "curl",
        ]
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "# Documentation:\n",
                "# https://docs.docker.com/engine/install/ubuntu/\n",
                "\n",
                "for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do\n",
                "    sudo apt-get remove $pkg\n",
                "done\n",
                "\n",
                "sudo apt autoremove -y\n",
                "\n",
                "sudo apt-get update\n",
                "\n",
                f"sudo apt-get install --no-install-recommends -y {' '.join(docker1_pkgs)}\n",
                "\n",
                "sudo install -m 0755 -d /etc/apt/keyrings\n",
                "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc\n",
                "sudo chmod a+r /etc/apt/keyrings/docker.asc\n",
            ]
        )

        if edit_docker_daemon_json:

            daemon_json = {
                "insecure-registries" : [
                    url_harbor,
                ],
                "max-concurrent-uploads": 1,
            }

            daemon_json_ = json.dumps(daemon_json, indent=2)

            script.writelines(
                [
                    "\n",
                    "sudo -s << EOF\n",
                    "mkdir -p /etc/docker\n",
                    "touch /etc/docker/daemon.json\n",
                    "cat > /etc/docker/daemon.json\n",
                    f"{daemon_json_}\n",
                    "EOF\n",
                ]
            )

        docker_pkgs = [
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
        ]
        script.writelines(
            [
                "\n",
                "echo \\\n",
                "  \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \\\n",
                "  $(. /etc/os-release && echo \"${UBUNTU_CODENAME:-$VERSION_CODENAME}\") stable\" | \\\n",
                "  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null\n",
                "sudo apt-get update\n",
                "\n",
                f"sudo apt-get install --no-install-recommends -y {' '.join(docker_pkgs)}\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "# https://docs.docker.com/engine/install/linux-postinstall/\n",
                "\n",
                f"# These steps have already been executed in script_initial_checks()\n",
                f"# sudo groupadd --force --gid {DOCKER_GID} docker\n",
                f"# sudo usermod --append --groups docker \"{docker_user}\"\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "sudo systemctl daemon-reload\n",
                # Todo
                #  - [x] This step causes the Harbor issues:
                "sudo systemctl restart docker\n",
                "\n",
                # Todo
                #  - [x] And this is the *best* solution I could come up with so far:
                f"# sudo rm -rf {pathlib.Path(openstudiolandscapes_repo_dir, '.landscapes', '.harbor', 'bin').as_posix()}/*\n",
                f"# sudo rm -rf {pathlib.Path(openstudiolandscapes_repo_dir, '.landscapes', '.harbor', 'data').as_posix()}/*\n",
                f"sudo git config --global --add safe.directory {pathlib.Path(openstudiolandscapes_repo_dir).as_posix()}\n",
                f"sudo git -C {pathlib.Path(openstudiolandscapes_repo_dir).as_posix()} clean -d -x --force {pathlib.Path(openstudiolandscapes_repo_dir, '.landscapes', '.harbor').as_posix()}\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "echo \"Your /etc/docker/daemon.json file looks like:\"\n",
                "cat /etc/docker/daemon.json\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_install_openstudiolandscapes(
    openstudiolandscapes_repo_dir: pathlib.Path,
) -> pathlib.Path:

    print(" INSTALL OPENSTUDIOLANDSCAPES ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                f"cd {openstudiolandscapes_repo_dir.as_posix()}\n",
                f"{shutil.which('python3.11')} -m venv .venv\n",
                "\n",
                "source .venv/bin/activate\n",
                "pip install --upgrade pip setuptools setuptools_scm wheel\n",
                "\n",
                "pip install -e .[dev]\n",
                "\n",
                "nox -s clone_features\n",
                "nox -s install_features_into_engine\n",
                "\n",
                "deactivate\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_etc_hosts() -> pathlib.Path:

    print(" EDIT /etc/hosts ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "for fqdn in \\\n",
                "    dagster.farm.evil \\\n",
                "    postgres-dagster.farm.evil \\\n",
                "    harbor.farm.evil \\\n",
                "    pi-hole.farm.evil \\\n",
                "; do \n",
                "    sed -i -e \"\$a127.0.0.1    $fqdn\" -e \"/127.0.0.1    ${fqdn}/d\" /etc/hosts\n",
                "done\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "echo \"Your /etc/hosts file looks like:\"\n",
                "cat /etc/hosts\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_harbor_prepare(
    openstudiolandscapes_repo_dir: pathlib.Path,
) -> pathlib.Path:

    print(" INIT HARBOR ".center(_get_terminal_size()[0], "#"))

    # Todo:
    #  - [x] docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Head "http://%2Fvar%2Frun%2Fdocker.sock/_ping": dial unix /var/run/docker.sock: connect: permission denied
    #        -> should not happen anymore with
    #               sudo groupadd --force docker
    #               sudo usermod --append --groups docker $USER
    #           in script_initial_checks()
    #  - [ ] Bad return code
    #        Run 'docker run --help' for more information
    #        nox > Command /usr/bin/bash /home/user/git/repos/OpenStudioLandscapes/.landscapes/.harbor/bin/prepare failed with exit code 126
    #        nox > Session harbor_prepare failed.
    #        ------------------------------------------------------------ RETURN CODE -------------------------------------------------------------
    #        Return Code = 0
    #        session.run() would return True/False based on success but
    #        I'm not sure yet if that would mean nox-abuse.

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                f"cd {openstudiolandscapes_repo_dir.as_posix()}\n",
                "source .venv/bin/activate\n",
                "nox --session harbor_prepare\n",
                "deactivate\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_harbor_up(
    openstudiolandscapes_repo_dir: pathlib.Path,
) -> pathlib.Path:

    print(" INIT HARBOR UP ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                f"cd {openstudiolandscapes_repo_dir.as_posix()}\n",
                "source .venv/bin/activate\n",
                "nox --session harbor_up_detach\n",
                "\n",
                "deactivate\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_harbor_init(
    url_harbor: str = URL_HARBOR,
    username_harbor: str = ADMIN_HARBOR,
    password_harbor: str = PASSWORD_HARBOR,
) -> pathlib.Path:

    print(" INIT HARBOR ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
            ]
        )

        # Todo:
        #  - [ ] Find a better way to deal with this:
        #        #!/bin/env bash
        #
        #
        #
        #        # Create project openstudiolandscapes
        #
        #        echo "Giving Harbor some time before performing this POST request..."
        #        for i in $(seq 10); do
        #            echo -ne "."
        #            sleep 1
        #        done
        #        echo -ne "
        #        "
        #
        #        curl -v -X 'POST' \
        #          'http://harbor.farm.evil:80/api/v2.0/projects' \
        #          -H 'accept: application/json' \
        #          -H 'X-Resource-Name-In-Location: false' \
        #          -H 'authorization: Basic YWRtaW46SGFyYm9yMTIzNDU=' \
        #          -H 'Content-Type: application/json' \
        #          -d '{
        #          "project_name": "openstudiolandscapes",
        #          "public": true
        #        }'
        #
        #
        #        # Delete project library
        #
        #        echo "Giving Harbor some time before performing this DELETE request..."
        #        for i in $(seq 10); do
        #            echo -ne "."
        #            sleep 1
        #        done
        #        echo -ne "
        #        "
        #
        #        curl -v -X 'DELETE' \
        #          'http://harbor.farm.evil:80/api/v2.0/projects/library' \
        #          -H 'accept: application/json' \
        #          -H 'X-Is-Resource-Name: false' \
        #          -H 'authorization: Basic YWRtaW46SGFyYm9yMTIzNDU='
        #
        #
        #        exit 0
        #
        #        Result:L
        #        -----------
        #        Giving Harbor some time before performing this POST request...
        #        ..........
        #        Note: Unnecessary use of -X or --request, POST is already inferred.
        #        *   Trying 127.0.0.1:80...
        #        * Connected to harbor.farm.evil (127.0.0.1) port 80 (#0)
        #        > POST /api/v2.0/projects HTTP/1.1
        #        > Host: harbor.farm.evil
        #        > User-Agent: curl/7.81.0
        #        > accept: application/json
        #        > X-Resource-Name-In-Location: false
        #        > authorization: Basic YWRtaW46SGFyYm9yMTIzNDU=
        #        > Content-Type: application/json
        #        > Content-Length: 62
        #        >
        #        * Mark bundle as not supporting multiuse
        #        < HTTP/1.1 502 Bad Gateway
        #        < Server: nginx
        #        < Date: Sun, 08 Jun 2025 08:46:02 GMT
        #        < Content-Type: text/html
        #        < Content-Length: 150
        #        < Connection: keep-alive
        #        <
        #        <html>
        #        <head><title>502 Bad Gateway</title></head>
        #        <body>
        #        <center><h1>502 Bad Gateway</h1></center>
        #        <hr><center>nginx</center>
        #        </body>
        #        </html>
        #        * Connection #0 to host harbor.farm.evil left intact
        #        Giving Harbor some time before performing this DELETE request...
        #        ..........
        #        *   Trying 127.0.0.1:80...
        #        * Connected to harbor.farm.evil (127.0.0.1) port 80 (#0)
        #        > DELETE /api/v2.0/projects/library HTTP/1.1
        #        > Host: harbor.farm.evil
        #        > User-Agent: curl/7.81.0
        #        > accept: application/json
        #        > X-Is-Resource-Name: false
        #        > authorization: Basic YWRtaW46SGFyYm9yMTIzNDU=
        #        >
        #        * Mark bundle as not supporting multiuse
        #        < HTTP/1.1 502 Bad Gateway
        #        < Server: nginx
        #        < Date: Sun, 08 Jun 2025 08:46:12 GMT
        #        < Content-Type: text/html
        #        < Content-Length: 150
        #        < Connection: keep-alive
        #        <
        #        <html>
        #        <head><title>502 Bad Gateway</title></head>
        #        <body>
        #        <center><h1>502 Bad Gateway</h1></center>
        #        <hr><center>nginx</center>
        #        </body>
        #        </html>
        #        * Connection #0 to host harbor.farm.evil left intact

        sleep_ = 10
        # Create `openstudiolandscapes` if it does not exist
        script.writelines(
            [
                "\n",
                "# Create project openstudiolandscapes\n",
                "\n",
                "echo \"Giving Harbor some time before performing this POST request...\"\n",
                f"for i in $(seq {str(sleep_)}); do\n",
                # f"    echo -ne $(({str(sleep_)}-$i+1))\n",
                f"    echo -ne \".\"\n",
                "    sleep 1\n",
                "done\n",
                f"echo -ne \"\n\"\n",
                "\n",
                # Todo
                #  - [ ] This is not working! Investigate!
                "curl -v -X 'POST' \\\n",
                f"  '{url_harbor}/api/v2.0/projects' \\\n",
                "  -H 'accept: application/json' \\\n",
                "  -H 'X-Resource-Name-In-Location: false' \\\n",
                f"  -H 'authorization: Basic {base64.b64encode(str(':'.join([username_harbor, password_harbor])).encode('utf-8')).decode('ascii')}' \\\n",
                "  -H 'Content-Type: application/json' \\\n",
                "  -d '{\n",
                "  \"project_name\": \"openstudiolandscapes\",\n",
                "  \"public\": true\n",
                "}'\n",
                "\n",
                # Todo:
                #  - [ ] confirmation/error
                #    like && success || error
                # "sleep 10\n",
            ]
        )

        # Delete `library` if it does exist
        script.writelines(
            [
                "\n",
                "# Delete project library\n",
                "\n",
                "echo \"Giving Harbor some time before performing this DELETE request...\"\n",
                f"for i in $(seq {str(sleep_)}); do\n",
                # f"    echo -ne $(({str(sleep_)}-$i+1))\n",
                f"    echo -ne \".\"\n",
                "    sleep 1\n",
                "done\n",
                f"echo -ne \"\n\"\n",
                "\n",
                "curl -v -X 'DELETE' \\\n",
                f"  '{url_harbor}/api/v2.0/projects/library' \\\n",
                "  -H 'accept: application/json' \\\n",
                "  -H 'X-Is-Resource-Name: false' \\\n",
                f"  -H 'authorization: Basic {base64.b64encode(str(':'.join([username_harbor, password_harbor])).encode('utf-8')).decode('ascii')}'\n",
                "\n",
                # Todo:
                #  - [ ] confirmation/error
                #        like && success || error
                # "sleep 10\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_harbor_down(
    openstudiolandscapes_repo_dir: pathlib.Path,
) -> pathlib.Path:

    print(" INIT HARBOR DOWN ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                f"cd {openstudiolandscapes_repo_dir.as_posix()}\n",
                "source .venv/bin/activate\n",
                "\n",
                "nox --session harbor_down\n",
                "\n",
                "deactivate\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_init_pihole(
    openstudiolandscapes_repo_dir: pathlib.Path,
) -> pathlib.Path:

    print(" INIT PI-HOLE ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                f"cd {openstudiolandscapes_repo_dir.as_posix()}\n",
                "source .venv/bin/activate\n",
                "nox --session pi_hole_prepare\n",
                "deactivate\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_add_alias(
    openstudiolandscapes_repo_dir: pathlib.Path,
    bashrc: pathlib.Path = pathlib.Path("~/.bashrc").expanduser(),
    # openstudiolandscapesrc: pathlib.Path = pathlib.Path("~/.openstudiolandscapesrc").expanduser(),
) -> pathlib.Path:

    print(" ADD ALIASES ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:

        str_repo_dir_ = openstudiolandscapes_repo_dir.as_posix()
        str_repo_dir_escaped = str_repo_dir_.replace("/", "\/")

        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                # Escape dots
                # Working syntax:
                # sed -i -e '$asource /home/user/git/repos/OpenStudioLandscapes/\.openstudiolandscapesrc' -e '/source \/home\/user\/git\/repos\/OpenStudioLandscapes\/\.openstudiolandscapesrc/d' /home/user/.bashrc
                f"sed -i -e '$asource {str_repo_dir_}/\.openstudiolandscapesrc' -e '/source {str_repo_dir_escaped}\/\.openstudiolandscapesrc/d' {bashrc.as_posix()}\n",
            ]
        )

        # script.writelines(
        #     [
        #         f"cat > {openstudiolandscapesrc.as_posix()}<< EOF\n",
        #         "# ~/.openstudiolandscapesrc\n",
        #         f"alias openstudiolandscapes-up=\"pushd {openstudiolandscapes_repo_dir.as_posix()} && source .venv/bin/activate && nox --sessions harbor_up_detach dagster_postgres_up_detach dagster_postgres && deactivate && popd\"\n",
        #         f"alias openstudiolandscapes-down=\"pushd {openstudiolandscapes_repo_dir.as_posix()} && source .venv/bin/activate && nox --sessions dagster_postgres_down harbor_down && deactivate && popd\"\n",
        #         f"alias openstudiolandscapes=\"openstudiolandscapes-up; sleep 5 && openstudiolandscapes-down;\"\n",
        #         "\n",
        #         "EOF\n",
        #     ]
        # )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


def script_reboot() -> pathlib.Path:

    print(" REBOOT ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "read -r -e -p \"Reboot now? \" choice_reboot\n",
                "[[ \"$choice_reboot\" == [Yy]* ]] \\\n",
                "    && sudo systemctl reboot \\\n",
                "|| echo \"Ok, let's reboot later.\"\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 1\n",
            ]
        )

        return pathlib.Path(script.name)


def script_initial_checks(
     docker_user: str,
) -> pathlib.Path:

    print(" INITIAL CHECKS ".center(_get_terminal_size()[0], "#"))

    with tempfile.NamedTemporaryFile(
            delete=False,
            encoding="utf-8",
            prefix=f"{SHELL_SCRIPTS_PREFIX}__{inspect.currentframe().f_code.co_name}__",
            suffix=".sh",
            mode="x",
    ) as script:
        script.writelines(
            [
                "#!/bin/env bash\n",
                "\n",
                "\n",
                "if ! groups $USER | grep -qw \"docker\"; then\n",
                f"    sudo groupadd --force --gid {DOCKER_GID} docker\n",
                f"    sudo usermod --append --groups docker \"{docker_user}\"\n",
                #f"    {shutil.which('bash')} {add_user_to_group_docker(docker_user=docker_user).as_posix()}\n",
                f"    echo \"User $USER has been added to group \\`docker\\`.\"\n",
                f"    echo \"Reboot now and re-run this scrip.\"\n",
                f"    # Reboot Script:\n",
                f"    {shutil.which('bash')} {script_reboot().as_posix()}\n",
                f"    exit 1\n",
                "fi\n",
                "\n",
                "if command -v \"docker/\"; then\n",
                "    if docker ps | grep \"goharbor/\"; then\n",
                "        echo \"Docker Container Harbor is running!\"\n",
                "        echo \"It is not advisable to perform this installation while Harbor is running.\"\n",
                "        echo\n",
                "        echo \"Stop the containers and re-run the installer.\"\n",
                "        echo \"Run `docker stop $(docker ps -q)` to stop all running containers.\"\n",
                "        echo\n",
                "        exit 1\n",
                "    fi\n",
                "fi\n",
                "\n",
                "echo \"Looking good! Let's go...\"\n",
                "\n",
            ]
        )

        script.writelines(
            [
                "\n",
                "exit 0\n",
            ]
        )

        return pathlib.Path(script.name)


if __name__ == "__main__":
    # print(" INSTALL DIRECTORY ".center(_get_terminal_size()[0], "#"))
    # print("(Press Enter to continue with the defaults)")
    # default_openstudiolandscapes_base = "~/git/repos"
    # default_openstudiolandscapes_subdir = "OpenStudioLandscapes"
    #
    # openstudiolandscapes_base = input(f"Install base dir ({default_openstudiolandscapes_base}): ".strip()) or default_openstudiolandscapes_base
    # openstudiolandscapes_subdir = input(f"Install sub dir ({default_openstudiolandscapes_subdir}): ".strip()) or default_openstudiolandscapes_subdir
    # OPENSTUDIOLANDSCAPES_DIR = pathlib.Path(openstudiolandscapes_base, openstudiolandscapes_subdir).expanduser()
    #
    # # openstudiolandscapes_base: str = input("OpenStudiolandscapes base directory: ")
    # # OPENSTUDIOLANDSCAPES_BASE: pathlib.Path = pathlib.Path("~/git/repos")
    # # OPENSTUDIOLANDSCAPES_SUFFIX: str = "OpenStudioLandscapes"
    # # OPENSTUDIOLANDSCAPES_DIR: pathlib.Path = OPENSTUDIOLANDSCAPES_BASE / OPENSTUDIOLANDSCAPES_SUFFIX
    # print(f"(Press Enter to continue with the default: {OPENSTUDIOLANDSCAPES_BASE.as_posix()})")

    print("".center(_get_terminal_size()[0], "#"))
    print(" OPENSTUDIOLANDSCAPES INSTALLER ".center(_get_terminal_size()[0], "#"))

    script_run(
        sudo=False,
        script=script_initial_checks(
            docker_user=getuser()
        ),
    )

    print(" INSTALL DIRECTORY ".center(_get_terminal_size()[0], "#"))
    print("(Press Enter to continue with the defaults)")

    OPENSTUDIOLANDSCAPES_DIR = None

    while OPENSTUDIOLANDSCAPES_DIR is None:
        default_openstudiolandscapes_base = "~/git/repos"
        default_openstudiolandscapes_subdir = "OpenStudioLandscapes"

        openstudiolandscapes_base = pathlib.Path(input(f"Install base dir ({default_openstudiolandscapes_base}): ".strip()) or default_openstudiolandscapes_base)

        if not openstudiolandscapes_base.expanduser().is_absolute():
            print(f"ERROR: Directory {openstudiolandscapes_base.as_posix()} is not absolute (~ is allowed).")
            continue
        if not openstudiolandscapes_base.expanduser().exists():
            print(f"ERROR: Directory {openstudiolandscapes_base.as_posix()} does not exist. Create it first (`mkdir -p {openstudiolandscapes_base}`) or choose a different one.")
            continue
        if openstudiolandscapes_base.expanduser().is_file():
            print(f"ERROR: Install Directory {openstudiolandscapes_base.as_posix()} is a file. Cannot continue.")
            continue

        try:
            probe = pathlib.Path(openstudiolandscapes_base / ".openstudiolandscapes_probe").expanduser()
            probe.mkdir(parents=True, exist_ok=True)
            probe.rmdir()
            del probe
        except Exception as e:
            print(f"ERROR: Unable to write to {openstudiolandscapes_base.as_posix()}: {e}")
            print(f"Make sure we have write permissions to `{openstudiolandscapes_base.as_posix()}` so that we can create a subdirectory.")
            print(f"i.e `sudo chown -R {getuser()}: {openstudiolandscapes_base.as_posix()}`.")
            continue

        openstudiolandscapes_subdir = input(f"Install sub dir ({default_openstudiolandscapes_subdir}): ".strip()) or default_openstudiolandscapes_subdir
        # Todo:
        #  - [ ] Maybe some more checks here
        OPENSTUDIOLANDSCAPES_DIR = pathlib.Path(openstudiolandscapes_base, openstudiolandscapes_subdir).expanduser()


    # if bool(input_):
    #     OPENSTUDIOLANDSCAPES_DIR = pathlib.Path(install_dir_base, OPENSTUDIOLANDSCAPES_SUFFIX).expanduser()
    # else:
    #     OPENSTUDIOLANDSCAPES_DIR = OPENSTUDIOLANDSCAPES_DIR.expanduser()

    print("".center(_get_terminal_size()[0], "#"))
    print(f"Install Directory is: {OPENSTUDIOLANDSCAPES_DIR.as_posix()}")
    print("".center(_get_terminal_size()[0], "#"))

    result = script_run(
        sudo=True,
        script=script_disable_unattended_upgrades(),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=True,
        script=script_prep(),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_clone_openstudiolandscapes(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=True,
        script=script_install_python(),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=True,
        script=script_install_docker(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
            docker_user=getuser(),
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_install_openstudiolandscapes(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=True,
        script=script_etc_hosts(),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_harbor_prepare(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_harbor_up(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_harbor_init(),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_harbor_down(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    # result = script_run(
    #     sudo=False,
    #     script=script_init_pihole(),
    # )
    #
    # if result:
    #     sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_add_alias(
            openstudiolandscapes_repo_dir=OPENSTUDIOLANDSCAPES_DIR,
        ),
    )

    if result:
        sys.exit(1)

    result = script_run(
        sudo=False,
        script=script_reboot(),
    )

    if result:
        sys.exit(1)

