FROM python:3.8.13-slim-bullseye

RUN apt-get update
RUN apt-get -y install build-essential libsqlcipher-dev libsqlite3-dev curl
ADD ./mosip_token_seeder/requirements.txt /seeder/mosip_token_seeder/requirements.txt
RUN pip3 install -r /seeder/mosip_token_seeder/requirements.txt

ARG container_user=mosip
ARG container_user_group=mosip
ARG container_user_uid=1001
ARG container_user_gid=1001

RUN groupadd -g ${container_user_gid} ${container_user_group} \
&& useradd -mN -u ${container_user_uid} -G ${container_user_group} -s /bin/bash ${container_user}

RUN chown -R ${container_user}:${container_user_group} /seeder

USER ${container_user}
ADD --chown=${container_user}:${container_user_group} . /seeder
WORKDIR /seeder

ENV TOKENSEEDER_ROOT__PID_GREP_NAME='gunicorn'
ENV TOKENSEEDER_GUNICORN__WORKERS=4
ENV TOKENSEEDER_GUNICORN__MAX_REQUESTS=10000
ENV TOKENSEEDER_GUNICORN__TIMEOUT=5
ENV TOKENSEEDER_GUNICORN__KEEP_ALIVE=5
ENV TOKENSEEDER_DB__PRINT_PASSWORD_ON_STARTUP='false'

CMD TOKENSEEDER_DB__PASSWORD=$(python3 -m mosip_token_seeder.repository dbinit) gunicorn \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${TOKENSEEDER_GUNICORN__WORKERS} \
    --bind 0.0.0.0:8080 \
    --max-requests ${TOKENSEEDER_GUNICORN__MAX_REQUESTS} \
    --timeout ${TOKENSEEDER_GUNICORN__TIMEOUT} \
    --keep-alive ${TOKENSEEDER_GUNICORN__KEEP_ALIVE} \
    --access-logfile "-" \
    --error-logfile "-" \
    app:app