"""
Tests for the error handling utilities.

This module contains tests for the custom exception classes and error handling utilities.
"""

import unittest
from economic_model_py.economic_model.utils.error_handling import (
    ModelError, CalculationError, ParameterError
)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling utilities."""

    def test_model_error_basic(self):
        """Test basic ModelError functionality."""
        # Create a simple ModelError
        error = ModelError("Test error message")
        
        # Check that the error message is correct
        self.assertEqual(str(error), "Test error message")
        
        # Check that the error has no details by default
        self.assertEqual(error.details, {})
        
    def test_model_error_with_details(self):
        """Test ModelError with details."""
        # Create a ModelError with details
        details = {"param1": "value1", "param2": 42}
        error = ModelError("Test error message", details=details)
        
        # Check that the error message is correct
        self.assertEqual(str(error), "Test error message")
        
        # Check that the details are correct
        self.assertEqual(error.details, details)
        
    def test_calculation_error(self):
        """Test CalculationError functionality."""
        # Create a CalculationError
        error = CalculationError("Calculation failed")
        
        # Check that it's a subclass of ModelError
        self.assertIsInstance(error, ModelError)
        
        # Check that the error message is correct
        self.assertEqual(str(error), "Calculation failed")
        
        # Create a CalculationError with details
        details = {"value": 42, "expected_range": [0, 10]}
        error = CalculationError("Value out of range", details=details)
        
        # Check that the details are correct
        self.assertEqual(error.details, details)
        
    def test_parameter_error(self):
        """Test ParameterError functionality."""
        # Create a ParameterError
        error = ParameterError("Invalid parameter")
        
        # Check that it's a subclass of ModelError
        self.assertIsInstance(error, ModelError)
        
        # Check that the error message is correct
        self.assertEqual(str(error), "Invalid parameter")
        
        # Create a ParameterError with details
        details = {"param_name": "alpha", "value": 1.5, "valid_range": [0, 1]}
        error = ParameterError("Parameter out of range", details=details)
        
        # Check that the details are correct
        self.assertEqual(error.details, details)
        
    def test_error_hierarchy(self):
        """Test the error class hierarchy."""
        # Create instances of each error type
        model_error = ModelError("Generic model error")
        calc_error = CalculationError("Calculation error")
        param_error = ParameterError("Parameter error")
        
        # Check the class hierarchy
        self.assertIsInstance(model_error, Exception)
        self.assertIsInstance(calc_error, ModelError)
        self.assertIsInstance(param_error, ModelError)
        
        # Check that the specific errors are not instances of each other
        self.assertNotIsInstance(calc_error, ParameterError)
        self.assertNotIsInstance(param_error, CalculationError)
        
    def test_error_with_nested_details(self):
        """Test errors with nested detail structures."""
        # Create a complex nested details structure
        nested_details = {
            "params": {
                "alpha": 0.3,
                "delta": 0.1
            },
            "state": {
                "K": 1000,
                "L": 100,
                "H": 1.0,
                "A": 1.0
            },
            "errors": [
                {"type": "overflow", "location": "production_function"},
                {"type": "domain_error", "location": "capital_calculation"}
            ]
        }
        
        # Create an error with the nested details
        error = CalculationError("Complex calculation error", details=nested_details)
        
        # Check that the details are preserved correctly
        self.assertEqual(error.details, nested_details)
        self.assertEqual(error.details["params"]["alpha"], 0.3)
        self.assertEqual(error.details["state"]["K"], 1000)
        self.assertEqual(error.details["errors"][0]["type"], "overflow")
        
    def test_error_serialization(self):
        """Test that errors can be serialized to string representation."""
        # Create an error with details
        details = {"param": "alpha", "value": 1.5, "valid_range": [0, 1]}
        error = ParameterError("Parameter out of range", details=details)
        
        # Convert to string
        error_str = str(error)
        
        # Check that the string contains the error message
        self.assertEqual(error_str, "Parameter out of range")
        
        # Check the repr
        error_repr = repr(error)
        self.assertIn("ParameterError", error_repr)
        self.assertIn("Parameter out of range", error_repr)


if __name__ == '__main__':
    unittest.main()
