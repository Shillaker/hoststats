#!/bin/bash

export VERSION=$(cat VERSION)

# Run dist tests in client container
docker-compose -f docker-compose-dev.yml \
    restart \
    target-one \
    target-two \
    target-three

