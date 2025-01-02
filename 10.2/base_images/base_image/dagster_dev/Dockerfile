FROM michimussato/base_image:latest AS dagster_dev
LABEL authors="michimussato@gmail.com"

ARG PYTHON_MAJ
ARG PYTHON_MIN
ENV PYTHON_MAJ=${PYTHON_MAJ}
ENV PYTHON_MIN=${PYTHON_MIN}

RUN python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

#WORKDIR /dagster
#COPY ./config/ .

ENTRYPOINT ["dagster", "dev", "--workspace", "/dagster/workspace.yaml", "--host", "0.0.0.0"]
