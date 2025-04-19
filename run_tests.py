#!/usr/bin/env python
"""
Test runner for the China Growth Game package.

This script discovers and runs all tests in the economic_model_py package.
It supports verbose output and coverage reporting.
"""

import unittest
import sys
import argparse
# Type hints would be used if we refactored this into functions

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run tests for the China Growth Game package.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Run tests with verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Generate coverage report')
    args = parser.parse_args()

    # Set verbosity level
    verbosity = 2 if args.verbose else 1

    # Discover and run all tests
    test_suite = unittest.defaultTestLoader.discover('economic_model_py/economic_model/tests')
    test_runner = unittest.TextTestRunner(verbosity=verbosity)

    # Run tests with coverage if requested
    if args.coverage:
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
            result = test_runner.run(test_suite)
            cov.stop()
            cov.save()
            print('\nCoverage report:')
            cov.report()
        except ImportError:
            print('\nCoverage package not installed. Run "pip install coverage" to enable coverage reporting.')
            result = test_runner.run(test_suite)
    else:
        result = test_runner.run(test_suite)

    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
