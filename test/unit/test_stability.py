"""Unit tests for the stability module in analysis.stability."""

import pytest
import numpy as np
from src.analysis.stability import calculate_combined_cg, create_stability_curve_points, GRAVITY
from src.geometry.hull import Hull
from src.geometry.point import Point3D


class TestCalculateCombinedCg:
    """Tests for calculate_combined_cg function."""

    def test_combined_cg_equal_weights(self):
        """Test combined CG with equal weights."""
        hull_weight = 50.0
        hull_cg = Point3D(2.5, 0.0, 0.15)
        payload_weight = 50.0
        payload_cg_z = 0.35

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        # With equal weights, CG should be midpoint
        assert combined.x == pytest.approx(2.5)  # Same as hull
        assert combined.y == pytest.approx(0.0)  # Centered
        assert combined.z == pytest.approx((0.15 + 0.35) / 2, abs=1e-6)  # Midpoint

    def test_combined_cg_hull_heavier(self):
        """Test combined CG when hull is heavier."""
        hull_weight = 75.0
        hull_cg = Point3D(2.5, 0.0, 0.15)
        payload_weight = 25.0
        payload_cg_z = 0.35

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        # Combined CG should be closer to hull CG
        assert combined.z < (0.15 + 0.35) / 2
        assert combined.z > 0.15  # But above hull CG

    def test_combined_cg_payload_heavier(self):
        """Test combined CG when payload is heavier."""
        hull_weight = 10.0
        hull_cg = Point3D(2.5, 0.0, 0.15)
        payload_weight = 90.0
        payload_cg_z = 0.35

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        # Combined CG should be closer to payload CG
        assert combined.z > (0.15 + 0.35) / 2
        assert combined.z < 0.35  # But below payload CG

    def test_combined_cg_payload_centered(self):
        """Test that payload is assumed centered laterally."""
        hull_weight = 50.0
        hull_cg = Point3D(2.5, 0.1, 0.15)  # Hull CG slightly off-center
        payload_weight = 50.0
        payload_cg_z = 0.35

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        # With payload centered and equal weights, y should be centered
        assert combined.y == pytest.approx(0.05, abs=1e-6)  # Average of 0.1 and 0.0

    def test_combined_cg_lightweight_hull(self):
        """Test combined CG with very lightweight hull (realistic kayak)."""
        hull_weight = 15.0
        hull_cg = Point3D(2.5, 0.0, 0.12)
        payload_weight = 85.0
        payload_cg_z = 0.30

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        total_weight = 100.0
        expected_z = (15.0 * 0.12 + 85.0 * 0.30) / total_weight
        assert combined.z == pytest.approx(expected_z, abs=1e-6)

    def test_combined_cg_returns_point3d(self):
        """Test that combined CG is returned as Point3D."""
        hull_weight = 50.0
        hull_cg = Point3D(2.5, 0.0, 0.15)
        payload_weight = 50.0
        payload_cg_z = 0.35

        combined = calculate_combined_cg(hull_weight, hull_cg, payload_weight, payload_cg_z)

        assert isinstance(combined, Point3D)


class TestGravityConstant:
    """Tests for GRAVITY constant."""

    def test_gravity_value(self):
        """Test that GRAVITY is set to correct value."""
        assert GRAVITY == 9.81

    def test_gravity_is_positive(self):
        """Test that GRAVITY is positive."""
        assert GRAVITY > 0


class TestCreateStabilityCurvePointsBasic:
    """Basic tests for create_stability_curve_points function."""

    def test_create_stability_curve_returns_tuple(self):
        """Test that create_stability_curve_points returns a tuple."""
        # Create a minimal hull for testing
        data = {
            "name": "Test",
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

        result = create_stability_curve_points(hull, paddler_cg_z=0.25, max_angle=30, step=15)

        assert isinstance(result, tuple)
        assert len(result) == 4  # Returns 4 values

    def test_create_stability_curve_returns_correct_types(self):
        """Test that return values are of correct types."""
        data = {
            "name": "Test",
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

        vanishing_angle, max_moment, max_moment_angle, stability_points = (
            create_stability_curve_points(hull, paddler_cg_z=0.25, max_angle=30, step=15)
        )

        # vanishing_angle can be None or float
        assert vanishing_angle is None or isinstance(vanishing_angle, (int, float))
        assert isinstance(max_moment, (int, float))
        assert isinstance(max_moment_angle, (int, float))
        assert isinstance(stability_points, list)

    def test_create_stability_curve_stability_points_structure(self):
        """Test that stability points have correct structure."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, max_angle=30, step=15
        )

        assert len(stability_points) > 0

        # Check first point structure
        point = stability_points[0]
        assert "angle" in point
        assert "gz" in point
        assert "moment" in point
        assert "cb_y" in point
        assert "cb_z" in point
        assert "cg_y" in point
        assert "cg_z" in point
        assert "waterline" in point
        assert "displacement" in point

    def test_create_stability_curve_zero_angle_included(self):
        """Test that zero angle point is included."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, max_angle=30, step=15
        )

        # First point should be at zero angle
        assert stability_points[0]["angle"] == 0.0

    def test_create_stability_curve_with_step(self):
        """Test that step parameter controls angle increments."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, max_angle=30, step=10
        )

        # Check that angles increment by step
        angles = [p["angle"] for p in stability_points]
        for i in range(1, len(angles)):
            diff = angles[i] - angles[i - 1]
            assert diff == pytest.approx(10.0, abs=1e-6)


class TestCreateStabilityCurvePointsPhysics:
    """Tests for physical correctness of stability calculations."""

    def test_upright_gz_near_zero(self):
        """Test that GZ at zero heel is near zero (symmetric hull)."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, max_angle=30, step=15
        )

        # At zero angle, GZ should be near zero for symmetric hull
        assert stability_points[0]["angle"] == 0.0
        assert abs(stability_points[0]["gz"]) < 0.01  # Small tolerance

    def test_moment_calculation(self):
        """Test that moment is calculated correctly from GZ."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, paddler_weight=80, hull_weight=10, max_angle=30, step=15
        )

        # Check moment = weight * g * GZ for each point
        total_weight = 90.0
        for point in stability_points:
            expected_moment = total_weight * GRAVITY * point["gz"]
            assert point["moment"] == pytest.approx(expected_moment, abs=1e-6)


class TestCreateStabilityCurvePointsParameters:
    """Tests for different parameter combinations."""

    def test_custom_paddler_cg_height(self):
        """Test with custom paddler CG height."""
        data = {
            "name": "Test",
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

        # Should work with different paddler CG heights
        _, _, _, points1 = create_stability_curve_points(
            hull, paddler_cg_z=0.20, max_angle=30, step=15
        )
        _, _, _, points2 = create_stability_curve_points(
            hull, paddler_cg_z=0.35, max_angle=30, step=15
        )

        assert len(points1) > 0
        assert len(points2) > 0
        # Higher paddler CG should generally reduce stability
        # (but this depends on hull geometry, so just check they're different)
        assert points1[1]["gz"] != points2[1]["gz"]

    def test_custom_weights(self):
        """Test with custom hull and paddler weights."""
        data = {
            "name": "Test",
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

        _, _, _, stability_points = create_stability_curve_points(
            hull, paddler_cg_z=0.25, paddler_weight=75.0, hull_weight=15.0, max_angle=30, step=15
        )

        assert len(stability_points) > 0
        # Total weight should be 90.0
        total_weight = 90.0
        for point in stability_points:
            expected_moment = total_weight * GRAVITY * point["gz"]
            assert point["moment"] == pytest.approx(expected_moment, rel=1e-3)
