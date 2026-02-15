"""Unit tests for the Point3D class in geometry.point module."""

import pytest
import numpy as np
from src.geometry.point import Point3D


class TestPoint3DInit:
    """Tests for Point3D initialization."""

    def test_init_with_integers(self):
        """Test Point3D initialization with integer values."""
        p = Point3D(1, 2, 3)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0
        assert isinstance(p.x, float)
        assert isinstance(p.y, float)
        assert isinstance(p.z, float)

    def test_init_with_floats(self):
        """Test Point3D initialization with float values."""
        p = Point3D(1.5, 2.5, 3.5)
        assert p.x == 1.5
        assert p.y == 2.5
        assert p.z == 3.5

    def test_init_origin(self):
        """Test Point3D initialization at origin."""
        p = Point3D(0, 0, 0)
        assert p.x == 0.0
        assert p.y == 0.0
        assert p.z == 0.0

    def test_init_negative_values(self):
        """Test Point3D initialization with negative values."""
        p = Point3D(-1.5, -2.5, -3.5)
        assert p.x == -1.5
        assert p.y == -2.5
        assert p.z == -3.5


class TestPoint3DProperties:
    """Tests for Point3D properties."""

    def test_coordinates_property(self):
        """Test coordinates property returns numpy array."""
        p = Point3D(1, 2, 3)
        coords = p.coordinates
        assert isinstance(coords, np.ndarray)
        assert len(coords) == 3
        assert coords[0] == 1.0
        assert coords[1] == 2.0
        assert coords[2] == 3.0

    def test_coordinates_order(self):
        """Test coordinates property order is [x, y, z]."""
        p = Point3D(5.5, 3.5, 1.5)
        coords = p.coordinates
        np.testing.assert_array_equal(coords, np.array([5.5, 3.5, 1.5]))


class TestPoint3DDistance:
    """Tests for distance calculations."""

    def test_distance_to_itself(self):
        """Test distance to the same point is zero."""
        p1 = Point3D(1, 2, 3)
        assert p1.distance_to(p1) == pytest.approx(0.0)

    def test_distance_to_along_x(self):
        """Test distance along x-axis."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(3, 0, 0)
        assert p1.distance_to(p2) == pytest.approx(3.0)

    def test_distance_to_along_y(self):
        """Test distance along y-axis."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(0, 4, 0)
        assert p1.distance_to(p2) == pytest.approx(4.0)

    def test_distance_to_along_z(self):
        """Test distance along z-axis."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(0, 0, 5)
        assert p1.distance_to(p2) == pytest.approx(5.0)

    def test_distance_to_3d(self):
        """Test 3D distance (3-4-5 triangle)."""
        p1 = Point3D(0, 0, 0)
        p2 = Point3D(2, 3, 6)
        # sqrt(4 + 9 + 36) = sqrt(49) = 7
        assert p1.distance_to(p2) == pytest.approx(7.0)

    def test_distance_to_origin(self):
        """Test distance to origin."""
        p = Point3D(3, 4, 0)
        assert p.distance_to_origin() == pytest.approx(5.0)

    def test_distance_to_origin_3d(self):
        """Test distance to origin in 3D."""
        p = Point3D(1, 2, 2)
        # sqrt(1 + 4 + 4) = sqrt(9) = 3
        assert p.distance_to_origin() == pytest.approx(3.0)


class TestPoint3DTranslate:
    """Tests for translation operations."""

    def test_translate_x(self):
        """Test translation along x-axis."""
        p = Point3D(1, 2, 3)
        p2 = p.translate(dx=5)
        assert p2.x == 6.0
        assert p2.y == 2.0
        assert p2.z == 3.0
        # Original should be unchanged
        assert p.x == 1.0

    def test_translate_y(self):
        """Test translation along y-axis."""
        p = Point3D(1, 2, 3)
        p2 = p.translate(dy=3)
        assert p2.x == 1.0
        assert p2.y == 5.0
        assert p2.z == 3.0

    def test_translate_z(self):
        """Test translation along z-axis."""
        p = Point3D(1, 2, 3)
        p2 = p.translate(dz=4)
        assert p2.x == 1.0
        assert p2.y == 2.0
        assert p2.z == 7.0

    def test_translate_all_axes(self):
        """Test translation along all axes."""
        p = Point3D(1, 2, 3)
        p2 = p.translate(dx=1, dy=2, dz=3)
        assert p2.x == 2.0
        assert p2.y == 4.0
        assert p2.z == 6.0

    def test_translate_negative(self):
        """Test translation with negative values."""
        p = Point3D(5, 5, 5)
        p2 = p.translate(dx=-2, dy=-3, dz=-1)
        assert p2.x == 3.0
        assert p2.y == 2.0
        assert p2.z == 4.0


class TestPoint3DRotation:
    """Tests for rotation operations."""

    def test_rotate_x_zero_angle(self):
        """Test rotation around x-axis with zero angle."""
        p = Point3D(1, 2, 3)
        p2 = p.rotate_x(0)
        assert p2.x == pytest.approx(1.0)
        assert p2.y == pytest.approx(2.0)
        assert p2.z == pytest.approx(3.0)

    def test_rotate_x_90_degrees(self):
        """Test rotation around x-axis by 90 degrees."""
        p = Point3D(1, 0, 1)
        p2 = p.rotate_x(90)
        assert p2.x == pytest.approx(1.0)
        assert p2.y == pytest.approx(1.0, abs=1e-10)
        assert p2.z == pytest.approx(0.0, abs=1e-10)

    def test_rotate_x_180_degrees(self):
        """Test rotation around x-axis by 180 degrees."""
        p = Point3D(1, 2, 3)
        p2 = p.rotate_x(180)
        assert p2.x == pytest.approx(1.0)
        assert p2.y == pytest.approx(-2.0)
        assert p2.z == pytest.approx(-3.0)

    def test_rotate_y_zero_angle(self):
        """Test rotation around y-axis with zero angle."""
        p = Point3D(1, 2, 3)
        p2 = p.rotate_y(0)
        assert p2.x == pytest.approx(1.0)
        assert p2.y == pytest.approx(2.0)
        assert p2.z == pytest.approx(3.0)

    def test_rotate_y_90_degrees(self):
        """Test rotation around y-axis by 90 degrees."""
        p = Point3D(1, 1, 0)
        p2 = p.rotate_y(90)
        assert p2.x == pytest.approx(0.0, abs=1e-10)
        assert p2.y == pytest.approx(1.0)
        assert p2.z == pytest.approx(-1.0, abs=1e-10)

    def test_rotate_z_zero_angle(self):
        """Test rotation around z-axis with zero angle."""
        p = Point3D(1, 2, 3)
        p2 = p.rotate_z(0)
        assert p2.x == pytest.approx(1.0)
        assert p2.y == pytest.approx(2.0)
        assert p2.z == pytest.approx(3.0)

    def test_rotate_z_90_degrees(self):
        """Test rotation around z-axis by 90 degrees."""
        p = Point3D(1, 0, 5)
        p2 = p.rotate_z(90)
        assert p2.x == pytest.approx(0.0, abs=1e-10)
        assert p2.y == pytest.approx(1.0)
        assert p2.z == pytest.approx(5.0)


class TestPoint3DScale:
    """Tests for scaling operations."""

    def test_scale_uniform(self):
        """Test uniform scaling."""
        p = Point3D(1, 2, 3)
        p2 = p.scale(sx=2, sy=2, sz=2)
        assert p2.x == 2.0
        assert p2.y == 4.0
        assert p2.z == 6.0

    def test_scale_x_only(self):
        """Test scaling only x-axis."""
        p = Point3D(2, 3, 4)
        p2 = p.scale(sx=3)
        assert p2.x == 6.0
        assert p2.y == 3.0
        assert p2.z == 4.0

    def test_scale_non_uniform(self):
        """Test non-uniform scaling."""
        p = Point3D(1, 2, 3)
        p2 = p.scale(sx=2, sy=3, sz=4)
        assert p2.x == 2.0
        assert p2.y == 6.0
        assert p2.z == 12.0

    def test_scale_zero(self):
        """Test scaling to zero."""
        p = Point3D(5, 5, 5)
        p2 = p.scale(sx=0, sy=0, sz=0)
        assert p2.x == 0.0
        assert p2.y == 0.0
        assert p2.z == 0.0


class TestPoint3DOperators:
    """Tests for operator overloading."""

    def test_repr(self):
        """Test string representation."""
        p = Point3D(1.234, 2.345, 3.456)
        repr_str = repr(p)
        assert "Point3D" in repr_str
        assert "1.234" in repr_str
        assert "2.345" in repr_str
        assert "3.456" in repr_str

    def test_equality_same_points(self):
        """Test equality operator for identical points."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(1, 2, 3)
        assert p1 == p2

    def test_equality_different_points(self):
        """Test equality operator for different points."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(1, 2, 4)
        assert p1 != p2

    def test_equality_with_tolerance(self):
        """Test equality with numerical tolerance."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(1.0000001, 2.0000001, 3.0000001)
        assert p1 == p2

    def test_equality_with_non_point(self):
        """Test equality with non-Point3D object."""
        p = Point3D(1, 2, 3)
        assert p != "not a point"
        assert p != [1, 2, 3]
        assert p != None

    def test_addition(self):
        """Test point addition."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(4, 5, 6)
        p3 = p1 + p2
        assert p3.x == 5.0
        assert p3.y == 7.0
        assert p3.z == 9.0

    def test_subtraction(self):
        """Test point subtraction."""
        p1 = Point3D(5, 7, 9)
        p2 = Point3D(1, 2, 3)
        p3 = p1 - p2
        assert p3.x == 4.0
        assert p3.y == 5.0
        assert p3.z == 6.0

    def test_multiplication_left(self):
        """Test point multiplication (left)."""
        p = Point3D(1, 2, 3)
        p2 = p * 3
        assert p2.x == 3.0
        assert p2.y == 6.0
        assert p2.z == 9.0

    def test_multiplication_right(self):
        """Test point multiplication (right)."""
        p = Point3D(1, 2, 3)
        p2 = 3 * p
        assert p2.x == 3.0
        assert p2.y == 6.0
        assert p2.z == 9.0

    def test_division(self):
        """Test point division."""
        p = Point3D(6, 9, 12)
        p2 = p / 3
        assert p2.x == 2.0
        assert p2.y == 3.0
        assert p2.z == 4.0

    def test_division_by_zero(self):
        """Test division by zero raises error."""
        p = Point3D(1, 2, 3)
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            p / 0


class TestPoint3DVectorOperations:
    """Tests for vector operations."""

    def test_dot_product_perpendicular(self):
        """Test dot product of perpendicular vectors."""
        p1 = Point3D(1, 0, 0)
        p2 = Point3D(0, 1, 0)
        assert p1.dot(p2) == pytest.approx(0.0)

    def test_dot_product_parallel(self):
        """Test dot product of parallel vectors."""
        p1 = Point3D(1, 0, 0)
        p2 = Point3D(2, 0, 0)
        assert p1.dot(p2) == pytest.approx(2.0)

    def test_dot_product_general(self):
        """Test dot product of general vectors."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(4, 5, 6)
        # 1*4 + 2*5 + 3*6 = 4 + 10 + 18 = 32
        assert p1.dot(p2) == pytest.approx(32.0)

    def test_cross_product_unit_vectors(self):
        """Test cross product of unit vectors."""
        p1 = Point3D(1, 0, 0)
        p2 = Point3D(0, 1, 0)
        p3 = p1.cross(p2)
        assert p3.x == pytest.approx(0.0)
        assert p3.y == pytest.approx(0.0)
        assert p3.z == pytest.approx(1.0)

    def test_cross_product_parallel_vectors(self):
        """Test cross product of parallel vectors is zero."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(2, 4, 6)
        p3 = p1.cross(p2)
        assert p3.x == pytest.approx(0.0)
        assert p3.y == pytest.approx(0.0)
        assert p3.z == pytest.approx(0.0)

    def test_cross_product_general(self):
        """Test cross product of general vectors."""
        p1 = Point3D(1, 2, 3)
        p2 = Point3D(4, 5, 6)
        p3 = p1.cross(p2)
        # i: 2*6 - 3*5 = 12 - 15 = -3
        # j: 3*4 - 1*6 = 12 - 6 = 6
        # k: 1*5 - 2*4 = 5 - 8 = -3
        assert p3.x == pytest.approx(-3.0)
        assert p3.y == pytest.approx(6.0)
        assert p3.z == pytest.approx(-3.0)


class TestPoint3DCopy:
    """Tests for copy operation."""

    def test_copy_creates_new_object(self):
        """Test that copy creates a new object."""
        p1 = Point3D(1, 2, 3)
        p2 = p1.copy()
        assert p1 == p2
        assert p1 is not p2

    def test_copy_independence(self):
        """Test that copied point is independent."""
        p1 = Point3D(1, 2, 3)
        p2 = p1.copy()
        p2.x = 10
        assert p1.x == 1.0
        assert p2.x == 10.0
