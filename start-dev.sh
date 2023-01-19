#!/bin/bash
set -e

CONTAINER_NAME="homeassistant_green_energy"
CONTAINER_ENGINE="${1:-podman}"
COMPOSE_ENGINE="${2:-podman-compose}"

printf "\n>>> Removing running Home Assistant\n"
$COMPOSE_ENGINE down || true

printf "\n>>> Starting Home Assistant\n"
$COMPOSE_ENGINE up -d --build

watch() {
    printf "\n>>> Watching folder $1/ for changes...\n"

    while [[ true ]]
    do
        files=`find $1 -type f \( -iname \*.py -o -iname \*.json \) -mtime -$2s`
        if [[ $files != "" ]] ; then
            printf "\n>>> Changed files: $files, restarting the Home Assistant\n"
            $CONTAINER_ENGINE restart $CONTAINER_NAME
        fi
        sleep $2
    done
}

watch "./custom_components/green_energy" 3
