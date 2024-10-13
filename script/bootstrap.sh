#!/bin/sh
# Resolve internal dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(dirname "$0")/../"

./script/install.sh
./script/setup-playwright.sh
