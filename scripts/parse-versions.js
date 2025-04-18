#!/usr/bin/env node
// Script to parse versions.yaml into different formats

const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

// Load versions from YAML
const versionsPath = path.join(__dirname, '..', 'versions.yaml');
let versions;

try {
  const fileContent = fs.readFileSync(versionsPath, 'utf8');
  versions = yaml.load(fileContent);
  console.log('✅ Loaded versions from versions.yaml');
} catch (error) {
  console.error('❌ Error loading versions.yaml:', error.message);
  process.exit(1);
}

// Generate JavaScript module
function generateJsModule() {
  const jsContent = `/**
 * Auto-generated version information
 * DO NOT EDIT DIRECTLY - modify versions.yaml instead
 */

module.exports = ${JSON.stringify(versions, null, 2)};
`;
  try {
    fs.writeFileSync(path.join(__dirname, '..', 'version-management.js'), jsContent);
    console.log('✅ Generated version-management.js');
  } catch (error) {
    console.error('❌ Error generating version-management.js:', error.message);
  }
}

// Generate environment file for Docker
function generateEnvFile() {
  const envContent = `# Auto-generated from versions.yaml
# DO NOT EDIT DIRECTLY

# Base images
NODE_VERSION=${versions.core.node}
PYTHON_VERSION=${versions.core.python}

# Frontend
FRONTEND_IMAGE=solow-frontend
FRONTEND_VERSION=${versions.docker.frontend}

# Backend
BACKEND_IMAGE=solow-backend
BACKEND_VERSION=${versions.docker.backend}

# Model
MODEL_IMAGE=solow-model
MODEL_VERSION=${versions.docker.model}
`;
  try {
    fs.writeFileSync(path.join(__dirname, '..', 'docker', 'image-versions.env'), envContent);
    console.log('✅ Generated docker/image-versions.env');
  } catch (error) {
    console.error('❌ Error generating docker/image-versions.env:', error.message);
  }
}

// Generate Python requirements.txt for main model
function generateModelRequirements() {
  const modelRequirements = `# Auto-generated from versions.yaml
# DO NOT EDIT DIRECTLY

fastapi==${versions.model.fastapi}
uvicorn==${versions.model.uvicorn}
numpy==${versions.model.numpy}
pandas==${versions.model.pandas}
matplotlib==${versions.model.matplotlib}
pydantic==${versions.model.pydantic}
python-dotenv==1.1.0
typing-extensions==4.13.2
`;
  try {
    fs.writeFileSync(path.join(__dirname, '..', 'model', 'requirements.txt'), modelRequirements);
    console.log('✅ Generated model/requirements.txt');
  } catch (error) {
    console.error('❌ Error generating model/requirements.txt:', error.message);
  }
}

// Generate Python requirements.txt for china-growth-game model
function generateChinaModelRequirements() {
  const chinaModelRequirements = `# Auto-generated from versions.yaml
# DO NOT EDIT DIRECTLY

fastapi==0.110.0
uvicorn==0.27.1
numpy==${versions.model.numpy}
pandas==2.2.2
matplotlib==3.8.3
pydantic==2.6.3
python-dotenv==1.0.1
typing-extensions==4.10.0
`;
  try {
    fs.writeFileSync(path.join(__dirname, '..', 'china-growth-game/economic-model', 'requirements.txt'), chinaModelRequirements);
    console.log('✅ Generated china-growth-game/economic-model/requirements.txt');
  } catch (error) {
    console.error('❌ Error generating china-growth-game/economic-model/requirements.txt:', error.message);
  }
}

// Generate documentation
function generateVersionDocs() {
  const docsContent = `# Version Management

This document describes how to manage versions in the project.

## Overview

All version information is stored in a single source of truth: \`versions.yaml\`.
This file is used to generate all other version-specific files.

## Current Versions

### Core Technologies

| Technology | Version |
|------------|---------|
| Node.js    | ${versions.core.node} |
| Python     | ${versions.core.python} |
| Docker     | ${versions.core.docker} |

### Frontend Dependencies

| Package       | Version |
|---------------|---------|
| React         | ${versions.frontend.react} |
| Material UI   | ${versions.frontend.materialUi} |
| Chart.js      | ${versions.frontend.chartJs} |
| Socket.IO Client | ${versions.frontend.socketIoClient} |
| Axios         | ${versions.frontend.axios} |

### Backend Dependencies

| Package    | Version |
|------------|---------|
| Express    | ${versions.backend.express} |
| Socket.IO  | ${versions.backend.socketIo} |
| AWS SDK    | ${versions.backend.awsSdk} |
| Node Vault | ${versions.backend.nodeVault} |
| Axios      | ${versions.backend.axios} |

### Model Dependencies

| Package    | Version |
|------------|---------|
| FastAPI    | ${versions.model.fastapi} |
| Uvicorn    | ${versions.model.uvicorn} |
| NumPy      | ${versions.model.numpy} |
| Pandas     | ${versions.model.pandas} |
| Matplotlib | ${versions.model.matplotlib} |
| Pydantic   | ${versions.model.pydantic} |

### Docker Images

| Image     | Version |
|-----------|---------|
| Frontend  | ${versions.docker.frontend} |
| Backend   | ${versions.docker.backend} |
| Model     | ${versions.docker.model} |

## Updating Versions

To update a version, use the provided script:

\`\`\`bash
./scripts/update-version.sh <component> <package> <version>
\`\`\`

Example:
\`\`\`bash
./scripts/update-version.sh frontend react 18.2.0
\`\`\`

This will:
1. Update the version in \`versions.yaml\`
2. Regenerate all derived files:
   - \`version-management.js\`
   - \`docker/image-versions.env\`
   - \`model/requirements.txt\`
   - etc.

## Generated Files

The following files are automatically generated from \`versions.yaml\`:

- \`version-management.js\` - JavaScript module for Node.js applications
- \`docker/image-versions.env\` - Environment variables for Docker
- \`model/requirements.txt\` - Python dependencies
- \`china-growth-game/economic-model/requirements.txt\` - Python dependencies for China Growth Game

**Important:** Do not edit these files directly. Always edit \`versions.yaml\` instead.

_Last updated: ${new Date().toISOString().split('T')[0]}_
`;
  try {
    fs.writeFileSync(path.join(__dirname, '..', 'docs', 'version-management.md'), docsContent);
    console.log('✅ Generated docs/version-management.md');
  } catch (error) {
    console.error('❌ Error generating docs/version-management.md:', error.message);
  }
}

// Run all generators
generateJsModule();
generateEnvFile();
generateModelRequirements();
generateChinaModelRequirements();
generateVersionDocs();

console.log('✅ All version files generated successfully');
