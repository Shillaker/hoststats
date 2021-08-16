#!/bin/bash

set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_ROOT="${THIS_DIR}/.."

export DOCKER_BUILDKIT=1

pushd ${PROJ_ROOT} >> /dev/null

# Run dist tests in client container
docker-compose run --rm client nosetests hoststats.disttest --nocapture

popd >> /dev/null
