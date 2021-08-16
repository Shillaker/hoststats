#!/bin/bash
set -e
set -x

export VERSION=$(cat VERSION)
TAG=shillaker/hoststats:${VERSION}

export DOCKER_BUILDKIT=1
docker build -t ${TAG} --build-arg VERSION=${VERSION} .

docker push ${TAG}

