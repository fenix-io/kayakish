"""Unit tests for the Hull class in geometry.hull module."""

import pytest
from src.geometry.hull import Hull, WaterlineCalculationError
from src.geometry.point import Point3D
from src.geometry.curve import Curve


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
    """Integration tests for build method."""

    def test_build_basic_setup(self):
        """Test that build initializes hull attributes correctly."""
        data = {
            "name": "Simple Kayak",
            "description": "Test kayak",
            "target_waterline": 0.1,
            "target_weight": 10.0,
            "target_payload": 80.0,
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.05], [2.0, 0.0, 0.0]]},
                {"name": "gunwale", "points": [[0.0, 0.0, 0.3], [1.0, 0.3, 0.25], [2.0, 0.0, 0.3]]},
            ],
        }

        hull = Hull()
        hull.build(data)

        # Verify basic metadata
        assert hull.name == "Simple Kayak"
        assert hull.description == "Test kayak"
        assert hull.target_waterline == 0.1
        assert hull.target_weight == 10.0
        assert hull.target_payload == 80.0

        # Verify dimensions are calculated
        assert hull.length() > 0
        assert hull.beam() > 0
        assert hull.depth() > 0

        # Verify curves: keel (centerline, not mirrored) + gunwale + mirrored gunwale = 3
        assert len(hull.curves) == 3

        # Verify profiles are generated
        assert len(hull.profiles) > 0

        # Verify volume and CG are calculated
        assert hull.volume > 0
        assert hull.cg is not None
        assert isinstance(hull.cg, Point3D)

        # Verify waterline calculation completed
        assert hull.waterline > 0
        assert hull.cb is not None
        assert isinstance(hull.cb, Point3D)
        assert hull.displacement > 0

    def test_build_sets_min_max_bounds(self):
        """Test that build sets min/max bounds correctly."""
        data = {
            "name": "Test",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.05], [2.0, 0.0, 0.0]]},
                {
                    "name": "gunwale",
                    "points": [[0.0, 0.2, 0.2], [1.0, 0.25, 0.18], [2.0, 0.2, 0.2]],
                },
            ],
        }

        hull = Hull()
        hull.build(data)

        # Check bounds are set correctly
        assert hull.min_x == pytest.approx(0.0, abs=1e-6)
        assert hull.max_x == pytest.approx(2.0, abs=1e-6)
        assert hull.min_y == pytest.approx(-0.25, abs=1e-6)  # Mirrored curve
        assert hull.max_y == pytest.approx(0.25, abs=1e-6)
        assert hull.min_z == pytest.approx(0.0, abs=1e-6)
        assert hull.max_z == pytest.approx(0.2, abs=1e-6)

    def test_build_creates_mirrored_curves(self):
        """Test that build creates mirrored curves for asymmetric curves."""
        data = {
            "name": "Test",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.05], [2.0, 0.0, 0.0]]},
                {"name": "chine", "points": [[0.0, 0.2, 0.1], [1.0, 0.25, 0.08], [2.0, 0.2, 0.1]]},
                {
                    "name": "gunwale",
                    "points": [[0.0, 0.15, 0.25], [1.0, 0.2, 0.22], [2.0, 0.15, 0.25]],
                },
            ],
        }

        hull = Hull()
        hull.build(data)

        # Should have keel (not mirrored) + chine + gunwale + 2 mirrored = 5 total
        assert len(hull.curves) == 5

        # Check that mirrored curves exist
        curve_names = [c.name for c in hull.curves]
        assert "keel" in curve_names
        assert "chine" in curve_names
        assert "gunwale" in curve_names
        assert "Mirror of chine" in curve_names
        assert "Mirror of gunwale" in curve_names

    def test_build_with_centerline_only_curve(self):
        """Test that centerline curves (y=0) are not mirrored."""
        data = {
            "name": "Test",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.05], [2.0, 0.0, 0.0]]},
                {"name": "stem", "points": [[0.0, 0.0, 0.3], [1.0, 0.0, 0.28], [2.0, 0.0, 0.3]]},
                {
                    "name": "gunwale",
                    "points": [[0.0, 0.2, 0.25], [1.0, 0.25, 0.23], [2.0, 0.2, 0.25]],
                },
            ],
        }

        hull = Hull()
        hull.build(data)

        # Keel and stem are centerline (not mirrored), gunwale is mirrored
        # Total: 2 centerline + 1 side + 1 mirrored = 4
        assert len(hull.curves) == 4

        # Check which curves are mirrored
        mirrored_curves = [c for c in hull.curves if c.mirrored]
        non_mirrored_curves = [c for c in hull.curves if not c.mirrored]

        assert len(mirrored_curves) == 1
        assert len(non_mirrored_curves) == 3

    def test_waterline_calculation_exceeds_weight_capacity(self):
        """Test that WaterlineCalculationError is raised when target weight exceeds hull capacity."""
        # Create a very small hull with minimal volume
        data = {
            "name": "TinyHull",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [1.0, 0.0, 0.0]]},
                {
                    "name": "gunwale",
                    "points": [[0.0, 0.1, 0.05], [0.5, 0.12, 0.05], [1.0, 0.1, 0.05]],
                },
            ],
            "weights": [
                {"name": "paddler", "weight": 500.0, "position": [0.5, 0.0, 0.1]}
            ],  # Way too heavy
        }

        hull = Hull()
        with pytest.raises(WaterlineCalculationError) as exc_info:
            hull.build(data)

        # Check that the error message contains useful information
        error_msg = str(exc_info.value)
        assert "500" in error_msg or "weight" in error_msg.lower()

    def test_waterline_calculation_insufficient_volume(self):
        """Test that WaterlineCalculationError is raised when hull has insufficient volume."""
        # Create a hull with curves that result in zero volume at low waterlines
        data = {
            "name": "FlatHull",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]},
                {"name": "chine", "points": [[0.0, 0.01, 0.0], [1.0, 0.01, 0.0], [2.0, 0.01, 0.0]]},
            ],
            "weights": [{"name": "paddler", "weight": 10.0, "position": [1.0, 0.0, 0.05]}],
        }

        hull = Hull()
        with pytest.raises(WaterlineCalculationError) as exc_info:
            hull.build(data)

        # Check that the error message mentions volume
        error_msg = str(exc_info.value)
        assert "volume" in error_msg.lower() or "insufficient" in error_msg.lower()

    def test_waterline_calculation_convergence_failure(self):
        """Test handling when waterline calculation doesn't converge within max iterations."""
        # Create a hull that is too small to support the weight
        # The waterline will go out of bounds (exceed hull depth)
        data = {
            "name": "BadConvergenceHull",
            "curves": [
                {"name": "keel", "points": [[0.0, 0.0, 0.0], [0.5, 0.0, 0.01], [1.0, 0.0, 0.0]]},
                # Very narrow and shallow hull
                {
                    "name": "gunwale",
                    "points": [[0.0, 0.05, 0.02], [0.5, 0.06, 0.025], [1.0, 0.05, 0.02]],
                },
            ],
            "weights": [{"name": "paddler", "weight": 85.0, "position": [0.5, 0.0, 0.015]}],
        }

        hull = Hull()
        # This should raise an exception because the hull is too small to support 85kg
        with pytest.raises(WaterlineCalculationError):
            hull.build(data)


class TestHullWettedSurfaceArea:
    """Tests for wetted_surface_area method."""

    def test_wetted_surface_area_returns_positive(self):
        """Test wetted surface area returns a positive value."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        sw = hull.wetted_surface_area()
        assert sw > 0

    def test_wetted_surface_area_increases_with_waterline(self):
        """Test wetted surface area increases with higher waterline."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        sw1 = hull.wetted_surface_area(waterline=0.10)
        sw2 = hull.wetted_surface_area(waterline=0.15)
        assert sw2 > sw1

    def test_wetted_surface_area_no_waterline_raises_error(self):
        """Test wetted surface area without waterline raises error."""
        hull = Hull()
        hull.waterline = None
        with pytest.raises(ValueError, match="Invalid waterline"):
            hull.wetted_surface_area()

    def test_wetted_surface_area_custom_step(self):
        """Test wetted surface area with custom step size."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        # Smaller step should give slightly different (more accurate) result
        sw_coarse = hull.wetted_surface_area(step=0.10)
        sw_fine = hull.wetted_surface_area(step=0.05)
        # Both should be positive and reasonably close
        assert sw_coarse > 0
        assert sw_fine > 0
        assert abs(sw_coarse - sw_fine) / sw_fine < 0.05  # Within 5%


class TestHullWaterlineLength:
    """Tests for waterline_length method."""

    def test_waterline_length_returns_positive(self):
        """Test waterline length returns a positive value."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        lwl = hull.waterline_length()
        assert lwl > 0

    def test_waterline_length_less_than_loa(self):
        """Test waterline length is less than or equal to LOA."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        lwl = hull.waterline_length()
        loa = hull.length()
        assert lwl <= loa

    def test_waterline_length_increases_with_waterline(self):
        """Test waterline length changes with waterline height."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        # Waterline length depends on hull shape - can increase or decrease with height
        lwl1 = hull.waterline_length(waterline=0.08)
        lwl2 = hull.waterline_length(waterline=0.15)
        # Verify both are positive and different
        assert lwl1 > 0
        assert lwl2 > 0
        assert lwl1 != lwl2

    def test_waterline_length_no_waterline_raises_error(self):
        """Test waterline length without waterline raises error."""
        hull = Hull()
        hull.waterline = None
        with pytest.raises(ValueError, match="Invalid waterline"):
            hull.waterline_length()


class TestHullWaterlineBeam:
    """Tests for waterline_beam method."""

    def test_waterline_beam_returns_positive(self):
        """Test waterline beam returns a positive value."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        bwl = hull.waterline_beam()
        assert bwl > 0

    def test_waterline_beam_less_than_or_equal_to_beam(self):
        """Test waterline beam is less than or equal to maximum beam."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        bwl = hull.waterline_beam()
        beam = hull.beam()
        # Waterplane beam should be less than or equal to maximum beam
        assert bwl <= beam * 1.01  # Small tolerance for numerical precision

    def test_waterline_beam_at_different_waterlines(self):
        """Test waterline beam at different waterlines."""
        data = {
            "name": "Test Kayak",
            "curves": [
                {"name": "keel", "points": [[0, 0, 0], [2.5, 0, 0.05], [5, 0, 0]]},
                {
                    "name": "starboard_chine",
                    "points": [[0, 0.2, 0.05], [2.5, 0.4, 0.15], [5, 0.2, 0.05]],
                },
                {
                    "name": "port_chine",
                    "points": [[0, -0.2, 0.05], [2.5, -0.4, 0.15], [5, -0.2, 0.05]],
                },
                {
                    "name": "starboard_gunnel",
                    "points": [[0, 0.25, 0.15], [2.5, 0.5, 0.25], [5, 0.25, 0.15]],
                },
                {
                    "name": "port_gunnel",
                    "points": [[0, -0.25, 0.15], [2.5, -0.5, 0.25], [5, -0.25, 0.15]],
                },
            ],
            "weights": [{"name": "test", "weight": 75, "position": [2.5, 0, 0.1]}],
        }
        hull = Hull()
        hull.build(data)
        # Both should be positive
        bwl1 = hull.waterline_beam(waterline=0.08)
        bwl2 = hull.waterline_beam(waterline=0.15)
        assert bwl1 > 0
        assert bwl2 > 0

    def test_waterline_beam_no_waterline_raises_error(self):
        """Test waterline beam without waterline raises error."""
        hull = Hull()
        hull.waterline = None
        with pytest.raises(ValueError, match="Invalid waterline"):
            hull.waterline_beam()
