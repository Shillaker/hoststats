#!/bin/bash

export VERSION=$(cat VERSION)

# Run dist tests in client container
docker-compose run --rm client nosetests hoststats.disttest --nocapture

# Print out all the logs
docker-compose logs
