#!/usr/bin/env python
"""
Test runner script for the economic model.
Runs all tests and generates a coverage report.
"""

import os
import sys
import subprocess
import argparse

def run_tests(args):
    """Run the tests with the specified options."""
    # Base command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])
    
    # Add markers
    if args.unit:
        cmd.append("-m unit")
    elif args.integration:
        cmd.append("-m integration")
    elif args.benchmark:
        cmd.append("-m benchmark")
    elif args.api:
        cmd.append("-m api")
    
    # Add specific test files
    if args.test_file:
        cmd.append(args.test_file)
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode

def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for the economic model")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--benchmark", action="store_true", help="Run only benchmark tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("test_file", nargs="?", help="Specific test file to run")
    
    args = parser.parse_args()
    
    # Run the tests
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main())
