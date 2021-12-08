#!/bin/bash

export VERSION=$(cat VERSION)

# Run dist tests in client container
docker-compose run --rm client nosetests hoststats.disttest --nocapture

RETURN_CODE=$?

if [[ $RETURN_CODE == 0 ]]; then
    echo ""
    echo "Dist tests passed"
    echo ""
else
    # Print out all the logs
    docker-compose logs

    echo ""
    echo "Dist tests failed"
    echo ""
fi

exit $RETURN_CODE
