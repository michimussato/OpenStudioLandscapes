#!/bin/bash


if [ "$1" = "install" ]; then
    echo "Installing DeadlineClient (proxyconfig)...";

    mkdir -p /var/lib/Thinkbox/Deadline10

    ./DeadlineClient-${DEADLINE_VERSION}-linux-x64-installer.run \
    --mode unattended \
    --prefix /opt/Thinkbox/Deadline10 \
    --repositorydir /opt/Thinkbox/DeadlineRepository10 \
    --launcherdaemon false \
    --enable-components proxyconfig \
    --httpport 8888 \
    --enabletls false \
    --proxyalwaysrunning false \
    --blockautoupdateoverride NotBlocked

    mv -f /tmp/installbuilder_installer.log /opt/Thinkbox/Deadline10
    cat /opt/Thinkbox/Deadline10/installbuilder_installer.log

    exit 0;
fi;
