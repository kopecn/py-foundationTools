import unittest
import tempfile
import json
from pathlib import Path
from dataModelHelpers.dataModelHelper import DataModelHelper
from dataModelHelpers.commonTypes.GeoCoordinate import GeoCoordinate


class TestDataModelHelper(unittest.TestCase):
    """
    Test the DataModelHelper base class functionality using GeoCoordinate as a concrete implementation.

    This test suite verifies that the DataModelHelper base class provides correct
    saveToFile and loadFromFile functionality when properly implemented by subclasses.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_data_model.json"

        # Test data using GeoCoordinate as DataModelHelper implementation
        self.complete_model = GeoCoordinate(latitude=40.7128, longitude=-74.0060)
        self.partial_model = GeoCoordinate(latitude=51.5074, longitude=-0.1278)
        self.minimal_model = GeoCoordinate(latitude=0.0, longitude=0.0)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if self.test_file.exists():
            self.test_file.unlink()
        self.temp_dir.rmdir()

    def test_saveToFile_creates_valid_json(self):
        """Test that DataModelHelper.saveToFile creates properly formatted JSON."""
        self.complete_model.saveToFile(self.test_file)

        # Verify file exists
        self.assertTrue(self.test_file.exists())

        # Verify JSON structure and formatting
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)

        # Check that JSON is properly formatted (indented)
        self.assertIn("\n", content)  # Should have newlines due to indent=4

        # Verify data structure
        expected = {"latitude": 40.7128, "longitude": -74.0060}
        self.assertEqual(data, expected)

    def test_saveToFile_uses_to_dict_method(self):
        """Test that saveToFile correctly uses the subclass's to_dict method."""
        self.partial_model.saveToFile(self.test_file)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Should contain both latitude and longitude (both are now required)
        expected = {"latitude": 51.5074, "longitude": -0.1278}
        self.assertEqual(data, expected)
        self.assertIn("longitude", data)

    def test_saveToFile_handles_minimal_data(self):
        """Test that saveToFile handles models with minimal valid data."""
        self.minimal_model.saveToFile(self.test_file)

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Should contain both latitude and longitude with zero values
        expected = {"latitude": 0.0, "longitude": 0.0}
        self.assertEqual(data, expected)

    def test_saveToFile_utf8_encoding(self):
        """Test that saveToFile uses UTF-8 encoding."""
        self.complete_model.saveToFile(self.test_file)

        # Read with explicit encoding to verify
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["latitude"], 40.7128)

    def test_loadFromFile_uses_from_dict_method(self):
        """Test that loadFromFile correctly uses the subclass's from_dict method."""
        # Create test JSON file
        test_data = {"latitude": 35.6762, "longitude": 139.6503}
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Load using DataModelHelper method
        loaded_model = GeoCoordinate.loadFromFile(self.test_file)

        # Verify it's the correct type and has correct data
        self.assertIsInstance(loaded_model, GeoCoordinate)
        self.assertEqual(loaded_model.latitude, 35.6762)
        self.assertEqual(loaded_model.longitude, 139.6503)

    def test_loadFromFile_requires_complete_data(self):
        """Test that loadFromFile requires both latitude and longitude."""
        # Create test JSON with only latitude - should fail
        test_data = {"latitude": 48.8566}
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        with self.assertRaises(AssertionError):
            GeoCoordinate.loadFromFile(self.test_file)

    def test_loadFromFile_requires_non_empty_data(self):
        """Test that loadFromFile requires non-empty JSON object."""
        test_data = {}
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        with self.assertRaises(AssertionError):
            GeoCoordinate.loadFromFile(self.test_file)

    def test_roundtrip_data_integrity(self):
        """Test that saveToFile followed by loadFromFile preserves data."""
        test_models = [
            self.complete_model,
            self.partial_model,
            self.minimal_model,
            GeoCoordinate(latitude=-90.0, longitude=-180.0),  # Edge case: negative extreme values
            GeoCoordinate(latitude=90.0, longitude=180.0),   # Edge case: positive extreme values
        ]

        for i, model in enumerate(test_models):
            with self.subTest(model=i):
                test_file = self.temp_dir / f"roundtrip_{i}.json"

                # Save using DataModelHelper
                model.saveToFile(test_file)

                # Load using DataModelHelper
                loaded_model = GeoCoordinate.loadFromFile(test_file)

                # Verify data integrity
                self.assertEqual(model.latitude, loaded_model.latitude)
                self.assertEqual(model.longitude, loaded_model.longitude)

                # Clean up
                test_file.unlink()

    def test_loadFromFile_error_handling_invalid_json(self):
        """Test that loadFromFile properly raises exceptions for invalid JSON."""
        # Create file with invalid JSON
        with open(self.test_file, "w") as f:
            f.write("invalid json content")

        with self.assertRaises(json.JSONDecodeError):
            GeoCoordinate.loadFromFile(self.test_file)

    def test_loadFromFile_error_handling_missing_file(self):
        """Test that loadFromFile properly raises exceptions for missing files."""
        nonexistent_file = self.temp_dir / "does_not_exist.json"

        with self.assertRaises(FileNotFoundError):
            GeoCoordinate.loadFromFile(nonexistent_file)

    def test_saveToFile_error_handling_invalid_path(self):
        """Test that saveToFile properly raises exceptions for invalid paths."""
        invalid_path = Path("/invalid/directory/that/does/not/exist/test.json")

        with self.assertRaises(OSError):
            self.complete_model.saveToFile(invalid_path)

    def test_datamodel_helper_inheritance(self):
        """Test that GeoCoordinate properly inherits from DataModelHelper."""
        self.assertIsInstance(self.complete_model, DataModelHelper)
        self.assertTrue(hasattr(self.complete_model, "saveToFile"))
        self.assertTrue(hasattr(self.complete_model, "loadFromFile"))
        self.assertTrue(hasattr(self.complete_model, "to_dict"))
        self.assertTrue(hasattr(self.complete_model, "from_dict"))

    def test_class_method_returns_correct_type(self):
        """Test that loadFromFile class method returns the correct subclass type."""
        test_data = {"latitude": 12.34, "longitude": 56.78}
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Call on the subclass
        loaded_model = GeoCoordinate.loadFromFile(self.test_file)

        # Should return GeoCoordinate, not DataModelHelper
        self.assertIsInstance(loaded_model, GeoCoordinate)
        self.assertEqual(type(loaded_model), GeoCoordinate)


if __name__ == "__main__":
    unittest.main()
