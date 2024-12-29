#!/bin/sh
# Resolve all dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(dirname "$0")/.."

echo "Installing frontend..."

export CI=true && \
    corepack enable && \
    cd frontend && \
    yarn

# Build the frontend
yarn build-prod
