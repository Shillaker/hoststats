#!/bin/bash

set -e

rm -rf dist/ build/

python3 -m build

python3 -m twine upload dist/*

