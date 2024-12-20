FROM cgwire/cgwire:latest AS kitsu
# https://hub.docker.com/r/cgwire/cgwire
LABEL authors="michael"

#RUN tar -cvzf /var/lib/postgresql/14/main.tar.gz /var/lib/postgresql/14/main

WORKDIR /opt/zou
CMD ["/opt/zou/start_zou.sh"]
#ENTRYPOINT ["top", "-b"]

#root@kitsu-10-2:/opt/zou# cat start_zou.sh
##!/bin/bash
#
## create /var/run/postgresql
#. /usr/share/postgresql-common/init.d-functions
#create_socket_directory
#
#echo Running Zou...
#supervisord -c /etc/supervisord.conf


#root@kitsu-10-2:/opt/zou# cat init_zou.sh
##!/bin/bash
#export LC_ALL=C.UTF-8
#export LANG=C.UTF-8
#
#service postgresql start
#service redis-server start
#
#. /opt/zou/env/bin/activate
#
#zou upgrade-db
#zou init-data
#zou create-admin admin@example.com --password mysecretpassword
#
#service postgresql stop
#service redis-server stop
