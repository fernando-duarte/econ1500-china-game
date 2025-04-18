#!/bin/bash
# Script to load Docker image versions for local development and CI

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load the versions from the environment file
if [ -f "$SCRIPT_DIR/image-versions.env" ]; then
  echo "Loading Docker image versions from $SCRIPT_DIR/image-versions.env"
  set -a  # automatically export all variables
  source "$SCRIPT_DIR/image-versions.env"
  set +a
else
  echo "Error: image-versions.env not found in $SCRIPT_DIR"
  exit 1
fi

# Validate that required variables are set
if [ -z "$NODE_VERSION" ] || [ -z "$PYTHON_VERSION" ] || \
   [ -z "$FRONTEND_IMAGE" ] || [ -z "$FRONTEND_VERSION" ] || \
   [ -z "$BACKEND_IMAGE" ] || [ -z "$BACKEND_VERSION" ] || \
   [ -z "$MODEL_IMAGE" ] || [ -z "$MODEL_VERSION" ]; then
  echo "Error: Missing required version variables"
  exit 1
fi

echo "Successfully loaded Docker image versions:"
echo "- Node.js: $NODE_VERSION"
echo "- Python: $PYTHON_VERSION"
echo "- Frontend: $FRONTEND_IMAGE:$FRONTEND_VERSION"
echo "- Backend: $BACKEND_IMAGE:$BACKEND_VERSION"
echo "- Model: $MODEL_IMAGE:$MODEL_VERSION" 