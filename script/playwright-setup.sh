#!/bin/sh
# Setup pre-commit

# Stop on errors
set -e

cd "$(dirname "$0")/../"

cd frontend
yarn playwright install-deps
yarn playwright install
