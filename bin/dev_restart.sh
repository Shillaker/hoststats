#!/bin/bash

export VERSION=$(cat VERSION)

# Restart the target containers
docker-compose -f docker-compose-dev.yml \
    restart \
    target-one \
    target-two \
    target-three

