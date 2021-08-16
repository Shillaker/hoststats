#!/bin/bash
set -e

# Git tag
VERSION=$(cat VERSION)
git tag --force v${VERSION}
git push --force origin v${VERSION}

