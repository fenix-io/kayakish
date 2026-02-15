"""Unit tests for the Hull class in geometry.hull module."""

import pytest
import numpy as np
from src.geometry.hull import Hull
from src.geometry.point import Point3D
from src.geometry.curve import Curve
from src.geometry.profile import Profile


class TestHullInit:
    """Tests for Hull initialization."""

    def test_init_creates_empty_hull(self):
        """Test that Hull initialization creates empty lists."""
        hull = Hull()
        assert hasattr(hull, "curves")
        assert hasattr(hull, "profiles")
        assert isinstance(hull.curves, list)
        assert isinstance(hull.profiles, list)
        assert len(hull.curves) == 0
        assert len(hull.profiles) == 0


class TestHullInitializeFromData:
    """Tests for initialize_from_data method."""

    def test_initialize_from_data_basic(self):
        """Test initialize_from_data with basic data."""
        data = {
            "name": "Test Kayak",
            "description": "A test kayak",
            "target_waterline": 0.15,
            "target_weight": 10.0,
            "target_payload": 80.0,
        }
        hull = Hull()
        hull.initialize_from_data(data)

        assert hull.name == "Test Kayak"
        assert hull.description == "A test kayak"
        assert hull.target_waterline == 0.15
        assert hull.target_weight == 10.0
        assert hull.target_payload == 80.0

    def test_initialize_from_data_with_defaults(self):
        """Test initialize_from_data uses defaults for missing values."""
        data = {}
        hull = Hull()
        hull.initialize_from_data(data)

        assert hull.name == "KAYAK HULL"
        assert hull.description == "KAYAK HULL"
        assert hull.target_waterline == 0.1
        assert hull.target_weight == 100
        assert hull.target_payload == 100

    def test_initialize_from_data_with_curves(self):
        """Test initialize_from_data with curve data."""
        data = {
            "name": "Test",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [1, 0, 0.1], [2, 0, 0]], "mirrored": False}
            ],
        }
        hull = Hull()
        hull.initialize_from_data(data)

        assert len(hull.curves) == 1
        assert hull.curves[0].name == "keel"
        assert len(hull.curves[0].points) == 3

    def test_initialize_from_data_with_profiles(self):
        """Test initialize_from_data with profile data."""
        data = {
            "name": "Test",
            "profiles": [{"station": 1.0, "points": [[1, 0, 0], [1, 0.5, 0.3], [1, -0.5, 0.3]]}],
        }
        hull = Hull()
        hull.initialize_from_data(data)

        assert len(hull.profiles) == 1
        assert hull.profiles[0].station == 1.0
        assert len(hull.profiles[0].points) == 3

    def test_initialize_from_data_with_cg(self):
        """Test initialize_from_data with CG data."""
        data = {"name": "Test", "cg": [1.5, 0.0, 0.2]}
        hull = Hull()
        hull.initialize_from_data(data)

        assert hull.cg is not None
        assert hull.cg.x == 1.5
        assert hull.cg.y == 0.0
        assert hull.cg.z == 0.2

    def test_initialize_from_data_with_cb(self):
        """Test initialize_from_data with CB data."""
        data = {"name": "Test", "cb": [1.5, 0.0, 0.15]}
        hull = Hull()
        hull.initialize_from_data(data)

        assert hull.cb is not None
        assert hull.cb.x == 1.5
        assert hull.cb.y == 0.0
        assert hull.cb.z == 0.15

    def test_initialize_from_data_with_bounds(self):
        """Test initialize_from_data with min/max bounds."""
        data = {
            "name": "Test",
            "min_x": 0.0,
            "max_x": 5.0,
            "min_y": -0.3,
            "max_y": 0.3,
            "min_z": 0.0,
            "max_z": 0.4,
        }
        hull = Hull()
        hull.initialize_from_data(data)

        assert hull.min_x == 0.0
        assert hull.max_x == 5.0
        assert hull.min_y == -0.3
        assert hull.max_y == 0.3
        assert hull.min_z == 0.0
        assert hull.max_z == 0.4


class TestHullDimensions:
    """Tests for hull dimension methods."""

    def test_length(self):
        """Test length calculation."""
        hull = Hull()
        hull.min_x = 0.0
        hull.max_x = 5.0
        assert hull.length() == 5.0

    def test_beam(self):
        """Test beam calculation."""
        hull = Hull()
        hull.min_y = -0.3
        hull.max_y = 0.3
        assert hull.beam() == 0.6

    def test_depth(self):
        """Test depth calculation."""
        hull = Hull()
        hull.min_z = 0.0
        hull.max_z = 0.4
        assert hull.depth() == 0.4


class TestHullUpdateMinMax:
    """Tests for _update_min_max method."""

    def test_update_min_max_first_point(self):
        """Test _update_min_max with first point."""
        hull = Hull()
        hull.min_x = float("inf")
        hull.max_x = float("-inf")
        hull.min_y = float("inf")
        hull.max_y = float("-inf")
        hull.min_z = float("inf")
        hull.max_z = float("-inf")

        point = Point3D(1.0, 2.0, 3.0)
        hull._update_min_max(point)

        assert hull.min_x == 1.0
        assert hull.max_x == 1.0
        assert hull.min_y == 2.0
        assert hull.max_y == 2.0
        assert hull.min_z == 3.0
        assert hull.max_z == 3.0

    def test_update_min_max_expands_bounds(self):
        """Test _update_min_max expands bounds correctly."""
        hull = Hull()
        hull.min_x = 1.0
        hull.max_x = 2.0
        hull.min_y = 0.0
        hull.max_y = 1.0
        hull.min_z = 0.0
        hull.max_z = 1.0

        # Point outside current bounds
        point = Point3D(3.0, 2.0, 2.0)
        hull._update_min_max(point)

        assert hull.max_x == 3.0
        assert hull.max_y == 2.0
        assert hull.max_z == 2.0

    def test_update_min_max_negative_values(self):
        """Test _update_min_max with negative values."""
        hull = Hull()
        hull.min_x = 0.0
        hull.max_x = 1.0
        hull.min_y = 0.0
        hull.max_y = 1.0
        hull.min_z = 0.0
        hull.max_z = 1.0

        point = Point3D(-1.0, -0.5, -0.2)
        hull._update_min_max(point)

        assert hull.min_x == -1.0
        assert hull.min_y == -0.5
        assert hull.min_z == -0.2


class TestHullGetPointsAt:
    """Tests for _get_points_at method."""

    def test_get_points_at_no_curves(self):
        """Test _get_points_at with no curves."""
        hull = Hull()
        points = hull._get_points_at(1.0)
        assert points == []

    def test_get_points_at_with_curves(self):
        """Test _get_points_at with valid curves."""
        hull = Hull()
        # Create a simple curve
        curve_points = [Point3D(0, 0, 0), Point3D(2, 0.5, 0.3)]
        curve = Curve("test", curve_points)
        hull.curves.append(curve)

        # Get points at x=1.0 (midpoint)
        points = hull._get_points_at(1.0)

        # Should get one point from the curve
        assert len(points) >= 1

    def test_get_points_at_outside_range(self):
        """Test _get_points_at with x outside curve range."""
        hull = Hull()
        curve_points = [Point3D(0, 0, 0), Point3D(1, 0.5, 0.3)]
        curve = Curve("test", curve_points)
        hull.curves.append(curve)

        # Request x outside range
        points = hull._get_points_at(5.0)

        # Should return empty list when no curves can provide a point
        assert len(points) == 0


class TestHullGetPointsBelowWaterline:
    """Tests for _get_points_below_waterline method."""

    def test_get_points_below_waterline_all_below(self):
        """Test _get_points_below_waterline when all points are below."""
        hull = Hull()
        points = [Point3D(1.0, 0.0, 0.1), Point3D(1.0, 0.5, 0.2), Point3D(1.0, -0.5, 0.2)]
        waterline = 0.5

        below = hull._get_points_below_waterline(points, waterline)

        # All points should be included
        assert len(below) >= 3

    def test_get_points_below_waterline_all_above(self):
        """Test _get_points_below_waterline when all points are above."""
        hull = Hull()
        points = [Point3D(1.0, 0.0, 0.6), Point3D(1.0, 0.5, 0.7), Point3D(1.0, -0.5, 0.7)]
        waterline = 0.5

        below = hull._get_points_below_waterline(points, waterline)

        # No points should be included
        assert len(below) == 0

    def test_get_points_below_waterline_with_intersection(self):
        """Test _get_points_below_waterline with waterline intersection."""
        hull = Hull()
        points = [
            Point3D(1.0, 0.0, 0.0),  # Below
            Point3D(1.0, 0.5, 0.3),  # Below
            Point3D(1.0, 0.0, 0.8),  # Above
            Point3D(1.0, -0.5, 0.3),  # Below
        ]
        waterline = 0.5

        below = hull._get_points_below_waterline(points, waterline)

        # Should include points below waterline plus intersection points
        assert len(below) >= 3

        # Check that there are intersection points at waterline
        waterline_points = [p for p in below if abs(p.z - waterline) < 1e-6]
        assert len(waterline_points) >= 1

    def test_get_points_below_waterline_less_than_3_points(self):
        """Test _get_points_below_waterline with less than 3 points."""
        hull = Hull()
        points = [Point3D(1.0, 0.0, 0.1), Point3D(1.0, 0.5, 0.2)]
        waterline = 0.5

        below = hull._get_points_below_waterline(points, waterline)

        # Should return empty when less than 3 points
        assert below == []

    def test_get_points_below_waterline_empty(self):
        """Test _get_points_below_waterline with empty list."""
        hull = Hull()
        points = []
        waterline = 0.5

        below = hull._get_points_below_waterline(points, waterline)

        assert below == []


class TestHullAsDict:
    """Tests for as_dict method."""

    def test_as_dict_returns_dict(self):
        """Test that as_dict returns a dictionary."""
        hull = Hull()
        hull.name = "Test"
        result = hull.as_dict()
        assert isinstance(result, dict)

    def test_as_dict_includes_attributes(self):
        """Test that as_dict includes hull attributes."""
        hull = Hull()
        hull.name = "Test Kayak"
        hull.description = "A test"
        result = hull.as_dict()

        assert "name" in result
        assert result["name"] == "Test Kayak"


class TestHullBuildIntegration:
    """Integration tests for build method (requires more setup)."""

    def test_build_simple_hull(self):
        """Test building a simple hull from data."""
        data = {
            "name": "Simple Kayak",
            "description": "Test kayak",
            "target_waterline": 0.1,
            "target_weight": 10.0,
            "target_payload": 80.0,
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [2.5, 0.0, 0.05], [5.0, 0.0, 0.0]]},
                {"name": "gunwale", "points": [[0.0, 0.0, 0.3], [2.5, 0.3, 0.25], [5.0, 0.0, 0.3]]},
            ],
        }

        hull = Hull()
        hull.build(data)

        # Basic assertions
        assert hull.name == "Simple Kayak"
        assert hull.length() > 0
        assert hull.beam() > 0
        assert hull.depth() > 0
        assert len(hull.curves) > 0  # Should include mirrored curves
        assert len(hull.profiles) > 0  # Should generate profiles
        assert hull.volume > 0
        assert hull.cg is not None
        assert hull.waterline > 0
        assert hull.cb is not None
        assert hull.displacement > 0

    def test_build_sets_min_max_bounds(self):
        """Test that build sets min/max bounds correctly."""
        data = {
            "name": "Test",
            "curves": [{"name": "keel", "points": [[0.0, 0.0, 0.0], [5.0, 0.0, 0.1]]}],
        }

        hull = Hull()
        hull.build(data)

        assert hull.min_x == pytest.approx(0.0)
        assert hull.max_x == pytest.approx(5.0)
        assert hull.min_z == pytest.approx(0.0)
        profile = ModelProfile(
            station=1.0, port_points=[YZPoint(y=0.0, z=0.5), YZPoint(y=0.2, z=0.4)]
        )
        hull = Hull(metadata=metadata, profiles=[profile])

        result = prepare_hull(hull)

        assert result.name == "Kayak 001"
        assert hasattr(result, "profiles")
        assert len(result.profiles) == 1

    def test_prepare_hull_multiple_profiles(self):
        """Test prepare_hull with multiple profiles."""
        metadata = Metadata(name="Multi Profile Kayak")
        profiles = [
            ModelProfile(station=0.0, port_points=[YZPoint(y=0.0, z=0.3)]),
            ModelProfile(station=1.0, port_points=[YZPoint(y=0.0, z=0.5), YZPoint(y=0.2, z=0.4)]),
            ModelProfile(station=2.0, port_points=[YZPoint(y=0.0, z=0.6), YZPoint(y=0.3, z=0.5)]),
        ]
        hull = Hull(metadata=metadata, profiles=profiles)

        result = prepare_hull(hull)

        assert result.name == "Multi Profile Kayak"
        assert len(result.profiles) == 3

    def test_prepare_hull_with_none_metadata_fields(self):
        """Test prepare_hull with optional metadata fields as None."""
        metadata = Metadata(
            name="Minimal Kayak", description=None, target_waterline=None, target_payload=None
        )
        hull = Hull(metadata=metadata, profiles=[])

        result = prepare_hull(hull)

        assert result.name == "Minimal Kayak"
        assert result.description is None
        assert result.target_waterline is None
        assert result.target_payload is None

    def test_prepare_hull_profile_processing(self):
        """Test that profiles are processed (sorted, completed)."""
        metadata = Metadata(name="Processing Test")
        profile = ModelProfile(
            station=1.0,
            port_points=[YZPoint(y=0.3, z=0.3), YZPoint(y=0.0, z=0.5), YZPoint(y=0.2, z=0.4)],
        )
        hull = Hull(metadata=metadata, profiles=[profile])

        result = prepare_hull(hull)

        # Profile should be added
        assert hasattr(result, "profiles")
        assert len(result.profiles) == 1


class TestPrepareHullIntegration:
    """Integration tests for hull preparation workflow."""

    def test_full_hull_preparation_workflow(self):
        """Test complete workflow with realistic hull data."""
        metadata = Metadata(
            name="Sea Kayak Pro",
            description="High-performance sea kayak",
            target_waterline=0.12,
            target_payload=100.0,
        )

        profiles = [
            ModelProfile(station=0.0, port_points=[YZPoint(y=0.0, z=0.30)]),
            ModelProfile(
                station=1.0,
                port_points=[
                    YZPoint(y=0.00, z=0.30),
                    YZPoint(y=0.18, z=0.28),
                    YZPoint(y=0.12, z=0.15),
                ],
            ),
            ModelProfile(
                station=2.0,
                port_points=[
                    YZPoint(y=0.00, z=0.35),
                    YZPoint(y=0.20, z=0.30),
                    YZPoint(y=0.15, z=0.20),
                ],
            ),
            ModelProfile(station=3.0, port_points=[YZPoint(y=0.0, z=0.30)]),
        ]

        hull = Hull(metadata=metadata, profiles=profiles)
        result = prepare_hull(hull)

        # Verify all metadata transferred
        assert result.name == "Sea Kayak Pro"
        assert result.description == "High-performance sea kayak"
        assert result.target_waterline == 0.12
        assert result.target_payload == 100.0

        # Verify profiles were processed
        assert len(result.profiles) == 4

        # Check profile at station 1.0
        station_1_profile = result.profiles[1]
        assert station_1_profile.station == 1.0

        # Check data_points: 3 original + 2 mirrored (excluding centerline) = 5
        assert len(station_1_profile.data_points) == 5

        # Check circular interpolation points (should be 120 for 360/3 degrees)
        assert len(station_1_profile.points) > 0
        assert len(station_1_profile.points) <= 120

        # Sample some points around the circle to verify they have correct station
        for point in station_1_profile.points[::30]:  # Sample every 30th point
            assert point.x == 1.0  # All points should be at station 1.0
            # Verify points are within reasonable bounds
            assert -0.3 <= point.y <= 0.3
            assert 0.0 <= point.z <= 0.4

    def test_prepare_hull_with_complex_profiles(self):
        """Test hull preparation with complex profile data."""
        metadata = Metadata(name="Complex Hull")

        profiles = [
            ModelProfile(
                station=i * 0.5,
                port_points=[
                    YZPoint(y=0.0, z=0.5),
                    YZPoint(y=0.1 * (i + 1), z=0.4),
                    YZPoint(y=0.15 * (i + 1), z=0.3),
                    YZPoint(y=0.2 * (i + 1), z=0.2),
                ],
            )
            for i in range(5)
        ]

        hull = Hull(metadata=metadata, profiles=profiles)
        result = prepare_hull(hull)

        assert result.name == "Complex Hull"
        assert len(result.profiles) == 5
