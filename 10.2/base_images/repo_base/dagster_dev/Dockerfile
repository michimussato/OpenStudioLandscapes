FROM michimussato/repo_base:latest AS dagster_dev
LABEL authors="michimussato@gmail.com"

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG PYTHON_PAT
ENV PYTHON_MAJ=${PYTHON_MAJ}
ENV PYTHON_MIN=${PYTHON_MIN}
ENV PYTHON_PAT=${PYTHON_PAT}

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

#WORKDIR /dagster
#COPY ./config/ .

ENTRYPOINT ["dagster", "dev", "--workspace", "/dagster/workspace.yaml", "--host", "0.0.0.0"]
