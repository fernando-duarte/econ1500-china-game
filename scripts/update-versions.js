#!/usr/bin/env node

/**
 * Version Update Script
 * 
 * This script updates version information across the codebase
 * based on the centralized version management file.
 * 
 * Usage: node scripts/update-versions.js
 */

const fs = require('fs');
const path = require('path');
const versions = require('../version-management');

// Paths to files that need version updates
const FILES = {
  // Docker files
  'docker/image-versions.env': updateDockerVersions,
  'backend/Dockerfile': updateBackendDockerfile,
  'frontend/Dockerfile': updateFrontendDockerfile,
  'model/Dockerfile': updateModelDockerfile,
  
  // Package files
  'backend/package.json': updateBackendPackage,
  'frontend/package.json': updateFrontendPackage,
  'china-growth-game/package.json': updateChinaGrowthGamePackage,
  
  // Python requirements
  'model/requirements.txt': updateModelRequirements,
  'china-growth-game/economic-model/requirements.txt': updateChinaModelRequirements,
  
  // Documentation
  'docs/version-management.md': updateVersionDocs,
  'readme.md': updateReadme,
};

// Main function
async function main() {
  console.log('🔄 Updating version information across the codebase...');
  
  for (const [filePath, updateFn] of Object.entries(FILES)) {
    try {
      const fullPath = path.join(process.cwd(), filePath);
      if (fs.existsSync(fullPath)) {
        await updateFn(fullPath);
        console.log(`✅ Updated ${filePath}`);
      } else {
        console.warn(`⚠️ File not found: ${filePath}`);
      }
    } catch (error) {
      console.error(`❌ Error updating ${filePath}:`, error.message);
    }
  }
  
  console.log('\n🎉 Version update complete!');
  console.log('📝 Remember to run tests and verify the changes before committing.');
}

// Update functions for each file type
function updateDockerVersions(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  
  content = content.replace(/NODE_VERSION=.+/, `NODE_VERSION=${versions.core.node}`);
  content = content.replace(/PYTHON_VERSION=.+/, `PYTHON_VERSION=${versions.core.python}`);
  content = content.replace(/FRONTEND_VERSION=.+/, `FRONTEND_VERSION=${versions.docker.frontend}`);
  content = content.replace(/BACKEND_VERSION=.+/, `BACKEND_VERSION=${versions.docker.backend}`);
  content = content.replace(/MODEL_VERSION=.+/, `MODEL_VERSION=${versions.docker.model}`);
  
  fs.writeFileSync(filePath, content);
}

function updateBackendDockerfile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(/ARG NODE_VERSION=.+/, `ARG NODE_VERSION=${versions.core.node}`);
  fs.writeFileSync(filePath, content);
}

function updateFrontendDockerfile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(/ARG NODE_VERSION=.+/, `ARG NODE_VERSION=${versions.core.node}`);
  fs.writeFileSync(filePath, content);
}

function updateModelDockerfile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  content = content.replace(/ARG PYTHON_VERSION=.+/, `ARG PYTHON_VERSION=${versions.core.python}`);
  fs.writeFileSync(filePath, content);
}

function updateBackendPackage(filePath) {
  const pkg = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  // Update dependencies
  pkg.dependencies.axios = versions.backend.axios;
  pkg.dependencies.express = versions.backend.express;
  pkg.dependencies['socket.io'] = versions.backend.socketIo;
  pkg.dependencies['node-vault'] = versions.backend.nodeVault;
  pkg.dependencies['aws-sdk'] = versions.backend.awsSdk;
  
  // Update version
  pkg.version = versions.docker.backend;
  
  fs.writeFileSync(filePath, JSON.stringify(pkg, null, 2) + '\n');
}

function updateFrontendPackage(filePath) {
  const pkg = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  // Update dependencies
  pkg.dependencies.react = versions.frontend.react;
  pkg.dependencies['react-dom'] = versions.frontend.react;
  pkg.dependencies['@mui/material'] = versions.frontend.materialUi;
  pkg.dependencies['@mui/icons-material'] = versions.frontend.materialUi;
  pkg.dependencies['chart.js'] = versions.frontend.chartJs;
  pkg.dependencies['socket.io-client'] = versions.frontend.socketIoClient;
  pkg.dependencies.axios = versions.frontend.axios;
  
  // Update version
  pkg.version = versions.docker.frontend;
  
  fs.writeFileSync(filePath, JSON.stringify(pkg, null, 2) + '\n');
}

function updateChinaGrowthGamePackage(filePath) {
  const pkg = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  // Update dependencies
  pkg.dependencies.express = versions.chinaGrowthGame.express;
  pkg.dependencies['@mui/material'] = versions.chinaGrowthGame.materialUi;
  pkg.dependencies['@mui/icons-material'] = versions.chinaGrowthGame.materialUi;
  pkg.dependencies['socket.io'] = versions.chinaGrowthGame.socketIo;
  pkg.dependencies['socket.io-client'] = versions.chinaGrowthGame.socketIo;
  pkg.dependencies['aws-sdk'] = versions.chinaGrowthGame.awsSdk;
  
  fs.writeFileSync(filePath, JSON.stringify(pkg, null, 2) + '\n');
}

function updateModelRequirements(filePath) {
  const requirements = [
    `fastapi==${versions.model.fastapi}`,
    `uvicorn==${versions.model.uvicorn}`,
    `numpy==${versions.model.numpy}`,
    `pandas==${versions.model.pandas}`,
    `matplotlib==${versions.model.matplotlib}`,
    `pydantic==${versions.model.pydantic}`,
    `python-dotenv==1.1.0`,
    `typing-extensions==4.13.2`
  ].join('\n');
  
  fs.writeFileSync(filePath, requirements);
}

function updateChinaModelRequirements(filePath) {
  // For the china-growth-game model, we keep the original versions
  // as they differ from the main model component
  const requirements = [
    `fastapi==0.110.0`,
    `uvicorn==0.27.1`,
    `numpy==${versions.model.numpy}`,
    `pandas==2.2.2`,
    `matplotlib==3.8.3`,
    `pydantic==2.6.3`,
    `python-dotenv==1.0.1`,
    `typing-extensions==4.10.0`
  ].join('\n');
  
  fs.writeFileSync(filePath, requirements);
}

function updateVersionDocs(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Update core technologies
  content = content.replace(/\| Node\.js\s+\| [^|]+\|/, `| Node.js    | ${versions.core.node} |`);
  content = content.replace(/\| Python\s+\| [^|]+\|/, `| Python     | ${versions.core.python} |`);
  
  // Update frontend dependencies
  content = content.replace(/\| React\s+\| [^|]+\|/, `| React         | ${versions.frontend.react} |`);
  content = content.replace(/\| Material UI\s+\| [^|]+\|/, `| Material UI   | ${versions.frontend.materialUi} |`);
  content = content.replace(/\| Chart\.js\s+\| [^|]+\|/, `| Chart.js      | ${versions.frontend.chartJs} |`);
  
  // Update backend dependencies
  content = content.replace(/\| Express\s+\| [^|]+\|/, `| Express    | ${versions.backend.express} |`);
  content = content.replace(/\| Socket\.IO\s+\| [^|]+\|/, `| Socket.IO  | ${versions.backend.socketIo} |`);
  
  // Update model dependencies
  content = content.replace(/\| FastAPI\s+\| [^|]+\|/, `| FastAPI    | ${versions.model.fastapi} |`);
  content = content.replace(/\| Uvicorn\s+\| [^|]+\|/, `| Uvicorn    | ${versions.model.uvicorn} |`);
  content = content.replace(/\| NumPy\s+\| [^|]+\|/, `| NumPy      | ${versions.model.numpy} |`);
  content = content.replace(/\| Pandas\s+\| [^|]+\|/, `| Pandas     | ${versions.model.pandas} |`);
  
  fs.writeFileSync(filePath, content);
}

function updateReadme(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Update technology stack section
  content = content.replace(/Node\.js [0-9.]+/, `Node.js ${versions.core.node}`);
  content = content.replace(/Python [0-9.]+/, `Python ${versions.core.python}`);
  content = content.replace(/React [0-9.]+/, `React ${versions.frontend.react}`);
  content = content.replace(/Material UI [0-9.]+/, `Material UI ${versions.frontend.materialUi}`);
  content = content.replace(/Express [0-9.]+/, `Express ${versions.backend.express}`);
  
  fs.writeFileSync(filePath, content);
}

// Run the script
main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});
