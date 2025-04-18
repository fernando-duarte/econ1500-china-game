#!/bin/bash
# Script to update a specific version in versions.yaml

set -e

COMPONENT=$1
PACKAGE=$2
VERSION=$3

if [ -z "$COMPONENT" ] || [ -z "$PACKAGE" ] || [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/update-version.sh <component> <package> <version>"
  echo "Example: ./scripts/update-version.sh frontend react 18.2.0"
  exit 1
fi

# Check if yq is installed
if ! command -v yq &> /dev/null; then
  echo "Error: yq is not installed. Please install it first."
  echo "On macOS: brew install yq"
  echo "On Linux: wget https://github.com/mikefarah/yq/releases/download/v4.30.8/yq_linux_amd64 -O /usr/local/bin/yq && chmod +x /usr/local/bin/yq"
  exit 1
fi

# Check if versions.yaml exists
if [ ! -f "versions.yaml" ]; then
  echo "Error: versions.yaml not found in the current directory."
  exit 1
fi

# Update the version in YAML file using yq
yq -i ".${COMPONENT}.${PACKAGE} = \"${VERSION}\"" versions.yaml

echo "✅ Updated ${COMPONENT}.${PACKAGE} to version ${VERSION} in versions.yaml"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Error: Node.js is not installed. Please install it first."
  exit 1
fi

# Check if parse-versions.js exists
if [ ! -f "scripts/parse-versions.js" ]; then
  echo "Error: scripts/parse-versions.js not found."
  exit 1
fi

# Make sure the script is executable
chmod +x scripts/parse-versions.js

# Regenerate all version files
node scripts/parse-versions.js

echo "✅ All version files have been updated"
