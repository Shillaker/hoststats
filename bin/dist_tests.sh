#!/bin/bash

export VERSION=$(cat VERSION)

# Run dist tests in client container
docker-compose run --rm client nosetests hoststats.disttest --nocapture

RETURN_CODE=$?

# Print out all the logs
docker-compose logs

exit $RETURN_CODE
