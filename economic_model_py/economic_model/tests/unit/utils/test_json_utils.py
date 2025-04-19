"""
Tests for the json_utils module.

This module tests the JSON serialization utilities for handling numpy types.
"""

import unittest
import numpy as np
import json
from china_growth_game.economic_model.utils.json_utils import (
    convert_numpy_values,
    numpy_safe_json_dumps,
    numpy_safe_json_loads,
    NumpyEncoder
)


class TestJsonUtils(unittest.TestCase):
    """Test case for the json_utils module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a sample dictionary with numpy values
        self.sample_data = {
            'int64': np.int64(42),
            'float64': np.float64(3.14),
            'array1d': np.array([1, 2, 3]),
            'array2d': np.array([[1, 2], [3, 4]]),
            'nested': {
                'int32': np.int32(99),
                'float32': np.float32(2.71)
            },
            'mixed_list': [1, np.int64(2), 'three', np.float64(4.0)]
        }

    def test_convert_numpy_values(self):
        """Test the convert_numpy_values function."""
        # Convert numpy values to Python native types
        converted_data = convert_numpy_values(self.sample_data)

        # Check that the converted data has the correct types
        self.assertIsInstance(converted_data['int64'], int)
        self.assertIsInstance(converted_data['float64'], float)
        self.assertIsInstance(converted_data['array1d'], list)
        self.assertIsInstance(converted_data['array2d'], list)
        self.assertIsInstance(converted_data['nested']['int32'], int)
        self.assertIsInstance(converted_data['nested']['float32'], float)
        self.assertIsInstance(converted_data['mixed_list'][1], int)
        self.assertIsInstance(converted_data['mixed_list'][3], float)

        # Check that the values are preserved
        self.assertEqual(converted_data['int64'], 42)
        self.assertEqual(converted_data['float64'], 3.14)
        self.assertEqual(converted_data['array1d'], [1, 2, 3])
        self.assertEqual(converted_data['array2d'], [[1, 2], [3, 4]])
        self.assertEqual(converted_data['nested']['int32'], 99)
        self.assertEqual(converted_data['nested']['float32'], 2.71)
        self.assertEqual(converted_data['mixed_list'], [1, 2, 'three', 4.0])

    def test_numpy_safe_json_dumps(self):
        """Test the numpy_safe_json_dumps function."""
        # Convert the sample data to a JSON string
        json_str = numpy_safe_json_dumps(self.sample_data)

        # Check that the result is a string
        self.assertIsInstance(json_str, str)

        # Parse the JSON string back to a Python object
        parsed_data = json.loads(json_str)

        # Check that the parsed data has the correct values
        self.assertEqual(parsed_data['int64'], 42)
        self.assertEqual(parsed_data['float64'], 3.14)
        self.assertEqual(parsed_data['array1d'], [1, 2, 3])
        self.assertEqual(parsed_data['array2d'], [[1, 2], [3, 4]])
        self.assertEqual(parsed_data['nested']['int32'], 99)
        self.assertEqual(parsed_data['nested']['float32'], 2.71)
        self.assertEqual(parsed_data['mixed_list'], [1, 2, 'three', 4.0])

    def test_numpy_safe_json_loads(self):
        """Test the numpy_safe_json_loads function."""
        # Create a JSON string
        json_str = '{"value": 42, "list": [1, 2, 3]}'

        # Parse the JSON string
        parsed_data = numpy_safe_json_loads(json_str)

        # Check that the parsed data has the correct values
        self.assertEqual(parsed_data['value'], 42)
        self.assertEqual(parsed_data['list'], [1, 2, 3])

    def test_numpy_encoder(self):
        """Test the NumpyEncoder class."""
        # Convert the sample data to a JSON string using the NumpyEncoder
        json_str = json.dumps(self.sample_data, cls=NumpyEncoder)

        # Check that the result is a string
        self.assertIsInstance(json_str, str)

        # Parse the JSON string back to a Python object
        parsed_data = json.loads(json_str)

        # Check that the parsed data has the correct values
        self.assertEqual(parsed_data['int64'], 42)
        self.assertEqual(parsed_data['float64'], 3.14)
        self.assertEqual(parsed_data['array1d'], [1, 2, 3])
        self.assertEqual(parsed_data['array2d'], [[1, 2], [3, 4]])
        self.assertEqual(parsed_data['nested']['int32'], 99)
        self.assertEqual(parsed_data['nested']['float32'], 2.71)
        self.assertEqual(parsed_data['mixed_list'], [1, 2, 'three', 4.0])


if __name__ == '__main__':
    unittest.main()
