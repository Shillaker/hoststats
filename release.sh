#!/bin/bash

set -e

rm -rf dist/ build/

python3 -m build

ll dist/

python3 -m twine upload --repository host-stats dist/*

