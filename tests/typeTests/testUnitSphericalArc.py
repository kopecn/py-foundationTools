import unittest
import math
from foundationTypes.mathTypes.UnitSphericalArc import (
    UnitSphericalArc,
)


class TestUnitSphericalArc(unittest.TestCase):
    """
    Test the UnitSphericalArc data model.

    This test suite verifies serialization, deserialization, and data integrity
    for the UnitSphericalArc class.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Test data with various coordinate values
        self.short_arc = UnitSphericalArc(
            arc_length=math.pi / 4, azimuth=0.0, radius_angle=math.pi / 6
        )
        self.semicircle_arc = UnitSphericalArc(
            arc_length=math.pi, azimuth=math.pi / 2, radius_angle=math.pi / 3
        )
        self.arbitrary_arc = UnitSphericalArc(
            arc_length=1.5, azimuth=2.0, radius_angle=0.8
        )

    def test_from_dict_creates_valid_instance(self):
        """Test that from_dict creates a valid UnitSphericalArc instance."""
        test_data = {"arcLength": 1.0, "azimuth": 0.5, "radiusAngle": 0.3}
        arc = UnitSphericalArc.from_dict(test_data)

        self.assertIsInstance(arc, UnitSphericalArc)
        self.assertEqual(arc.arc_length, 1.0)
        self.assertEqual(arc.azimuth, 0.5)
        self.assertEqual(arc.radius_angle, 0.3)

    def test_to_dict_produces_correct_structure(self):
        """Test that to_dict produces the correct dictionary structure."""
        result = self.short_arc.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIn("arcLength", result)
        self.assertIn("azimuth", result)
        self.assertIn("radiusAngle", result)
        self.assertEqual(result["arcLength"], math.pi / 4)
        self.assertEqual(result["azimuth"], 0.0)
        self.assertEqual(result["radiusAngle"], math.pi / 6)

    def test_roundtrip_data_integrity(self):
        """Test that to_dict followed by from_dict preserves data."""
        test_arcs = [
            self.short_arc,
            self.semicircle_arc,
            self.arbitrary_arc,
            UnitSphericalArc(arc_length=0.0, azimuth=0.0, radius_angle=0.0),
            UnitSphericalArc(
                arc_length=2 * math.pi, azimuth=2 * math.pi, radius_angle=math.pi
            ),
            UnitSphericalArc(
                arc_length=-math.pi, azimuth=math.pi, radius_angle=math.pi / 2
            ),
        ]

        for i, arc in enumerate(test_arcs):
            with self.subTest(arc=i):
                # Serialize to dict
                arc_dict = arc.to_dict()

                # Deserialize back to object
                restored_arc = UnitSphericalArc.from_dict(arc_dict)

                # Verify data integrity
                self.assertEqual(arc.arc_length, restored_arc.arc_length)
                self.assertEqual(arc.azimuth, restored_arc.azimuth)
                self.assertEqual(arc.radius_angle, restored_arc.radius_angle)

    def test_from_dict_requires_all_fields(self):
        """Test that from_dict requires all three fields."""
        incomplete_data = {"arcLength": 1.0, "azimuth": 0.5}

        with self.assertRaises(AssertionError):
            UnitSphericalArc.from_dict(incomplete_data)

    def test_from_dict_validates_types(self):
        """Test that from_dict validates numeric types."""
        # Test with invalid type (string instead of number)
        invalid_data = {"arcLength": "not a number", "azimuth": 0.5, "radiusAngle": 0.3}

        with self.assertRaises(AssertionError):
            UnitSphericalArc.from_dict(invalid_data)

    def test_from_dict_accepts_integers(self):
        """Test that from_dict accepts integers and converts to float."""
        test_data = {"arcLength": 1, "azimuth": 2, "radiusAngle": 3}
        arc = UnitSphericalArc.from_dict(test_data)

        self.assertIsInstance(arc.arc_length, float)
        self.assertIsInstance(arc.azimuth, float)
        self.assertIsInstance(arc.radius_angle, float)
        self.assertEqual(arc.arc_length, 1.0)
        self.assertEqual(arc.azimuth, 2.0)
        self.assertEqual(arc.radius_angle, 3.0)

    def test_to_dict_preserves_numeric_types(self):
        """Test that to_dict preserves numeric types correctly."""
        arc = UnitSphericalArc(arc_length=1.5, azimuth=2.5, radius_angle=3.5)
        result = arc.to_dict()

        self.assertIsInstance(result["arcLength"], (int, float))
        self.assertIsInstance(result["azimuth"], (int, float))
        self.assertIsInstance(result["radiusAngle"], (int, float))


if __name__ == "__main__":
    unittest.main()
