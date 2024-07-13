#!/bin/sh
# Resolve internal dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(dirname "$0")/../"

echo "Installing internal dependencies..."

python3 -m pip install -e .'[test]'

# Setup frontend and install Playwright
cd frontend

yarn

../script/setup-playwright.sh
