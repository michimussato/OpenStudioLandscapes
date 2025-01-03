FROM michimussato/base_image:latest AS dagster_dev
LABEL authors="michimussato@gmail.com"

ARG PYTHON_MAJ
ARG PYTHON_MIN

ENV DAGSTER_HOME="/dagster/materializations"

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

WORKDIR /dagster
COPY ./config/workspace.yaml .

WORKDIR /dagster/materializations
COPY ./config/materializations/dagster.yaml .

WORKDIR /dagster

ENTRYPOINT ["dagster", "dev"]
CMD ["--workspace", "/dagster/workspace.yaml", "--host", "0.0.0.0"]
