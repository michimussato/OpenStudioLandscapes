FROM michimussato/base_image:latest AS dagster_dev
LABEL authors="michimussato@gmail.com"

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG DAGSTER_WORKSPACE="/dagster"
ARG DAGSTER_HOME="/dagster/materializations"

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

WORKDIR ${DAGSTER_WORKSPACE}
COPY ./config/workspace.yaml .

WORKDIR ${DAGSTER_HOME}
COPY ./config/materializations/dagster.yaml .

WORKDIR ${DAGSTER_WORKSPACE}

ENTRYPOINT ["dagster", "dev"]
CMD []
