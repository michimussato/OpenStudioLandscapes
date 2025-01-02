FROM michimussato/base_image_10_2:latest AS client_installer_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG DEADLINE_VERSION
ARG INSTALLERS_ROOT

ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV INSTALLERS_ROOT=$INSTALLERS_ROOT

WORKDIR /installers/Deadline-10.2.1.1-linux-installers

COPY /Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run .

RUN chmod a+x /installers/Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run

#RUN ["/installers/Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run", "--help"]
RUN ["/installers/Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run", "--prefix", "/opt/Thinkbox/Deadline10", "--repositorydir", "/opt/Thinkbox/DeadlineRepository10"]
#RUN "/installers/Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run --prefix /opt/Thinkbox/Deadline10 --repositorydir /opt/Thinkbox/DeadlineRepository10"

ENTRYPOINT []
