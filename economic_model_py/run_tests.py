#!/usr/bin/env python
"""
Test runner for the China Growth Game economic model.

This script runs all the unit tests for the economic model.
"""

import unittest
import sys
import os

def run_tests():
    """Run all unit tests for the economic model."""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the parent directory to the Python path
    parent_dir = os.path.dirname(script_dir)
    sys.path.insert(0, parent_dir)
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        os.path.join(script_dir, 'economic_model_py', 'economic_model', 'tests'),
        pattern='test_*.py'
    )
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return non-zero exit code if tests failed
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
