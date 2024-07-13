#!/bin/sh
# Setup pre-commit

# Stop on errors
set -e

yes | npx playwright install-deps
npx playwright install
