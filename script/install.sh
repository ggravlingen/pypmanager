#!/bin/sh
# Resolve internal dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(dirname "$0")/../"

# Install backend using uv with lockfile
echo "Installing backend with uv"
uv sync --all-extras

# Install frontend
echo "Installing frontend"
script/install-frontend.sh
