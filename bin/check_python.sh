#!/bin/bash

set -e

# Check all files
FILES_TO_CHECK=$(git ls-files -- "*.py")

# Run black
python3 -m black --check ${FILES_TO_CHECK}

# Run isort
python3 -m isort --profile black ${FILES_TO_CHECK}

# Run flake8
python3 -m flake8 ${FILES_TO_CHECK}

# Check for any git changes
git diff --exit-code
