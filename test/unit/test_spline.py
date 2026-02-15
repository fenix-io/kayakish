"""Unit tests for the Spline3D class in geometry.spline module."""

import pytest
import numpy as np
from src.geometry.spline import Spline3D
from src.geometry.point import Point3D


class TestSpline3DInit:
    """Tests for Spline3D initialization."""

    def test_init_with_name_and_points(self):
        """Test Spline3D initialization with name and points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test_spline", points)
        assert spline.name == "test_spline"
        assert len(spline.points) == 3
        assert spline.bc_type == "natural"

    def test_init_with_boundary_condition(self):
        """Test Spline3D initialization with custom boundary condition."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points, bc_type="clamped")
        assert spline.bc_type == "clamped"

    def test_init_auto_parametrization_monotonic_x(self):
        """Test auto parametrization chooses 'x' for monotonic x."""
        # Monotonic x coordinates
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0.5, 2)]
        spline = Spline3D("test", points, parametrization="auto")
        assert spline.parametrization == "x"

    def test_init_auto_parametrization_non_monotonic_x(self):
        """Test auto parametrization chooses 'chord' for non-monotonic x."""
        # Non-monotonic x coordinates
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(0.5, 0.5, 2)]
        spline = Spline3D("test", points, parametrization="auto")
        assert spline.parametrization == "chord"

    def test_init_extracts_coordinates(self):
        """Test that initialization extracts coordinate arrays."""
        points = [Point3D(0, 1, 2), Point3D(3, 4, 5), Point3D(6, 7, 8)]
        spline = Spline3D("test", points)
        np.testing.assert_array_equal(spline.x, np.array([0, 3, 6]))
        np.testing.assert_array_equal(spline.y, np.array([1, 4, 7]))
        np.testing.assert_array_equal(spline.z, np.array([2, 5, 8]))


class TestSpline3DEvalT:
    """Tests for eval_t method."""

    def test_eval_t_at_control_points(self):
        """Test eval_t at parameter values corresponding to control points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points, parametrization="x")

        # For 'x' parametrization, t=x for control points
        p0 = spline.eval_t(0)
        assert p0.x == pytest.approx(0.0)
        assert p0.y == pytest.approx(0.0)
        assert p0.z == pytest.approx(0.0)

        p1 = spline.eval_t(1)
        assert p1.x == pytest.approx(1.0)
        assert p1.y == pytest.approx(1.0)
        assert p1.z == pytest.approx(1.0)

    def test_eval_t_interpolates(self):
        """Test eval_t provides smooth interpolation."""
        points = [Point3D(0, 0, 0), Point3D(2, 2, 2)]
        spline = Spline3D("test", points, parametrization="x")

        # Midpoint should be approximately (1, 1, 1) for linear case
        p_mid = spline.eval_t(1.0)
        assert p_mid.x == pytest.approx(1.0)
        assert p_mid.y == pytest.approx(1.0, abs=0.1)  # Allow for interpolation
        assert p_mid.z == pytest.approx(1.0, abs=0.1)


class TestSpline3DEvalX:
    """Tests for eval_x method."""

    def test_eval_x_at_control_points(self):
        """Test eval_x at x-coordinates of control points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points, parametrization="x")

        p0 = spline.eval_x(0)
        assert p0.x == pytest.approx(0.0)
        assert p0.y == pytest.approx(0.0)

        p2 = spline.eval_x(2)
        assert p2.x == pytest.approx(2.0)
        assert p2.y == pytest.approx(0.0)

    def test_eval_x_outside_range_raises_error(self):
        """Test eval_x raises error when x is outside curve range."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points, parametrization="x")

        with pytest.raises(ValueError, match="outside the curve range"):
            spline.eval_x(-1)

        with pytest.raises(ValueError, match="outside the curve range"):
            spline.eval_x(3)

    def test_eval_x_interpolates(self):
        """Test eval_x provides interpolation between points."""
        points = [Point3D(0, 0, 0), Point3D(2, 2, 2)]
        spline = Spline3D("test", points, parametrization="x")

        p_mid = spline.eval_x(1.0)
        assert p_mid.x == pytest.approx(1.0)
        # y and z should be interpolated
        assert 0 <= p_mid.y <= 2
        assert 0 <= p_mid.z <= 2


class TestSpline3DTangent:
    """Tests for tangent method."""

    def test_tangent_is_unit_vector(self):
        """Test that tangent returns a unit vector."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        t_vec = spline.tangent(spline.t[1])
        # Check it's a unit vector
        norm = np.linalg.norm(t_vec)
        assert norm == pytest.approx(1.0)

    def test_tangent_direction_straight_line(self):
        """Test tangent direction for a straight line."""
        # Straight line along x-axis
        points = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        t_vec = spline.tangent(spline.t[1])
        # Should point in x direction
        assert t_vec[0] > 0.99  # Nearly 1
        assert abs(t_vec[1]) < 0.01
        assert abs(t_vec[2]) < 0.01


class TestSpline3DCurvature:
    """Tests for curvature method."""

    def test_curvature_straight_line(self):
        """Test that curvature is zero for a straight line."""
        points = [Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        curv = spline.curvature(spline.t[1])
        assert curv == pytest.approx(0.0, abs=1e-6)

    def test_curvature_curved_path(self):
        """Test that curvature is non-zero for a curved path."""
        # Curved path
        points = [Point3D(0, 0, 0), Point3D(1, 1, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        curv = spline.curvature(spline.t[1])
        assert curv > 0  # Should be positive for curved path


class TestSpline3DNormal:
    """Tests for normal method."""

    def test_normal_is_unit_vector(self):
        """Test that normal returns a unit vector."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        n_vec = spline.normal(spline.t[1])
        # Check it's a unit vector
        norm = np.linalg.norm(n_vec)
        assert norm == pytest.approx(1.0, abs=1e-6)

    def test_normal_perpendicular_to_tangent(self):
        """Test that normal is perpendicular to tangent."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 0), Point3D(2, 0, 0)]
        spline = Spline3D("test", points)

        t_vec = spline.tangent(spline.t[1])
        n_vec = spline.normal(spline.t[1])

        # Dot product should be zero (perpendicular)
        dot_product = np.dot(t_vec, n_vec)
        assert dot_product == pytest.approx(0.0, abs=1e-6)


class TestSpline3DSample:
    """Tests for sample method."""

    def test_sample_default(self):
        """Test sample method with default number of points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points)

        samples = spline.sample()
        assert len(samples) == 200  # Default n=200
        assert all(isinstance(p, Point3D) for p in samples)

    def test_sample_custom_n(self):
        """Test sample method with custom number of points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points)

        samples = spline.sample(n=50)
        assert len(samples) == 50

    def test_sample_includes_endpoints(self):
        """Test that sample includes endpoints."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points, parametrization="x")

        samples = spline.sample(n=10)
        # First sample should be close to first point
        assert samples[0].x == pytest.approx(0.0, abs=1e-6)
        # Last sample should be close to last point
        assert samples[-1].x == pytest.approx(2.0, abs=1e-6)


class TestSpline3DLength:
    """Tests for length method."""

    def test_length_returns_positive(self):
        """Test that length returns a positive value."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points)

        length = spline.length()
        assert length > 0

    def test_length_straight_line(self):
        """Test length for a straight line."""
        # Line of length 10
        points = [Point3D(0, 0, 0), Point3D(10, 0, 0)]
        spline = Spline3D("test", points, parametrization="x")

        length = spline.length()
        assert length == pytest.approx(10.0)


class TestSpline3DIsMonotonicX:
    """Tests for is_monotonic_x method."""

    def test_is_monotonic_x_true_increasing(self):
        """Test is_monotonic_x for increasing x."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        spline = Spline3D("test", points)

        assert spline.is_monotonic_x()

    def test_is_monotonic_x_true_decreasing(self):
        """Test is_monotonic_x for decreasing x."""
        points = [Point3D(2, 0, 0), Point3D(1, 1, 1), Point3D(0, 0, 2)]
        spline = Spline3D("test", points)

        assert spline.is_monotonic_x()

    def test_is_monotonic_x_false(self):
        """Test is_monotonic_x for non-monotonic x."""
        points = [Point3D(0, 0, 0), Point3D(2, 1, 1), Point3D(1, 0, 2)]
        spline = Spline3D("test", points)

        assert not spline.is_monotonic_x()


class TestSpline3DApplyRotationOnXAxis:
    """Tests for apply_rotation_on_x_axis method."""

    def test_rotation_zero_angle(self):
        """Test rotation with zero angle returns same points."""
        points = [Point3D(0, 1, 1), Point3D(1, 1, 1), Point3D(2, 1, 1)]
        spline = Spline3D("test", points)
        origin = Point3D(0, 0, 0)

        rotated_spline = spline.apply_rotation_on_x_axis(origin, 0)

        # Points should be unchanged
        for i, p in enumerate(rotated_spline.points):
            assert p.x == pytest.approx(points[i].x)
            assert p.y == pytest.approx(points[i].y)
            assert p.z == pytest.approx(points[i].z)

    def test_rotation_90_degrees(self):
        """Test rotation by 90 degrees around x-axis."""
        points = [Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(2, 0, 1)]
        spline = Spline3D("test", points)
        origin = Point3D(0, 0, 0)

        rotated_spline = spline.apply_rotation_on_x_axis(origin, 90)

        # z=1 should rotate to y=1 (approximately)
        for p in rotated_spline.points:
            assert p.z == pytest.approx(0.0, abs=1e-10)
            assert p.y == pytest.approx(1.0, abs=1e-10)

    def test_rotation_creates_new_spline(self):
        """Test that rotation creates a new spline object."""
        points = [Point3D(0, 1, 1), Point3D(1, 1, 1), Point3D(2, 1, 1)]
        spline = Spline3D("test", points)
        origin = Point3D(0, 0, 0)

        rotated_spline = spline.apply_rotation_on_x_axis(origin, 45)

        # Should be a different object
        assert rotated_spline is not spline
        assert rotated_spline.name == spline.name

    def test_rotation_around_custom_origin(self):
        """Test rotation around a custom origin point."""
        points = [Point3D(0, 1, 1), Point3D(1, 1, 1), Point3D(2, 1, 1)]
        spline = Spline3D("test", points)
        origin = Point3D(0, 1, 1)  # Same as first point

        rotated_spline = spline.apply_rotation_on_x_axis(origin, 90)

        # First point should remain at origin
        assert rotated_spline.points[0].y == pytest.approx(1.0, abs=1e-10)
        assert rotated_spline.points[0].z == pytest.approx(1.0, abs=1e-10)


class TestSpline3DEdgeCases:
    """Tests for edge cases."""

    def test_two_point_spline(self):
        """Test spline with minimum points (2)."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1)]
        spline = Spline3D("test", points)

        # Should create without error
        assert len(spline.points) == 2

        # Should be able to evaluate
        p = spline.eval_t(spline.t[0])
        assert p is not None

    def test_collinear_points(self):
        """Test spline with collinear points."""
        # All points on a line
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 2, 2)]
        spline = Spline3D("test", points)

        # Should create without error
        assert len(spline.points) == 3

        # Curvature should be near zero
        curv = spline.curvature(spline.t[1])
        assert curv == pytest.approx(0.0, abs=1e-6)
