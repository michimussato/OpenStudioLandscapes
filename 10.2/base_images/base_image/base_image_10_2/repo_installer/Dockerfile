
# AUTO-GENERATED
FROM michimussato/build_base_image_10_2:1736157622.6988559 AS build_repository_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

WORKDIR /installers

RUN deadline-wrapper-10-2              -vv              install-repository              --installer /installers/DeadlineRepository.run              --deadline-version 10.2.1.1              --prefix "/opt/Thinkbox/DeadlineRepository10"              --dbtype "MongoDB"              --dbhost mongodb-10-2              --dbport 21017              --dbname deadline10db

WORKDIR /opt/Thinkbox

ENTRYPOINT []
