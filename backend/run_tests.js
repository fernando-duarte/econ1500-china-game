#!/usr/bin/env node
/**
 * Test runner script for the Node.js backend.
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
  .option('unit', {
    alias: 'u',
    type: 'boolean',
    description: 'Run only unit tests'
  })
  .option('integration', {
    alias: 'i',
    type: 'boolean',
    description: 'Run only integration tests'
  })
  .option('e2e', {
    alias: 'e',
    type: 'boolean',
    description: 'Run only end-to-end tests'
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
  const args = ['mocha'];
  
  // Add verbosity
  if (options.verbose) {
    args.push('--verbose');
  }
  
  // Add coverage
  if (options.coverage) {
    args.unshift('nyc', '--reporter=lcov', '--reporter=text');
  }
  
  // Add test files
  if (options.file) {
    args.push(options.file);
  } else if (options.unit) {
    args.push('test/**/*.test.js', '!test/integration/**', '!test/e2e/**');
  } else if (options.integration) {
    args.push('test/integration/**/*.test.js');
  } else if (options.e2e) {
    args.push('test/e2e/**/*.test.js');
  } else {
    args.push('test/**/*.test.js');
  }
  
  // Run the tests
  console.log(`Running command: ${cmd} ${args.join(' ')}`);
  
  return new Promise((resolve) => {
    const testProcess = spawn(cmd, args, {
      stdio: 'inherit',
      shell: true
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
    process.exit(exitCode);
  } catch (error) {
    console.error('Error running tests:', error);
    process.exit(1);
  }
}

// Run the main function
main();
