import unittest
import math
from foundationTypes.mathTypes.UnitSphericalSmallCircle import (
    UnitSphericalSmallCircle,
)


class TestUnitSphericalSmallCircle(unittest.TestCase):
    """
    Test the UnitSphericalSmallCircle data model.

    This test suite verifies serialization, deserialization, and data integrity
    for the UnitSphericalSmallCircle class.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Test data with various coordinate values
        self.equator_circle = UnitSphericalSmallCircle(
            azimuth=0.0, polar=0.0, radius_angle=math.pi / 4
        )
        self.north_pole_circle = UnitSphericalSmallCircle(
            azimuth=math.pi, polar=math.pi / 2, radius_angle=math.pi / 6
        )
        self.arbitrary_circle = UnitSphericalSmallCircle(
            azimuth=1.5, polar=-0.5, radius_angle=0.8
        )

    def test_from_dict_creates_valid_instance(self):
        """Test that from_dict creates a valid UnitSphericalSmallCircle instance."""
        test_data = {"azimuth": 1.0, "polar": 0.5, "radiusAngle": 0.3}
        circle = UnitSphericalSmallCircle.from_dict(test_data)

        self.assertIsInstance(circle, UnitSphericalSmallCircle)
        self.assertEqual(circle.azimuth, 1.0)
        self.assertEqual(circle.polar, 0.5)
        self.assertEqual(circle.radius_angle, 0.3)

    def test_to_dict_produces_correct_structure(self):
        """Test that to_dict produces the correct dictionary structure."""
        result = self.equator_circle.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIn("azimuth", result)
        self.assertIn("polar", result)
        self.assertIn("radiusAngle", result)
        self.assertEqual(result["azimuth"], 0.0)
        self.assertEqual(result["polar"], 0.0)
        self.assertEqual(result["radiusAngle"], math.pi / 4)

    def test_roundtrip_data_integrity(self):
        """Test that to_dict followed by from_dict preserves data."""
        test_circles = [
            self.equator_circle,
            self.north_pole_circle,
            self.arbitrary_circle,
            UnitSphericalSmallCircle(azimuth=0.0, polar=0.0, radius_angle=0.0),
            UnitSphericalSmallCircle(
                azimuth=2 * math.pi, polar=-math.pi / 2, radius_angle=math.pi
            ),
        ]

        for i, circle in enumerate(test_circles):
            with self.subTest(circle=i):
                # Serialize to dict
                circle_dict = circle.to_dict()

                # Deserialize back to object
                restored_circle = UnitSphericalSmallCircle.from_dict(circle_dict)

                # Verify data integrity
                self.assertEqual(circle.azimuth, restored_circle.azimuth)
                self.assertEqual(circle.polar, restored_circle.polar)
                self.assertEqual(circle.radius_angle, restored_circle.radius_angle)

    def test_from_dict_requires_all_fields(self):
        """Test that from_dict requires all three fields."""
        incomplete_data = {"azimuth": 1.0, "polar": 0.5}

        with self.assertRaises(AssertionError):
            UnitSphericalSmallCircle.from_dict(incomplete_data)

    def test_from_dict_validates_types(self):
        """Test that from_dict validates numeric types."""
        # Test with invalid type (string instead of number)
        invalid_data = {"azimuth": "not a number", "polar": 0.5, "radius": 0.3}

        with self.assertRaises(AssertionError):
            UnitSphericalSmallCircle.from_dict(invalid_data)

    def test_from_dict_accepts_integers(self):
        """Test that from_dict accepts integers and converts to float."""
        test_data = {"azimuth": 1, "polar": 2, "radiusAngle": 3}
        circle = UnitSphericalSmallCircle.from_dict(test_data)

        self.assertIsInstance(circle.azimuth, float)
        self.assertIsInstance(circle.polar, float)
        self.assertIsInstance(circle.radius_angle, float)
        self.assertEqual(circle.azimuth, 1.0)
        self.assertEqual(circle.polar, 2.0)
        self.assertEqual(circle.radius_angle, 3.0)

    def test_to_dict_preserves_numeric_types(self):
        """Test that to_dict preserves numeric types correctly."""
        circle = UnitSphericalSmallCircle(azimuth=1.5, polar=2.5, radius_angle=3.5)
        result = circle.to_dict()

        self.assertIsInstance(result["azimuth"], (int, float))
        self.assertIsInstance(result["polar"], (int, float))
        self.assertIsInstance(result["radiusAngle"], (int, float))


if __name__ == "__main__":
    unittest.main()
