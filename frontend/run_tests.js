#!/usr/bin/env node
/**
 * Test runner script for the React frontend.
 * Runs all tests and generates a coverage report.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse command line arguments
const argv = yargs(hideBin(process.argv))
  .option('verbose', {
    alias: 'v',
    type: 'boolean',
    description: 'Run tests with verbose output'
  })
  .option('coverage', {
    alias: 'c',
    type: 'boolean',
    description: 'Generate coverage report'
  })
  .option('watch', {
    alias: 'w',
    type: 'boolean',
    description: 'Watch for changes and rerun tests'
  })
  .option('component', {
    alias: 'comp',
    type: 'boolean',
    description: 'Run only component tests'
  })
  .option('context', {
    alias: 'ctx',
    type: 'boolean',
    description: 'Run only context tests'
  })
  .option('service', {
    alias: 's',
    type: 'boolean',
    description: 'Run only service tests'
  })
  .option('file', {
    alias: 'f',
    type: 'string',
    description: 'Specific test file to run'
  })
  .help()
  .alias('help', 'h')
  .argv;

/**
 * Run the tests with the specified options.
 * @param {Object} options - Test options
 * @returns {Promise<number>} - Exit code
 */
async function runTests(options) {
  // Base command
  const cmd = 'npx';
  const args = ['react-scripts', 'test'];
  
  // Add test environment variables
  const env = {
    ...process.env,
    CI: options.watch ? undefined : 'true'
  };
  
  // Add coverage
  if (options.coverage) {
    args.push('--coverage');
  }
  
  // Add watch mode
  if (options.watch) {
    args.push('--watchAll');
  }
  
  // Add test files
  if (options.file) {
    args.push(options.file);
  } else if (options.component) {
    args.push('src/components/__tests__');
  } else if (options.context) {
    args.push('src/contexts/__tests__');
  } else if (options.service) {
    args.push('src/services/__tests__');
  }
  
  // Run the tests
  console.log(`Running command: ${cmd} ${args.join(' ')}`);
  
  return new Promise((resolve) => {
    const testProcess = spawn(cmd, args, {
      stdio: 'inherit',
      shell: true,
      env
    });
    
    testProcess.on('close', (code) => {
      resolve(code);
    });
  });
}

/**
 * Main function
 */
async function main() {
  try {
    const exitCode = await runTests(argv);
    
    // Only exit if not in watch mode
    if (!argv.watch) {
      process.exit(exitCode);
    }
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

// Run the main function
main();
