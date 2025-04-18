#!/usr/bin/env node

/**
 * Version Validation Script
 *
 * This script validates that versions are consistent across the codebase.
 * It can be run in CI/CD pipelines to ensure version integrity.
 *
 * Usage: node scripts/validate-versions.js
 */

const fs = require('fs');
const path = require('path');
const versions = require('../version-management');

// Files to validate
const FILES_TO_VALIDATE = [
  'docker/image-versions.env',
  'backend/Dockerfile',
  'frontend/Dockerfile',
  'model/Dockerfile',
  'backend/package.json',
  'frontend/package.json',
  'china-growth-game/package.json',
  'model/requirements.txt',
  'china-growth-game/economic-model/requirements.txt',
  'docs/version-management.md',
  'readme.md'
];

// Validation rules
const VALIDATION_RULES = [
  // Docker image versions
  {
    file: 'docker/image-versions.env',
    patterns: [
      { regex: new RegExp(`NODE_VERSION=${versions.core.node}`), message: 'Node.js version mismatch' },
      { regex: new RegExp(`PYTHON_VERSION=${versions.core.python}`), message: 'Python version mismatch' },
      { regex: new RegExp(`FRONTEND_VERSION=${versions.docker.frontend}`), message: 'Frontend version mismatch' },
      { regex: new RegExp(`BACKEND_VERSION=${versions.docker.backend}`), message: 'Backend version mismatch' },
      { regex: new RegExp(`MODEL_VERSION=${versions.docker.model}`), message: 'Model version mismatch' }
    ]
  },

  // Dockerfiles
  {
    file: 'backend/Dockerfile',
    patterns: [
      { regex: new RegExp(`ARG NODE_VERSION=${versions.core.node}`), message: 'Node.js version mismatch in backend Dockerfile' }
    ]
  },
  {
    file: 'frontend/Dockerfile',
    patterns: [
      { regex: new RegExp(`ARG NODE_VERSION=${versions.core.node}`), message: 'Node.js version mismatch in frontend Dockerfile' }
    ]
  },
  {
    file: 'model/Dockerfile',
    patterns: [
      { regex: new RegExp(`ARG PYTHON_VERSION=${versions.core.python}`), message: 'Python version mismatch in model Dockerfile' }
    ]
  },

  // Package.json files
  {
    file: 'backend/package.json',
    jsonValidations: [
      { path: 'dependencies.express', value: versions.backend.express, message: 'Express version mismatch in backend' },
      { path: 'dependencies["socket.io"]', value: versions.backend.socketIo, message: 'Socket.IO version mismatch in backend' },
      { path: 'dependencies["aws-sdk"]', value: versions.backend.awsSdk, message: 'AWS SDK version mismatch in backend' }
    ]
  },
  {
    file: 'frontend/package.json',
    jsonValidations: [
      { path: 'dependencies.react', value: versions.frontend.react, message: 'React version mismatch in frontend' },
      { path: 'dependencies["@mui/material"]', value: versions.frontend.materialUi, message: 'Material UI version mismatch in frontend' },
      { path: 'dependencies["chart.js"]', value: versions.frontend.chartJs, message: 'Chart.js version mismatch in frontend' }
    ]
  },

  // Python requirements
  {
    file: 'model/requirements.txt',
    patterns: [
      { regex: new RegExp(`fastapi==${versions.model.fastapi}`), message: 'FastAPI version mismatch in model requirements' },
      { regex: new RegExp(`uvicorn==${versions.model.uvicorn}`), message: 'Uvicorn version mismatch in model requirements' },
      { regex: new RegExp(`numpy==${versions.model.numpy}`), message: 'NumPy version mismatch in model requirements' },
      { regex: new RegExp(`pandas==${versions.model.pandas}`), message: 'Pandas version mismatch in model requirements' }
    ]
  }
];

// Main function
async function main() {
  console.log('🔍 Validating version consistency across the codebase...');

  let errors = 0;

  // Check if all files exist
  for (const file of FILES_TO_VALIDATE) {
    const fullPath = path.join(process.cwd(), file);
    if (!fs.existsSync(fullPath)) {
      console.error(`❌ File not found: ${file}`);
      errors++;
    }
  }

  // Validate each file against rules
  for (const rule of VALIDATION_RULES) {
    const fullPath = path.join(process.cwd(), rule.file);

    if (!fs.existsSync(fullPath)) {
      continue; // Skip if file doesn't exist (already reported)
    }

    // Read file content
    const content = fs.readFileSync(fullPath, 'utf8');

    // Check patterns
    if (rule.patterns) {
      for (const pattern of rule.patterns) {
        if (!pattern.regex.test(content)) {
          console.error(`❌ ${pattern.message} in ${rule.file}`);
          errors++;
        }
      }
    }

    // Check JSON validations
    if (rule.jsonValidations) {
      try {
        const json = JSON.parse(content);

        for (const validation of rule.jsonValidations) {
          // Navigate to the nested property
          const path = validation.path;
          let value;

          // Handle paths with bracket notation like dependencies["socket.io"]
          if (path.includes('[')) {
            // Use Function constructor to safely evaluate the path
            // This is a common pattern for accessing nested properties with special characters
            try {
              value = new Function('obj', `return obj.${path}`)(json);
            } catch (e) {
              console.error(`❌ Error accessing path ${path} in ${rule.file}: ${e.message}`);
              errors++;
              continue;
            }
          } else {
            // Handle simple dot notation
            const parts = path.split('.');
            value = json;

            for (const part of parts) {
              value = value[part];
              if (value === undefined) break;
            }
          }

          if (value !== validation.value) {
            console.error(`❌ ${validation.message} in ${rule.file}: expected ${validation.value}, got ${value}`);
            errors++;
          }
        }
      } catch (error) {
        console.error(`❌ Error parsing JSON in ${rule.file}: ${error.message}`);
        errors++;
      }
    }
  }

  // Report results
  if (errors === 0) {
    console.log('✅ All version validations passed!');
    process.exit(0);
  } else {
    console.error(`❌ Found ${errors} version inconsistencies`);
    process.exit(1);
  }
}

// Run the script
main().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});
