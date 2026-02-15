"""Unit tests for the Curve class in geometry.curve module."""

import pytest
from src.geometry.curve import Curve
from src.geometry.point import Point3D


class TestCurveInit:
    """Tests for Curve initialization."""

    def test_init_without_mirrored_flag(self):
        """Test Curve initialization without mirrored flag."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test_curve", points)
        assert curve.name == "test_curve"
        assert len(curve.points) == 3
        assert curve.mirrored == False

    def test_init_with_mirrored_true(self):
        """Test Curve initialization with mirrored=True."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("mirrored_curve", points, mirrored=True)
        assert curve.mirrored == True
        assert curve.name == "mirrored_curve"

    def test_init_with_mirrored_false(self):
        """Test Curve initialization with mirrored=False."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("normal_curve", points, mirrored=False)
        assert curve.mirrored == False

    def test_curve_inherits_from_spline3d(self):
        """Test that Curve inherits from Spline3D."""
        from src.geometry.spline import Spline3D

        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points)
        assert isinstance(curve, Spline3D)

    def test_curve_has_spline3d_methods(self):
        """Test that Curve has all Spline3D methods."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points)

        # Check key methods exist
        assert hasattr(curve, "eval_t")
        assert hasattr(curve, "eval_x")
        assert hasattr(curve, "tangent")
        assert hasattr(curve, "curvature")
        assert hasattr(curve, "sample")

    def test_init_with_custom_bc_type(self):
        """Test Curve initialization with custom boundary condition."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points, bc_type="clamped", mirrored=True)
        assert curve.bc_type == "clamped"
        assert curve.mirrored == True

    def test_init_with_custom_parametrization(self):
        """Test Curve initialization with custom parametrization."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points, parametrization="chord", mirrored=False)
        assert curve.parametrization == "chord"
        assert curve.mirrored == False


class TestCurveUsage:
    """Tests for using Curve like a Spline3D."""

    def test_curve_can_be_evaluated(self):
        """Test that Curve can be evaluated at parameter t."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points, parametrization="x")

        p = curve.eval_t(1.0)
        assert p.x == pytest.approx(1.0)
        assert p.y == pytest.approx(1.0)
        assert p.z == pytest.approx(1.0)

    def test_curve_can_sample(self):
        """Test that Curve can sample points."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points)

        samples = curve.sample(n=50)
        assert len(samples) == 50

    def test_mirrored_flag_preserved_after_rotation(self):
        """Test that mirrored flag is accessible after operations."""
        points = [Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(2, 0, 1)]
        curve = Curve("test", points, mirrored=True)

        # Perform rotation
        origin = Point3D(0, 0, 0)
        rotated = curve.apply_rotation_on_x_axis(origin, 45)

        # Original curve should still have mirrored flag
        assert curve.mirrored == True
        # Rotated is a new Spline3D, may not have mirrored attribute
        # but that's okay - it's a new object


class TestCurveMirroredSemantics:
    """Tests for mirrored flag semantics."""

    def test_mirrored_flag_does_not_affect_geometry(self):
        """Test that mirrored flag doesn't affect geometric calculations."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve1 = Curve("test1", points, mirrored=False)
        curve2 = Curve("test2", points, mirrored=True)

        # Both should produce same geometric results
        p1 = curve1.eval_t(curve1.t[1])
        p2 = curve2.eval_t(curve2.t[1])

        assert p1.x == pytest.approx(p2.x)
        assert p1.y == pytest.approx(p2.y)
        assert p1.z == pytest.approx(p2.z)

    def test_mirrored_flag_is_metadata(self):
        """Test that mirrored flag acts as metadata."""
        points = [Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(2, 0, 2)]
        curve = Curve("test", points, mirrored=True)

        # It's just a flag, doesn't affect the curve itself
        assert curve.mirrored == True
        # The points themselves are unchanged
        assert curve.points[0].y == 0.0
        assert curve.points[1].y == 1.0
