FROM registry.altlinux.org/alt/alt:p11 AS base
LABEL version='0.1.0'

RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
<<EOF
set -e
mkdir --parents /var/cache/apt/archives/partial/ /var/lib/apt/lists/partial/
apt-get update
apt-get install -y glibc-pthread python3-module-pip git
EOF

WORKDIR /app

COPY swagger.yaml /app/swagger.yaml

ENV ADAPTER_SWAGGER_PATH=/app/swagger.yaml

CMD ["python3", "-m", "adapter.main"]


################
## Dev image  ##
################

FROM base AS dev
LABEL name='saltbox-filebrowser-adapter-dev' version='0.1.0'
WORKDIR /mnt/saltbox-filebrowser-adapter/
ENV DEV_MODE=1
VOLUME /mnt/saltbox-filebrowser-adapter/
VOLUME /mnt/saltbox-sdk/
ENV SALTBOX_SDK_SRC_PATH /mnt/saltbox-sdk/


################
## Main image ##
################

FROM base AS main
LABEL name='saltbox-filebrowser-adapter' version='0.1.0'
RUN \
  --mount=type=bind,target=/mnt/saltbox-filebrowser-adapter/,readwrite \
  --mount=type=cache,target=/root/.cache/pip/ \
  pip3 install -r /mnt/saltbox-filebrowser-adapter/local_requirements.txt \
  && pip3 install /mnt/saltbox-filebrowser-adapter/
