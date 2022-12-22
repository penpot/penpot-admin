#!/usr/bin/env bash

set -x

REV=$(git rev-list --count HEAD)
DOCKER_CLI_EXPERIMENTAL=enabled
PLATFORM=${PENPOT_BUILD_PLATFORMS:-linux/amd64,linux/arm64,linux/arm/v7};
# PLATFORM=${PENPOT_BUILD_PLATFORMS:-linux/amd64};

DOCKER_IMAGE="penpotapp/admin";
OPTIONS="-t $DOCKER_IMAGE:v1.$REV";

IFS=", "
read -a TAGS <<< $PENPOT_BUILD_TAGS;

for element in "${TAGS[@]}"; do
    OPTIONS="$OPTIONS -t $DOCKER_IMAGE:$element";
done

docker buildx inspect penpot > /dev/null 2>&1;
docker run --privileged --rm tonistiigi/binfmt --install all

if [ $? -eq 1 ]; then
    docker buildx create --name=penpot-build --use
    docker buildx inspect --bootstrap > /dev/null 2>&1;
else
    docker buildx use penpot-build;
    docker buildx inspect --bootstrap  > /dev/null 2>&1;
fi

unset IFS;
docker buildx build --platform ${PLATFORM// /,} $OPTIONS -f Dockerfile "$@" .;
