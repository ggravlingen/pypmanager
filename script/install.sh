#!/bin/sh
# Resolve internal dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(dirname "$0")/../"

# Install backend
echo "Installing backend"
python3 -m pip install -e .'[test]'

# Instasll frontend
echo "Installing frontend"
script/install-frontend.sh
