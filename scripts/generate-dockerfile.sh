#!/bin/bash
# Script to generate Dockerfiles from templates

set -e

COMPONENT=$1
ENV=${2:-development}

# Check arguments
if [ -z "$COMPONENT" ]; then
  echo "Usage: ./scripts/generate-dockerfile.sh <component> [environment]"
  echo "Example: ./scripts/generate-dockerfile.sh model production"
  echo "Components: model, frontend, backend"
  echo "Environments: development (default), production"
  exit 1
fi

# Load versions
if [ -f "./docker/image-versions.env" ]; then
  source ./docker/image-versions.env
else
  echo "Error: docker/image-versions.env not found. Run scripts/parse-versions.js first."
  exit 1
fi

# Set environment-specific variables
if [ "$ENV" == "production" ]; then
  CREATE_USER=true
  INCLUDE_HEALTHCHECK=true
  USE_VENV=true
  BUILD_FOR_PRODUCTION=true
  
  # Environment-specific system dependencies
  MODEL_SYSTEM_DEPENDENCIES="build-essential curl wget"
  FRONTEND_SYSTEM_DEPENDENCIES="curl"
  BACKEND_SYSTEM_DEPENDENCIES="curl"
else
  CREATE_USER=false
  INCLUDE_HEALTHCHECK=false
  USE_VENV=true
  BUILD_FOR_PRODUCTION=false
  
  # Development system dependencies
  MODEL_SYSTEM_DEPENDENCIES="gcc"
  FRONTEND_SYSTEM_DEPENDENCIES=""
  BACKEND_SYSTEM_DEPENDENCIES=""
fi

# Set component-specific variables
if [ "$COMPONENT" == "model" ]; then
  TEMPLATE="./docker/templates/model.Dockerfile.template"
  if [ "$ENV" == "production" ]; then
    OUTPUT="./model/Dockerfile.prod"
  else
    OUTPUT="./model/Dockerfile"
  fi
  PORT=8000
  REQUIREMENTS_PATH="."
  APP_PATH="."
  SYSTEM_DEPENDENCIES="$MODEL_SYSTEM_DEPENDENCIES"
  START_COMMAND='["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]'
  
elif [ "$COMPONENT" == "frontend" ]; then
  TEMPLATE="./docker/templates/frontend.Dockerfile.template"
  if [ "$ENV" == "production" ]; then
    OUTPUT="./frontend/Dockerfile.prod"
    PORT=80
    START_COMMAND='["npm", "run", "serve"]'
  else
    OUTPUT="./frontend/Dockerfile"
    PORT=3000
    START_COMMAND='["npm", "start"]'
  fi
  PACKAGE_PATH="."
  APP_PATH="."
  SYSTEM_DEPENDENCIES="$FRONTEND_SYSTEM_DEPENDENCIES"
  
elif [ "$COMPONENT" == "backend" ]; then
  TEMPLATE="./docker/templates/backend.Dockerfile.template"
  if [ "$ENV" == "production" ]; then
    OUTPUT="./backend/Dockerfile.prod"
  else
    OUTPUT="./backend/Dockerfile"
  fi
  PORT=4000
  PACKAGE_PATH="."
  APP_PATH="."
  SYSTEM_DEPENDENCIES="$BACKEND_SYSTEM_DEPENDENCIES"
  START_COMMAND='["node", "server.js"]'
  
else
  echo "Error: Unknown component '$COMPONENT'"
  echo "Supported components: model, frontend, backend"
  exit 1
fi

# Check if template exists
if [ ! -f "$TEMPLATE" ]; then
  echo "Error: Template not found: $TEMPLATE"
  exit 1
fi

# Create temporary file with variables substituted
TMP_FILE=$(mktemp)
cat "$TEMPLATE" > "$TMP_FILE"

# Replace variables in the template
sed -i.bak "s|\${PYTHON_VERSION}|$PYTHON_VERSION|g" "$TMP_FILE"
sed -i.bak "s|\${NODE_VERSION}|$NODE_VERSION|g" "$TMP_FILE"
sed -i.bak "s|\${SYSTEM_DEPENDENCIES}|$SYSTEM_DEPENDENCIES|g" "$TMP_FILE"
sed -i.bak "s|\${CREATE_USER}|$CREATE_USER|g" "$TMP_FILE"
sed -i.bak "s|\${USE_VENV}|$USE_VENV|g" "$TMP_FILE"
sed -i.bak "s|\${REQUIREMENTS_PATH}|$REQUIREMENTS_PATH|g" "$TMP_FILE"
sed -i.bak "s|\${PACKAGE_PATH}|$PACKAGE_PATH|g" "$TMP_FILE"
sed -i.bak "s|\${APP_PATH}|$APP_PATH|g" "$TMP_FILE"
sed -i.bak "s|\${PORT}|$PORT|g" "$TMP_FILE"
sed -i.bak "s|\${INCLUDE_HEALTHCHECK}|$INCLUDE_HEALTHCHECK|g" "$TMP_FILE"
sed -i.bak "s|\${BUILD_FOR_PRODUCTION}|$BUILD_FOR_PRODUCTION|g" "$TMP_FILE"
sed -i.bak "s|\${START_COMMAND}|$START_COMMAND|g" "$TMP_FILE"

# Ensure output directory exists
mkdir -p $(dirname "$OUTPUT")

# Move the processed file to the output location
mv "$TMP_FILE" "$OUTPUT"
rm -f "$TMP_FILE.bak"

echo "✅ Generated $OUTPUT from template"

# If this is for the china-growth-game model, also generate that Dockerfile
if [ "$COMPONENT" == "model" ] && [ "$ENV" == "development" ]; then
  CHINA_OUTPUT="./china-growth-game/docker/Dockerfile.economic-model"
  
  # Create a simplified version for china-growth-game
  cat > "$CHINA_OUTPUT" << EOF
# Auto-generated from template - DO NOT EDIT DIRECTLY
FROM python:${PYTHON_VERSION}-slim

WORKDIR /app

COPY economic-model/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY economic-model/ .

ENV PYTHONPATH=/app

EXPOSE 8000

# Run the application directly
CMD ["python", "app.py"]
EOF

  echo "✅ Generated $CHINA_OUTPUT"
fi
