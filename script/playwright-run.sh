#!/bin/sh
set -e

cd "$(dirname "$0")/../frontend"

# Check if the first argument is --update-snapshots
if [ "$1" = "--update-snapshots" ]; then
    # If --update-snapshots is passed, append it to the yarn command
    echo "Updating snapshots..."
    yarn build-prod
    yarn concurrently "yarn playwright-server" "yarn playwright-cicd --update-snapshots" --kill-others --success first
else
    # If no arguments or different arguments are passed, just run the command without --update-snapshots
    yarn build-prod
    yarn concurrently "yarn playwright-server" "yarn playwright-cicd" --kill-others --success first
fi
