FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-2022-11-11

ARG container_user=mosip
ARG container_user_group=mosip
ARG container_user_uid=1001
ARG container_user_gid=1001
WORKDIR /home/${container_user}
RUN chown -R ${container_user}:${container_user} /home/${container_user}
USER ${container_user_uid}:${container_user_gid}

RUN pip3 install \
        pyjwt==2.6.0 \
        python-multipart==0.0.5 \
        cryptography==38.0.3
