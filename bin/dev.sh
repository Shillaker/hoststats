#!/bin/bash

export VERSION=$(cat VERSION)

# Start things up in the background. Do so in sequence so they don't trample on
# each other when reinstalling hoststats
docker-compose -f docker-compose-dev.yml up --no-recreate -d target-one
docker-compose -f docker-compose-dev.yml up --no-recreate -d target-two
docker-compose -f docker-compose-dev.yml up --no-recreate -d target-three

# Run dist tests in client container
docker-compose -f docker-compose-dev.yml run --rm client /bin/bash

