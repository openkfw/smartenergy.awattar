#!/bin/bash
set -e

export PROJECT=green_energy
CONTAINER_NAME="homeassistant_green_energy"

podman network create -d bridge $PROJECT || true

printf "\n>>> Building the Mock API image\n"
podman build -t mock-api ./mock_api

printf "\n>>> Removing running Mock API container\n"
podman rm -f mock-api || true

printf "\n>>> Starting Mock API container\n"
podman run -d --name mock-api \
--network $PROJECT \
-p 4000:4000 \
mock-api

printf "\n>>> Building a custom Home Assistant image\n"
podman build -t ha-custom .

printf "\n>>> Removing running Home Assistant container\n"
podman rm -f $CONTAINER_NAME || true

printf "\n>>> Starting Home Assistant container\n"
podman run -d --name $CONTAINER_NAME \
--network $PROJECT \
--cap-add=CAP_NET_RAW,CAP_NET_BIND_SERVICE \
--restart=unless-stopped \
-p 8123:8123 \
-v /etc/localtime:/etc/localtime:ro \
ha-custom

printf "\n>>> Running containers:\n"
podman ps

printf "\n>>> Downloading HACS\n"
sleep 10
podman exec $CONTAINER_NAME sh -c "cd /config && wget -O - https://get.hacs.xyz | bash -"

printf "\n>>> Restarting HA container to enable HACS\n"
podman restart $CONTAINER_NAME

printf "\n>>> You can open Home Assistant in your browser at: http://127.0.0.1:8123"
