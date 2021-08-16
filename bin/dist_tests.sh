#!/bin/bash
set -e

export VERSION=$(cat VERSION)

# Run dist tests in client container
docker-compose run --rm client nosetests hoststats.disttest --nocapture
